"""ui/components.py - ชิ้นส่วนหน้าตาที่ใช้ซ้ำทั้งเว็บ (หัวเว็บ, แบนเนอร์, การ์ดอาหาร, ฟุตเตอร์ ฯลฯ)

หน้าต่าง ๆ ใน views/ เรียกใช้ฟังก์ชันจากไฟล์นี้ เพื่อให้ทุกหน้าหน้าตาเหมือนกัน
ถ้าอยากเปลี่ยนตำแหน่งโลโก้: แก้ LOGO_SIDE เป็น "left" หรือ "right"
"""
import base64
import html
import os

import streamlit as st

import database as db
from utils import is_open_now
from ui import assets as A
from ui import content

from config import LOGO_FILES, LOGO_SIDE   # ตำแหน่งโลโก้ ("right"/"left") และชื่อไฟล์โลโก้ที่ค้นหา แก้ได้ใน config.py
NAV_PAGES = ["หน้าแรก", "เมนูอาหาร", "จองโต๊ะ", "สมาชิก", "ติดตามออเดอร์"]
CART_PAGE = "ตะกร้า"
ADMIN_PAGE = "แอดมิน"

esc = html.escape


# ---------------------------------------------------------------- ตัวช่วยพื้นฐาน
def H(s):
    """ตัดช่องว่างหน้าบรรทัดของ HTML (กัน Markdown มองว่าเป็นบล็อกโค้ด)"""
    return "".join(line.strip() for line in s.splitlines())


def render(s):
    st.markdown(H(s), unsafe_allow_html=True)


def baht(x):
    return f"฿{x:,.0f}"


def refresh_cfg():
    """โหลดการตั้งค่าร้านเก็บไว้ในหน่วยความจำของรอบนี้ (เรียกต้นสคริปต์ครั้งเดียว)"""
    st.session_state["_cfg"] = db.get_all_settings()


def cfg(key, default=""):
    data = st.session_state.get("_cfg")
    if data is None:
        refresh_cfg()
        data = st.session_state["_cfg"]
    value = data.get(key, default)
    return default if value is None else value


def shop():
    return cfg("shop_name", "Maharaja Palace")


def safe_url(u):
    """รับเฉพาะลิงก์ http/https เพื่อความปลอดภัย"""
    u = (u or "").strip()
    return u if u.lower().startswith(("http://", "https://")) else ""


# ---------------------------------------------------------------- การนำทาง
def go(page, **state):
    """เปลี่ยนหน้า (ใช้เป็น on_click ของปุ่ม) และตั้งค่า session_state เพิ่มเติมได้"""
    st.session_state.page = page
    for k, v in state.items():
        st.session_state[k] = v


def add_to_cart(mid, stock, name):
    cur = st.session_state.cart.get(mid, 0)
    if 0 <= stock <= cur:
        st.toast("สต็อกไม่พอสำหรับเมนูนี้", icon=":material/warning:")
    else:
        st.session_state.cart[mid] = cur + 1
        st.toast(f"เพิ่ม {name} แล้ว", icon=":material/shopping_cart:")


def cart_count():
    return sum(st.session_state.cart.values())


def cart_total(menu_rows):
    by_id = {m["id"]: m for m in menu_rows}
    return sum(by_id[k]["price"] * q for k, q in st.session_state.cart.items() if k in by_id)


def ico(name, size=18, color=A.MAROON):
    """ไอคอนเส้นขนาดเล็กแทนอิโมจิ (ใช้ในข้อความ HTML)"""
    return f'<img class="ico" src="{A.svg_src(A.line_icon(name, color))}" width="{size}" height="{size}" alt="">'


# ---------------------------------------------------------------- โลโก้
def _mime_of(path):
    ext = os.path.splitext(path)[1].lower()
    return {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".svg": "image/svg+xml"}.get(ext, "image/png")


