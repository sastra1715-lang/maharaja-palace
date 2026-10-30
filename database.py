"""database.py - ชั้นฐานข้อมูล SQLite ของร้านอาหารอินเดีย"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = "restaurant.db"
DELIVERY_FEE = 50          # ค่าส่งมาตรฐาน (บาท)
FREE_DELIVERY_OVER = 800   # ซื้อครบเท่านี้ส่งฟรี

# สถานะการชำระเงิน
PAY_PENDING, PAY_OK, PAY_FAIL = "รอแอดมินตรวจสอบ", "ชำระเงินแล้ว", "ไม่ผ่านการตรวจสอบ"
# วิธีชำระเงินที่ลูกค้าเลือกได้ (โอนเงินต้องแนบสลิป · เงินสดจ่ายที่ร้าน/ปลายทาง)
PAY_TRANSFER, PAY_CASH = "โอนเงิน", "เงินสด"
PAYMENT_METHODS = [PAY_TRANSFER, PAY_CASH]
# สถานะออเดอร์
ST_READY = "อาหารพร้อมแล้ว"
TYPE_DELIVERY, TYPE_PICKUP, TYPE_DINE = "จัดส่ง", "รับที่ร้าน", "ทานที่ร้าน"
ST_WAIT, ST_COOK, ST_SHIP, ST_DONE, ST_CANCEL = (
    "รอยืนยันการชำระเงิน", "กำลังเตรียมอาหาร", "กำลังจัดส่ง", "จัดส่งสำเร็จ", "ยกเลิก")


def steps_for(order_type):
    """ขั้นตอนของออเดอร์ตามรูปแบบการรับอาหาร"""
    if order_type in (TYPE_PICKUP, TYPE_DINE):
        return [ST_WAIT, ST_COOK, ST_READY, ST_DONE]
    return [ST_WAIT, ST_COOK, ST_READY, ST_SHIP, ST_DONE]


TIERS = [(0, "🥈 Silver", 1.0), (2000, "🥇 Gold", 1.5), (5000, "💎 Platinum", 2.0)]  # (ยอดสะสม, ระดับ, ตัวคูณแต้ม)
DEFAULT_SETTINGS = {
    "shop_name": "Maharaja Palace", "open_hours": "10:00–22:00 น.", "phone": "0XX-XXX-XXXX",
    "address": "(ใส่ที่อยู่ร้าน)", "pay_note": "ชื่อบัญชี: (ใส่ชื่อร้าน) · ธนาคาร: (ใส่ชื่อธนาคาร) · เลขบัญชี: (ใส่เลขบัญชี)",
    "promo_banner": "ใช้โค้ด WELCOME10 ลด 10% สำหรับลูกค้าใหม่ · สะสมแต้มทุกออเดอร์",
    "about_text": "ร้านอาหารอินเดียต้นตำรับ ปรุงด้วยเครื่องเทศสดและเตาดินแบบดั้งเดิม ใส่ใจทุกจาน เพื่อประสบการณ์รสชาติระดับมหาราชา",
    "delivery_fee": "50", "free_over": "800", "points_rate": "10",
    # --- ส่วนที่เพิ่มสำหรับหน้าตาใหม่ (ไม่กระทบข้อมูลเดิม) ---
    "tagline": "ROYAL INDIAN CUISINE · อาหารอินเดียรสต้นตำรับ",
    "instagram": "https://www.instagram.com/",
    "facebook": "https://www.facebook.com/",
    "line": "https://line.me/",
    "tiktok": "https://www.tiktok.com/",
    "youtube": "https://www.youtube.com/",
    "x_twitter": "",
    "logo_data": "", "logo_mime": ""}

SEED = [
    ("Samosa", "สมอซ่า", "ของทานเล่น", "แป้งทอดกรอบไส้มันฝรั่งและถั่วลันเตา เสิร์ฟพร้อมซอสมิ้นต์", 89, "🥟"),
    ("Onion Bhaji", "หอมใหญ่ชุบแป้งทอด", "ของทานเล่น", "หอมใหญ่ทอดกรอบหอมเครื่องเทศ", 79, "🧅"),
    ("Paneer Tikka", "ปาเนียร์ทิกก้า", "ทันดูรี", "ชีสปาเนียร์หมักโยเกิร์ตย่างเตาดิน", 189, "🧀"),
    ("Chicken Tikka", "ไก่ทิกก้า", "ทันดูรี", "อกไก่หมักเครื่องเทศย่างเตาดิน", 199, "🍗"),
    ("Tandoori Chicken", "ไก่ทันดูรี", "ทันดูรี", "ไก่ทั้งตัวหมักโยเกิร์ตและมาซาลา ย่างหอมควัน", 249, "🔥"),
    ("Seekh Kebab", "เสียกเคบับ", "ทันดูรี", "เนื้อสับปรุงรสเสียบไม้ย่าง", 219, "🍢"),
    ("Butter Chicken", "บัตเตอร์ชิคเก้น", "แกงอินเดีย", "ไก่ในซอสมะเขือเทศครีมเนยละมุน", 259, "🍛"),
    ("Chicken Tikka Masala", "ไก่ทิกก้ามาซาลา", "แกงอินเดีย", "ไก่ย่างในซอสมาซาลารสเข้มข้น", 259, "🍛"),
    ("Palak Paneer", "ปาลักปาเนียร์", "แกงอินเดีย", "ชีสปาเนียร์ในแกงผักโขมเนียนนุ่ม", 219, "🥬"),
    ("Dal Makhani", "ดาลมาคานี", "แกงอินเดีย", "ถั่วดำและถั่วแดงเคี่ยวช้า หอมเนย", 169, "🫘"),
    ("Lamb Rogan Josh", "แกะโรแกนโจช", "แกงอินเดีย", "เนื้อแกะตุ๋นซอสเครื่องเทศสไตล์แคชเมียร์", 329, "🐑"),
    ("Chana Masala", "ชานามาซาลา", "แกงอินเดีย", "ถั่วลูกไก่ในซอสมะเขือเทศเครื่องเทศ", 149, "🌶️"),
    ("Fish Curry", "แกงปลาอินเดีย", "แกงอินเดีย", "ปลาในแกงมะพร้าวสไตล์อินเดียใต้", 289, "🐟"),
    ("Chicken Biryani", "ข้าวหมกไก่บิรยานี", "ข้าวและขนมปัง", "ข้าวบาสมาติหมกไก่ หอมหญ้าฝรั่น", 239, "🍚"),
    ("Lamb Biryani", "ข้าวหมกแกะบิรยานี", "ข้าวและขนมปัง", "ข้าวบาสมาติหมกเนื้อแกะนุ่ม", 289, "🍚"),
    ("Garlic Naan", "นานกระเทียม", "ข้าวและขนมปัง", "แป้งนานอบเตาดินทาเนยกระเทียม", 59, "🫓"),
    ("Butter Naan", "นานเนย", "ข้าวและขนมปัง", "แป้งนานนุ่มทาเนย", 49, "🫓"),
    ("Jeera Rice", "ข้าวผัดเมล็ดยี่หร่า", "ข้าวและขนมปัง", "ข้าวบาสมาติหอมยี่หร่า", 69, "🍚"),
    ("Gulab Jamun", "กุหลาบจามุน", "ของหวานและเครื่องดื่ม", "ขนมนมทอดแช่น้ำเชื่อมกลิ่นกุหลาบ", 99, "🍮"),
    ("Mango Lassi", "มังโกลัสซี่", "ของหวานและเครื่องดื่ม", "โยเกิร์ตปั่นมะม่วงสุก", 99, "🥭"),
]


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db():
    with conn() as c:
        c.executescript(f"""
        CREATE TABLE IF NOT EXISTS menu(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, name_th TEXT, category TEXT,
            description TEXT, price REAL NOT NULL,
            emoji TEXT DEFAULT '🍛', available INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT, phone TEXT, address TEXT, note TEXT,
            subtotal REAL, delivery_fee REAL, total REAL,
            payment_status TEXT DEFAULT '{PAY_PENDING}',
            order_status TEXT DEFAULT '{ST_WAIT}',
            rider_name TEXT, rider_phone TEXT,
            created_at TEXT, updated_at TEXT);
        CREATE TABLE IF NOT EXISTS order_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER, menu_id INTEGER, name TEXT, price REAL, qty INTEGER);
        CREATE TABLE IF NOT EXISTS coupons(
            code TEXT PRIMARY KEY, percent REAL, min_total REAL DEFAULT 0, active INTEGER DEFAULT 1);
        """)
        for col in ("transfer_time TEXT", "coupon_code TEXT", "discount REAL DEFAULT 0",
                    "receipt_no TEXT", "rating INTEGER", "review TEXT"):
            try:
                c.execute(f"ALTER TABLE orders ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass  # มีคอลัมน์อยู่แล้ว
        if c.execute("SELECT COUNT(*) FROM coupons").fetchone()[0] == 0:
            c.execute("INSERT INTO coupons VALUES('WELCOME10', 10, 300, 1)")
        if c.execute("SELECT COUNT(*) FROM menu").fetchone()[0] == 0:
            c.executemany(
                "INSERT INTO menu(name,name_th,category,description,price,emoji) VALUES(?,?,?,?,?,?)", SEED)
        _migrate2(c)
        c.execute("""CREATE TABLE IF NOT EXISTS reservations(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, date TEXT, time TEXT,
            guests INTEGER, note TEXT, status TEXT DEFAULT 'รอยืนยัน', created_at TEXT)""")
        for col in ("order_type TEXT DEFAULT 'จัดส่ง'", "table_no TEXT"):
            try:
                c.execute(f"ALTER TABLE orders ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass
        try:
            c.execute("ALTER TABLE menu ADD COLUMN stock INTEGER DEFAULT -1")  # -1 = ไม่จำกัด
        except sqlite3.OperationalError:
            pass
        try:
            c.execute("ALTER TABLE menu ADD COLUMN tag TEXT")
            veg = ("Samosa", "Onion Bhaji", "Paneer Tikka", "Palak Paneer", "Dal Makhani", "Chana Masala",
                   "Jeera Rice", "Butter Naan", "Gulab Jamun", "Mango Lassi")
            c.execute(f"UPDATE menu SET tag='🌱 มังสวิรัติ' WHERE name IN ({','.join('?' * len(veg))})", veg)
            c.execute("UPDATE menu SET tag='🌶️ เผ็ด' WHERE name IN ('Lamb Rogan Josh','Fish Curry')")
            c.execute("UPDATE menu SET tag='🔥 ขายดี' WHERE name IN ('Butter Chicken','Chicken Biryani','Garlic Naan')")
        except sqlite3.OperationalError:
            pass
        # --- วิธีชำระเงิน + สลิปโอนเงิน (เพิ่มภายหลัง ข้อมูลเดิมไม่หาย) ---
        try:
            c.execute(f"ALTER TABLE orders ADD COLUMN payment_method TEXT DEFAULT '{PAY_TRANSFER}'")
        except sqlite3.OperationalError:
            pass
        c.execute("""CREATE TABLE IF NOT EXISTS slips(
            order_id INTEGER PRIMARY KEY, mime TEXT, data BLOB, uploaded_at TEXT)""")


# ---------- เมนู ----------
def get_menu(only_available=False):
    q = "SELECT * FROM menu" + (" WHERE available=1 AND stock<>0" if only_available else "") + " ORDER BY id"
    with conn() as c:
        return c.execute(q).fetchall()


def add_menu(name, name_th, category, description, price, emoji, stock=-1, tag=""):
    with conn() as c:
        return c.execute("INSERT INTO menu(name,name_th,category,description,price,emoji,stock,tag) VALUES(?,?,?,?,?,?,?,?)",
                  (name, name_th, category, description, price, emoji, stock, tag)).lastrowid


def update_menu(mid, name, name_th, category, description, price, emoji, available, stock=-1, tag=""):
    with conn() as c:
        c.execute("""UPDATE menu SET name=?,name_th=?,category=?,description=?,price=?,emoji=?,available=?,
                     stock=?,tag=? WHERE id=?""",
                  (name, name_th, category, description, price, emoji, int(available), stock, tag, mid))


def delete_menu(mid):
    with conn() as c:
        c.execute("DELETE FROM menu WHERE id=?", (mid,))


# ---------- ออเดอร์ ----------
def calc_fee(subtotal):
    return 0 if subtotal >= free_over() else float(get_setting("delivery_fee"))


def free_over():
    return float(get_setting("free_over"))


def create_order(name, phone, address, note, cart, transfer_time, coupon="", order_type=TYPE_DELIVERY, table_no="", points_use=0,
                 payment_method=PAY_TRANSFER, slip=None, slip_mime=None):
    """cart = {menu_id: qty}  ราคาดึงจากฐานข้อมูลเสมอ ไม่เชื่อค่าจากหน้าเว็บ"""
    with conn() as c:
        rows = {r["id"]: r for r in c.execute("SELECT * FROM menu WHERE available=1")}
        items = [(rows[m], q) for m, q in cart.items() if m in rows and q > 0]
        if not items:
            return None
        if any(r["stock"] >= 0 and q > r["stock"] for r, q in items):
            return None  # สต็อกไม่พอ
        subtotal = sum(r["price"] * q for r, q in items)
        discount, _ = apply_coupon(coupon, subtotal)
        mrow = c.execute("SELECT points FROM members WHERE phone=?", (phone,)).fetchone()
        pts = int(max(0, min(points_use, mrow["points"] if mrow else 0, subtotal - discount)))  # 1 แต้ม = 1 บาท
        fee = calc_fee(subtotal - discount - pts) if order_type == TYPE_DELIVERY else 0
        cur = c.execute(
            """INSERT INTO orders(customer_name,phone,address,note,subtotal,delivery_fee,total,
               transfer_time,coupon_code,discount,order_type,table_no,points_used,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (name, phone, address, note, subtotal, fee, subtotal - discount - pts + fee, transfer_time,
             coupon.strip().upper() if discount else None, discount, order_type, table_no, pts, now(), now()))
        oid = cur.lastrowid
        c.execute("UPDATE orders SET payment_method=? WHERE id=?", (payment_method, oid))
        if slip:   # สลิปโอนเงินเก็บแยกตาราง เพื่อไม่ให้ตารางออเดอร์ใหญ่เกินจำเป็น
            c.execute("INSERT OR REPLACE INTO slips(order_id,mime,data,uploaded_at) VALUES(?,?,?,?)",
                      (oid, slip_mime or "image/jpeg", slip, now()))
        c.executemany("INSERT INTO order_items(order_id,menu_id,name,price,qty) VALUES(?,?,?,?,?)",
                      [(oid, r["id"], r["name"], r["price"], q) for r, q in items])
        c.executemany("UPDATE menu SET stock=stock-? WHERE id=? AND stock>=0", [(q, r["id"]) for r, q in items])
        c.execute("INSERT INTO members(phone,name,created_at) VALUES(?,?,?) "
                  "ON CONFLICT(phone) DO UPDATE SET name=excluded.name", (phone, name, now()))
        if pts:
            c.execute("UPDATE members SET points=points-? WHERE phone=?", (pts, phone))
        return oid


