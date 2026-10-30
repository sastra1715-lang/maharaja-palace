"""views/customer.py - หน้าฝั่งลูกค้าทั้งหมด

หน้าแรก · เมนูอาหาร · ตะกร้า/ชำระเงิน · จองโต๊ะ · สมาชิก · ติดตามออเดอร์
(ตรรกะการสั่งซื้อ คูปอง แต้มสะสม สต็อก เหมือนเดิมทุกอย่าง เปลี่ยนเฉพาะหน้าตา)
"""
import base64
import os
from datetime import date, time

import streamlit as st

import database as db
from config import QR_IMAGE
from utils import clean_text, valid_phone
from ui import components as C
from ui.components import baht, esc, render


# =====================================================================
# หน้าแรก
# =====================================================================
def page_home():
    menu = db.get_menu(only_available=True)
    reviews = db.get_reviews()

    C.hero_slider(menu)

    # ปุ่มเรียกใช้งานหลักใต้แบนเนอร์
    _, a, b, c, _ = st.columns([2.2, 2, 2, 2, 2.2])
    a.button("สั่งอาหารเลย", key="cta_menu", type="primary", use_container_width=True, icon=":material/restaurant_menu:",
             on_click=C.go, args=("เมนูอาหาร",))
    b.button("จองโต๊ะ", key="cta_reserve", use_container_width=True, icon=":material/event_seat:", on_click=C.go, args=("จองโต๊ะ",))
    c.button("ติดตามออเดอร์", key="cta_track", use_container_width=True, icon=":material/search:", on_click=C.go, args=("ติดตามออเดอร์",))

    C.info_chips(reviews)

    # หมวดหมู่
    C.section("เลือกตามหมวดอาหาร", "แตะหมวดที่ชอบเพื่อดูเมนูทั้งหมดในหมวดนั้น", "MENU CATEGORIES")
    C.category_tiles(menu)

    # เมนูแนะนำ
    C.section("เมนูแนะนำของเชฟ", "จานเด็ดที่ลูกค้าสั่งบ่อยที่สุด", "CHEF'S SPECIAL")
    feat = [i for i in menu if i["tag"] and "ขายดี" in i["tag"]]
    feat += [i for i in menu if i not in feat]
    if feat:
        C.dish_grid(feat[:4], "h", per_row=4)
    else:
        st.info("ยังไม่มีเมนูในระบบ")
    _, mid, _ = st.columns([3, 2, 3])
    mid.button("ดูเมนูทั้งหมด →", key="home_all", use_container_width=True, on_click=C.go, args=("เมนูอาหาร",))

    # โปรโมชัน (คูปองที่เปิดใช้งานจริง)
    if db.get_active_coupons():
        C.section("โปรโมชันพิเศษ", "ใช้โค้ดที่หน้าตะกร้าเพื่อรับส่วนลดทันที", "PROMOTIONS")
        C.promo_cards()

    # จุดเด่น
    C.section("ทำไมต้องสั่งกับเรา", "", "WHY CHOOSE US")
    C.feature_blocks()

    # รู้จักเครื่องเทศ
    C.section("รู้จักเครื่องเทศอินเดีย", "หัวใจของรสชาติในทุกจาน และระดับความเผ็ดที่เลือกได้ตอนสั่ง", "SPICE STORY")
    C.spice_guide()

    # เกี่ยวกับร้าน
    C.section("เกี่ยวกับร้าน", "", "ABOUT US")
    avg = f"{sum(r['rating'] for r in reviews) / len(reviews):.1f}" if reviews else "-"
    s = db.stats()
    render(f"""
    <div class="about-box">
      <p>{esc(C.cfg('about_text'))}</p>
      <div class="about-stats">
        <div class="stat-pill"><div class="n">{len(menu)}</div><div class="l">เมนูให้เลือก</div></div>
        <div class="stat-pill"><div class="n">{s['orders']}</div><div class="l">ออเดอร์ที่ผ่านมา</div></div>
        <div class="stat-pill"><div class="n">{avg}</div><div class="l">คะแนนเฉลี่ย</div></div>
      </div>
    </div>""")

    # รีวิว
    if reviews:
        C.section("เสียงจากลูกค้า", "", "REVIEWS")
        C.review_cards(reviews, 3)

    # ติดต่อ
    C.section("ติดต่อและเดินทางมาหาเรา", "", "VISIT US")
    render(f"""
    <div class="chips">
      <span class="chip"><b>{esc(C.cfg('address'))}</b></span>
      <span class="chip"><b>{esc(C.cfg('phone'))}</b></span>
      <span class="chip">เปิด <b>{esc(C.cfg('open_hours'))}</b></span>
    </div>""")