def logo_src():
    """ลำดับความสำคัญ: โลโก้ที่อัปโหลดในแอดมิน > ไฟล์ logo.* ในโฟลเดอร์ > โลโก้ในตัว"""
    data, mime = cfg("logo_data"), cfg("logo_mime")
    if data:
        return f"data:{mime or 'image/png'};base64,{data}"
    for name in LOGO_FILES:
        if os.path.exists(name):
            with open(name, "rb") as f:
                return f"data:{_mime_of(name)};base64," + base64.b64encode(f.read()).decode()
    return A.svg_src(A.logo_svg())


def brand_html(side=None):
    side = side or LOGO_SIDE
    img = f'<img src="{logo_src()}" alt="logo">'
    text = (f'<div class="brand-text"><div class="brand-name">{esc(shop())}</div>'
            f'<div class="brand-sub">Royal Indian Cuisine</div></div>')
    body = (img + text) if side == "left" else (text + img)
    return f'<div class="brand {"left" if side == "left" else ""}">{body}</div>'


# ---------------------------------------------------------------- หัวเว็บ
def open_status():
    """ป้ายสถานะร้านตามเวลาปัจจุบัน (อ่านจากการตั้งค่า 'เวลาเปิด-ปิด')"""
    state = is_open_now(cfg("open_hours"))
    if state is None:
        return ""
    return ('<span class="open-pill on">● เปิดอยู่ตอนนี้</span>' if state
            else '<span class="open-pill off">● ปิดบริการ</span>')


def utility_bar():
    g = A.GOLD_LIGHT
    render(f"""
    <div class="utility">
      {open_status()}
      <span>{ico('clock', 16, g)}เปิดบริการ <b>{esc(cfg('open_hours'))}</b></span>
      <span>{ico('phone', 16, g)}<b>{esc(cfg('phone'))}</b></span>
      <span>{ico('truck', 16, g)}ส่งฟรีเมื่อครบ <b>{baht(db.free_over())}</b></span>
    </div>""")


def topbar():
    """แถบเมนูหลัก: ปุ่มนำทาง + ปุ่มตะกร้า + โลโก้ (ไม่มีปุ่มเข้าสู่ระบบสมาชิก)"""
    pages = NAV_PAGES + ([ADMIN_PAGE] if st.session_state.get("admin") else [])
    current = st.session_state.page
    menu_rows = db.get_menu(only_available=True)
    qty = cart_count()
    cart_label = f"ตะกร้า · {qty} · {baht(cart_total(menu_rows))}" if qty else "ตะกร้า"

    with st.container(key="topbar"):
        if LOGO_SIDE == "left":
            c_brand, c_nav, c_cart = st.columns([3.4, 7, 2.6])
        else:
            c_nav, c_cart, c_brand = st.columns([7, 2.6, 3.4])
        with c_nav:
            for col, pg, n in zip(st.columns(len(pages)), pages, range(len(pages))):
                col.button(pg, key=f"nav_{n}", use_container_width=True, on_click=go, args=(pg,),
                           type="primary" if pg == current else "secondary")
        with c_cart:
            st.button(cart_label, key="cart_btn", on_click=go, args=(CART_PAGE,), use_container_width=True,
                      icon=":material/shopping_cart:")
        with c_brand:
            render(brand_html())
    render('<div class="toran"></div>')


def ticker():
    """แถบข้อความโปรโมชันวิ่งต่อเนื่อง"""
    msgs = [cfg("promo_banner"), f"เปิด {cfg('open_hours')}",
            f"ส่งฟรีเมื่อสั่งครบ {baht(db.free_over())}",
            f"ทุก ฿{cfg('points_rate')} ได้ 1 แต้ม สะสมแต้มแลกส่วนลดได้",
            "ทานที่ร้าน · รับเองที่ร้าน · จัดส่งถึงบ้าน"]
    msgs = [m for m in msgs if m]
    one = "".join(f"<span>{esc(m)}</span>" for m in msgs)
    render(f'<div class="ticker"><div class="ticker-track">{one}{one}</div></div>')


