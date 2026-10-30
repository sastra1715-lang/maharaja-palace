"""views/admin.py - ระบบหลังบ้านสำหรับพนักงาน/เจ้าของร้าน (ฟังก์ชันเดิมครบทุกอย่าง จัดหน้าตาใหม่)

แท็บ: ภาพรวม · ออเดอร์ · ครัว · เมนู · จองโต๊ะ · สมาชิก · ไรเดอร์ · บัญชี · คูปอง · รีวิว · ตั้งค่า
ใหม่: ตั้งค่า > โลโก้ร้าน (อัปโหลดเปลี่ยนโลโก้ได้) และลิงก์โซเชียลที่แสดงในฟุตเตอร์
"""
import base64
import io
from datetime import date

import streamlit as st

import database as db
from config import ADMIN_PASSWORD
from ui import components as C
from ui.components import baht, esc, render

MAX_IMG = 800_000        # ขนาดรูปอาหารสูงสุด (ไบต์)
MAX_LOGO = 1_000_000     # ขนาดไฟล์โลโก้สูงสุด (ไบต์)


def _prep_food_image(upload):
    """รับไฟล์จาก st.file_uploader -> (bytes, None) หรือ (None, ข้อความผิดพลาด)
    รูปที่ใหญ่เกิน MAX_IMG จะถูกย่อ/บีบอัดอัตโนมัติเป็น JPEG แทนที่จะถูกทิ้งเงียบๆ"""
    raw = upload.getvalue()
    if len(raw) < MAX_IMG:
        return raw, None
    try:
        from PIL import Image, ImageOps
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw)))
        if im.mode != "RGB":
            im = im.convert("RGB")
        im.thumbnail((1200, 1200))
        for q in (85, 75, 65, 50):
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=q, optimize=True)
            if buf.tell() < MAX_IMG:
                return buf.getvalue(), None
        return None, "รูปใหญ่เกินไป ย่อแล้วก็ยังเกิน 800KB กรุณาใช้รูปที่เล็กลง"
    except Exception as e:  # noqa: BLE001
        return None, f"อ่านไฟล์รูปไม่ได้: {e}"


def _save_food_image(mid, upload):
    """บันทึกรูปอาหาร แล้วคืน True ถ้าสำเร็จ · ถ้าไม่สำเร็จจะแจ้งเตือนให้เห็น"""
    data, err = _prep_food_image(upload)
    if err:
        st.session_state["_img_err"] = f"บันทึกข้อมูลเมนูแล้ว แต่ไม่ได้บันทึกรูป: {err}"
        return False
    db.set_menu_image(mid, data)
    return True


# =====================================================================
# ทางเข้า / โครงหน้าแอดมิน
# =====================================================================
def _logout():
    st.session_state.admin = False
    st.session_state.page = "หน้าแรก"


def page_admin():
    if not st.session_state.admin:
        _login()
        return

    render(f"""
    <div class="admin-head"><div><div class="t">ศูนย์ควบคุมร้าน</div>
    <div class="s">{esc(C.shop())} · จัดการออเดอร์ เมนู บัญชี และการตั้งค่าทั้งหมด</div></div></div>""")
    _, out = st.columns([6, 1.4])
    out.button("ออกจากระบบ", key="logout_btn", on_click=_logout, use_container_width=True)

    s = db.stats()
    C.kpi_grid([("ออเดอร์ทั้งหมด", f"{s['orders']:,}"), ("รายได้ (ชำระแล้ว)", baht(s["revenue"])),
                ("รอตรวจสลิป", s["waiting"]), ("กำลังจัดส่ง", s["shipping"])])

    names = ["ภาพรวม", "ออเดอร์", "ครัว", "เมนู", "จองโต๊ะ", "สมาชิก", "ไรเดอร์",
             "บัญชี", "คูปอง", "รีวิว", "ตั้งค่า"]
    funcs = [admin_dashboard, admin_orders, admin_kitchen, admin_menu, admin_reservations, admin_members,
             admin_riders, admin_accounting, admin_coupons, admin_reviews, admin_settings]
    for tab, fn in zip(st.tabs(names), funcs):
        with tab:
            fn()