# =====================================================================
# เมนูอาหาร
# =====================================================================
def _set_cat(name):
    st.session_state["menu_cat"] = name


SORTS = ["เมนูแนะนำ", "ราคา: ต่ำ → สูง", "ราคา: สูง → ต่ำ", "ชื่อ A → Z"]


def page_menu():
    C.page_title("เมนูอาหารทั้งหมด", "เลือกเมนูที่ถูกใจ แล้วกดใส่ตะกร้าได้เลย ไม่ต้องสมัครสมาชิก")
    items = db.get_menu(only_available=True)
    cats = list(dict.fromkeys(i["category"] for i in items if i["category"]))
    options = ["ทั้งหมด"] + cats
    if st.session_state.get("menu_cat") not in options:
        st.session_state["menu_cat"] = "ทั้งหมด"

    c1, c2, c3 = st.columns([4, 2, 2])
    q = c1.text_input("ค้นหา", placeholder="ค้นหาเมนู เช่น biryani, ไก่, มังสวิรัติ",
                      key="menu_q", label_visibility="collapsed").strip().lower()
    sort = c2.selectbox("เรียงตาม", SORTS, key="menu_sort", label_visibility="collapsed")
    veg = c3.toggle("เฉพาะมังสวิรัติ", key="menu_veg")

    cat = st.session_state["menu_cat"]
    for n, (col, name) in enumerate(zip(st.columns(len(options)), options)):
        col.button(name, key=f"mc_{n}", use_container_width=True, on_click=_set_cat, args=(name,),
                   type="primary" if name == cat else "secondary")

    shown = [i for i in items
             if (cat == "ทั้งหมด" or i["category"] == cat)
             and q in f"{i['name']} {i['name_th']} {i['description']} {i['tag'] or ''}".lower()
             and (not veg or "มังสวิรัติ" in (i["tag"] or ""))]
    if sort == SORTS[1]:
        shown.sort(key=lambda i: i["price"])
    elif sort == SORTS[2]:
        shown.sort(key=lambda i: -i["price"])
    elif sort == SORTS[3]:
        shown.sort(key=lambda i: i["name"].lower())

    st.caption(f"พบ {len(shown)} เมนู")
    if not shown:
        render('<div class="empty-cart"><div class="big">&nbsp;</div><div class="t">ไม่พบเมนูที่ค้นหา</div>'
               '<div class="s">ลองเปลี่ยนคำค้นหรือหมวดหมู่ดูนะครับ</div></div>')
        return
    grouped = cat == "ทั้งหมด" and not q and not veg and sort == SORTS[0]
    if grouped:
        # มุมมองแบ่งตามหมวด (เหมือนเว็บสั่งอาหาร) ใช้เมื่อไม่ได้ค้นหา/กรอง/เรียงลำดับ
        for c_name in cats:
            part = [i for i in shown if i["category"] == c_name]
            if part:
                C.category_heading(c_name, items, len(part))
                C.dish_grid(part, "m", per_row=4)
        rest = [i for i in shown if not i["category"]]
        if rest:
            C.category_heading("อื่นๆ", items, len(rest))
            C.dish_grid(rest, "m", per_row=4)
    else:
        C.dish_grid(shown, "m", per_row=4)


# =====================================================================
# ตะกร้า / ชำระเงิน
# =====================================================================
def _inc(mid, cap):
    cart = st.session_state.cart
    cart[mid] = min(cart.get(mid, 0) + 1, cap)


def _dec(mid):
    cart = st.session_state.cart
    if cart.get(mid, 0) <= 1:
        cart.pop(mid, None)
    else:
        cart[mid] -= 1


def _remove(mid):
    st.session_state.cart.pop(mid, None)