# ---------------------------------------------------------------- ส่วนหัวข้อ
def section(title, sub="", kicker="", ornament=True):
    orn = f'<img src="{A.svg_src(A.divider())}" alt="">' if ornament else ""
    k = f'<div class="sec-kicker">{esc(kicker)}</div>' if kicker else ""
    s = f'<div class="sec-sub">{esc(sub)}</div>' if sub else ""
    render(f'<div class="sec">{k}<div class="sec-title">{esc(title)}</div>{s}{orn}</div>')


def page_title(title, sub=""):
    s = f"<p>{esc(sub)}</p>" if sub else ""
    render(f'<div class="page-title"><h1>{esc(title)}</h1>{s}</div>')


# ---------------------------------------------------------------- แบนเนอร์หลัก
def _art(item, fallback):
    """รูปในจานของสไลด์: ใช้รูปเมนูจริงถ้ามี ไม่มีก็ใช้อีโมจิ"""
    if item is not None and item["image"]:
        b64 = base64.b64encode(item["image"]).decode()
        return f'<img src="data:image/jpeg;base64,{b64}" alt="">'
    if item is not None and item["emoji"]:
        return esc(item["emoji"])
    return fallback


def hero_slider(menu):
    feat = [i for i in menu if i["tag"] and "ขายดี" in i["tag"]] + [i for i in menu if not (i["tag"] and "ขายดี" in i["tag"])]
    pick = (feat + [None, None, None])[:3]
    pa = A.svg_src(A.paisley(A.GOLD, A.MAROON_DARK))
    pb = A.svg_src(A.paisley(A.GOLD_LIGHT, A.MAROON))
    about = cfg("about_text")
    about = about if len(about) <= 150 else about[:147] + "…"

    def slide(cls, kicker, title, desc, pill, art):
        return f"""
        <div class="slide {cls}">
          <div class="slide-text">
            <div class="slide-kicker">{kicker}</div>
            <div class="slide-title">{title}</div>
            <div class="slide-desc">{desc}</div>
            <span class="slide-pill">{pill}</span>
          </div>
          <div class="slide-art">
            <img class="paisley-a" src="{pa}" alt=""><img class="paisley-b" src="{pb}" alt="">
            <div class="plate">{art}</div>
          </div>
        </div>"""

    promo = cfg("promo_banner") or "สั่งอาหารออนไลน์ได้ง่าย ๆ"
    promo = promo if len(promo) <= 70 else promo[:67] + "…"
    s1 = slide("s1", esc(cfg("tagline") or "Royal Indian Cuisine"),
               f"ยินดีต้อนรับสู่<br><em>{esc(shop())}</em>", esc(about), esc(promo), _art(pick[0], "🍛"))
    s2 = slide("s2", "FRESH SPICES · เครื่องเทศสด", "รสจัดจ้านแบบ<br><em>ต้นตำรับอินเดีย</em>",
               "ปรุงด้วยเครื่องเทศสดและเตาดินแบบดั้งเดิม ใส่ใจทุกจาน เพื่อประสบการณ์รสชาติระดับมหาราชา",
               "ดูเมนูแนะนำของเชฟด้านล่าง", _art(pick[1], "🍛"))
    s3 = slide("s3", "ORDER YOUR WAY · สั่งได้ตามใจ", "ทานที่ร้าน รับเอง<br><em>หรือส่งถึงบ้าน</em>",
               f"สั่งง่าย ไม่ต้องสมัครสมาชิก ส่งฟรีเมื่อสั่งครบ {baht(db.free_over())} ติดตามสถานะได้ตลอด",
               f"เปิด {esc(cfg('open_hours'))}", _art(pick[2], "🍛"))
    render(f'<div class="hero">{s1}{s2}{s3}</div>')