def _login():
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        render("""
        <div class="login-card"><div class="ic"></div><div class="t">เข้าสู่ระบบพนักงาน</div>
        <div class="s">สำหรับเจ้าของร้านและพนักงานเท่านั้น</div></div>""")
        with st.form("admin_login"):
            pw = st.text_input("รหัสผ่านแอดมิน", type="password")
            if st.form_submit_button("เข้าสู่ระบบ", use_container_width=True, type="primary"):
                if pw == ADMIN_PASSWORD:
                    st.session_state.admin = True
                    st.rerun()
                else:
                    st.error("รหัสผ่านไม่ถูกต้อง")
        st.button("← กลับหน้าแรก", key="login_back", on_click=C.go, args=("หน้าแรก",), use_container_width=True)


# =====================================================================
# ภาพรวม / ครัว
# =====================================================================
def _head(title, sub=""):
    """หัวข้อบล็อกแบบมีแถบสีด้านหน้า (แทนหัวข้อ markdown ธรรมดา)"""
    small = f"<small>{esc(sub)}</small>" if sub else ""
    render(f'<div class="blk-title">{esc(title)}{small}</div>')


def _chart_card(col, title, df, color):
    """กราฟแท่งในกรอบกระจก"""
    with col.container(border=True):
        render(f'<div class="chart-cap">{esc(title)}</div>')
        st.bar_chart(df, color=color)


def admin_dashboard():
    import pandas as pd
    month_names = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]

    t = db.today_stats()
    _head("วันนี้")
    C.kpi_grid([("ออเดอร์วันนี้", t["orders"]), ("รายได้วันนี้", baht(t["revenue"])),
                ("เฉลี่ยต่อออเดอร์", baht(t["avg"])), ("เมนูที่เปิดขาย", len(db.get_menu(only_available=True)))])

    # ---- รายได้รายเดือน / รายปี (ใหม่) ----
    ps = db.period_stats()
    _head("รายได้เดือนนี้และปีนี้", "นับเฉพาะออเดอร์ที่ชำระเงินแล้ว")
    C.kpi_grid([("รายได้เดือนนี้", baht(ps["month"][0])), ("ออเดอร์เดือนนี้", ps["month"][1]),
                ("รายได้ปีนี้", baht(ps["year"][0])), ("ออเดอร์ปีนี้", ps["year"][1])])
    months, years = db.revenue_by_month(), db.revenue_by_year()
    if months:
        def _label(ym):
            y, m = ym.split("-")
            return f"{month_names[int(m) - 1]} {y}"
        c = st.columns(2)
        _chart_card(c[0], "รายได้รายเดือน (บาท)",
                    pd.DataFrame([(_label(m), r) for m, r, _ in months], columns=["เดือน", "รายได้"]).set_index("เดือน"), "#FF9F1C")
        _chart_card(c[1], "รายได้รายปี (บาท)",
                    pd.DataFrame([(y, r) for y, r, _ in years], columns=["ปี", "รายได้"]).set_index("ปี"), "#E91E73")
        with st.expander("ตารางสรุปรายเดือนและรายปี"):
            t1, t2 = st.columns(2)
            t1.dataframe(pd.DataFrame([(_label(m), r, n) for m, r, n in months], columns=["เดือน", "รายได้ (บาท)", "ออเดอร์"]),
                         hide_index=True, use_container_width=True)
            t2.dataframe(pd.DataFrame(years, columns=["ปี", "รายได้ (บาท)", "ออเดอร์"]),
                         hide_index=True, use_container_width=True)
    else:
        st.info("ยังไม่มียอดขายรายเดือน/รายปี (จะแสดงเมื่อมีออเดอร์ที่ชำระเงินแล้ว)")

    # ---- กราฟเดิม ----
    daily, top = db.daily_revenue(), db.top_items()
    if not daily:
        st.info("ยังไม่มียอดขาย")
    else:
        _head("รายละเอียดยอดขาย")
        c = st.columns(2)
        _chart_card(c[0], "รายได้รายวัน", pd.DataFrame(daily, columns=["วันที่", "รายได้"]).set_index("วันที่"), "#E91E73")
        _chart_card(c[1], "เมนูขายดี", pd.DataFrame(top, columns=["เมนู", "จำนวน"]).set_index("เมนู"), "#F28C28")
        cats, types = db.revenue_by_category(), db.order_type_split()
        c = st.columns(2)
        if cats:
            _chart_card(c[0], "รายได้ตามหมวดอาหาร", pd.DataFrame(cats, columns=["หมวด", "รายได้"]).set_index("หมวด"), "#D4A017")
        if types:
            _chart_card(c[1], "ช่องทางการรับอาหาร", pd.DataFrame(types, columns=["ช่องทาง", "ออเดอร์"]).set_index("ช่องทาง"), "#1FC2BA")
    for m in [m for m in db.get_menu() if m["stock"] is not None and 0 <= m["stock"] <= 5]:
        st.warning(f"สต็อกใกล้หมด: {m['name']} เหลือ {m['stock']}")