def get_orders(status=None):
    with conn() as c:
        if status:
            return c.execute("SELECT * FROM orders WHERE order_status=? ORDER BY id DESC", (status,)).fetchall()
        return c.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()


def get_order_items(oid):
    with conn() as c:
        return c.execute("SELECT * FROM order_items WHERE order_id=?", (oid,)).fetchall()


def track_order(oid, phone):
    with conn() as c:
        return c.execute("SELECT * FROM orders WHERE id=? AND phone=?", (oid, phone.strip())).fetchone()


def _log(c, msg):
    c.execute("INSERT INTO logs(ts,msg) VALUES(?,?)", (now(), msg))


def confirm_payment(oid):
    with conn() as c:
        o = c.execute("SELECT * FROM orders WHERE id=? AND order_status=?", (oid, ST_WAIT)).fetchone()
        if not o:
            return
        m = c.execute("SELECT total_spent FROM members WHERE phone=?", (o["phone"],)).fetchone()
        mult = tier_info(m["total_spent"] if m else 0)[1]
        earned = int(o["total"] // float(get_setting("points_rate")) * mult)
        c.execute("""UPDATE orders SET payment_status=?, order_status=?, receipt_no=?, points_earned=?, updated_at=?
                     WHERE id=?""", (PAY_OK, ST_COOK, f"RC{oid:06d}", earned, now(), oid))
        c.execute("UPDATE members SET points=points+?, total_spent=total_spent+? WHERE phone=?",
                  (earned, o["total"], o["phone"]))
        _log(c, f"ยืนยันการชำระเงิน ออเดอร์ #{oid} [{o['payment_method'] or PAY_TRANSFER}] ({o['total']:,.0f} บาท, ให้ {earned} แต้ม)")


def reject_payment(oid):
    with conn() as c:
        o = c.execute("SELECT * FROM orders WHERE id=? AND order_status=?", (oid, ST_WAIT)).fetchone()
        if not o:
            return
        c.execute("UPDATE orders SET payment_status=?, order_status=?, updated_at=? WHERE id=?",
                  (PAY_FAIL, ST_CANCEL, now(), oid))
        if o["points_used"]:
            c.execute("UPDATE members SET points=points+? WHERE phone=?", (o["points_used"], o["phone"]))
        for it in c.execute("SELECT * FROM order_items WHERE order_id=?", (oid,)).fetchall():
            c.execute("UPDATE menu SET stock=stock+? WHERE id=? AND stock>=0", (it["qty"], it["menu_id"]))
        _log(c, f"ปฏิเสธการชำระเงิน ออเดอร์ #{oid} (คืนแต้มและสต็อกแล้ว)")


def set_status(oid, status, rider_name=None, rider_phone=None):
    """เปลี่ยนสถานะได้เฉพาะออเดอร์ที่ชำระเงินแล้วเท่านั้น"""
    with conn() as c:
        c.execute("""UPDATE orders SET order_status=?, rider_name=COALESCE(?,rider_name),
                     rider_phone=COALESCE(?,rider_phone), updated_at=? WHERE id=? AND payment_status=?""",
                  (status, rider_name, rider_phone, now(), oid, PAY_OK))
        _log(c, f"ออเดอร์ #{oid} → {status}" + (f" (ไรเดอร์ {rider_name})" if rider_name else ""))


def stats():
    with conn() as c:
        r = c.execute(f"""SELECT COUNT(*) n,
            COALESCE(SUM(CASE WHEN payment_status='{PAY_OK}' THEN total END),0) revenue,
            SUM(CASE WHEN order_status='{ST_WAIT}' THEN 1 ELSE 0 END) waiting,
            SUM(CASE WHEN order_status='{ST_SHIP}' THEN 1 ELSE 0 END) shipping FROM orders""").fetchone()
        return {"orders": r["n"], "revenue": r["revenue"], "waiting": r["waiting"] or 0,
                "shipping": r["shipping"] or 0}


# ---------- คูปองส่วนลด ----------
def apply_coupon(code, subtotal):
    code = (code or "").strip().upper()
    if not code:
        return 0, ""
    with conn() as c:
        r = c.execute("SELECT * FROM coupons WHERE code=? AND active=1", (code,)).fetchone()
    if not r:
        return 0, "ไม่พบโค้ดนี้หรือโค้ดถูกปิดใช้งาน"
    if subtotal < r["min_total"]:
        return 0, f"โค้ดนี้ใช้ได้เมื่อซื้อครบ ฿{r['min_total']:,.0f}"
    return round(subtotal * r["percent"] / 100), f"ใช้โค้ด {code} ลด {r['percent']:.0f}%"


def get_coupons():
    with conn() as c:
        return c.execute("SELECT * FROM coupons ORDER BY code").fetchall()


def save_coupon(code, percent, min_total, active=True):
    with conn() as c:
        c.execute("INSERT OR REPLACE INTO coupons VALUES(?,?,?,?)",
                  (code.strip().upper(), percent, min_total, int(active)))


def delete_coupon(code):
    with conn() as c:
        c.execute("DELETE FROM coupons WHERE code=?", (code,))


# ---------- รีวิว ----------
def add_review(oid, rating, review):
    with conn() as c:
        c.execute("UPDATE orders SET rating=?, review=? WHERE id=? AND order_status=? AND rating IS NULL",
                  (rating, review, oid, ST_DONE))


def get_reviews():
    with conn() as c:
        return c.execute("SELECT id, customer_name, rating, review, updated_at FROM orders "
                         "WHERE rating IS NOT NULL ORDER BY updated_at DESC").fetchall()


# ---------- จองโต๊ะ ----------
def create_reservation(name, phone, date, time, guests, note):
    with conn() as c:
        return c.execute("INSERT INTO reservations(name,phone,date,time,guests,note,created_at) VALUES(?,?,?,?,?,?,?)",
                         (name, phone, date, time, guests, note, now())).lastrowid


def get_reservations(phone=None):
    with conn() as c:
        if phone:
            return c.execute("SELECT * FROM reservations WHERE phone=? ORDER BY id DESC", (phone.strip(),)).fetchall()
        return c.execute("SELECT * FROM reservations ORDER BY date, time").fetchall()


def set_reservation(rid, status):
    with conn() as c:
        c.execute("UPDATE reservations SET status=? WHERE id=?", (status, rid))


# ---------- รายงาน ----------
def daily_revenue():
    with conn() as c:
        return [tuple(r) for r in c.execute(
            "SELECT substr(created_at,1,10), SUM(total) FROM orders WHERE payment_status=? GROUP BY 1 ORDER BY 1",
            (PAY_OK,))]


def revenue_by_month():
    """รายได้รายเดือน [(ปี-เดือน, รายได้, จำนวนออเดอร์)] เฉพาะออเดอร์ที่ชำระเงินแล้ว"""
    with conn() as c:
        return [tuple(r) for r in c.execute(
            "SELECT substr(created_at,1,7), SUM(total), COUNT(*) FROM orders WHERE payment_status=? GROUP BY 1 ORDER BY 1",
            (PAY_OK,))]


def revenue_by_year():
    """รายได้รายปี [(ปี, รายได้, จำนวนออเดอร์)] เฉพาะออเดอร์ที่ชำระเงินแล้ว"""
    with conn() as c:
        return [tuple(r) for r in c.execute(
            "SELECT substr(created_at,1,4), SUM(total), COUNT(*) FROM orders WHERE payment_status=? GROUP BY 1 ORDER BY 1",
            (PAY_OK,))]


def period_stats():
    """ยอดเดือนนี้และปีนี้: {'month': (รายได้, ออเดอร์), 'year': (รายได้, ออเดอร์)}"""
    ym, y = now()[:7], now()[:4]
    out = {}
    with conn() as c:
        for key, n, val in (("month", 7, ym), ("year", 4, y)):
            r = c.execute("SELECT COALESCE(SUM(total),0), COUNT(*) FROM orders WHERE payment_status=? AND substr(created_at,1,?)=?",
                          (PAY_OK, n, val)).fetchone()
            out[key] = (r[0], r[1])
    return out


def top_items(limit=8):
    with conn() as c:
        return [tuple(r) for r in c.execute(
            """SELECT i.name, SUM(i.qty) q FROM order_items i JOIN orders o ON o.id=i.order_id
               WHERE o.payment_status=? GROUP BY i.name ORDER BY q DESC LIMIT ?""", (PAY_OK, limit))]


def _migrate2(c):
    c.executescript("""
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS members(phone TEXT PRIMARY KEY, name TEXT, points INTEGER DEFAULT 0,
        total_spent REAL DEFAULT 0, created_at TEXT);
    CREATE TABLE IF NOT EXISTS riders(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, active INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT,
        description TEXT, amount REAL);
    CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, msg TEXT);""")
    for t, col in (("orders", "points_used INTEGER DEFAULT 0"), ("orders", "points_earned INTEGER DEFAULT 0"),
                   ("menu", "image BLOB")):
        try:
            c.execute(f"ALTER TABLE {t} ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass
    for k, v in DEFAULT_SETTINGS.items():
        c.execute("INSERT OR IGNORE INTO settings VALUES(?,?)", (k, v))


# ---------- ตั้งค่าร้าน / บันทึกกิจกรรม ----------
def get_setting(k):
    with conn() as c:
        r = c.execute("SELECT value FROM settings WHERE key=?", (k,)).fetchone()
    return r["value"] if r else DEFAULT_SETTINGS.get(k, "")


def get_all_settings():
    """อ่านการตั้งค่าทั้งหมดในครั้งเดียว (ค่าที่ไม่มีใช้ค่าเริ่มต้น)"""
    out = dict(DEFAULT_SETTINGS)
    with conn() as c:
        for r in c.execute("SELECT key, value FROM settings"):
            out[r["key"]] = r["value"]
    return out


def set_setting(k, v):
    """บันทึกการตั้งค่าเดี่ยว (ใช้กับโลโก้ที่เป็นข้อมูลขนาดใหญ่)"""
    with conn() as c:
        c.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (k, str(v)))


def get_active_coupons():
    with conn() as c:
        return c.execute("SELECT * FROM coupons WHERE active=1 ORDER BY percent DESC").fetchall()


def save_settings(vals):
    with conn() as c:
        for k, v in vals.items():
            if k in ("delivery_fee", "free_over", "points_rate"):
                try:
                    if float(v) <= 0 and k == "points_rate":
                        continue
                    float(v)
                except ValueError:
                    continue
            c.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (k, str(v).strip()))
        _log(c, "แก้ไขการตั้งค่าร้าน")