def info_chips(reviews):
    rate = (f"{ico('star')}<b>{sum(r['rating'] for r in reviews) / len(reviews):.1f}/5</b> ({len(reviews)} รีวิว)"
            if reviews else f"{ico('star')}<b>ยินดีต้อนรับลูกค้าใหม่</b>")
    render(f"""
    <div class="chips">
      <span class="chip">{ico('utensils')}<b>ทานที่ร้าน</b></span>
      <span class="chip">{ico('store')}<b>รับที่ร้าน</b></span>
      <span class="chip">{ico('truck')}<b>จัดส่งถึงบ้าน</b></span>
      <span class="chip">{ico('leaf')}มีเมนู<b>มังสวิรัติ</b></span>
      <span class="chip">{rate}</span>
    </div>""")


# ---------------------------------------------------------------- การ์ดอาหาร
def dish_card(i, kp):
    """การ์ดเมนูหนึ่งใบ + ปุ่มใส่ตะกร้า"""
    stock = i["stock"] if i["stock"] is not None else -1
    tag = i["tag"] or ""
    veg = '<span class="veg-mark" title="มังสวิรัติ"></span>' if "มังสวิรัติ" in tag else ""
    badge = f'<span class="dish-tag">{esc(tag)}</span>' if tag and "มังสวิรัติ" not in tag else ""
    left = f'<span class="dish-left">เหลือ {stock} ที่</span>' if 0 <= stock <= 5 else ""
    if i["image"]:
        media = f'<img src="data:image/jpeg;base64,{base64.b64encode(i["image"]).decode()}" alt="{esc(i["name"])}">'
    else:
        media = f'<span class="emo">{esc(i["emoji"] or "🍛")}</span>'
    with st.container(key=f"card_{kp}_{i['id']}"):
        render(f"""
        <div class="dish-media">{veg}{badge}{media}</div>
        <div class="dish-body">
          <div class="dish-name">{esc(i['name'])}</div>
          <div class="dish-th">{esc(i['name_th'] or '')}</div>
          <div class="dish-desc">{esc(i['description'] or '')}</div>
          <div class="dish-price">{baht(i['price'])} {left}</div>
        </div>""")
        st.button("ใส่ตะกร้า", key=f"{kp}add{i['id']}", use_container_width=True, type="primary",
                  icon=":material/add_shopping_cart:",
                  on_click=add_to_cart, args=(i["id"], stock, i["name"]))


def dish_grid(items, kp, per_row=4):
    """จัดการ์ดเป็นตารางตามจำนวนคอลัมน์"""
    for start in range(0, len(items), per_row):
        row = items[start:start + per_row]
        cols = st.columns(per_row)
        for col, it in zip(cols, row):
            with col:
                dish_card(it, kp)
        render('<div style="height:.6rem"></div>')


# ---------------------------------------------------------------- หมวดหมู่ / โปรโมชัน / จุดเด่น

_CAT_IMAGES = {
    "ของทานเล่น": "starters.jpg",
    "ทันดูรี": "tandoori.jpg",
    "แกงอินเดีย": "curry.jpg",
    "ข้าวและขนมปัง": "rice_bread.jpg",
    "ของหวานและเครื่องดื่ม": "desserts.jpg",
}


def _cat_image(cat):
    """path รูปประจำหมวดจากโฟลเดอร์ ui/images ถ้าไม่มีไฟล์คืน None (ไม่พึ่งฟังก์ชันใน assets.py)"""
    name = _CAT_IMAGES.get(cat)
    if not name:
        return None
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", name)
    return path if os.path.isfile(path) else None