def admin_kitchen():
    st.caption("คิวอาหารที่ชำระเงินแล้ว รอห้องครัวทำ")
    if st.button("รีเฟรชคิว", key="kitchen_refresh"):
        st.rerun()
    orders = db.get_orders(db.ST_COOK)
    if not orders:
        st.success("ไม่มีคิวค้าง ")
    for o in reversed(orders):
        where = f"โต๊ะ {o['table_no']}" if o["order_type"] == db.TYPE_DINE else o["order_type"]
        items = "".join(f'<div class="k-item">{esc(it["name"])} × <b>{it["qty"]}</b></div>'
                        for it in db.get_order_items(o["id"]))
        note = f'<div style="color:#FFC233">หมายเหตุ: {esc(o["note"])}</div>' if o["note"] else ""
        render(f"""<div class="kitchen-ticket"><div class="k-head">#{o['id']} · {esc(where)}
        <span style="font-weight:400;color:#C4B6AA"> · เริ่มคิว {o['updated_at'][11:16]}</span></div>{items}{note}</div>""")
        if st.button("ทำเสร็จแล้ว", key=f"rd{o['id']}", type="primary"):
            db.set_status(o["id"], db.ST_READY)
            st.rerun()


# =====================================================================
# ออเดอร์
# =====================================================================
def _slip_panel(o, method):
    """แสดงวิธีชำระเงินและรูปสลิปให้แอดมินตรวจเทียบยอด"""
    if method == db.PAY_CASH:
        st.info(f"ชำระเงินสด · เก็บเงิน {baht(o['total'])} ({o['order_type']})")
        return
    sl = db.get_slip(o["id"])
    if not sl:
        if o["order_status"] == db.ST_WAIT:
            st.warning("ลูกค้ายังไม่ได้แนบสลิป รอลูกค้าแนบ หรือติดต่อกลับทางเบอร์โทร")
        return
    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(bytes(sl["data"]), caption=f"สลิปที่ลูกค้าแนบ · {sl['uploaded_at']}", use_container_width=True)
    with c2:
        render(f"""<div class="pay-box"><div class="pb-l">ยอดที่ต้องได้รับ</div><div class="pb-v">{baht(o['total'])}</div>
        <div class="pb-n">ลูกค้าแจ้งเวลาโอน: {esc(o['transfer_time'] or '-')}<br>ตรวจชื่อบัญชี ยอดเงิน และเวลาในสลิปให้ตรงก่อนกดยืนยัน</div></div>""")
        st.download_button("ดาวน์โหลดสลิป", bytes(sl["data"]), file_name=f"slip_{o['id']}.{(sl['mime'] or 'image/jpeg').split('/')[-1]}",
                           mime=sl["mime"] or "image/jpeg", key=f"dl_slip_{o['id']}", icon=":material/download:")