def get_logs(n=60):
    with conn() as c:
        return c.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (n,)).fetchall()


# ---------- สมาชิก & แต้มสะสม ----------
def tier_info(spent):
    cur = TIERS[0]
    for t in TIERS:
        if spent >= t[0]:
            cur = t
    return cur[1], cur[2]


def next_tier(spent):
    return next(((t[1], t[0]) for t in TIERS if t[0] > spent), None)


def get_member(phone):
    with conn() as c:
        return c.execute("SELECT * FROM members WHERE phone=?", (phone.strip(),)).fetchone()


def get_members():
    with conn() as c:
        return c.execute("SELECT * FROM members ORDER BY total_spent DESC").fetchall()


def adjust_points(phone, delta):
    with conn() as c:
        c.execute("UPDATE members SET points=MAX(0, points+?) WHERE phone=?", (delta, phone))
        _log(c, f"ปรับแต้มสมาชิก {phone} ({delta:+d})")


def get_orders_by_phone(phone):
    with conn() as c:
        return c.execute("SELECT * FROM orders WHERE phone=? ORDER BY id DESC", (phone.strip(),)).fetchall()


# ---------- ไรเดอร์ ----------
def get_riders(active_only=False):
    with conn() as c:
        return c.execute("SELECT * FROM riders" + (" WHERE active=1" if active_only else "") + " ORDER BY id").fetchall()