def category_tiles(menu):
    """การ์ดหมวดหมู่ กรอบกระจกใส: รูป (ถ้ามี) ชื่อ จำนวนเมนู และปุ่ม อยู่ในการ์ดเดียว"""
    cats = list(dict.fromkeys(i["category"] for i in menu if i["category"]))
    if not cats:
        return

    cols = st.columns(min(len(cats), 5))

    for index, cat in enumerate(cats):
        n = sum(1 for i in menu if i["category"] == cat)

        with cols[index % len(cols)]:
            with st.container(key=f"catcard_{index}"):
                image_path = _cat_image(cat)

                if image_path:
                    st.image(image_path, use_container_width=True)

                # ใช้ render() เพื่อตัดช่องว่างหน้าบรรทัด ไม่งั้น Markdown มองเป็นบล็อกโค้ด (ทำให้มีแถบสีส้มพาดข้อความ)
                render(f'<div class="cat-tile"><div class="cat-name">{esc(cat)}</div>'
                       f'<div class="cat-count">{n} เมนู</div></div>')

                st.button(
                    "ดูหมวดนี้",
                    key=f"cat_{index}_{cat}",
                    use_container_width=True,
                    on_click=go,
                    args=("เมนูอาหาร",),
                    kwargs={"menu_cat": cat},
                )


def promo_cards():
    coupons = db.get_active_coupons()
    if not coupons:
        return
    cols = st.columns(min(len(coupons), 3))
    for n, cp in enumerate(coupons[:3]):
        mn = f"เมื่อซื้อครบ {baht(cp['min_total'])}" if cp["min_total"] else "ไม่มีขั้นต่ำ"
        with cols[n % len(cols)]:
            render(f"""
            <div class="promo-card">
              <div class="promo-pct">{cp['percent']:.0f}%<small>ลด</small></div>
              <div class="promo-code">{esc(cp['code'])}</div>
              <div class="promo-desc">ส่วนลด {cp['percent']:.0f}% {mn}</div>
              <span class="promo-use">กรอกโค้ดที่หน้าตะกร้า</span>
            </div>""")


def feature_blocks():
    items = [("leaf", "เครื่องเทศสดใหม่", "คัดเครื่องเทศและสมุนไพรปรุงสดทุกจานเพื่อกลิ่นรสที่เข้มข้นแบบต้นตำรับ"),
             ("flame", "เตาดินทันดูร์", "ย่างด้วยเตาดินแบบดั้งเดิม ได้กลิ่นหอมควันและเนื้อสัมผัสที่เป็นเอกลักษณ์"),
             ("truck", "สั่งง่าย ส่งถึงบ้าน", "ไม่ต้องสมัครสมาชิก สั่งได้ทันที ติดตามสถานะออเดอร์ได้ตลอด"),
             ("gift", "สะสมแต้มทุกออเดอร์", f"ทุก ฿{cfg('points_rate')} ได้ 1 แต้ม ใช้แต้มแทนเงินสดได้ 1 แต้ม = ฿1")]
    cols = st.columns(len(items))
    for col, (name, t, d) in zip(cols, items):
        with col:
            render(f'<div class="feature"><div class="f-ico">{ico(name, 32, A.GOLD_LIGHT)}</div>'
                   f'<div class="f-title">{t}</div><div class="f-desc">{d}</div></div>')


def review_cards(reviews, limit=3):
    if not reviews:
        return
    cols = st.columns(min(limit, len(reviews)))
    for col, r in zip(cols, reviews[:limit]):
        name = (r["customer_name"] or "ลูกค้า").split()[0]
        with col:
            render(f"""
            <div class="review-card"><div class="review-stars">{'★' * r['rating']}{'☆' * (5 - r['rating'])}</div>
            <div class="review-text">{esc(r['review'] or 'อร่อยมาก ขอบคุณค่ะ/ครับ')}</div>
            <div class="review-by">— คุณ{esc(name)}</div></div>""")


# ---------------------------------------------------------------- ความรู้เครื่องเทศ / ระดับความเผ็ด
def spice_guide():
    """การ์ดแนะนำเครื่องเทศอินเดีย + แถบอธิบายระดับความเผ็ด"""
    cards = "".join(
        f'<div class="spice-card"><div class="sp-ico">{ico}</div><div class="sp-th">{esc(th)}</div>'
        f'<div class="sp-en">{esc(en)}</div><div class="sp-desc">{esc(desc)}</div></div>'
        for ico, th, en, desc in content.SPICES)
    levels = "".join(
        f'<span class="lvl"><b>{"●" * n}{"○" * (3 - n)}</b> {esc(lb)} <i>{esc(ds)}</i></span>'
        for lb, n, ds in content.SPICE_LEVELS)
    render(f'<div class="spice-grid">{cards}</div><div class="lvl-row">{levels}</div>')