def admin_orders():
    flt = st.selectbox("กรองสถานะ", ["ทั้งหมด", db.ST_WAIT, db.ST_COOK, db.ST_READY, db.ST_SHIP, db.ST_DONE, db.ST_CANCEL])
    orders = db.get_orders(None if flt == "ทั้งหมด" else flt)
    if not orders:
        st.info("ไม่มีออเดอร์ในสถานะนี้")
    waiting = sum(1 for o in orders if o["order_status"] == db.ST_WAIT)
    if waiting:
        st.warning(f"มี {waiting} ออเดอร์รอตรวจสอบการชำระเงิน (เปิดอยู่ด้านล่าง ตรวจสลิปแล้วกดยืนยันได้เลย)")
    for o in orders:
        where = f"โต๊ะ {o['table_no']}" if o["order_type"] == db.TYPE_DINE else o["order_type"]
        method = o["payment_method"] or db.PAY_TRANSFER
        with st.expander(f"#{o['id']} · {o['customer_name']} · {where} · {baht(o['total'])} · {method} · {o['order_status']}",
                         expanded=o["order_status"] == db.ST_WAIT):
            render(f"""
            <div class="info-card">{esc(o['phone'])}<br>{esc(o['address'] or '-')}<br>{esc(o['note'] or '-')}<br>
            {esc(o['created_at'])}<hr>
            {''.join(f"<div>• {esc(it['name'])} × {it['qty']}</div>" for it in db.get_order_items(o['id']))}<hr>
            ชำระเงิน {C.pay_badge(o['payment_status'])} &nbsp; สถานะ {C.status_badge(o['order_status'])}<br>
            เวลาที่ลูกค้าแจ้งว่าโอน: <b>{esc(o['transfer_time'] or '-')}</b> · ยอดที่ต้องได้รับ: <b>{baht(o['total'])}</b>
            {f" · {esc(o['coupon_code'])}" if o['coupon_code'] else ''}</div>""")
            if o["rating"]:
                st.write(f"{'★' * o['rating']} {o['review'] or ''}")
            _slip_panel(o, method)
            if o["order_status"] == db.ST_WAIT:
                a, b = st.columns(2)
                if a.button("ยืนยันการชำระเงิน", key=f"ok{o['id']}", type="primary"):
                    db.confirm_payment(o["id"])
                    st.rerun()
                if b.button("ไม่พบยอดโอน / ยกเลิก", key=f"no{o['id']}"):
                    db.reject_payment(o["id"])
                    st.rerun()
            elif o["payment_status"] == db.PAY_OK:
                opts = db.steps_for(o["order_type"])[1:]
                cur = opts.index(o["order_status"]) if o["order_status"] in opts else 0
                nxt = st.selectbox("เปลี่ยนสถานะ", opts, index=cur, key=f"st{o['id']}")
                rn = rp = None
                if o["order_type"] == db.TYPE_DELIVERY:
                    rd = {f"{r['name']} ({r['phone']})": r for r in db.get_riders(True)}
                    pick = st.selectbox("มอบหมายไรเดอร์", ["-"] + list(rd), key=f"rd_{o['id']}")
                    if pick != "-":
                        rn, rp = rd[pick]["name"], rd[pick]["phone"]
                if st.button("บันทึก", key=f"sv{o['id']}", type="primary"):
                    db.set_status(o["id"], nxt, rn, rp)
                    st.rerun()