def add_rider(name, phone):
    with conn() as c:
        c.execute("INSERT INTO riders(name,phone) VALUES(?,?)", (name, phone))


def toggle_rider(rid):
    with conn() as c:
        c.execute("UPDATE riders SET active=1-active WHERE id=?", (rid,))


def delete_rider(rid):
    with conn() as c:
        c.execute("DELETE FROM riders WHERE id=?", (rid,))


def rider_deliveries(name):
    with conn() as c:
        return c.execute("SELECT COUNT(*) FROM orders WHERE rider_name=? AND order_status=?", (name, ST_DONE)).fetchone()[0]


# ---------- บัญชีรายจ่าย ----------
def add_expense(date, category, description, amount):
    with conn() as c:
        c.execute("INSERT INTO expenses(date,category,description,amount) VALUES(?,?,?,?)", (date, category, description, amount))
        _log(c, f"บันทึกรายจ่าย {category} {amount:,.0f} บาท")


def get_expenses():
    with conn() as c:
        return c.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC").fetchall()


def delete_expense(eid):
    with conn() as c:
        c.execute("DELETE FROM expenses WHERE id=?", (eid,))


def total_expenses():
    with conn() as c:
        return c.execute("SELECT COALESCE(SUM(amount),0) FROM expenses").fetchone()[0]