MAX_SLIP = 3_000_000          # สลิปใหญ่สุด 3MB
SLIP_TYPES = ["png", "jpg", "jpeg", "webp"]


def _cart_row(m, q, cap):
    """แถวสินค้าหนึ่งรายการ: ชื่อ · − จำนวน + · ราคารวม · ลบ (แถวเดียวไม่ซ้อนคอลัมน์)"""
    if m["image"]:
        ico = f'<img src="data:image/jpeg;base64,{base64.b64encode(m["image"]).decode()}" alt="">'
    else:
        ico = esc(m["emoji"] or "🍛")
    c1, c2, c3, c4, c5, c6 = st.columns([4.6, .8, .6, .8, 1.5, .8], vertical_alignment="center")
    c1.markdown(C.H(f"""<div class="cart-row"><div class="cart-ico">{ico}</div>
        <div><div class="cart-name">{esc(m['name'])}</div><div class="cart-th">{esc(m['name_th'] or '')} · {baht(m['price'])}</div></div></div>"""),
                unsafe_allow_html=True)
    c2.button("", icon=":material/remove:", key=f"qty_m_{m['id']}", on_click=_dec, args=(m["id"],), use_container_width=True)
    c3.markdown(f'<div class="qty-val">{q}</div>', unsafe_allow_html=True)
    c4.button("", icon=":material/add:", key=f"qty_p_{m['id']}", on_click=_inc, args=(m["id"], cap),
              use_container_width=True, disabled=q >= cap)
    c5.markdown(f'<div class="cart-price">{baht(m["price"] * q)}</div>', unsafe_allow_html=True)
    c6.button("", icon=":material/delete:", key=f"qty_x_{m['id']}", on_click=_remove, args=(m["id"],), help="ลบออกจากตะกร้า")


def _pay_label(method, otype):
    if method == db.PAY_TRANSFER:
        return "โอนเงิน / สแกน QR (แนบสลิป)"
    return {db.TYPE_DELIVERY: "เงินสดปลายทาง (จ่ายตอนรับอาหาร)", db.TYPE_PICKUP: "เงินสดที่ร้าน (จ่ายตอนมารับ)",
            db.TYPE_DINE: "เงินสดที่ร้าน (จ่ายหลังทาน)"}[otype]