# =====================================================================
# เมนู
# =====================================================================
def admin_menu():
    if st.session_state.get("_img_err"):
        st.warning(st.session_state.pop("_img_err"))
    with st.expander("เพิ่มเมนูใหม่"):
        with st.form("addmenu", clear_on_submit=True):
            c = st.columns(2)
            n, th = c[0].text_input("ชื่ออังกฤษ"), c[1].text_input("ชื่อไทย")
            c = st.columns(5)
            cat = c[0].text_input("หมวดหมู่")
            pr = c[1].number_input("ราคา", 0.0, step=5.0)
            em = c[2].text_input("อีโมจิ", "🍛")
            sk = c[3].number_input("สต็อก (-1=ไม่จำกัด)", -1, 9999, -1)
            tg = c[4].text_input("ป้ายกำกับ", help="ใส่คำว่า มังสวิรัติ เพื่อให้ขึ้นสัญลักษณ์จุดเขียว · ขายดี เพื่อขึ้นหน้าแรก")
            ds = st.text_area("คำอธิบาย")
            img = st.file_uploader("รูปอาหาร (ไม่เกิน 800KB)", type=["png", "jpg", "jpeg"], key="newimg")
            if st.form_submit_button("เพิ่มเมนู", type="primary") and n.strip():
                nid = db.add_menu(n.strip(), th, cat or "อื่นๆ", ds, pr, em, sk, tg)
                if img:
                    _save_food_image(nid, img)
                st.rerun()
    for i in db.get_menu():
        shown = "" if i["available"] and i["stock"] != 0 else "(ซ่อน/หมด)"
        with st.expander(f"{shown} {i['emoji']} {i['name']} — {baht(i['price'])}"):
            if i["image"]:
                st.image(bytes(i["image"]), width=160)
            with st.form(f"edit{i['id']}"):
                c = st.columns(2)
                n, th = c[0].text_input("ชื่ออังกฤษ", i["name"]), c[1].text_input("ชื่อไทย", i["name_th"] or "")
                c = st.columns(5)
                cat = c[0].text_input("หมวดหมู่", i["category"] or "")
                pr = c[1].number_input("ราคา", 0.0, value=float(i["price"]), step=5.0)
                em = c[2].text_input("อีโมจิ", i["emoji"] or "")
                sk = c[3].number_input("สต็อก (-1=ไม่จำกัด)", -1, 9999, int(i["stock"] if i["stock"] is not None else -1))
                tg = c[4].text_input("ป้ายกำกับ", i["tag"] or "")
                ds = st.text_area("คำอธิบาย", i["description"] or "")
                av = st.checkbox("เปิดขาย", bool(i["available"]))
                img = st.file_uploader("เปลี่ยนรูปอาหาร", type=["png", "jpg", "jpeg"], key=f"img{i['id']}")
                a, b = st.columns(2)
                if a.form_submit_button("บันทึก", type="primary"):
                    db.update_menu(i["id"], n, th, cat, ds, pr, em, av, sk, tg)
                    if img:
                        _save_food_image(i["id"], img)
                    st.rerun()
                if b.form_submit_button("ลบเมนู"):
                    db.delete_menu(i["id"])
                    st.rerun()


# =====================================================================
# จองโต๊ะ / สมาชิก / ไรเดอร์
# =====================================================================
def admin_reservations():
    rs = db.get_reservations()
    if not rs:
        st.info("ยังไม่มีการจอง")
    for r in rs:
        c = st.columns([6, 2, 2])
        kind = {"ยืนยันแล้ว": "ok", "ยกเลิก": "bad"}.get(r["status"], "wait")
        extra = f" · {esc(r['note'])}" if r["note"] else ""
        c[0].markdown(
            C.H(f"""<div class="info-card">#{r['id']} <b>{esc(r['name'])}</b> {esc(r['phone'])} ·
            {esc(r['date'])} {esc(r['time'])} · {r['guests']} ที่นั่ง {extra}
            &nbsp;<span class="badge {kind}">{esc(r['status'])}</span></div>"""), unsafe_allow_html=True)
        if r["status"] == "รอยืนยัน":
            if c[1].button("ยืนยัน", key=f"rc{r['id']}", type="primary"):
                db.set_reservation(r["id"], "ยืนยันแล้ว")
                st.rerun()
            if c[2].button("ยกเลิก", key=f"rx{r['id']}"):
                db.set_reservation(r["id"], "ยกเลิก")
                st.rerun()


def admin_members():
    import pandas as pd
    ms = db.get_members()
    if not ms:
        st.info("ยังไม่มีสมาชิก")
        return
    st.dataframe(pd.DataFrame([{"เบอร์": m["phone"], "ชื่อ": m["name"], "ระดับ": db.tier_info(m["total_spent"])[0],
                                "แต้ม": m["points"], "ยอดสะสม": m["total_spent"]} for m in ms]),
                 use_container_width=True, hide_index=True)
    with st.form("adjp"):
        c = st.columns(2)
        ph = c[0].selectbox("สมาชิก", [m["phone"] for m in ms])
        d = c[1].number_input("ปรับแต้ม (+/-)", -10000, 10000, 0)
        if st.form_submit_button("ปรับแต้ม", type="primary"):
            db.adjust_points(ph, int(d))
            st.rerun()