# ---------- รูปเมนู ----------
def set_menu_image(mid, data):
    with conn() as c:
        c.execute("UPDATE menu SET image=? WHERE id=?", (data, mid))


# ---------- รายงานเพิ่มเติมสำหรับหน้าภาพรวมของแอดมิน ----------
def today_stats():
    """ยอดของวันนี้: จำนวนออเดอร์ · รายได้ที่ชำระแล้ว · ยอดเฉลี่ยต่อออเดอร์"""
    day = now()[:10]
    with conn() as c:
        r = c.execute(
            "SELECT COUNT(*) n, COALESCE(SUM(CASE WHEN payment_status=? THEN total END),0) rev, "
            "SUM(CASE WHEN payment_status=? THEN 1 ELSE 0 END) paid FROM orders WHERE substr(created_at,1,10)=?",
            (PAY_OK, PAY_OK, day)).fetchone()
    paid = r["paid"] or 0
    return {"orders": r["n"], "revenue": r["rev"], "avg": (r["rev"] / paid) if paid else 0}


def revenue_by_category():
    """รายได้แยกตามหมวดอาหาร (เฉพาะออเดอร์ที่ชำระเงินแล้ว)"""
    with conn() as c:
        return [tuple(r) for r in c.execute(
            """SELECT COALESCE(m.category,'อื่นๆ'), SUM(i.price*i.qty) FROM order_items i
               JOIN orders o ON o.id=i.order_id LEFT JOIN menu m ON m.id=i.menu_id
               WHERE o.payment_status=? GROUP BY 1 ORDER BY 2 DESC""", (PAY_OK,))]