def page_cart():
    C.page_title("ตะกร้าและการสั่งซื้อ", "ทำตามขั้นตอน 1 ถึง 5 ด้านล่าง ใช้เวลาไม่ถึงนาที")
    cart = st.session_state.cart
    menu = {m["id"]: m for m in db.get_menu(only_available=True)}
    for mid in [m for m in cart if m not in menu]:
        del cart[mid]
    if not cart:
        render('<div class="empty-cart"><div class="big">&nbsp;</div><div class="t">ตะกร้ายังว่างอยู่</div>'
               '<div class="s">เลือกเมนูอร่อย ๆ จากร้านเราได้เลยครับ</div></div>')
        _, mid, _ = st.columns([3, 2, 3])
        mid.button("ไปเลือกเมนู", key="cart_goto_menu", type="primary", use_container_width=True,
                   on_click=C.go, args=("เมนูอาหาร",))
        return

    left, right = st.columns([3, 2], gap="large")
    with left:
        # ---------- 1) รายการอาหาร ----------
        with st.container(key="sec_items"):
            C.step_head(1, "รายการอาหารของคุณ", f"{len(cart)} รายการ · กด − + เพื่อปรับจำนวน")
            subtotal = 0
            for mid, q in list(cart.items()):
                m = menu[mid]
                cap = m["stock"] if m["stock"] is not None and m["stock"] >= 0 else 50
                q = min(q, cap)
                cart[mid] = q
                _cart_row(m, q, cap)
                subtotal += m["price"] * q
            C.upsell_row(menu, cart)

        # ---------- 2) วิธีรับอาหาร ----------
        with st.container(key="sec_how"):
            C.step_head(2, "รับอาหารแบบไหน")
            labels = {db.TYPE_DELIVERY: "จัดส่งถึงบ้าน", db.TYPE_PICKUP: "รับที่ร้าน", db.TYPE_DINE: "ทานที่ร้าน"}
            otype = st.radio("รูปแบบการรับอาหาร", list(labels), key="otype", horizontal=True,
                             format_func=labels.get, label_visibility="collapsed")

        # ---------- 3) ส่วนลด ----------
        with st.container(key="sec_disc"):
            C.step_head(3, "โค้ดส่วนลดและแต้มสะสม", "ไม่บังคับ ข้ามได้ถ้าไม่มี")
            k1, k2 = st.columns(2)
            mphone = k1.text_input("เบอร์ที่เคยสั่ง (เพื่อใช้แต้มสะสม)", key="mphone").strip()
            code = k2.text_input("โค้ดส่วนลด", key="coupon").strip()
            mem = db.get_member(mphone) if mphone else None
            disc, msg = db.apply_coupon(code, subtotal)
            if code:
                (st.success if disc else st.warning)(msg)
            pts = 0
            if mem and mem["points"] > 0:
                st.caption(f"{db.tier_info(mem['total_spent'])[0]} · คุณมี {mem['points']:,} แต้ม (1 แต้ม = ฿1)")
                pts = int(st.number_input("ใช้แต้มสะสมเป็นส่วนลด", 0, int(max(0, min(mem["points"], subtotal - disc))), 0))
        fee = db.calc_fee(subtotal - disc - pts) if otype == db.TYPE_DELIVERY else 0
        total = subtotal - disc - pts + fee

        # ---------- 4) วิธีชำระเงิน ----------
        with st.container(key="sec_pay"):
            C.step_head(4, "วิธีชำระเงิน")
            method = st.radio("วิธีชำระเงิน", db.PAYMENT_METHODS, key="paymethod", horizontal=True,
                              format_func=lambda m: _pay_label(m, otype), label_visibility="collapsed")
            if method == db.PAY_TRANSFER:
                q1, q2 = st.columns([1, 1], vertical_alignment="center")
                with q1:
                    if QR_IMAGE.startswith("http") or os.path.exists(QR_IMAGE):
                        st.image(QR_IMAGE, width=250)
                    else:
                        st.warning("ร้านยังไม่ได้ใส่รูป QR (ดูวิธีตั้งค่าที่ config.py)")
                with q2:
                    render(f"""<div class="pay-box"><div class="pb-l">ยอดที่ต้องโอน</div><div class="pb-v">{baht(total)}</div>
                    <div class="pb-n">{esc(C.cfg('pay_note'))}</div></div>""")
                render('<div class="slip-hint"><b>โอนแล้วอย่าลืมแนบสลิปในขั้นตอนที่ 5</b> '
                       'ร้านจะตรวจสลิปแล้วเริ่มทำอาหารทันทีที่ยืนยัน</div>')
            else:
                render(f'<div class="slip-hint"><b>ชำระเงินสด {baht(total)}</b> · '
                       f'{esc(_pay_label(method, otype))} ร้านจะเริ่มทำอาหารเมื่อยืนยันออเดอร์</div>')

        # ---------- 5) ข้อมูลผู้สั่ง + ยืนยัน ----------
        with st.container(key="sec_form"):
            C.step_head(5, "ข้อมูลผู้สั่งและยืนยัน")
            with st.form("checkout"):
                f1, f2 = st.columns(2)
                name = f1.text_input("ชื่อผู้รับ")
                phone = f2.text_input("เบอร์โทร", value=mphone)
                address = st.text_area("ที่อยู่จัดส่ง") if otype == db.TYPE_DELIVERY else ""
                table = st.text_input("หมายเลขโต๊ะ") if otype == db.TYPE_DINE else ""
                spice = st.select_slider("ระดับความเผ็ด", ["ไม่เผ็ด", "เผ็ดน้อย", "เผ็ดกลาง", "เผ็ดมาก"], "เผ็ดกลาง")
                note = st.text_input("หมายเหตุ (เช่น แพ้ถั่ว)")
                slip, ttime = None, ""
                if method == db.PAY_TRANSFER:
                    slip = st.file_uploader("แนบสลิปโอนเงิน (PNG / JPG ไม่เกิน 3MB)", type=SLIP_TYPES, key="slip_up")
                    ttime = st.text_input("เวลาที่โอน (ไม่บังคับ เช่น 14:35)")
                ok = st.form_submit_button(f"ยืนยันสั่งซื้อ · {baht(total)}", use_container_width=True, type="primary")
            if ok:
                name, note = clean_text(name, 80), clean_text(note, 200)
                if not (name and phone.strip()):
                    st.error("กรุณากรอกชื่อและเบอร์โทร")
                elif not valid_phone(phone):
                    st.error("เบอร์โทรไม่ถูกต้อง กรุณากรอกตัวเลข 8-15 หลัก")
                elif otype == db.TYPE_DELIVERY and not address.strip():
                    st.error("กรุณากรอกที่อยู่จัดส่ง")
                elif otype == db.TYPE_DINE and not table.strip():
                    st.error("กรุณาระบุหมายเลขโต๊ะ")
                elif method == db.PAY_TRANSFER and slip is None:
                    st.error("เลือกโอนเงิน ต้องแนบสลิปก่อนยืนยัน (หรือเปลี่ยนเป็นจ่ายเงินสดในขั้นตอนที่ 4)")
                elif slip is not None and len(slip.getvalue()) > MAX_SLIP:
                    st.error("ไฟล์สลิปใหญ่เกิน 3MB กรุณาลดขนาดรูปแล้วลองใหม่")
                else:
                    oid = db.create_order(name, phone.strip(), clean_text(address, 300) or "-",
                                          f"[{spice}] {note}".strip(), dict(cart), clean_text(ttime, 20) or "-", code,
                                          otype, table.strip(), pts, payment_method=method,
                                          slip=slip.getvalue() if slip else None, slip_mime=slip.type if slip else None)
                    if oid:
                        st.session_state.cart = {}
                        st.session_state.last_order = (oid, phone.strip())
                        st.session_state.track = (oid, phone.strip())
                        st.session_state.page = "ติดตามออเดอร์"
                        st.rerun()
                    else:
                        st.error("สั่งไม่สำเร็จ (สต็อกอาจไม่พอ) กรุณาตรวจสอบตะกร้าอีกครั้ง")

    # ---------------- ฝั่งขวา: สรุปยอด (ติดอยู่กับหน้าจอขณะเลื่อน) ----------------
    with right:
        with st.container(key="sum_sticky"):
            if otype == db.TYPE_DELIVERY:
                C.delivery_progress(subtotal - disc - pts)
            rows = [f'<div class="sum-row"><span>ยอดอาหาร</span><span>{baht(subtotal)}</span></div>']
            if disc:
                rows.append(f'<div class="sum-row disc"><span>ส่วนลดโค้ด</span><span>-{baht(disc)}</span></div>')
            if pts:
                rows.append(f'<div class="sum-row disc"><span>ใช้แต้มสะสม</span><span>-{baht(pts)}</span></div>')
            if otype == db.TYPE_DELIVERY:
                rows.append(f'<div class="sum-row"><span>ค่าจัดส่ง</span><span>{baht(fee) if fee else "ฟรี"}</span></div>')
            earn = int(total // float(db.get_setting("points_rate")))
            render(f"""
            <div class="summary-card"><h4>สรุปคำสั่งซื้อ</h4>{''.join(rows)}
            <div class="sum-row total"><span>ยอดชำระทั้งหมด</span><span>{baht(total)}</span></div>
            <div class="sum-meta"><span>{esc(labels[otype])}</span><span>{esc(method)}</span></div>
            <div class="sum-note">จะได้รับประมาณ {earn} แต้ม หลังร้านยืนยันการชำระเงิน</div></div>""")


def order_done_banner():
    if "last_order" in st.session_state:
        oid, phone = st.session_state.last_order
        st.success(f"สั่งซื้อสำเร็จ! เลขออเดอร์ **#{oid}** (เบอร์ {phone}) · รอร้านยืนยันการชำระเงิน "
                   f"ติดตามสถานะได้ที่หน้านี้ตลอดเวลา")


# =====================================================================
# จองโต๊ะ
# =====================================================================
def page_reserve():
    C.page_title("จองโต๊ะ", "จองล่วงหน้าเพื่อความสะดวก ร้านจะยืนยันกลับตามเบอร์ที่ให้ไว้")
    left, right = st.columns([3, 2], gap="large")
    with left:
        with st.form("resv", clear_on_submit=True):
            c = st.columns(2)
            name, phone = c[0].text_input("ชื่อผู้จอง"), c[1].text_input("เบอร์โทร")
            c = st.columns(3)
            d = c[0].date_input("วันที่", min_value=date.today())
            t = c[1].time_input("เวลา", time(18, 0))
            g = c[2].number_input("จำนวนที่นั่ง", 1, 30, 2)
            note = st.text_input("ความต้องการพิเศษ (เช่น วันเกิด, ริมหน้าต่าง)")
            if st.form_submit_button("จองโต๊ะ", use_container_width=True, type="primary"):
                if not (name.strip() and phone.strip()):
                    st.error("กรุณากรอกชื่อและเบอร์โทร")
                elif not valid_phone(phone):
                    st.error("เบอร์โทรไม่ถูกต้อง กรุณากรอกตัวเลข 8-15 หลัก")
                else:
                    rid = db.create_reservation(clean_text(name, 80), phone.strip(), str(d), t.strftime("%H:%M"), g,
                                                clean_text(note, 200))
                    st.success(f"ส่งคำขอจองเลขที่ #{rid} แล้ว รอร้านยืนยัน ตรวจสถานะได้ทางขวามือ")
    with right:
        render(f"""
        <div class="info-card"><b>ข้อมูลการจอง</b><br>
        เวลาให้บริการ {esc(C.cfg('open_hours'))}<br>สอบถาม {esc(C.cfg('phone'))}<br>
        {esc(C.cfg('address'))}</div>""")
        st.markdown("#### ตรวจสอบสถานะการจอง")
        ph = st.text_input("เบอร์โทรที่ใช้จอง", key="resv_phone")
        if ph.strip():
            found = db.get_reservations(ph)
            if not found:
                st.info("ไม่พบการจองจากเบอร์นี้")
            for r in found:
                kind = {"ยืนยันแล้ว": "ok", "ยกเลิก": "bad"}.get(r["status"], "wait")
                render(f"""<div class="info-card" style="margin-bottom:.5rem">#{r['id']} · {esc(r['date'])} {esc(r['time'])}
                · {r['guests']} ที่นั่ง<br><span class="badge {kind}">{esc(r['status'])}</span></div>""")


# =====================================================================
# สมาชิก / แต้มสะสม (ไม่ต้องสมัคร ระบบสร้างให้อัตโนมัติเมื่อสั่งครั้งแรก)
# =====================================================================
def page_member():
    C.page_title("แต้มสะสมของคุณ", f"สมัครอัตโนมัติเมื่อสั่งอาหารครั้งแรก · ทุก ฿{C.cfg('points_rate')} ได้ 1 แต้ม "
                                   f"(Gold x1.5 · Platinum x2) · 1 แต้ม = ฿1")
    phone = st.text_input("เบอร์โทรที่ใช้สั่งอาหาร", key="member_phone", placeholder="กรอกเบอร์เพื่อดูแต้มและประวัติ").strip()
    if not phone:
        render('<div class="info-card">กรอกเบอร์โทรที่เคยใช้สั่งอาหาร เพื่อดูแต้มสะสมและประวัติการสั่งซื้อ</div>')
        return
    m = db.get_member(phone)
    if not m:
        st.warning("ยังไม่พบข้อมูลของเบอร์นี้ · ลองสั่งอาหารสักครั้ง ระบบจะสร้างแต้มสะสมให้อัตโนมัติ")
        return
    tier, mult = db.tier_info(m["total_spent"])
    C.kpi_grid([("ระดับ", tier), ("แต้มสะสม", f"{m['points']:,}"), ("ยอดสะสม", baht(m["total_spent"])),
                ("ตัวคูณแต้ม", f"x{mult}")])
    nxt = db.next_tier(m["total_spent"])
    if nxt:
        st.progress(min(m["total_spent"] / nxt[1], 1.0), text=f"อีก {baht(nxt[1] - m['total_spent'])} ถึงระดับ {nxt[0]}")
    st.markdown("#### ประวัติการสั่งซื้อ")
    for o in db.get_orders_by_phone(phone):
        render(f"""<div class="info-card" style="margin-bottom:.5rem">#{o['id']} · {esc(o['created_at'][:16])} · {esc(o['order_type'])}
        · <b>{baht(o['total'])}</b> &nbsp; {C.status_badge(o['order_status'])}</div>""")


# =====================================================================
# ติดตามออเดอร์ + ใบเสร็จ
# =====================================================================
def _vat(total):
    from receipt_pdf import vat_split
    return vat_split(total)


def shop_info():
    """ข้อมูลร้านสำหรับหัวใบเสร็จ (ดึงจากหน้าตั้งค่าแอดมิน)"""
    return {"name": C.shop(), "tagline": C.cfg("tagline"), "address": C.cfg("address"),
            "phone": C.cfg("phone"), "hours": C.cfg("open_hours")}


def build_receipt(o, items):
    rows = "".join(f"<tr><td>{esc(i['name'])}</td><td align=center>{i['qty']}</td>"
                   f"<td align=right>{i['price'] * i['qty']:,.0f}</td></tr>" for i in items)
    return f"""<html><meta charset="utf-8"><body style="font-family:sans-serif;max-width:420px;margin:auto;color:#3B1F14">
<div style="background:#8B1A1A;color:#F2D272;padding:14px;text-align:center;border-bottom:4px solid #D4A017">
<h2 style="margin:0">{esc(C.shop())}</h2><div>ใบเสร็จรับเงิน · {esc(o['receipt_no'] or '')}</div></div>
<p>ออเดอร์ #{o['id']} ({esc(o['order_type'])}) · {esc(o['payment_method'] or 'โอนเงิน')}<br>ลูกค้า: {esc(o['customer_name'])}<br>วันที่: {o['updated_at']}</p>
<table width=100%>{rows}</table><hr>
<p align=right>ยอดอาหาร {o['subtotal']:,.0f}<br>ส่วนลด -{o['discount'] or 0:,.0f}<br>ใช้แต้ม -{o['points_used'] or 0:,.0f}<br>ค่าส่ง {o['delivery_fee']:,.0f}<br>
<b>รวมทั้งสิ้น {o['total']:,.2f} บาท</b><br><small>ราคาก่อน VAT {_vat(o['total'])[0]:,.2f} · VAT {_vat(o['total'])[1]:,.2f} (รวมในราคาแล้ว)</small></p><p align=center>ชำระเงินแล้ว · ขอบคุณที่อุดหนุน Namaste</p></body></html>"""


def page_track():
    C.page_title("ติดตามออเดอร์", "กรอกเลขออเดอร์และเบอร์โทรที่ใช้สั่ง เพื่อดูสถานะล่าสุด")
    order_done_banner()
    d_oid, d_phone = st.session_state.get("last_order", (1, ""))
    c1, c2, c3 = st.columns([2, 3, 2])
    oid = c1.number_input("เลขออเดอร์", min_value=1, value=d_oid, step=1)
    phone = c2.text_input("เบอร์โทรที่สั่ง", value=d_phone)
    c3.markdown('<div style="height:1.7rem"></div>', unsafe_allow_html=True)
    if c3.button("ค้นหา", type="primary", use_container_width=True, icon=":material/search:"):
        st.session_state.track = (int(oid), phone)
    if "track" not in st.session_state:
        return
    o = db.track_order(*st.session_state.track)
    if not o:
        st.error("ไม่พบออเดอร์ ตรวจสอบเลขออเดอร์และเบอร์โทรอีกครั้ง")
        return
    render(f'<h3 style="margin-bottom:.2rem">ออเดอร์ #{o["id"]} &nbsp;{C.status_badge(o["order_status"])}</h3>')
    if o["order_status"] == db.ST_CANCEL:
        st.error("ออเดอร์ถูกยกเลิก (ตรวจสอบการชำระเงินไม่ผ่าน) กรุณาติดต่อร้าน")
    else:
        C.timeline(o["order_type"], o["order_status"])
    if o["order_type"] == db.TYPE_DINE:
        st.caption(f"ทานที่ร้าน · โต๊ะ {o['table_no']}")
    elif o["order_type"] == db.TYPE_PICKUP:
        st.caption("รับที่ร้าน · มารับเมื่อสถานะเป็น “อาหารพร้อมแล้ว”")
    if o["rider_name"]:
        st.info(f"ผู้ส่ง: {o['rider_name']}  โทร {o['rider_phone'] or '-'}")
    method = o["payment_method"] or db.PAY_TRANSFER
    render(f'<div class="info-card">วิธีชำระเงิน: <b>{esc(method)}</b> &nbsp;{C.pay_badge(o["payment_status"])}</div>')
    if method == db.PAY_TRANSFER and o["order_status"] == db.ST_WAIT:
        sl = db.get_slip(o["id"])
        if sl:
            st.success("ร้านได้รับสลิปของคุณแล้ว กำลังตรวจสอบ")
            with st.expander("ดูสลิปที่แนบไว้"):
                st.image(bytes(sl["data"]), width=280)
        else:
            st.warning("ยังไม่พบสลิปโอนเงิน กรุณาแนบสลิปเพื่อให้ร้านตรวจสอบและเริ่มทำอาหาร")
        up = st.file_uploader("แนบ/เปลี่ยนสลิป (PNG / JPG ไม่เกิน 3MB)", type=SLIP_TYPES, key=f"slip_late_{o['id']}")
        if up is not None and st.button("ส่งสลิป", type="primary", key=f"slip_send_{o['id']}"):
            if len(up.getvalue()) > MAX_SLIP:
                st.error("ไฟล์สลิปใหญ่เกิน 3MB")
            elif db.attach_slip(o["id"], o["phone"], up.getvalue(), up.type):
                st.rerun()
            else:
                st.error("แนบสลิปไม่สำเร็จ (ออเดอร์อาจถูกยืนยันหรือยกเลิกแล้ว)")
    elif method == db.PAY_CASH and o["order_status"] == db.ST_WAIT:
        st.info("ชำระเงินสด: กรุณาจ่ายเงินที่ร้านหรือตอนรับอาหาร ร้านจะยืนยันและเริ่มทำอาหาร")
    items = db.get_order_items(o["id"])
    lines = "".join(f"<div>• {esc(it['name'])} × {it['qty']} — {baht(it['price'] * it['qty'])}</div>" for it in items)
    render(f"""<div class="info-card">{lines}<hr>
    <b>รวม {baht(o['total'])}</b> (ส่วนลด {baht(o['discount'] or 0)} · ค่าส่ง {baht(o['delivery_fee'])})
    · สั่งเมื่อ {esc(o['created_at'])}</div>""")
    if o["receipt_no"]:
        st.success(f"ออกใบเสร็จแล้ว เลขที่ {o['receipt_no']}" +
                   (f" · ได้รับ {o['points_earned']} แต้ม" if o["points_earned"] else ""))
        try:
            from receipt_pdf import build_receipt_pdf
            st.download_button("ดาวน์โหลดใบเสร็จ (PDF)", build_receipt_pdf(o, items, shop_info()), type="primary",
                               file_name=f"{o['receipt_no']}.pdf", mime="application/pdf", icon=":material/download:")
        except Exception as e:  # ไม่มี reportlab / ไม่พบฟอนต์ -> ใช้ไฟล์ HTML แทนและบอกวิธีแก้
            st.warning(f"สร้างไฟล์ PDF ไม่ได้ ({e}) · ติดตั้งด้วย: pip install reportlab")
            st.download_button("ดาวน์โหลดใบเสร็จ (HTML)", build_receipt(o, items),
                               file_name=f"{o['receipt_no']}.html", mime="text/html", icon=":material/download:")
    if o["order_status"] == db.ST_DONE:
        if o["rating"]:
            st.write(f"รีวิวของคุณ: {'★' * o['rating']}  {o['review'] or ''}")
        else:
            with st.form("review"):
                r = st.slider("ให้คะแนนความพึงพอใจ", 1, 5, 5)
                t = st.text_input("ความคิดเห็น")
                if st.form_submit_button("ส่งรีวิว", type="primary"):
                    db.add_review(o["id"], r, t)
                    st.rerun()
    st.button("รีเฟรชสถานะ", icon=":material/refresh:")
