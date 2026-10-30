"""app.py - ร้านอาหารอินเดีย Maharaja Palace (Streamlit + SQLite)  ดีไซน์ใหม่โทนอินเดีย

รัน :  pip install -r requirements.txt   แล้ว   streamlit run app.py
โครงสร้างไฟล์
  app.py            จุดเริ่มต้น: ตั้งค่าหน้า โหลดธีม ประกอบหัวเว็บ/เนื้อหา/ฟุตเตอร์
  config.py         รหัสแอดมิน · รูป QR · ตำแหน่งโลโก้
  database.py       ฐานข้อมูล SQLite (ข้อมูลและฟังก์ชันเดิมทั้งหมด)
  ui/               ธีม CSS · กราฟิก SVG · ชิ้นส่วนหน้าตา (หัวเว็บ การ์ดอาหาร ฟุตเตอร์)
  views/customer.py หน้าลูกค้า: หน้าแรก เมนู ตะกร้า จองโต๊ะ สมาชิก ติดตามออเดอร์
  views/admin.py    หลังบ้านพนักงาน/เจ้าของร้าน
"""
import streamlit as st

from config import PAGE_ICON, PAGE_TITLE

# set_page_config ต้องเป็นคำสั่ง Streamlit คำสั่งแรกเสมอ
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide", initial_sidebar_state="collapsed")

# ตรวจสภาพแวดล้อมก่อนเริ่ม จะได้เห็นข้อความที่เข้าใจง่ายแทน error ยาวๆ
try:
    _v = tuple(int(x) for x in st.__version__.split(".")[:2])
except ValueError:
    _v = (99, 0)
if _v < (1, 40):
    st.error(f"Streamlit เวอร์ชัน {st.__version__} เก่าเกินไป กรุณารัน: pip install -U streamlit (ต้อง 1.40 ขึ้นไป)")
    st.stop()
try:
    import importlib
    import database as db
    db = importlib.reload(db)  # กัน Streamlit ใช้ database.py เวอร์ชันเก่าที่ค้างอยู่ในหน่วยความจำ
except ImportError:
    st.error("ไม่พบ database.py — ต้องวางไว้โฟลเดอร์เดียวกับ app.py และตั้งชื่อ database.py (ห้ามมีเว้นวรรค)")
    st.stop()
if not hasattr(db, "get_all_settings"):
    st.error(f"database.py ที่ใช้อยู่เป็นเวอร์ชันเก่า (ไฟล์: {db.__file__}) กรุณาแทนที่ด้วยไฟล์ database.py ล่าสุดจากชุดนี้ "
             f"แล้วหยุดและรัน streamlit ใหม่")
    st.stop()

db.init_db()

from ui import components as C   # noqa: E402  (นำเข้าหลังตรวจสภาพแวดล้อม)
from ui.theme import build_css   # noqa: E402
from views import admin, customer  # noqa: E402

st.markdown(build_css(), unsafe_allow_html=True)

# ---------------- สถานะเริ่มต้นของเซสชัน ----------------
st.session_state.setdefault("cart", {})
st.session_state.setdefault("admin", False)
st.session_state.setdefault("page", "หน้าแรก")
C.refresh_cfg()

PAGES = {
    "หน้าแรก": customer.page_home,
    "เมนูอาหาร": customer.page_menu,
    "จองโต๊ะ": customer.page_reserve,
    "สมาชิก": customer.page_member,
    "ติดตามออเดอร์": customer.page_track,
    C.CART_PAGE: customer.page_cart,
    C.ADMIN_PAGE: admin.page_admin,
}

# ---------------- ประกอบหน้า: หัวเว็บ → เนื้อหา → ฟุตเตอร์ ----------------
C.topbar()
C.ticker()
with st.container(key="pagebody"):
    PAGES.get(st.session_state.page, customer.page_home)()
C.footer()
