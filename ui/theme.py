"""ui/theme.py - ธีมสีและ CSS ทั้งหมดของเว็บ  (ดีไซน์ปี 2026: ดาร์กโมเดิร์น · กระจกโปร่ง · เรืองแสงอบอุ่น)

โทนสีอินเดีย : ม่วงมะเหมี่ยวเข้ม (พื้นหลัง) · หญ้าฝรั่น · ดาวเรือง · ชมพูรานี · เขียวนกยูง
แก้สีทั้งเว็บได้ที่ตัวแปร :root ด้านล่าง ไม่ต้องไปไล่แก้ทีละที่
หมายเหตุ: ชื่อ class เดิมทั้งหมดยังอยู่ครบ จึงไม่กระทบข้อมูลและฟังก์ชันของเว็บ เปลี่ยนแค่หน้าตา
"""
from ui import assets as A

# ใช้ __ชื่อ__ แทนตำแหน่งที่จะใส่ data-URI ของลายพื้นหลัง (กันปัญหาปีกกาของ CSS ชนกับ f-string)
_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Prompt:wght@300;400;500;600;700&display=swap');

/* =====================================================================
   1) ตัวแปรสีและขนาดหลัก
   ===================================================================== */
:root {
  /* พื้นผิว (จากมืดสุดไปสว่างขึ้น) */
  --bg: #0E0A14;
  --bg-2: #150E1E;
  --surface: #1A1226;
  --surface-2: #231833;
  --glass: rgba(255, 255, 255, .055);
  --glass-2: rgba(255, 255, 255, .09);
  /* เส้นขอบ */
  --line: rgba(255, 214, 140, .17);
  --line-strong: rgba(255, 190, 90, .42);
  /* ตัวอักษร (ตัดกับพื้นมืดชัดเจน อ่านง่าย) */
  --ink: #F7EFE3;
  --muted: #C4B6AA;
  --dim: #9C8E86;
  /* สีอินเดีย */
  --saffron: #FF9F1C;
  --saffron-deep: #F07A00;
  --marigold: #FFC233;
  --gold: #E9B949;
  --gold-light: #FFE08A;
  --rani: #E91E73;
  --maroon: #9C1F45;
  --maroon-dark: #2B0A1A;
  --maroon-soft: #C2305A;
  --peacock: #1FC2BA;
  --leaf: #4CD07D;
  --danger: #FF6B6B;
  /* เก่า: เก็บชื่อไว้เพื่อให้ส่วนอื่นที่อ้างถึงยังใช้ได้ */
  --cream: var(--bg);
  --cream-deep: var(--surface-2);
  --paper: var(--surface);
  /* ขนาด/เงา/ฟอนต์ */
  --radius: 22px;
  --shadow-sm: 0 2px 10px rgba(0, 0, 0, .35);
  --shadow-md: 0 14px 34px rgba(0, 0, 0, .5);
  --shadow-lg: 0 24px 60px rgba(0, 0, 0, .6);
  --glow: 0 0 0 1px rgba(255, 159, 28, .55), 0 12px 36px rgba(255, 159, 28, .22);
  --grad-warm: linear-gradient(135deg, #FFC233 0%, #FF9F1C 55%, #F07A00 100%);
  --grad-rani: linear-gradient(135deg, #E91E73 0%, #9C1F45 100%);
  --grad-text: linear-gradient(92deg, #FFE08A 0%, #FF9F1C 52%, #FF5C93 100%);
  --font-head: 'Sora', 'Prompt', sans-serif;
  --font-body: 'Prompt', 'Noto Sans Thai', sans-serif;
  /* ลายพื้นหลังอินเดีย ประกาศครั้งเดียวแล้วเรียกใช้ซ้ำด้วย var() เพื่อให้ CSS เบา */
  --mandala: @@MANDALA@@;
  --mandala-light: @@MANDALA_LIGHT@@;
  --jaali: @@JAALI@@;
  --toran: @@TORAN@@;
}

/* =====================================================================
   2) พื้นหลังหน้าเว็บ + ซ่อนส่วนเกินของ Streamlit
   ===================================================================== */
html { scroll-behavior: smooth; color-scheme: dark; }
html, body, [class*="css"], .stApp { font-family: var(--font-body); }
.stApp {
  background-color: var(--bg);
  background-image:
    radial-gradient(900px 520px at 8% -6%, rgba(233, 30, 115, .20), transparent 60%),
    radial-gradient(800px 520px at 96% 4%, rgba(255, 159, 28, .17), transparent 60%),
    radial-gradient(900px 600px at 50% 112%, rgba(31, 194, 186, .12), transparent 62%),
    __MANDALA__,
    linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
  background-attachment: fixed;
  color: var(--ink); font-size: 1.04rem; line-height: 1.6;
}
::selection { background: rgba(255, 159, 28, .45); color: #fff; }
/* แถบเลื่อนแบบใหม่: บาง มน ไม่มีลูกศรหัวท้าย ไล่สีหญ้าฝรั่น→ชมพู */
::-webkit-scrollbar { width: 12px; height: 12px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #FF9F1C, #E91E73); border-radius: 999px;
  border: 3px solid var(--bg); background-clip: padding-box;
}
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #FFC233, #FF5C93); background-clip: padding-box; border: 3px solid var(--bg); }
::-webkit-scrollbar-button { display: none; width: 0; height: 0; }
::-webkit-scrollbar-corner { background: transparent; }
@supports not selector(::-webkit-scrollbar) { * { scrollbar-width: thin; scrollbar-color: #FF9F1C transparent; } }
[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer,
[data-testid="stDecoration"], [data-testid="stSidebar"], [data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; visibility: hidden !important; }
.block-container { padding: 0 0 0 0 !important; max-width: 100% !important; }
.block-container > [data-testid="stVerticalBlock"], [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-pagebody { gap: 1rem !important; }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
[data-testid="stAppViewContainer"] > .main > div:first-child { padding-top: 0; }
.stApp a { color: var(--marigold); }

/* พื้นที่เนื้อหากลางจอ (จำกัดความกว้างให้อ่านสบาย) */
.page-wrap, .st-key-pagebody {
  width: 100%; max-width: 1240px; margin-left: auto; margin-right: auto;
  padding-left: 1.4rem; padding-right: 1.4rem; box-sizing: border-box;
}
.st-key-pagebody { padding-top: 1.6rem; padding-bottom: 1rem; }

h1, h2, h3, h4 { font-family: var(--font-head) !important; color: var(--gold-light) !important; letter-spacing: .2px; font-weight: 700 !important; }
h1 { font-size: 2.5rem !important; } h2 { font-size: 1.75rem !important; } h3 { font-size: 1.35rem !important; }
h4, h5 { font-family: var(--font-body) !important; font-weight: 600 !important; color: var(--ink) !important; }

/* =====================================================================
   3) แถบข้อมูลด้านบนสุด (เวลาเปิด / เบอร์โทร / ที่อยู่)
   ===================================================================== */
.utility {
  background: rgba(8, 5, 12, .92); color: var(--muted); font-size: .82rem;
  display: flex; justify-content: center; align-items: center; gap: 1.6rem; flex-wrap: wrap;
  padding: 0 1rem; letter-spacing: .3px; height: 44px; box-sizing: border-box; line-height: 1.2;
  position: relative; z-index: 3; overflow: hidden; border-bottom: 1px solid var(--line);
}
.utility .ico { vertical-align: -3px; margin-right: .4rem; }
.ico { vertical-align: -4px; margin-right: .45rem; }
.chip .ico { margin-right: .5rem; }
.utility span { color: var(--muted) !important; white-space: nowrap; }
.utility b { color: #fff !important; font-weight: 500; }
.open-pill { border-radius: 999px; padding: .08rem .75rem; font-weight: 600; font-size: .78rem; border: 1px solid transparent; }
.utility .open-pill.on { background: rgba(76, 208, 125, .16); color: #8FF0B2 !important; border-color: rgba(76, 208, 125, .6); }
.utility .open-pill.off { background: rgba(255, 107, 107, .15); color: #FFB3B3 !important; border-color: rgba(255, 107, 107, .55); }

/* =====================================================================
   4) แถบเมนูหลัก (กระจกโปร่งติดขอบบน + โลโก้มุมขวา + ตะกร้า)
   ===================================================================== */
.st-key-topbar {
  position: relative; z-index: 100; box-sizing: border-box;
  width: calc(100% - 2.8rem); max-width: calc(1240px - 2.8rem); margin: 1rem auto 0;
  padding: .55rem 1rem; border-radius: 26px;
  background: linear-gradient(180deg, rgba(34, 23, 51, .78), rgba(20, 13, 30, .78));
  border: 1px solid var(--line-strong);
  -webkit-backdrop-filter: blur(18px) saturate(140%); backdrop-filter: blur(18px) saturate(140%);
  box-shadow: 0 14px 40px rgba(0, 0, 0, .5), inset 0 1px 0 rgba(255, 255, 255, .08);
}
.st-key-topbar [data-testid="stHorizontalBlock"] { max-width: none; margin: 0; align-items: center; gap: .7rem; }
.st-key-topbar [data-testid="stColumn"] { display: flex; flex-direction: column; justify-content: center; }
.st-key-topbar [data-testid="stMarkdownContainer"] p { margin: 0; }
.toran, .footer-toran { display: none; }

/* ปุ่มเมนูนำทาง: แคปซูลโปร่งใส หน้าที่เปิดอยู่เป็นสีหญ้าฝรั่นเรืองแสง */
.st-key-topbar [class*="st-key-nav_"] button {
  background: var(--glass) !important; border: 1px solid var(--line) !important;
  border-radius: 999px !important; min-height: 2.6rem; padding: .35rem .4rem !important; box-shadow: none;
}
.st-key-topbar [class*="st-key-nav_"] button p {
  color: var(--ink) !important; font-size: .98rem !important; font-weight: 500 !important; white-space: nowrap;
}
.st-key-topbar [class*="st-key-nav_"] button:hover { background: var(--glass-2) !important; border-color: var(--saffron) !important; transform: none; }
.st-key-topbar [class*="st-key-nav_"] button[kind="primary"], .st-key-topbar [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"] {
  background: var(--grad-warm) !important; border: 1px solid rgba(255, 255, 255, .35) !important;
  box-shadow: 0 6px 20px rgba(255, 159, 28, .38);
}
.st-key-topbar [class*="st-key-nav_"] button[kind="primary"] p, .st-key-topbar [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"] p {
  color: #1D0F04 !important; font-weight: 700 !important;
}

/* ปุ่มตะกร้า */
.st-key-cart_btn button {
  background: var(--grad-rani) !important; color: #fff !important; border: 1px solid rgba(255, 255, 255, .28) !important;
  border-radius: 999px !important; font-weight: 600 !important; padding: .45rem 1.1rem !important;
  box-shadow: 0 6px 20px rgba(233, 30, 115, .38); white-space: nowrap;
}
.st-key-cart_btn button p { color: #fff !important; font-weight: 600; }
.st-key-cart_btn button:hover { filter: brightness(1.12); transform: translateY(-1px); }

/* โลโก้ + ชื่อร้าน */
.brand { display: flex; align-items: center; justify-content: flex-end; gap: .8rem; min-height: 56px; }
.brand.left { justify-content: flex-start; }
.brand img { height: 52px; display: block; width: auto; max-width: 120px; object-fit: contain; filter: drop-shadow(0 2px 8px rgba(255, 159, 28, .35)); }
.brand-text { text-align: right; line-height: 1.15; display: flex; flex-direction: column; justify-content: center; }
.brand.left .brand-text { text-align: left; }
.brand-name {
  font-family: var(--font-head); font-size: 1.5rem; letter-spacing: .8px; font-weight: 700;
  background: var(--grad-text); -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; color: var(--gold-light) !important;
}
.brand-sub { font-size: .66rem; color: var(--muted) !important; letter-spacing: 2.4px; text-transform: uppercase; }

/* =====================================================================
   5) ป้ายโปรวิ่ง (ticker)
   ===================================================================== */
.ticker {
  position: relative; overflow: hidden; box-sizing: border-box;
  width: calc(100% - 2.8rem); max-width: calc(1240px - 2.8rem); margin: .8rem auto 0;
  background: #181122; border: 1px solid var(--line); border-radius: 999px;
}
.ticker::before, .ticker::after { content: ""; position: absolute; top: 0; bottom: 0; width: 70px; z-index: 2; pointer-events: none; }
.ticker::before { left: 0; background: linear-gradient(90deg, #181122, transparent); }
.ticker::after { right: 0; background: linear-gradient(270deg, #181122, transparent); }
.ticker-track { display: inline-flex; white-space: nowrap; animation: ticker 42s linear infinite; padding: .5rem 0; }
.ticker-track span { color: var(--muted) !important; font-size: .88rem; font-weight: 500; padding: 0 1.4rem; display: inline-flex; align-items: center; }
.ticker-track span::before {
  content: ""; width: 6px; height: 6px; border-radius: 50%; margin-right: 1.4rem; flex-shrink: 0;
  background: var(--grad-warm); box-shadow: 0 0 10px rgba(255, 159, 28, .8);
}
.ticker:hover .ticker-track { animation-play-state: paused; }
@keyframes ticker { from { transform: translateX(0); } to { transform: translateX(-50%); } }

/* =====================================================================
   6) แบนเนอร์หลัก (สไลด์อัตโนมัติ ใช้ CSS ล้วน)
   ===================================================================== */
.hero {
  position: relative; height: 400px; border-radius: 28px; overflow: hidden;
  box-shadow: var(--shadow-lg), 0 0 0 1px var(--line-strong);
}
.slide {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: space-between;
  padding: 2rem 3.4rem; opacity: 0; animation: slidefade 18s infinite; overflow: hidden;
}
.slide.s1 { background: radial-gradient(600px 400px at 85% 30%, rgba(255, 159, 28, .38), transparent 65%), linear-gradient(120deg, #1C0B24 0%, #4A1042 50%, #8E1B45 120%); animation-delay: 0s; opacity: 1; }
.slide.s2 { background: radial-gradient(600px 400px at 85% 30%, rgba(31, 194, 186, .38), transparent 65%), linear-gradient(120deg, #0B1530 0%, #123C5A 50%, #0E5A5E 125%); animation-delay: 6s; }
.slide.s3 { background: radial-gradient(600px 400px at 85% 30%, rgba(255, 194, 51, .34), transparent 65%), linear-gradient(120deg, #25090F 0%, #6B1B14 50%, #B8470A 125%); animation-delay: 12s; }
@keyframes slidefade {
  0% { opacity: 0; } 3% { opacity: 1; }
  30% { opacity: 1; } 34% { opacity: 0; } 100% { opacity: 0; }
}
.slide::before {
  content: ""; position: absolute; inset: 0; background-image: __MANDALA_LIGHT__; background-size: 150px;
  opacity: .7; pointer-events: none;
}
.slide-text { position: relative; z-index: 2; max-width: 56%; }
.slide-kicker { color: var(--marigold) !important; letter-spacing: 3.2px; font-size: .82rem; text-transform: uppercase; margin-bottom: .7rem; font-weight: 600; }
.slide-title { font-family: var(--font-head); font-weight: 700; font-size: 3rem; line-height: 1.12; color: #fff !important; text-shadow: 0 4px 20px rgba(0, 0, 0, .5); margin-bottom: .8rem; }
.slide-title em { font-style: normal; background: var(--grad-text); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: var(--gold-light) !important; }
.slide-desc { color: #F1E6DA !important; font-size: 1.08rem; line-height: 1.65; margin-bottom: 1.1rem; max-width: 520px; }
.slide-pill {
  display: inline-block; background: rgba(255, 255, 255, .12); border: 1px solid rgba(255, 224, 138, .55);
  color: var(--gold-light) !important; border-radius: 999px; padding: .4rem 1.15rem; font-size: .9rem;
  -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
}
.slide-art { position: relative; z-index: 2; width: 300px; height: 300px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.slide-art .plate {
  width: 270px; height: 270px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  background: radial-gradient(circle at 35% 30%, #3C2852, #1A1226 72%); border: 6px solid var(--marigold);
  box-shadow: 0 0 0 10px rgba(255, 194, 51, .14), 0 0 70px rgba(255, 159, 28, .35), 0 24px 50px rgba(0, 0, 0, .55);
  font-size: 8rem; overflow: hidden; animation: floaty 5s ease-in-out infinite;
}
.slide-art .plate img { width: 100%; height: 100%; object-fit: cover; }
.slide-art .paisley-a { position: absolute; top: -26px; right: -30px; width: 110px; transform: rotate(18deg); opacity: .85; }
.slide-art .paisley-b { position: absolute; bottom: -22px; left: -34px; width: 96px; transform: rotate(-150deg); opacity: .8; }
@keyframes floaty { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }

/* =====================================================================
   7) ชิปข้อมูลบริการ
   ===================================================================== */
.chips { display: flex; flex-wrap: wrap; gap: .7rem; justify-content: center; margin: 1.3rem 0 .4rem; }
.chip {
  display: inline-flex; align-items: center; gap: .5rem; background: var(--glass); border: 1px solid var(--line);
  border-radius: 999px; padding: .5rem 1.15rem; box-shadow: var(--shadow-sm); font-size: .92rem; color: var(--ink) !important;
  -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px);
}
.chip b { color: var(--marigold) !important; font-weight: 600; }

/* =====================================================================
   8) หัวข้อส่วนต่าง ๆ
   ===================================================================== */
.sec { text-align: center; margin: 2.4rem 0 1.2rem; }
.sec .sec-kicker { color: var(--saffron) !important; letter-spacing: 3.2px; font-size: .78rem; text-transform: uppercase; font-weight: 600; }
.sec .sec-title {
  font-family: var(--font-head); font-weight: 700; font-size: 2.05rem; margin: .1rem 0 .2rem;
  background: var(--grad-text); -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; color: var(--gold-light) !important;
}
.sec .sec-sub { color: var(--muted) !important; font-size: .98rem; }
.sec img { display: block; margin: .35rem auto 0; max-width: 100%; }
.page-title { text-align: left; margin: .2rem 0 1rem; }
.page-title h1 { margin: 0; }
.page-title p { color: var(--muted) !important; margin: .2rem 0 0; }

/* =====================================================================
   9) ไทล์หมวดหมู่
   ===================================================================== */
.cat-tile {
  position: relative; z-index: 1; padding: 1.3rem 1rem .9rem;
  display: flex; flex-direction: column; align-items: center; gap: .55rem;
}
.cat-name {
  font-family: var(--font-head); font-weight: 700; font-size: 1.12rem; line-height: 1.3;
  min-height: 2.9rem; display: flex; align-items: center; justify-content: center; text-align: center;
  color: #FFFFFF !important; text-shadow: 0 1px 8px rgba(0, 0, 0, .45);
}
.cat-count {
  display: block; padding: .12rem .85rem; border-radius: 999px; line-height: 1.5;
  background: rgba(255, 255, 255, .12); border: 1px solid rgba(255, 255, 255, .25);
  color: var(--gold-light) !important; font-size: .78rem; font-weight: 600;
}
/* การ์ดหมวดหมู่ แบบกระจกใส */
[class*="st-key-catcard_"] {
  position: relative; overflow: hidden; gap: .6rem !important; padding: 0 0 1rem 0;
  background: linear-gradient(160deg, rgba(255, 255, 255, .16) 0%, rgba(255, 255, 255, .05) 45%, rgba(255, 255, 255, .09) 100%);
  -webkit-backdrop-filter: blur(14px) saturate(140%); backdrop-filter: blur(14px) saturate(140%);
  border: 1px solid rgba(255, 255, 255, .28); border-radius: var(--radius);
  box-shadow: 0 8px 28px rgba(0, 0, 0, .35), inset 0 1px 0 rgba(255, 255, 255, .45);
  transition: transform .24s ease, box-shadow .24s ease, border-color .24s ease;
}
[class*="st-key-catcard_"]::before {
  content: ""; position: absolute; top: -40%; left: -30%; width: 90%; height: 90%; pointer-events: none;
  background: radial-gradient(circle, rgba(255, 255, 255, .22), transparent 65%);
}
[class*="st-key-catcard_"]:hover {
  transform: translateY(-6px); border-color: rgba(255, 200, 110, .75);
  box-shadow: 0 14px 36px rgba(0, 0, 0, .4), 0 0 24px rgba(255, 159, 28, .28), inset 0 1px 0 rgba(255, 255, 255, .55);
}
[class*="st-key-catcard_"] .stButton { padding: 0 1rem; margin-top: .4rem; position: relative; z-index: 1; }
[class*="st-key-catcard_"] [data-testid="stImage"] img { border-radius: 0; height: 150px; object-fit: cover; }
[class*="st-key-catcard_"] [data-testid="stMarkdownContainer"] p { margin: 0; }
[class*="st-key-catcard_"] [data-testid="stElementContainer"] { overflow: visible; }

/* =====================================================================
   10) การ์ดอาหาร
   ===================================================================== */
[class*="st-key-card_"] {
  background: linear-gradient(180deg, rgba(255, 255, 255, .07), rgba(255, 255, 255, .025));
  border: 1px solid var(--line); border-radius: var(--radius); padding: 0 0 .9rem 0;
  box-shadow: var(--shadow-sm); transition: transform .24s ease, box-shadow .24s ease, border-color .24s ease;
  overflow: hidden; gap: .55rem !important;
}
[class*="st-key-card_"]:hover { transform: translateY(-6px); box-shadow: var(--glow); border-color: var(--saffron); }
[class*="st-key-card_"] [data-testid="stMarkdownContainer"] p { margin: 0; }
[class*="st-key-card_"] .stButton { padding: 0 .9rem; }
.dish-media {
  position: relative; height: 172px; display: flex; align-items: center; justify-content: center; font-size: 4.4rem;
  background: radial-gradient(circle at 50% 42%, rgba(255, 159, 28, .30), rgba(233, 30, 115, .10) 58%, transparent 80%), var(--surface-2);
  border-bottom: 1px solid var(--line);
}
.dish-media::after {
  content: ""; position: absolute; inset: 0; background-image: __MANDALA_LIGHT__; background-size: 110px; opacity: .55; pointer-events: none;
}
.dish-media .emo { position: relative; z-index: 1; filter: drop-shadow(0 10px 14px rgba(0, 0, 0, .5)); transition: transform .3s ease; }
[class*="st-key-card_"]:hover .dish-media .emo { transform: scale(1.1) rotate(-4deg); }
.dish-media img { width: 100%; height: 100%; object-fit: cover; position: relative; z-index: 1; }
.dish-tag {
  position: absolute; top: 10px; right: 10px; z-index: 3; background: var(--grad-warm);
  color: #1D0F04 !important; font-size: .72rem; font-weight: 700; padding: .24rem .75rem; border-radius: 999px; box-shadow: var(--shadow-sm);
}
.veg-mark {
  position: absolute; top: 10px; left: 10px; z-index: 3; width: 20px; height: 20px; border: 2px solid var(--leaf);
  background: rgba(14, 10, 20, .85); border-radius: 5px; display: flex; align-items: center; justify-content: center;
}
.veg-mark::after { content: ""; width: 9px; height: 9px; border-radius: 50%; background: var(--leaf); }
.dish-body { padding: .15rem 1rem 0; }
.dish-name { font-family: var(--font-head); font-weight: 700; font-size: 1.13rem; color: var(--ink) !important; line-height: 1.25; }
.dish-th { color: var(--marigold) !important; font-size: .9rem; font-weight: 600; margin-bottom: .25rem; }
.dish-desc { color: var(--muted) !important; font-size: .88rem; line-height: 1.5; min-height: 2.4rem; }
.dish-price { margin-top: .45rem; font-size: 1.35rem; font-weight: 700; color: var(--gold-light) !important; display: flex; align-items: baseline; gap: .6rem; }
.dish-left { color: #FF9C9C !important; font-size: .76rem; font-weight: 500; }

/* =====================================================================
   11) การ์ดโปรโมชัน (คูปองจริงจากฐานข้อมูล)
   ===================================================================== */
.promo-card {
  position: relative; border-radius: var(--radius); padding: 1.3rem 1.4rem 1.2rem 5.3rem; overflow: hidden; min-height: 118px;
  background: linear-gradient(120deg, rgba(255, 159, 28, .16) 0%, rgba(233, 30, 115, .12) 100%);
  border: 1.5px dashed rgba(255, 159, 28, .75); box-shadow: var(--shadow-sm);
}
.promo-card::before, .promo-card::after {
  content: ""; position: absolute; top: 50%; width: 22px; height: 22px; border-radius: 50%;
  background: var(--bg); border: 1.5px dashed rgba(255, 159, 28, .75); transform: translateY(-50%);
}
.promo-card::before { left: -13px; } .promo-card::after { right: -13px; }
.promo-pct {
  position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); width: 62px; height: 62px; border-radius: 50%;
  background: var(--grad-rani); color: #fff !important;
  display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 1; font-family: var(--font-head);
  font-size: 1.35rem; border: 2px solid var(--marigold); box-shadow: 0 6px 18px rgba(233, 30, 115, .4);
}
.promo-pct small { font-size: .65rem; font-family: var(--font-body); color: #fff !important; margin-top: 2px; }
.promo-code { font-family: var(--font-head); font-weight: 700; font-size: 1.35rem; color: var(--gold-light) !important; letter-spacing: 2px; }
.promo-desc { color: var(--muted) !important; font-size: .88rem; }
.promo-use {
  display: inline-block; margin-top: .4rem; background: var(--grad-warm); color: #1D0F04 !important; font-size: .75rem; font-weight: 700;
  padding: .15rem .75rem; border-radius: 999px;
}

/* =====================================================================
   12) จุดเด่นของร้าน
   ===================================================================== */
.feature {
  text-align: center; padding: 1.5rem 1rem; border-radius: var(--radius);
  background: linear-gradient(180deg, rgba(255, 255, 255, .07), rgba(255, 255, 255, .025));
  border: 1px solid var(--line); height: 100%; box-shadow: var(--shadow-sm); transition: transform .22s ease, border-color .22s ease;
}
.feature:hover { transform: translateY(-4px); border-color: var(--line-strong); }
.feature .f-ico img { margin: 0; }
.feature .f-ico {
  width: 68px; height: 68px; margin: 0 auto .7rem; border-radius: 22px; display: flex; align-items: center; justify-content: center;
  font-size: 2rem; background: var(--grad-rani); border: 1px solid rgba(255, 255, 255, .25); box-shadow: 0 8px 22px rgba(233, 30, 115, .32);
}
.feature .f-title { font-family: var(--font-head); font-weight: 700; color: var(--gold-light) !important; font-size: 1.12rem; }
.feature .f-desc { color: var(--muted) !important; font-size: .9rem; line-height: 1.55; }

/* =====================================================================
   12.1) ความรู้เครื่องเทศ + หัวข้อหมวดในหน้าเมนู
   ===================================================================== */
.spice-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: .8rem; }
.spice-card {
  background: var(--glass); border: 1px solid var(--line); border-top: 3px solid var(--saffron); border-radius: 18px;
  padding: .95rem .7rem; text-align: center; box-shadow: var(--shadow-sm); transition: transform .2s ease, border-color .2s ease;
}
.spice-card:hover { transform: translateY(-4px); border-color: var(--line-strong); }
.sp-ico { font-size: 2rem; }
.sp-th { font-weight: 600; color: var(--ink) !important; }
.sp-en { font-size: .72rem; letter-spacing: 1.5px; text-transform: uppercase; color: var(--saffron) !important; margin-bottom: .3rem; }
.sp-desc { font-size: .8rem; color: var(--muted) !important; line-height: 1.5; }
.lvl-row { display: flex; flex-wrap: wrap; gap: .6rem; justify-content: center; margin-top: 1rem; }
.lvl { background: rgba(255, 159, 28, .12); border: 1px solid var(--line-strong); border-radius: 999px; padding: .3rem .95rem; font-size: .84rem; color: var(--gold-light) !important; }
.lvl i { color: var(--muted) !important; font-style: normal; margin-left: .3rem; }
.cat-head {
  display: flex; align-items: center; gap: .7rem; margin: 1.8rem 0 .9rem; padding-bottom: .55rem;
  border-bottom: 1px solid var(--line); position: relative;
}
.cat-head::before {
  content: ""; position: absolute; left: 0; bottom: -1px; width: 90px; height: 3px; border-radius: 3px; background: var(--grad-warm);
}
.cat-head::after { content: "✦"; position: absolute; right: 0; bottom: -.85rem; color: var(--saffron); background: var(--bg); padding: 0 .5rem; }
.ch-ico { font-size: 1.7rem; }
.ch-name { font-family: var(--font-head); font-weight: 700; font-size: 1.5rem; color: var(--gold-light) !important; }
.ch-count { color: var(--muted) !important; font-size: .85rem; margin-left: auto; margin-right: 1.5rem; }

/* =====================================================================
   13) เกี่ยวกับร้าน / รีวิว
   ===================================================================== */
.about-box {
  display: grid; grid-template-columns: 1.3fr 1fr; gap: 1.6rem; align-items: center;
  border: 1px solid var(--line-strong); border-radius: 28px; padding: 2rem 2.2rem; box-shadow: var(--shadow-md);
  background-image: __MANDALA_LIGHT__, linear-gradient(135deg, rgba(233, 30, 115, .14), rgba(255, 159, 28, .08) 55%, rgba(31, 194, 186, .08));
  background-size: 130px, auto; background-color: var(--surface);
}
.about-box p { color: var(--ink) !important; line-height: 1.85; margin: 0; }
.about-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: .7rem; }
.stat-pill {
  background: var(--glass-2); border-radius: 18px; padding: .95rem .4rem; text-align: center;
  border: 1px solid var(--line-strong);
}
.stat-pill .n { font-family: var(--font-head); font-weight: 700; font-size: 1.65rem; color: var(--marigold) !important; }
.stat-pill .l { font-size: .76rem; color: var(--muted) !important; }
.review-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, .07), rgba(255, 255, 255, .025)); border: 1px solid var(--line);
  border-radius: var(--radius); padding: 1.15rem 1.25rem; box-shadow: var(--shadow-sm); height: 100%; position: relative;
}
.review-card::before { content: "“"; position: absolute; top: -4px; right: 14px; font-family: var(--font-head); font-size: 3.8rem; color: var(--saffron); opacity: .5; }
.review-stars { color: var(--marigold) !important; letter-spacing: 2px; }
.review-text { color: var(--ink) !important; font-size: .94rem; min-height: 2.6rem; margin: .3rem 0 .5rem; }
.review-by { color: var(--muted) !important; font-size: .82rem; }

/* =====================================================================
   14) ตะกร้าและการชำระเงิน
   ===================================================================== */
.checkout-steps { display: flex; justify-content: center; align-items: center; gap: .5rem; margin: .4rem 0 1.4rem; flex-wrap: wrap; }
.co-step { display: flex; align-items: center; gap: .5rem; color: var(--dim) !important; font-weight: 500; font-size: .92rem; }
.co-step .dot {
  width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700;
  background: var(--glass); border: 1.5px solid var(--line); color: var(--muted) !important;
}
.co-step.on { color: var(--gold-light) !important; font-weight: 600; }
.co-step.on .dot { background: var(--grad-warm); border-color: transparent; color: #1D0F04 !important; box-shadow: 0 4px 14px rgba(255, 159, 28, .4); }
.co-line { width: 44px; height: 2px; background: var(--line); }
.cart-row { display: grid; grid-template-columns: 56px 1fr; gap: .8rem; align-items: center; }
.cart-ico {
  width: 56px; height: 56px; border-radius: 16px; background: radial-gradient(circle, rgba(255, 159, 28, .28), var(--surface-2)); display: flex;
  align-items: center; justify-content: center; font-size: 1.9rem; border: 1px solid var(--line-strong); overflow: hidden;
}
.cart-ico img { width: 100%; height: 100%; object-fit: cover; }
.cart-name { font-weight: 700; font-size: 1.05rem; color: var(--ink) !important; line-height: 1.25; }
.cart-th { font-size: .8rem; color: var(--muted) !important; }
.cart-price { font-weight: 700; font-size: 1.1rem; color: var(--gold-light) !important; text-align: right; }
.summary-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, .08), rgba(255, 255, 255, .03)); border: 1px solid var(--line-strong);
  border-radius: 24px; padding: 1.4rem 1.5rem; box-shadow: var(--shadow-md); position: relative;
}
.summary-card::before {
  content: ""; position: absolute; left: 24px; right: 24px; top: -1px; height: 3px; border-radius: 3px; background: var(--grad-warm);
}
.summary-card h4 { margin: 0 0 .6rem; }
.sum-row { display: flex; justify-content: space-between; padding: .3rem 0; font-size: .96rem; color: var(--ink) !important; }
.sum-row.disc { color: var(--leaf) !important; }
.sum-row.total {
  border-top: 1px dashed var(--line-strong); margin-top: .5rem; padding-top: .75rem; font-size: 1.3rem; font-weight: 700;
  color: var(--gold-light) !important;
}
.sum-note { color: var(--muted) !important; font-size: .82rem; margin-top: .5rem; }
.empty-cart { text-align: center; padding: 3rem 1rem; background: var(--glass); border: 1.5px dashed var(--line-strong); border-radius: 26px; }
.empty-cart .big { font-size: 4.5rem; }
.empty-cart .t { font-family: var(--font-head); font-weight: 700; color: var(--gold-light) !important; font-size: 1.4rem; }
.empty-cart .s { color: var(--muted) !important; }
.qr-box { text-align: center; background: #fff; border: 1px solid var(--line); border-radius: 18px; padding: 1rem; }

/* =====================================================================
   14.1) หน้าสั่งอาหารแบบเป็นขั้นตอน (การ์ดแยกส่วนอ่านง่าย)
   ===================================================================== */
[class*="st-key-sec_"] {
  background: linear-gradient(180deg, rgba(255, 255, 255, .06), rgba(255, 255, 255, .02));
  border: 1px solid var(--line); border-radius: 26px; padding: 1.3rem 1.5rem 1.4rem;
  box-shadow: var(--shadow-sm);
}
.step-head { display: flex; align-items: center; gap: .85rem; margin-bottom: .4rem; }
.sh-n {
  width: 40px; height: 40px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  background: var(--grad-warm); color: #1D0F04 !important;
  font-weight: 700; font-size: 1.1rem; box-shadow: 0 6px 16px rgba(255, 159, 28, .35);
}
.sh-t { font-family: var(--font-head); font-weight: 700; font-size: 1.3rem; color: var(--gold-light) !important; line-height: 1.2; }
.sh-s { color: var(--muted) !important; font-size: .9rem; }
.st-key-sum_sticky { position: sticky; top: 5.2rem; }
.pay-box { background: linear-gradient(135deg, rgba(255, 159, 28, .16), rgba(233, 30, 115, .10)); border: 1px solid var(--line-strong); border-radius: 20px; padding: 1rem 1.2rem; }
.pay-box .pb-l { color: var(--muted) !important; font-size: .88rem; font-weight: 600; }
.pay-box .pb-v { font-family: var(--font-head); font-weight: 700; font-size: 2.05rem; color: var(--marigold) !important; line-height: 1.2; }
.pay-box .pb-n { color: var(--ink) !important; font-size: .92rem; line-height: 1.55; margin-top: .3rem; }
.slip-hint {
  background: rgba(255, 159, 28, .10); border: 1.5px dashed var(--saffron); border-radius: 16px; padding: .8rem 1.1rem;
  color: var(--ink) !important; font-size: .95rem; margin-top: .6rem;
}
.slip-hint b { color: var(--marigold) !important; }
.sum-meta { display: flex; justify-content: space-between; gap: .5rem; margin-top: .6rem; font-size: .88rem; color: var(--ink) !important; font-weight: 600; }
.sum-meta span { background: var(--glass-2); border: 1px solid var(--line); border-radius: 999px; padding: .15rem .8rem; }

/* =====================================================================
   15) ไทม์ไลน์ติดตามออเดอร์
   ===================================================================== */
.timeline { display: flex; gap: 0; margin: 1rem 0 1.2rem; flex-wrap: wrap; }
.tl-step { flex: 1 1 110px; text-align: center; position: relative; padding: 0 .3rem; }
.tl-step::before { content: ""; position: absolute; top: 20px; left: -50%; width: 100%; height: 3px; background: var(--line); z-index: 0; }
.tl-step:first-child::before { display: none; }
.tl-step.on::before { background: var(--grad-warm); }
.tl-dot { font-weight: 700; color: var(--muted);
  position: relative; z-index: 1; width: 42px; height: 42px; margin: 0 auto .4rem; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; background: var(--surface-2); border: 2px solid var(--line-strong); font-size: 1.1rem;
}
.tl-step.on .tl-dot { background: var(--grad-warm); border-color: transparent; color: #1D0F04; }
.tl-step.now .tl-dot { box-shadow: 0 0 0 6px rgba(255, 159, 28, .26); animation: pulse 1.8s infinite; }
@keyframes pulse { 50% { box-shadow: 0 0 0 12px rgba(255, 159, 28, .06); } }
.tl-label { font-size: .82rem; color: var(--dim) !important; line-height: 1.3; }
.tl-step.on .tl-label { color: var(--gold-light) !important; font-weight: 600; }
.badge {
  display: inline-block; padding: .22rem .85rem; border-radius: 999px; font-size: .82rem; font-weight: 600;
  background: rgba(255, 159, 28, .16); color: var(--marigold) !important; border: 1px solid rgba(255, 159, 28, .6);
}
.badge.ok { background: rgba(76, 208, 125, .15); color: #8FF0B2 !important; border-color: rgba(76, 208, 125, .55); }
.badge.bad { background: rgba(255, 107, 107, .15); color: #FFB3B3 !important; border-color: rgba(255, 107, 107, .55); }
.badge.wait { background: rgba(255, 194, 51, .15); color: #FFD97A !important; border-color: rgba(255, 194, 51, .55); }
.badge.info { background: rgba(31, 194, 186, .15); color: #7FE9E3 !important; border-color: rgba(31, 194, 186, .55); }
.info-card { background: var(--glass); border: 1px solid var(--line); color: var(--ink); border-radius: 18px; padding: 1rem 1.2rem; box-shadow: var(--shadow-sm); }

/* =====================================================================
   16) แบบฟอร์ม / ปุ่ม / ช่องกรอก
   ===================================================================== */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
  border-radius: 14px; font-weight: 600; font-family: var(--font-body); transition: all .18s ease;
  border: 1px solid var(--line-strong); background: var(--glass); color: var(--ink);
}
.stButton > button p, .stFormSubmitButton > button p, .stDownloadButton > button p { color: inherit !important; font-weight: 600; }
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
  background: var(--glass-2); color: #fff; border-color: var(--saffron); transform: translateY(-1px); box-shadow: 0 6px 18px rgba(255, 159, 28, .22);
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primaryFormSubmit"],
.stButton > button[data-testid="stBaseButton-primary"], .stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--grad-warm); border-color: rgba(255, 255, 255, .3); color: #1D0F04;
  box-shadow: 0 6px 18px rgba(255, 159, 28, .35);
}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primaryFormSubmit"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover, .stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
  background: var(--grad-warm); filter: brightness(1.08); border-color: #fff; color: #1D0F04; box-shadow: 0 10px 26px rgba(255, 159, 28, .5);
}
.stFormSubmitButton > button { background: var(--grad-warm); color: #1D0F04; border-color: rgba(255, 255, 255, .3); }
.stFormSubmitButton > button:hover { background: var(--grad-warm); color: #1D0F04; filter: brightness(1.08); }

div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"] {
  background: rgba(255, 255, 255, .07) !important; border-radius: 14px !important; border: 1px solid var(--line-strong) !important;
}
.stApp input::placeholder, .stApp textarea::placeholder { color: var(--dim) !important; opacity: 1; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within, div[data-baseweb="textarea"]:focus-within {
  border-color: var(--saffron) !important; box-shadow: 0 0 0 3px rgba(255, 159, 28, .25) !important;
}
.stApp input, .stApp textarea { color: var(--ink) !important; font-family: var(--font-body) !important; font-size: 1rem !important; }
.stApp label p, .stApp [data-testid="stWidgetLabel"] p { color: var(--ink) !important; font-weight: 600; font-size: 1rem; }
/* รายการเลือก (dropdown) ให้พื้นเข้ม อ่านชัด */
[data-baseweb="popover"] > div, [data-baseweb="menu"], ul[role="listbox"] { background: #221733 !important; border: 1px solid var(--line-strong); border-radius: 14px; }
[data-baseweb="menu"] li, ul[role="listbox"] li { color: var(--ink) !important; }
[data-baseweb="menu"] li:hover, ul[role="listbox"] li:hover, ul[role="listbox"] li[aria-selected="true"] { background: rgba(255, 159, 28, .18) !important; }
[data-testid="stForm"] { background: var(--glass); border: 1px solid var(--line); border-radius: 22px; padding: 1.2rem 1.3rem; box-shadow: none; }
[data-testid="stFileUploaderDropzone"] { background: rgba(255, 159, 28, .06); border: 1.5px dashed var(--line-strong); border-radius: 16px; }
.stSlider [data-baseweb="slider"] div[role="slider"] { background: var(--saffron) !important; }
.stCheckbox label p { font-weight: 500; }

/* ปุ่มเพิ่ม-ลดจำนวนในตะกร้า */
[class*="st-key-qty_"] button { padding: .1rem .2rem; min-height: 2.1rem; border-radius: 50%; }
.qty-val { text-align: center; font-weight: 700; font-size: 1.05rem; color: var(--gold-light) !important; padding-top: .25rem; }

/* =====================================================================
   17) ตัวชี้วัด / แท็บ / ตาราง / กล่องแจ้งเตือน
   ===================================================================== */
[data-testid="stMetric"] {
  background: var(--glass); border: 1px solid var(--line); border-radius: 18px; padding: .85rem 1.05rem; box-shadow: var(--shadow-sm);
}
[data-testid="stMetricLabel"] p { color: var(--muted) !important; font-size: .82rem; }
[data-testid="stMetricValue"] { color: var(--gold-light) !important; font-family: var(--font-head); }
/* แท็บ: กรอบแคปซูลกระจก แท็บที่เลือกเป็นปุ่มไล่สี (เหมือน segmented control ยุคใหม่) */
[role="tablist"] {
  width: fit-content; max-width: 100%; border-bottom: 1px solid var(--line-strong) !important;
  gap: .3rem; padding: .35rem; flex-wrap: wrap; border: 1px solid var(--line-strong); border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, .07), rgba(255, 255, 255, .025));
  -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px); box-shadow: var(--shadow-sm);
}
[data-baseweb="tab-border"], [data-baseweb="tab-highlight"] { display: none !important; }
[role="tab"] {
  border-radius: 14px; padding: .55rem 1.05rem; height: auto; font-weight: 500; color: var(--muted); background: transparent;
  transition: all .18s ease;
}
[role="tab"] p { color: inherit !important; }
[role="tab"]:hover { background: var(--glass-2); color: var(--ink); }
[role="tab"][aria-selected="true"] { background: var(--grad-warm) !important; box-shadow: 0 6px 18px rgba(255, 159, 28, .35); }
[role="tab"][aria-selected="true"] p { color: #1D0F04 !important; font-weight: 700; }
[role="tabpanel"] { padding-top: 1.1rem; }
[data-testid="stExpander"] { background: var(--glass); border: 1px solid var(--line) !important; border-radius: 16px !important; box-shadow: var(--shadow-sm); }
[data-testid="stExpander"] summary p { color: var(--ink) !important; font-weight: 500; }
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
[data-testid="stAlert"] { border-radius: 16px; }
[data-testid="stToast"] { border: 1px solid var(--saffron); }
hr { border-color: var(--line) !important; }
.stProgress > div > div > div > div { background: var(--grad-warm) !important; }

/* =====================================================================
   18) แอดมิน
   ===================================================================== */
.admin-head {
  display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap;
  background: radial-gradient(500px 200px at 90% 0%, rgba(255, 159, 28, .25), transparent 70%), linear-gradient(120deg, #2A0F33, #5A1238);
  border: 1px solid var(--line-strong); border-radius: 24px; padding: 1.1rem 1.5rem;
  box-shadow: var(--shadow-md); margin-bottom: 1rem;
}
.admin-head .t { font-family: var(--font-head); font-weight: 700; font-size: 1.5rem; color: var(--gold-light) !important; }
.admin-head .s { color: var(--muted) !important; font-size: .86rem; }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: .9rem; margin-bottom: 1.1rem; }
.kpi {
  background: var(--glass); border: 1px solid var(--line); border-left: 5px solid var(--saffron); border-radius: 18px;
  padding: .95rem 1.15rem; box-shadow: var(--shadow-sm);
}
.kpi.k2 { border-left-color: var(--leaf); } .kpi.k3 { border-left-color: var(--rani); } .kpi.k4 { border-left-color: var(--peacock); }
.kpi .kl { color: var(--muted) !important; font-size: .82rem; }
.kpi .kv { font-family: var(--font-head); font-weight: 700; font-size: 1.75rem; color: var(--gold-light) !important; line-height: 1.2; }
.login-card {
  max-width: 440px; margin: 1.5rem auto; background: linear-gradient(180deg, rgba(255, 255, 255, .08), rgba(255, 255, 255, .03));
  border: 1px solid var(--line-strong); border-radius: 28px; padding: 1.7rem 1.9rem .7rem; box-shadow: var(--shadow-lg); text-align: center;
}
.login-card .ic { font-size: 2.6rem; }
.login-card .t { font-family: var(--font-head); font-weight: 700; font-size: 1.5rem; color: var(--gold-light) !important; }
.login-card .s { color: var(--muted) !important; font-size: .88rem; margin-bottom: .6rem; }
.kitchen-ticket {
  background: rgba(255, 159, 28, .08); border: 1.5px dashed var(--saffron); border-radius: 16px; padding: .9rem 1.1rem; margin-bottom: .6rem;
}
.kitchen-ticket .k-head { font-weight: 700; color: var(--marigold) !important; font-size: 1.05rem; }
.kitchen-ticket .k-item { font-size: .98rem; padding: .12rem 0; color: var(--ink) !important; }
.log-line { font-size: .84rem; color: var(--muted) !important; padding: .18rem 0; border-bottom: 1px dotted var(--line); }
.logo-preview { background: var(--surface-2); border: 1px solid var(--line); border-radius: 16px; padding: 1rem; text-align: center; }
.logo-preview img { max-height: 90px; max-width: 220px; object-fit: contain; }

/* =====================================================================
   19) ส่วนท้ายเว็บ (ฟุตเตอร์) + ไอคอนโซเชียล
   ===================================================================== */
.site-footer {
  margin-top: 3rem; color: var(--muted); position: relative;
  background: __JAALI__, linear-gradient(180deg, #14091F 0%, #0A0610 100%);
}
.site-footer::before {
  content: ""; position: absolute; left: 0; right: 0; top: 0; height: 3px;
  background: linear-gradient(90deg, var(--rani), var(--saffron), var(--marigold), var(--peacock));
}
.footer-toran { height: 16px; background-image: __TORAN__; background-repeat: repeat-x; background-size: 90px 16px; position: relative; top: 3px; }
.footer-grid {
  max-width: 1240px; margin: 0 auto; padding: 2rem 1.4rem 1.3rem; display: grid; gap: 2rem;
  grid-template-columns: 1.5fr 1fr 1.2fr 1.1fr;
}
.footer-grid h5 { font-family: var(--font-head) !important; font-weight: 700 !important; color: var(--gold-light) !important; font-size: 1.1rem; margin: 0 0 .7rem; letter-spacing: .6px; }
.footer-grid p, .footer-grid li, .footer-grid span { color: var(--muted) !important; font-size: .9rem; line-height: 1.75; }
.footer-grid ul { list-style: none; padding: 0; margin: 0; }
.footer-grid li { display: flex; align-items: flex-start; gap: .1rem; margin-bottom: .2rem; }
.footer-grid li .ico { margin-top: .3rem; flex-shrink: 0; }
.footer-brand { display: flex; align-items: center; gap: .7rem; margin-bottom: .7rem; }
.footer-brand img { height: 54px; width: auto; max-width: 110px; object-fit: contain; }
.footer-brand .n {
  font-family: var(--font-head); font-weight: 700; font-size: 1.4rem;
  background: var(--grad-text); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: var(--gold-light) !important;
}
.social-row { display: flex; gap: .55rem; flex-wrap: wrap; margin-top: .6rem; }
.social-btn {
  width: 42px; height: 42px; border-radius: 14px; display: inline-flex; align-items: center; justify-content: center;
  border: 1px solid var(--line-strong); background: var(--glass); transition: all .2s ease; text-decoration: none;
}
.social-btn img { width: 22px; height: 22px; }
.social-btn:hover { background: var(--grad-warm); border-color: #fff; transform: translateY(-3px) scale(1.06); box-shadow: 0 8px 20px rgba(255, 159, 28, .4); }
.pay-row { display: flex; gap: .45rem; flex-wrap: wrap; margin-top: .3rem; }
.pay-chip {
  border: 1px solid var(--line-strong); color: var(--gold-light) !important; border-radius: 10px; padding: .12rem .65rem;
  font-size: .78rem; background: var(--glass);
}
.footer-bottom {
  border-top: 1px solid var(--line); text-align: center; padding: .95rem 1rem 1.15rem; font-size: .84rem;
  color: var(--dim) !important; letter-spacing: .4px;
}
.footer-bottom b { color: var(--gold-light) !important; font-family: var(--font-head); font-weight: 700; }
.st-key-staff_btn {
  display: flex !important; flex-direction: column; align-items: center !important; justify-content: center;
  background: var(--jaali), #0A0610; padding: .2rem 0 1.8rem; margin-top: -1px;
  width: 100% !important; max-width: 100% !important; box-sizing: border-box;
}
.st-key-staff_btn > div { display: flex; justify-content: center; width: 100%; }
.st-key-staff_btn [data-testid="stElementContainer"], .st-key-staff_btn .stButton { width: auto !important; }
.st-key-staff_btn button {
  background: var(--glass) !important; border: 1px solid var(--line-strong) !important; border-radius: 999px !important;
  padding: .45rem 1.5rem !important; min-height: 0; color: var(--muted) !important; box-shadow: none;
}
.st-key-staff_btn button p { color: var(--muted) !important; font-size: .9rem; font-weight: 500; }
.st-key-staff_btn button:hover { background: var(--grad-warm) !important; border-color: #fff !important; }
.st-key-staff_btn button:hover p { color: #1D0F04 !important; }

/* =====================================================================
   20) จอเล็ก (มือถือ / แท็บเล็ต)
   ===================================================================== */
/* =====================================================================
   19.1) หัวข้อบล็อกในแอดมิน + กล่องกราฟแบบกรอบกระจก
   ===================================================================== */
.blk-title { display: flex; align-items: center; gap: .65rem; margin: 1.4rem 0 .8rem; font-family: var(--font-head); font-weight: 700; font-size: 1.25rem; color: var(--gold-light); }
.blk-title::before { content: ""; width: 5px; height: 1.3em; border-radius: 4px; background: var(--grad-warm); box-shadow: 0 0 14px rgba(255, 159, 28, .5); }
.blk-title small { font-family: var(--font-body); font-weight: 400; font-size: .85rem; color: var(--muted); margin-left: .2rem; }
[data-testid="stVerticalBlockBorderWrapper"] {
  background: linear-gradient(180deg, rgba(255, 255, 255, .06), rgba(255, 255, 255, .02));
  border: 1px solid var(--line) !important; border-radius: 22px !important; box-shadow: var(--shadow-sm);
}
.chart-cap { font-weight: 600; color: var(--ink); margin: .1rem 0 .3rem; }

/* =====================================================================
   19.2) การเคลื่อนไหว (micro-interactions) ให้ดูมืออาชีพ: นุ่ม เร็ว ไม่รบกวนสายตา
   ===================================================================== */
:root { --ease: cubic-bezier(.2, .8, .2, 1); }
@keyframes rise { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: none; } }
@keyframes tabin { from { opacity: 0; transform: translateY(12px) scale(.995); } to { opacity: 1; transform: none; } }
@keyframes pop { 0% { transform: scale(.8); opacity: .3; } 60% { transform: scale(1.14); } 100% { transform: scale(1); opacity: 1; } }
@keyframes textrise {
  0% { opacity: 0; transform: translateY(22px); } 4% { opacity: 0; transform: translateY(22px); }
  9% { opacity: 1; transform: none; } 30% { opacity: 1; transform: none; } 34% { opacity: 0; } 100% { opacity: 0; }
}

/* เปลี่ยนหน้า: เนื้อหาแต่ละส่วนไหลขึ้นมาทีละชิ้น */
.st-key-pagebody > * { animation: rise .55s var(--ease) both; }
.st-key-pagebody > *:nth-child(2) { animation-delay: .05s; } .st-key-pagebody > *:nth-child(3) { animation-delay: .10s; }
.st-key-pagebody > *:nth-child(4) { animation-delay: .15s; } .st-key-pagebody > *:nth-child(5) { animation-delay: .20s; }
.st-key-pagebody > *:nth-child(6) { animation-delay: .25s; } .st-key-pagebody > *:nth-child(n+7) { animation-delay: .3s; }

/* กดเลือกแท็บ: เนื้อหาในแท็บเลื่อนขึ้นพร้อมจางเข้า */
[role="tabpanel"] { animation: tabin .42s var(--ease) both; }
[role="tab"] { transition: background .25s var(--ease), color .25s var(--ease), transform .15s var(--ease), box-shadow .25s var(--ease); }
[role="tab"]:active { transform: scale(.95); }

/* ปุ่มทุกชนิด: ยกตัวเมื่อชี้ กดแล้วยุบเล็กน้อย */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button { transition: transform .18s var(--ease), box-shadow .25s var(--ease), background .25s var(--ease), border-color .25s var(--ease), filter .25s var(--ease); }
.stButton > button:active, .stFormSubmitButton > button:active, .stDownloadButton > button:active { transform: translateY(0) scale(.96) !important; box-shadow: none; }
.st-key-topbar [class*="st-key-nav_"] button { transition: transform .2s var(--ease), background .25s var(--ease), border-color .25s var(--ease), box-shadow .25s var(--ease); }
.st-key-topbar [class*="st-key-nav_"] button:hover { transform: translateY(-2px) !important; }
.st-key-topbar [class*="st-key-nav_"] button:active { transform: scale(.95) !important; }
.st-key-cart_btn button { transition: transform .2s var(--ease), filter .25s var(--ease); }
.st-key-cart_btn button:active { transform: scale(.95); }

/* การ์ดอาหาร/ส่วนต่างๆ: ปรากฏทีละใบ (เลื่อนตามลำดับคอลัมน์) */
[class*="st-key-card_"], .feature, .review-card, .promo-card, .spice-card, .cat-tile, .kpi, .summary-card, .info-card,
[data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"], [class*="st-key-sec_"] { animation: rise .6s var(--ease) both; }
[data-testid="stColumn"]:nth-child(2) > * { animation-delay: .06s; } [data-testid="stColumn"]:nth-child(3) > * { animation-delay: .12s; }
[data-testid="stColumn"]:nth-child(4) > * { animation-delay: .18s; } [data-testid="stColumn"]:nth-child(5) > * { animation-delay: .24s; }
[data-testid="stColumn"]:nth-child(n+6) > * { animation-delay: .3s; }
.kpi:nth-child(2) { animation-delay: .06s; } .kpi:nth-child(3) { animation-delay: .12s; } .kpi:nth-child(4) { animation-delay: .18s; }
.spice-card:nth-child(2) { animation-delay: .05s; } .spice-card:nth-child(3) { animation-delay: .10s; }
.spice-card:nth-child(4) { animation-delay: .15s; } .spice-card:nth-child(5) { animation-delay: .20s; } .spice-card:nth-child(6) { animation-delay: .25s; }
.cat-ico { transition: transform .3s var(--ease), box-shadow .3s var(--ease), border-color .3s var(--ease); }

/* ตัวเลขจำนวน/ยอดรวมเด้งนิดๆ เมื่อค่าเปลี่ยน · ป้ายสถานะค่อยๆ โผล่ */
.qty-val, .sum-row.total span:last-child, .cart-price, .pay-box .pb-v { animation: pop .4s var(--ease) both; }
.badge, .timeline { animation: rise .5s var(--ease) both; }
.tl-step.on::before { transform-origin: left; animation: grow .6s var(--ease) both; }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }

/* แบนเนอร์หลัก: ข้อความไหลขึ้นทุกครั้งที่เปลี่ยนสไลด์ */
.slide.s1 .slide-text { animation: textrise 18s var(--ease) infinite; animation-delay: 0s; }
.slide.s2 .slide-text { animation: textrise 18s var(--ease) infinite; animation-delay: 6s; }
.slide.s3 .slide-text { animation: textrise 18s var(--ease) infinite; animation-delay: 12s; }

/* ช่องกรอก / ตัวเลือก / กล่องเปิดปิด / แจ้งเตือน: เปลี่ยนสถานะนุ่มๆ */
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"] { transition: border-color .25s var(--ease), box-shadow .25s var(--ease), background .25s var(--ease); }
div[data-baseweb="input"]:hover, div[data-baseweb="select"] > div:hover, div[data-baseweb="textarea"]:hover { background: rgba(255, 255, 255, .10) !important; }
[data-baseweb="radio"] > div:first-child, [data-baseweb="checkbox"] > span:first-child { transition: all .22s var(--ease); }
[data-testid="stExpander"] { transition: border-color .25s var(--ease), background .25s var(--ease); }
[data-testid="stExpander"]:hover { border-color: var(--line-strong) !important; }
[data-testid="stExpander"] details[open] > div { animation: tabin .35s var(--ease) both; }
[data-testid="stAlert"] { animation: rise .45s var(--ease) both; }
[data-testid="stToast"] { animation: rise .35s var(--ease) both; }
[data-baseweb="popover"] > div { animation: tabin .22s var(--ease) both; }
.social-btn, .chip, .lvl { transition: transform .25s var(--ease), background .25s var(--ease), border-color .25s var(--ease), box-shadow .25s var(--ease); }
.chip:hover { transform: translateY(-2px); border-color: var(--saffron); }
.review-card, .promo-card { transition: transform .25s var(--ease), border-color .25s var(--ease), box-shadow .25s var(--ease); }
.review-card:hover, .promo-card:hover { transform: translateY(-4px); box-shadow: var(--glow); }

/* =====================================================================
   19.3) Liquid Glass: กระจกใสหลายชั้น เบลอ + เร่งสีพื้นหลัง มีไฮไลต์สะท้อนขอบบนและเงาด้านล่าง
   ===================================================================== */
:root {
  --lg-bg: linear-gradient(135deg, rgba(255, 255, 255, .15) 0%, rgba(255, 255, 255, .045) 42%, rgba(255, 255, 255, .09) 100%);
  --lg-border: 1px solid rgba(255, 255, 255, .17);
  --lg-shadow: inset 0 1.5px 0 rgba(255, 255, 255, .38), inset 0 -1px 0 rgba(255, 255, 255, .06),
               inset 0 0 26px rgba(255, 255, 255, .035), 0 14px 38px rgba(0, 0, 0, .42);
  --lg-blur: blur(22px) saturate(185%);
}
.st-key-topbar, [role="tablist"], [class*="st-key-card_"], .feature, .review-card, .kpi, [data-testid="stMetric"],
.summary-card, [class*="st-key-sec_"], [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"],
.info-card, .chip, .stat-pill, .spice-card, .empty-cart, [data-testid="stExpander"], .login-card, .pay-box {
  background: var(--lg-bg) !important; border: var(--lg-border) !important;
  box-shadow: var(--lg-shadow) !important;
  -webkit-backdrop-filter: var(--lg-blur); backdrop-filter: var(--lg-blur);
}
.kpi { border-left-width: 5px !important; }
.kpi { border-left-color: var(--saffron) !important; } .kpi.k2 { border-left-color: var(--leaf) !important; }
.kpi.k3 { border-left-color: var(--rani) !important; } .kpi.k4 { border-left-color: var(--peacock) !important; }
.st-key-topbar { border-radius: 28px; }
[role="tablist"] { border-radius: 22px; }
[class*="st-key-card_"]:hover, .review-card:hover, .feature:hover {
  box-shadow: var(--lg-shadow), 0 0 0 1px rgba(255, 159, 28, .55), 0 16px 44px rgba(255, 159, 28, .22) !important;
}
/* ปุ่มรอง/ปุ่มเมนู: แคปซูลกระจก */
.stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]), .stDownloadButton > button,
.st-key-topbar [class*="st-key-nav_"] button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]) {
  background: var(--lg-bg) !important; border: var(--lg-border) !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, .32), inset 0 -1px 0 rgba(255, 255, 255, .05), 0 6px 18px rgba(0, 0, 0, .3) !important;
  -webkit-backdrop-filter: blur(14px) saturate(170%); backdrop-filter: blur(14px) saturate(170%);
}
/* ปุ่มหลัก / แท็บที่เลือก / ตะกร้า: กระจกสีเข้มเงาแวว (เหมือนหยดแก้วสีส้ม/ชมพู) */
[role="tab"][aria-selected="true"], .stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"],
.stFormSubmitButton > button, .st-key-topbar [class*="st-key-nav_"] button[kind="primary"],
.st-key-topbar [class*="st-key-nav_"] button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(180deg, rgba(255, 226, 150, .98) 0%, rgba(255, 170, 45, .96) 52%, rgba(240, 122, 0, .96) 100%) !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, .75), inset 0 -2px 6px rgba(160, 70, 0, .35), 0 8px 22px rgba(255, 159, 28, .38) !important;
  border: 1px solid rgba(255, 255, 255, .45) !important;
}
.st-key-cart_btn button {
  background: linear-gradient(180deg, rgba(255, 110, 165, .98), rgba(233, 30, 115, .95) 55%, rgba(170, 20, 85, .96)) !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, .55), inset 0 -2px 6px rgba(90, 0, 40, .4), 0 8px 22px rgba(233, 30, 115, .4) !important;
  border: 1px solid rgba(255, 255, 255, .4) !important;
}
/* แท็บ: กรอบกระจกครอบตั้งแต่แรก แต่ละแท็บเป็นแคปซูลมน (ไม่ใช่สี่เหลี่ยม) */
[role="tablist"] { padding: .4rem; gap: .25rem; overflow: visible; }
[role="tab"] { border-radius: 16px !important; padding: .55rem 1.1rem; margin: 0; border: 1px solid transparent; }
[role="tab"]:hover:not([aria-selected="true"]) { background: rgba(255, 255, 255, .10); }
/* ช่องกรอก/ดรอปดาวน์: กระจกเข้มบาง */
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"] {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .12) !important; border: 1px solid rgba(255, 255, 255, .18) !important;
}
[data-baseweb="popover"] > div, [data-baseweb="menu"], ul[role="listbox"] {
  background: rgba(34, 23, 51, .78) !important; border: var(--lg-border) !important;
  -webkit-backdrop-filter: blur(24px) saturate(180%); backdrop-filter: blur(24px) saturate(180%);
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, .25), 0 18px 40px rgba(0, 0, 0, .55) !important;
}
.ticker { box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, .22); border-color: rgba(255, 255, 255, .15); }
/* ฉากหลังเรืองสีให้เห็นความใสของกระจกชัดขึ้น */
.stApp::before {
  content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background:
    radial-gradient(420px 420px at 14% 38%, rgba(233, 30, 115, .20), transparent 70%),
    radial-gradient(460px 460px at 88% 62%, rgba(255, 159, 28, .16), transparent 70%),
    radial-gradient(380px 380px at 52% 92%, rgba(31, 194, 186, .14), transparent 70%);
  animation: drift 24s ease-in-out infinite alternate;
}
@keyframes drift { from { transform: translate3d(-1.5%, -1%, 0) scale(1); } to { transform: translate3d(1.5%, 1.2%, 0) scale(1.06); } }
[data-testid="stAppViewContainer"] { position: relative; z-index: 1; }

/* =====================================================================
   19.4) โลกอนาคต: เส้นขอบเรืองแสงหมุน · กริด HUD · ประกายกวาดผ่าน · วงแหวนโฮโลแกรม
   (ทุกอย่างเป็น CSS ล้วน ไม่กระทบข้อมูล และหยุดเองเมื่อผู้ใช้ปิดแอนิเมชันในระบบ)
   ===================================================================== */
@property --ang { syntax: "<angle>"; inherits: false; initial-value: 0deg; }
@keyframes spin-ang { to { --ang: 360deg; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes spin-rev { to { transform: rotate(-360deg); } }
@keyframes sweep { 0%, 55% { left: -70%; } 100% { left: 140%; } }
@keyframes flow { to { background-position: 220% center; } }
@keyframes beam { from { transform: translateX(-120%) skewX(-18deg); } to { transform: translateX(260%) skewX(-18deg); } }
@keyframes materialize { from { opacity: 0; transform: translateY(18px) scale(.985); filter: blur(10px); } to { opacity: 1; transform: none; filter: blur(0); } }
@keyframes blink { 50% { opacity: .35; } }
:root { --grad-flow: linear-gradient(92deg, #FFE08A 0%, #FF9F1C 25%, #FF5C93 50%, #FF9F1C 75%, #FFE08A 100%); }

/* เปลี่ยนหน้า: โผล่ขึ้นแบบโฟกัสชัดจากภาพเบลอ */
.st-key-pagebody > * { animation-name: materialize; }

/* กริด HUD จางๆ ลอยด้านหลัง เฟดหายที่ขอบจอ */
.stApp::after {
  content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none; opacity: .55;
  background-image: linear-gradient(rgba(255, 214, 140, .06) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 214, 140, .06) 1px, transparent 1px);
  background-size: 64px 64px;
  -webkit-mask-image: radial-gradient(ellipse 75% 65% at 50% 38%, #000 0%, transparent 100%);
  mask-image: radial-gradient(ellipse 75% 65% at 50% 38%, #000 0%, transparent 100%);
}

/* ขอบเรืองแสงไล่สีหมุนรอบการ์ด (แสดงเมื่อชี้ / แถบเมนูและแท็บมีจางๆ ตลอด) */
[class*="st-key-card_"], .kpi, .feature, [class*="st-key-sec_"], .st-key-topbar, [role="tablist"] { position: relative; }
[class*="st-key-card_"]::before, .kpi::before, .feature::before, [class*="st-key-sec_"]::before, .st-key-topbar::before, [role="tablist"]::before {
  content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 1.5px; pointer-events: none; z-index: 3;
  background: conic-gradient(from var(--ang), transparent 0%, #FF9F1C 14%, #E91E73 28%, transparent 42%, transparent 58%, #1FC2BA 72%, #FFC233 86%, transparent 100%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor;
  mask: linear-gradient(#000 0 0) content-box exclude, linear-gradient(#000 0 0);
  opacity: 0; transition: opacity .35s var(--ease); animation: spin-ang 5s linear infinite;
}
[class*="st-key-card_"]:hover::before, .kpi:hover::before, .feature:hover::before, [class*="st-key-sec_"]:hover::before { opacity: 1; }
.st-key-topbar::before, [role="tablist"]::before { opacity: .55; animation-duration: 9s; }
.kpi::before { z-index: 1; }

/* ประกายแสงวิ่งผ่านปุ่มหลัก ปุ่มตะกร้า */
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"], .stFormSubmitButton > button, .st-key-cart_btn button {
  position: relative; overflow: hidden;
}
.stButton > button[kind="primary"]::after, .stButton > button[data-testid="stBaseButton-primary"]::after, .stFormSubmitButton > button::after, .st-key-cart_btn button::after {
  content: ""; position: absolute; top: 0; left: -70%; width: 38%; height: 100%; pointer-events: none;
  background: linear-gradient(100deg, transparent, rgba(255, 255, 255, .55), transparent); transform: skewX(-20deg);
  animation: sweep 4.2s ease-in-out infinite;
}

/* ตัวอักษรหัวข้อ: ไล่สีไหลต่อเนื่อง + แสงเรืองนุ่ม */
.brand-name, .sec .sec-title, .footer-brand .n {
  background: var(--grad-flow); background-size: 220% auto; -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; animation: flow 9s linear infinite; filter: drop-shadow(0 0 16px rgba(255, 159, 28, .28));
}
.kpi .kv, .pay-box .pb-v, .dish-price, .stat-pill .n, [data-testid="stMetricValue"] {
  font-variant-numeric: tabular-nums; text-shadow: 0 0 22px rgba(255, 194, 51, .35);
}
h1 { text-shadow: 0 0 28px rgba(255, 159, 28, .3); }

/* แบนเนอร์หลัก: กรอบมุม HUD + แสงกวาด + วงแหวนโฮโลแกรมรอบจาน */
.hero::after {
  content: ""; position: absolute; inset: 14px; z-index: 6; pointer-events: none; --c: rgba(255, 224, 138, .8);
  background:
    linear-gradient(var(--c), var(--c)) top left / 30px 2px no-repeat, linear-gradient(var(--c), var(--c)) top left / 2px 30px no-repeat,
    linear-gradient(var(--c), var(--c)) top right / 30px 2px no-repeat, linear-gradient(var(--c), var(--c)) top right / 2px 30px no-repeat,
    linear-gradient(var(--c), var(--c)) bottom left / 30px 2px no-repeat, linear-gradient(var(--c), var(--c)) bottom left / 2px 30px no-repeat,
    linear-gradient(var(--c), var(--c)) bottom right / 30px 2px no-repeat, linear-gradient(var(--c), var(--c)) bottom right / 2px 30px no-repeat;
}
.hero::before {
  content: ""; position: absolute; top: 0; bottom: 0; left: 0; width: 22%; z-index: 5; pointer-events: none;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, .10), transparent); animation: beam 7s ease-in-out infinite;
}
.slide-art::before {
  content: ""; position: absolute; inset: -6px; border-radius: 50%; border: 1.5px dashed rgba(255, 224, 138, .5); animation: spin 36s linear infinite;
}
.slide-art::after {
  content: ""; position: absolute; inset: 14px; border-radius: 50%; pointer-events: none;
  border: 2px solid transparent; border-top-color: rgba(31, 194, 186, .85); border-bottom-color: rgba(233, 30, 115, .8);
  animation: spin-rev 14s linear infinite; filter: drop-shadow(0 0 8px rgba(31, 194, 186, .6));
}

/* ไฟสถานะ "สด" ที่ป้ายโปร + เส้นขอบบนฟุตเตอร์ไหลสี */
.ticker-track span::before { animation: blink 2.4s ease-in-out infinite; }
.site-footer::before, .tl-step.on::before { background-size: 220% auto; }
.site-footer::before { background-image: linear-gradient(90deg, #E91E73, #FF9F1C, #FFC233, #1FC2BA, #E91E73); animation: flow 10s linear infinite; }
.tl-step.now .tl-dot { box-shadow: 0 0 0 6px rgba(255, 159, 28, .26), 0 0 26px rgba(255, 159, 28, .7); }
.badge { box-shadow: 0 0 14px rgba(255, 159, 28, .18); }
.badge.ok { box-shadow: 0 0 14px rgba(76, 208, 125, .22); } .badge.bad { box-shadow: 0 0 14px rgba(255, 107, 107, .22); }
.social-btn:hover, .cat-tile:hover .cat-ico { box-shadow: 0 0 26px rgba(255, 159, 28, .55); }

/* =====================================================================
   19.5) ปรับตำแหน่ง: การ์ดส่วนลดจัดกึ่งกลาง · โลโก้มุมขวาบนขยับขึ้นเล็กน้อย
   ===================================================================== */
.promo-card {
  display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
  padding: 1.3rem 1.6rem 1.2rem; gap: .25rem;
}
.promo-pct { position: relative; left: auto; top: auto; transform: none; margin: 0 auto .35rem; }
.promo-use { margin-top: .5rem; }
.st-key-topbar .brand { transform: translateY(var(--brand-lift, -10px)); align-items: center; }
.st-key-topbar .brand img { margin: 0; }
.st-key-topbar .brand-text { align-items: flex-end; justify-content: center; }

@media (max-width: 992px) {
  .hero { height: 450px; }
  .slide { padding: 1.6rem; flex-direction: column; justify-content: center; text-align: center; }
  .slide-text { max-width: 100%; }
  .slide-title { font-size: 2.1rem; }
  .slide-art { display: none; }
  .about-box { grid-template-columns: 1fr; }
  .footer-grid { grid-template-columns: 1fr 1fr; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .spice-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 640px) {
  [class*="st-key-sec_"] { padding: 1rem; }
  .st-key-sec_items [data-testid="stHorizontalBlock"] { flex-direction: row; flex-wrap: nowrap; gap: .3rem; }
  .st-key-sec_items [data-testid="stColumn"] { min-width: 0 !important; }
  .st-key-sum_sticky { position: static; }
  .st-key-topbar [data-testid="stHorizontalBlock"] { flex-direction: column-reverse; gap: .4rem; }
  .st-key-topbar [data-testid="stColumn"] [data-testid="stHorizontalBlock"] { flex-direction: row; flex-wrap: wrap; gap: .4rem; }
  .st-key-topbar [data-testid="stColumn"] [data-testid="stColumn"] { min-width: 30% !important; flex: 1 1 30% !important; }
  .utility { height: auto; min-height: 44px; padding: .4rem 1rem; }
  .page-wrap, .st-key-pagebody { padding-left: .8rem; padding-right: .8rem; }
  .st-key-topbar, .ticker { width: calc(100% - 1.6rem); }
  .st-key-topbar { border-radius: 22px; padding: .5rem .7rem; }
  .utility { font-size: .74rem; gap: .5rem 1rem; }
  .brand img { height: 44px; }
  .brand-name { font-size: 1.15rem; }
  .brand-sub { display: none; }
  .hero { height: 480px; border-radius: 20px; }
  .slide-title { font-size: 1.7rem; }
  .sec .sec-title { font-size: 1.5rem; }
  .footer-grid { grid-template-columns: 1fr; gap: 1.2rem; }
  .cat-ico { width: 68px; height: 68px; font-size: 1.9rem; border-radius: 22px; }
  .dish-media { height: 140px; }
  .about-stats { grid-template-columns: 1fr 1fr 1fr; }
  .kpi-grid { grid-template-columns: 1fr 1fr; }
  .spice-grid { grid-template-columns: 1fr 1fr; }
}
/* ผู้ใช้ที่ปิดแอนิเมชันในระบบ: หยุดการเคลื่อนไหวทั้งหมด */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
  .slide.s2, .slide.s3 { display: none; }
}
</style>
"""


def build_css():
    """ประกอบ CSS สมบูรณ์พร้อมฝังลายพื้นหลังอินเดียทั้งหมด (ลายทองจางๆ บนพื้นมืด)"""
    mandala = A.svg_css(A.mandala_tile(A.GOLD, 0.05, 240))
    mandala_light = A.svg_css(A.mandala_tile(A.GOLD_LIGHT, 0.13, 150))
    jaali = A.svg_css(A.jaali_tile(A.GOLD, 0.14, 44))
    toran = A.svg_css(A.toran_tile())
    css = (_CSS.replace("__MANDALA_LIGHT__", "var(--mandala-light)")
               .replace("__MANDALA__", "var(--mandala)")
               .replace("__JAALI__", "var(--jaali)")
               .replace("__TORAN__", "var(--toran)"))
    return (css.replace("@@MANDALA_LIGHT@@", mandala_light)
               .replace("@@MANDALA@@", mandala)
               .replace("@@JAALI@@", jaali)
               .replace("@@TORAN@@", toran))