def admin_riders():
    with st.form("addrider", clear_on_submit=True):
        c = st.columns(3)
        n, p = c[0].text_input("ชื่อไรเดอร์"), c[1].text_input("เบอร์โทร")
        if st.form_submit_button("เพิ่มไรเดอร์", type="primary") and n.strip():
            db.add_rider(n.strip(), p.strip())
            st.rerun()
    for r in db.get_riders():
        c = st.columns([4, 2, 2, 2])
        c[0].write(f"**{r['name']}** · {r['phone']}" + ("" if r["active"] else "  (หยุดงาน)"))
        c[1].write(f"ส่งสำเร็จ {db.rider_deliveries(r['name'])} งาน")
        if c[2].button("เปิด/ปิด", key=f"tr{r['id']}"):
            db.toggle_rider(r["id"])
            st.rerun()
        if c[3].button("ลบ", key=f"dr{r['id']}"):
            db.delete_rider(r["id"])
            st.rerun()


# =====================================================================
# บัญชี / คูปอง / รีวิว
# =====================================================================
def admin_accounting():
    import pandas as pd
    with st.form("addexp", clear_on_submit=True):
        c = st.columns(4)
        d = c[0].date_input("วันที่", date.today())
        cat = c[1].selectbox("หมวด", ["วัตถุดิบ", "ค่าแรง", "ค่าเช่า", "สาธารณูปโภค", "การตลาด", "อื่นๆ"])
        desc = c[2].text_input("รายละเอียด")
        amt = c[3].number_input("จำนวนเงิน", 0.0, step=50.0)
        if st.form_submit_button("บันทึกรายจ่าย", type="primary") and amt > 0:
            db.add_expense(str(d), cat, desc, amt)
            st.rerun()
    rev, exp = sum(r[1] for r in db.daily_revenue()), db.total_expenses()
    C.kpi_grid([("รายรับ (ชำระแล้ว)", baht(rev)), ("รายจ่าย", baht(exp)), ("กำไรสุทธิ", baht(rev - exp))])
    ex = db.get_expenses()
    if ex:
        df = pd.DataFrame([dict(r) for r in ex])
        st.bar_chart(df.groupby("category")["amount"].sum(), color="#D96F0B")
        st.dataframe(df, use_container_width=True, hide_index=True)
        c = st.columns(2)
        eid = c[0].selectbox("ลบรายการ (เลข id)", df["id"])
        if c[1].button("ลบรายจ่าย"):
            db.delete_expense(int(eid))
            st.rerun()
        st.download_button("ส่งออกรายจ่าย (CSV/Excel)", df.to_csv(index=False).encode("utf-8-sig"),
                           "expenses.csv", "text/csv")
    od = pd.DataFrame([{k: o[k] for k in ("id", "created_at", "customer_name", "phone", "order_type", "subtotal",
                                           "discount", "delivery_fee", "total", "payment_method", "payment_status", "order_status")}
                       for o in db.get_orders()])
    if len(od):
        st.download_button("ส่งออกออเดอร์ (CSV/Excel)", od.to_csv(index=False).encode("utf-8-sig"),
                           "orders.csv", "text/csv")


def admin_coupons():
    with st.form("addcoupon", clear_on_submit=True):
        c = st.columns(3)
        code = c[0].text_input("โค้ด")
        pct = c[1].number_input("ลด (%)", 1.0, 100.0, 10.0)
        mn = c[2].number_input("ขั้นต่ำ (บาท)", 0.0, value=0.0, step=50.0)
        if st.form_submit_button("บันทึกคูปอง", type="primary") and code.strip():
            db.save_coupon(code, pct, mn)
            st.rerun()
    for cp in db.get_coupons():
        c = st.columns([3, 2, 2, 2])
        c[0].write(f"**{cp['code']}** ลด {cp['percent']:.0f}% (ขั้นต่ำ {baht(cp['min_total'])})")
        c[1].write("เปิด" if cp["active"] else "ปิด")
        if c[2].button("เปิด/ปิด", key=f"tg{cp['code']}"):
            db.save_coupon(cp["code"], cp["percent"], cp["min_total"], not cp["active"])
            st.rerun()
        if c[3].button("ลบ", key=f"dc{cp['code']}"):
            db.delete_coupon(cp["code"])
            st.rerun()


def admin_reviews():
    rv = db.get_reviews()
    if not rv:
        st.info("ยังไม่มีรีวิว")
        return
    C.kpi_grid([("คะแนนเฉลี่ย", f"{sum(r['rating'] for r in rv) / len(rv):.2f} / 5"), ("จำนวนรีวิว", len(rv))])
    for r in rv:
        render(f"""<div class="info-card" style="margin-bottom:.5rem"><span style="color:#F28C28">{'★' * r['rating']}</span>
        <b>{esc(r['customer_name'])}</b> (#{r['id']}) — {esc(r['review'] or '')}</div>""")


