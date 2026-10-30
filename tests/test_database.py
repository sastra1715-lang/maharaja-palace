"""tests/test_database.py - ทดสอบตรรกะฐานข้อมูล (สั่งซื้อ คูปอง แต้ม สต็อก รายงาน)

รัน:  python -m unittest discover -s tests -v
ใช้ฐานข้อมูลชั่วคราว ไม่แตะ restaurant.db จริง
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db  # noqa: E402
import utils  # noqa: E402


class DbCase(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.remove(self.path)
        self._old = db.DB_PATH
        db.DB_PATH = self.path
        db.init_db()

    def tearDown(self):
        db.DB_PATH = self._old
        if os.path.exists(self.path):
            os.remove(self.path)

    def menu_id(self, name):
        return next(m["id"] for m in db.get_menu() if m["name"] == name)


class TestSettings(DbCase):
    def test_defaults_include_new_keys(self):
        s = db.get_all_settings()
        for k in ("shop_name", "tagline", "instagram", "facebook", "line", "tiktok", "youtube", "logo_data"):
            self.assertIn(k, s)

    def test_save_and_logo(self):
        db.save_settings({"shop_name": "Test Palace", "delivery_fee": "abc"})
        self.assertEqual(db.get_setting("shop_name"), "Test Palace")
        self.assertEqual(db.get_setting("delivery_fee"), "50")   # ค่าที่ไม่ใช่ตัวเลขถูกข้าม
        db.set_setting("logo_data", "QUJD")
        self.assertEqual(db.get_all_settings()["logo_data"], "QUJD")


class TestOrders(DbCase):
    def test_coupon(self):
        self.assertEqual(db.apply_coupon("welcome10", 500)[0], 50)
        self.assertEqual(db.apply_coupon("WELCOME10", 100)[0], 0)      # ไม่ถึงขั้นต่ำ
        self.assertEqual(db.apply_coupon("NOPE", 500)[0], 0)
        self.assertEqual(len(db.get_active_coupons()), 1)

    def test_order_flow_points_and_receipt(self):
        bc = self.menu_id("Butter Chicken")                  # 259 บาท
        oid = db.create_order("สมชาย", "0812345678", "กรุงเทพ", "", {bc: 2}, "14:35", "WELCOME10", db.TYPE_DELIVERY)
        o = db.track_order(oid, "0812345678")
        self.assertEqual(o["subtotal"], 518)
        self.assertEqual(o["discount"], 52)
        self.assertEqual(o["delivery_fee"], 50)               # 466 < 800 จึงมีค่าส่ง
        self.assertEqual(o["total"], 516)
        self.assertEqual(o["order_status"], db.ST_WAIT)
        db.confirm_payment(oid)
        o = db.track_order(oid, "0812345678")
        self.assertEqual(o["order_status"], db.ST_COOK)
        self.assertEqual(o["receipt_no"], f"RC{oid:06d}")
        self.assertEqual(o["points_earned"], 51)               # 516 // 10 x1.0
        self.assertEqual(db.get_member("0812345678")["points"], 51)

    def test_free_delivery_and_dine_in(self):
        lamb = self.menu_id("Lamb Rogan Josh")                 # 329 x3 = 987
        oid = db.create_order("A", "0800000000", "-", "", {lamb: 3}, "10:00", "", db.TYPE_DELIVERY)
        self.assertEqual(db.track_order(oid, "0800000000")["delivery_fee"], 0)
        oid2 = db.create_order("B", "0800000001", "-", "", {lamb: 1}, "10:00", "", db.TYPE_DINE, "5")
        self.assertEqual(db.track_order(oid2, "0800000001")["delivery_fee"], 0)

    def test_stock_limit_and_restore_on_reject(self):
        sam = self.menu_id("Samosa")
        with db.conn() as c:
            c.execute("UPDATE menu SET stock=3 WHERE id=?", (sam,))
        self.assertIsNone(db.create_order("A", "0800000002", "-", "", {sam: 4}, "1", "", db.TYPE_PICKUP))
        oid = db.create_order("A", "0800000002", "-", "", {sam: 2}, "1", "", db.TYPE_PICKUP)
        self.assertEqual(next(m for m in db.get_menu() if m["id"] == sam)["stock"], 1)
        db.reject_payment(oid)
        self.assertEqual(next(m for m in db.get_menu() if m["id"] == sam)["stock"], 3)
        self.assertEqual(db.track_order(oid, "0800000002")["order_status"], db.ST_CANCEL)

    def test_status_requires_payment(self):
        sam = self.menu_id("Samosa")
        oid = db.create_order("A", "0800000003", "-", "", {sam: 1}, "1", "", db.TYPE_PICKUP)
        db.set_status(oid, db.ST_DONE)                         # ยังไม่ชำระ ต้องไม่เปลี่ยน
        self.assertEqual(db.track_order(oid, "0800000003")["order_status"], db.ST_WAIT)
        db.confirm_payment(oid)
        db.set_status(oid, db.ST_READY)
        self.assertEqual(db.track_order(oid, "0800000003")["order_status"], db.ST_READY)

    def test_steps_by_type(self):
        self.assertNotIn(db.ST_SHIP, db.steps_for(db.TYPE_PICKUP))
        self.assertIn(db.ST_SHIP, db.steps_for(db.TYPE_DELIVERY))


class TestPayment(DbCase):
    def test_transfer_with_slip(self):
        sam = self.menu_id("Samosa")
        oid = db.create_order("A", "0800000010", "-", "", {sam: 1}, "-", "", db.TYPE_PICKUP,
                              payment_method=db.PAY_TRANSFER, slip=b"\x89PNGdata", slip_mime="image/png")
        o = db.track_order(oid, "0800000010")
        self.assertEqual(o["payment_method"], db.PAY_TRANSFER)
        sl = db.get_slip(oid)
        self.assertEqual(bytes(sl["data"]), b"\x89PNGdata")
        self.assertEqual(sl["mime"], "image/png")

    def test_cash_has_no_slip_and_confirm_works(self):
        sam = self.menu_id("Samosa")
        oid = db.create_order("A", "0800000011", "-", "", {sam: 1}, "-", "", db.TYPE_DINE, "2",
                              payment_method=db.PAY_CASH)
        self.assertFalse(db.slip_exists(oid))
        self.assertEqual(db.track_order(oid, "0800000011")["payment_method"], db.PAY_CASH)
        db.confirm_payment(oid)
        self.assertEqual(db.track_order(oid, "0800000011")["order_status"], db.ST_COOK)

    def test_attach_slip_later_rules(self):
        sam = self.menu_id("Samosa")
        oid = db.create_order("A", "0800000012", "-", "", {sam: 1}, "-", "", db.TYPE_PICKUP)
        self.assertFalse(db.attach_slip(oid, "0999999999", b"x", "image/png"))   # เบอร์ไม่ตรง
        self.assertTrue(db.attach_slip(oid, "0800000012", b"x", "image/png"))
        self.assertTrue(db.slip_exists(oid))
        db.confirm_payment(oid)
        self.assertFalse(db.attach_slip(oid, "0800000012", b"y", "image/png"))   # ยืนยันแล้วเปลี่ยนไม่ได้

    def test_split(self):
        sam = self.menu_id("Samosa")
        db.create_order("A", "0800000013", "-", "", {sam: 1}, "-", "", db.TYPE_PICKUP, payment_method=db.PAY_CASH)
        self.assertEqual(dict(db.payment_split())[db.PAY_CASH], 1)


class TestReports(DbCase):
    def test_reports(self):
        bc, nan = self.menu_id("Butter Chicken"), self.menu_id("Garlic Naan")
        oid = db.create_order("A", "0800000004", "-", "", {bc: 1, nan: 2}, "1", "", db.TYPE_DINE, "3")
        db.confirm_payment(oid)
        t = db.today_stats()
        self.assertEqual(t["orders"], 1)
        self.assertEqual(t["revenue"], 259 + 118)
        cats = dict(db.revenue_by_category())
        self.assertEqual(cats["แกงอินเดีย"], 259)
        self.assertEqual(cats["ข้าวและขนมปัง"], 118)
        self.assertEqual(dict(db.order_type_split())[db.TYPE_DINE], 1)


class TestUtils(unittest.TestCase):
    def test_phone(self):
        self.assertTrue(utils.valid_phone("081-234-5678"))
        self.assertTrue(utils.valid_phone("+66 81 234 5678"))
        self.assertFalse(utils.valid_phone("123"))
        self.assertFalse(utils.valid_phone(""))
        self.assertEqual(utils.digits_only("081-234"), "081234")

    def test_clean_text(self):
        self.assertEqual(utils.clean_text("  a   b \n c ", 10), "a b c")
        self.assertEqual(len(utils.clean_text("x" * 500, 50)), 50)


class TestOpenHours(unittest.TestCase):
    def at(self, h, m=0):
        return datetime(2026, 10, 24, h, m)

    def test_normal_hours(self):
        t = "10:00–22:00 น."
        self.assertTrue(utils.is_open_now(t, self.at(12)))
        self.assertFalse(utils.is_open_now(t, self.at(22)))
        self.assertFalse(utils.is_open_now(t, self.at(9, 59)))
        self.assertTrue(utils.is_open_now(t, self.at(10)))

    def test_overnight_and_unparseable(self):
        t = "18:00-02:00"
        self.assertTrue(utils.is_open_now(t, self.at(23)))
        self.assertTrue(utils.is_open_now(t, self.at(1, 30)))
        self.assertFalse(utils.is_open_now(t, self.at(12)))
        self.assertIsNone(utils.is_open_now("เปิดทุกวัน", self.at(12)))
        self.assertIsNone(utils.parse_hours("99:00-22:00"))


if __name__ == "__main__":
    unittest.main()