def category_heading(cat, items, count):
    """หัวข้อหมวดอาหารพร้อมรูปภาพ"""
    image_path = _cat_image(cat)

    if image_path:
        col_img, col_text = st.columns([1, 5])

        with col_img:
            st.image(image_path, use_container_width=True)

        with col_text:
            st.markdown(
                f"""
                <div class="cat-head">
                    <span class="ch-name">{esc(cat)}</span>
                    <span class="ch-count">{count} เมนู</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f"""
            <div class="cat-head">
                <span class="ch-name">{esc(cat)}</span>
                <span class="ch-count">{count} เมนู</span>
            </div>
            """,
            unsafe_allow_html=True
        )



def delivery_progress(subtotal):
    """แถบความคืบหน้าส่งฟรี: บอกว่าต้องสั่งเพิ่มอีกเท่าไรจึงส่งฟรี"""
    target = db.free_over()
    if target <= 0:
        return
    if subtotal >= target:
        st.success("ได้รับสิทธิ์ส่งฟรีแล้ว!")
    else:
        st.progress(min(subtotal / target, 1.0), text=f"สั่งเพิ่มอีก {baht(target - subtotal)} รับสิทธิ์ส่งฟรี")


def upsell_row(menu, cart, cats=("ข้าวและขนมปัง", "ของหวานและเครื่องดื่ม"), limit=4):
    """แนะนำเมนูที่มักสั่งคู่กัน (ขนมปัง/ข้าว/ของหวาน) ที่ยังไม่อยู่ในตะกร้า"""
    picks = [m for m in menu.values() if m["id"] not in cart and m["category"] in cats][:limit]
    if not picks:
        return
    st.markdown("##### สั่งคู่กันอร่อยกว่า")
    for col, m in zip(st.columns(len(picks)), picks):
        stock = m["stock"] if m["stock"] is not None else -1
        col.button(f"{m['name']} · {baht(m['price'])}", key=f"up_{m['id']}", icon=":material/add:",
                   use_container_width=True, on_click=add_to_cart, args=(m["id"], stock, m["name"]))


# ---------------------------------------------------------------- สถานะออเดอร์
def status_badge(status):
    kind = {db.ST_WAIT: "wait", db.ST_COOK: "info", db.ST_READY: "info", db.ST_SHIP: "info",
            db.ST_DONE: "ok", db.ST_CANCEL: "bad"}.get(status, "")
    return f'<span class="badge {kind}">{esc(status)}</span>'


def pay_badge(status):
    kind = {db.PAY_OK: "ok", db.PAY_FAIL: "bad", db.PAY_PENDING: "wait"}.get(status, "")
    return f'<span class="badge {kind}">{esc(status)}</span>'


def timeline(order_type, status):
    steps = db.steps_for(order_type)
    idx = steps.index(status) if status in steps else 0
    parts = []
    for k, s in enumerate(steps):
        cls = "on" if k <= idx else ""
        cls += " now" if k == idx else ""
        parts.append(f'<div class="tl-step {cls}"><div class="tl-dot">{"✓" if k < idx else k + 1}</div>'
                     f'<div class="tl-label">{esc(s)}</div></div>')
    render(f'<div class="timeline">{"".join(parts)}</div>')


def step_head(n, title, sub=""):
    """หัวข้อขั้นตอนแบบมีเลขวงกลม ใช้แบ่งหน้าสั่งอาหารเป็นช่วง ๆ ให้อ่านง่าย"""
    s = f'<div class="sh-s">{esc(sub)}</div>' if sub else ""
    render(f'<div class="step-head"><span class="sh-n">{n}</span><div><div class="sh-t">{esc(title)}</div>{s}</div></div>')


def checkout_steps(active):
    labels = ["ตรวจตะกร้า", "ข้อมูลผู้สั่ง", "ชำระเงิน"]
    out = []
    for n, lb in enumerate(labels, 1):
        out.append(f'<div class="co-step {"on" if n <= active else ""}"><span class="dot">{n}</span>{lb}</div>')
        if n < len(labels):
            out.append('<div class="co-line"></div>')
    render(f'<div class="checkout-steps">{"".join(out)}</div>')


# ---------------------------------------------------------------- ฟุตเตอร์
def footer():
    links = []
    for key, label in A.SOCIAL_ORDER:
        url = safe_url(cfg(key))
        if url:
            links.append(f'<a class="social-btn" href="{esc(url, quote=True)}" target="_blank" rel="noopener" '
                         f'title="{label}"><img src="{A.svg_src(A.social_icon(key))}" alt="{label}"></a>')
    social = f'<div class="social-row">{"".join(links)}</div>' if links else ""
    about = cfg("about_text")
    about = about if len(about) <= 170 else about[:167] + "…"
    render(f"""
    <div class="site-footer">
      <div class="footer-toran"></div>
      <div class="footer-grid">
        <div>
          <div class="footer-brand"><img src="{logo_src()}" alt="logo"><span class="n">{esc(shop())}</span></div>
          <p>{esc(about)}</p>
          <h5 style="margin-top:.9rem">ติดตามเรา</h5>
          {social}
        </div>
        <div>
          <h5>เวลาทำการ</h5>
          <ul><li>{ico('clock', 16, A.GOLD_LIGHT)}<span>{esc(cfg('open_hours'))}</span></li>
          <li>{ico('check', 16, A.GOLD_LIGHT)}<span>เปิดทุกวัน</span></li>
          <li>{ico('check', 16, A.GOLD_LIGHT)}<span>รับจองโต๊ะล่วงหน้าได้</span></li></ul>
        </div>
        <div>
          <h5>ติดต่อร้าน</h5>
          <ul><li>{ico('pin', 16, A.GOLD_LIGHT)}<span>{esc(cfg('address'))}</span></li>
          <li>{ico('phone', 16, A.GOLD_LIGHT)}<span>{esc(cfg('phone'))}</span></li></ul>
        </div>
        <div>
          <h5>บริการและการชำระเงิน</h5>
          <ul><li>{ico('utensils', 16, A.GOLD_LIGHT)}<span>ทานที่ร้าน · รับเอง · จัดส่ง</span></li>
          <li>{ico('truck', 16, A.GOLD_LIGHT)}<span>ค่าส่ง {baht(float(cfg('delivery_fee') or 0))} · ส่งฟรีเมื่อครบ {baht(db.free_over())}</span></li></ul>
          <div class="pay-row"><span class="pay-chip">โอนเงิน / QR</span><span class="pay-chip">เงินสด</span><span class="pay-chip">สะสมแต้ม</span></div>
        </div>
      </div>
      <div class="footer-bottom"><b>{esc(shop())}</b> · Namaste ขอบคุณที่ไว้วางใจ </div>
    </div>""")
    if not st.session_state.get("admin"):
        st.button("เข้าสู่ระบบพนักงาน", key="staff_btn", on_click=go, args=(ADMIN_PAGE,), icon=":material/lock:")


# ---------------------------------------------------------------- ส่วนของแอดมิน
def kpi_grid(items):
    """items = [(ป้าย, ค่า), ...] สูงสุด 4 ช่อง"""
    cells = "".join(f'<div class="kpi k{n}"><div class="kl">{esc(lb)}</div><div class="kv">{esc(str(v))}</div></div>'
                    for n, (lb, v) in enumerate(items, 1))
    render(f'<div class="kpi-grid">{cells}</div>')