# =====================================================================
# ตั้งค่า (ข้อมูลร้าน + โลโก้ + โซเชียล)
# =====================================================================
SHOP_LABELS = {
    "shop_name": "ชื่อร้าน", "tagline": "สโลแกนใต้ชื่อร้าน", "open_hours": "เวลาเปิด-ปิด",
    "phone": "เบอร์โทรร้าน", "address": "ที่อยู่ร้าน", "pay_note": "ข้อมูลบัญชีรับเงิน (แสดงใต้ QR)",
    "promo_banner": "ข้อความโปรโมชันหน้าแรก", "about_text": "เกี่ยวกับร้าน",
    "delivery_fee": "ค่าส่ง (บาท)", "free_over": "ส่งฟรีเมื่อซื้อครบ (บาท)", "points_rate": "ทุกกี่บาทได้ 1 แต้ม",
}
SOCIAL_LABELS = {
    "instagram": "Instagram (ลิงก์โปรไฟล์)", "facebook": "Facebook (ลิงก์เพจ)", "line": "LINE (ลิงก์ LINE OA)",
    "tiktok": "TikTok", "youtube": "YouTube", "x_twitter": "X (Twitter)",
}


def _save_logo(upload):
    data = upload.getvalue()
    if len(data) > MAX_LOGO:
        st.error("ไฟล์โลโก้ใหญ่เกิน 1MB กรุณาลดขนาดแล้วลองใหม่")
        return
    mime = upload.type or "image/png"
    db.set_setting("logo_data", base64.b64encode(data).decode())
    db.set_setting("logo_mime", mime)
    C.refresh_cfg()
    st.success("เปลี่ยนโลโก้เรียบร้อยแล้ว")
    st.rerun()


def _reset_logo():
    db.set_setting("logo_data", "")
    db.set_setting("logo_mime", "")
    C.refresh_cfg()


def admin_settings():
    st.markdown("#### โลโก้ร้าน")
    c1, c2 = st.columns([1, 2])
    with c1:
        render(f'<div class="logo-preview"><img src="{C.logo_src()}" alt="logo"></div>')
        using = "โลโก้ที่อัปโหลด" if C.cfg("logo_data") else "โลโก้ในตัว / ไฟล์ logo.*"
        st.caption(f"กำลังใช้: {using}")
    with c2:
        up = st.file_uploader("อัปโหลดโลโก้ใหม่ (PNG / JPG / WEBP / SVG ไม่เกิน 1MB · แนะนำพื้นโปร่งใส)",
                              type=["png", "jpg", "jpeg", "webp", "svg"], key="logo_upload")
        b1, b2 = st.columns(2)
        if b1.button("ใช้โลโก้นี้", key="logo_save", type="primary", disabled=up is None, use_container_width=True):
            _save_logo(up)
        if b2.button("↩กลับไปใช้โลโก้เดิม", key="logo_reset", use_container_width=True):
            _reset_logo()
            st.rerun()

    st.markdown("#### ข้อมูลร้านและการขาย")
    with st.form("settings"):
        vals = {}
        for k, label in SHOP_LABELS.items():
            cur = db.get_setting(k)
            vals[k] = st.text_area(label, cur) if k in ("about_text", "address") else st.text_input(label, cur)
        st.markdown("##### ลิงก์โซเชียล (แสดงเป็นไอคอนที่ฟุตเตอร์ · เว้นว่าง = ไม่แสดง)")
        for k, label in SOCIAL_LABELS.items():
            vals[k] = st.text_input(label, db.get_setting(k), placeholder="https://...")
        if st.form_submit_button("บันทึกการตั้งค่า", use_container_width=True, type="primary"):
            db.save_settings(vals)
            C.refresh_cfg()
            st.rerun()

    st.markdown("#### บันทึกกิจกรรมล่าสุด")
    for l in db.get_logs():
        render(f'<div class="log-line">{esc(l["ts"])} · {esc(l["msg"])}</div>')