def order_type_split():
    """จำนวนออเดอร์แยกตามรูปแบบการรับอาหาร (ทานที่ร้าน/รับเอง/จัดส่ง)"""
    with conn() as c:
        return [tuple(r) for r in c.execute(
            "SELECT COALESCE(order_type,'จัดส่ง'), COUNT(*) FROM orders GROUP BY 1 ORDER BY 2 DESC")]


# ---------- สลิปโอนเงิน / วิธีชำระเงิน ----------
def save_slip(oid, data, mime):
    with conn() as c:
        c.execute("INSERT OR REPLACE INTO slips(order_id,mime,data,uploaded_at) VALUES(?,?,?,?)",
                  (oid, mime or "image/jpeg", data, now()))


def get_slip(oid):
    """คืนแถว (mime, data, uploaded_at) ของสลิป หรือ None ถ้ายังไม่แนบ"""
    with conn() as c:
        return c.execute("SELECT * FROM slips WHERE order_id=?", (oid,)).fetchone()


def slip_exists(oid):
    with conn() as c:
        return c.execute("SELECT 1 FROM slips WHERE order_id=?", (oid,)).fetchone() is not None


def attach_slip(oid, phone, data, mime):
    """ลูกค้าแนบ/เปลี่ยนสลิปภายหลัง (ทำได้เฉพาะออเดอร์ของเบอร์นี้ที่ยังรอยืนยัน) คืน True ถ้าสำเร็จ"""
    with conn() as c:
        o = c.execute("SELECT 1 FROM orders WHERE id=? AND phone=? AND order_status=?",
                      (oid, phone.strip(), ST_WAIT)).fetchone()
        if not o:
            return False
        c.execute("INSERT OR REPLACE INTO slips(order_id,mime,data,uploaded_at) VALUES(?,?,?,?)",
                  (oid, mime or "image/jpeg", data, now()))
        _log(c, f"ลูกค้าแนบสลิป ออเดอร์ #{oid}")
        return True


def payment_split():
    """จำนวนออเดอร์แยกตามวิธีชำระเงิน"""
    with conn() as c:
        return [tuple(r) for r in c.execute(
            "SELECT COALESCE(payment_method,?), COUNT(*) FROM orders GROUP BY 1 ORDER BY 2 DESC", (PAY_TRANSFER,))]
