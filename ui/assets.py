"""ui/assets.py - กราฟิกสไตล์อินเดียที่สร้างด้วยโค้ด (SVG) ไม่ต้องมีไฟล์รูปภาพ

มีอะไรบ้าง
  - mandala_tile()   ลายแมนดาลา/ดอกบัว สำหรับพื้นหลังแบบอินเดีย
  - paisley()        ลายเพสลีย์ (โบเตห์) สำหรับตกแต่งแบนเนอร์
  - toran_tile()     ลายธงแขวนโทรัน ใช้เป็นขอบใต้แถบหัวเว็บ
  - divider()        เส้นคั่นหัวข้อรูปดอกบัว
  - logo_svg()       โลโก้ร้านในตัว (โดมอินเดีย + ดอกบัว) เปลี่ยนได้จากหน้าแอดมิน
  - social_icon()    ไอคอนโซเชียล (Instagram, Facebook, LINE, TikTok, YouTube, X)

ทุกอย่างถูกแปลงเป็น data-URI เพื่อฝังในหน้าเว็บได้เลย
"""
import base64
import math

# ---------------------------------------------------------------- ชุดสี
MAROON = "#8B1A1A"
MAROON_DARK = "#5E0F14"
SAFFRON = "#F28C28"
SAFFRON_DEEP = "#D96F0B"
GOLD = "#D4A017"
GOLD_LIGHT = "#F2D272"
CREAM = "#FFF7E8"
PAPER = "#FFFDF8"
PEACOCK = "#0F6E73"


# ---------------------------------------------------------------- ตัวช่วยแปลง
def svg_b64(svg):
    """แปลงข้อความ SVG เป็น base64"""
    return base64.b64encode(svg.encode("utf-8")).decode("ascii")


def svg_src(svg):
    """ค่า src สำหรับ <img>"""
    return "data:image/svg+xml;base64," + svg_b64(svg)


def svg_css(svg):
    """ค่าสำหรับใช้ใน CSS background-image"""
    return 'url("data:image/svg+xml;base64,' + svg_b64(svg) + '")'


# ---------------------------------------------------------------- แมนดาลา
def _rosette(cx, cy, r, petals, stroke, width=1.0):
    """วาดดอกไม้กลีบรอบวงกลมหนึ่งดอก"""
    parts = []
    for k in range(petals):
        ang = 360.0 / petals * k
        parts.append(
            f'<ellipse cx="{cx:.2f}" cy="{cy - r * 0.56:.2f}" rx="{r * 0.17:.2f}" ry="{r * 0.42:.2f}" '
            f'transform="rotate({ang:.2f} {cx:.2f} {cy:.2f})" fill="none" stroke="{stroke}" stroke-width="{width}"/>')
    for frac in (1.0, 0.62, 0.2):
        parts.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r * frac:.2f}" fill="none" '
                     f'stroke="{stroke}" stroke-width="{width}"/>')
    # จุดไข่ปลารอบนอก
    dots = petals * 2
    for k in range(dots):
        a = math.radians(360.0 / dots * k)
        parts.append(f'<circle cx="{cx + math.cos(a) * r * 1.12:.1f}" cy="{cy + math.sin(a) * r * 1.12:.1f}" '
                     f'r="{width * 0.9:.2f}" fill="{stroke}"/>')
    return "".join(parts)


def _diamond(cx, cy, s, stroke, width=1.0):
    pts = f"{cx},{cy - s} {cx + s},{cy} {cx},{cy + s} {cx - s},{cy}"
    return f'<polygon points="{pts}" fill="none" stroke="{stroke}" stroke-width="{width}"/>'


def mandala_tile(stroke=MAROON, opacity=0.08, size=150):
    """กระเบื้องลายแมนดาลาที่ต่อกันได้ไร้รอยต่อ (วางซ้ำเป็นพื้นหลัง)
    วาดดอกไม้หนึ่งดอกไว้ใน <defs> แล้วเรียกซ้ำด้วย <use> เพื่อให้ไฟล์เล็ก"""
    h = size / 2.0
    r = size * 0.30
    uses = "".join(f'<use href="#r" x="{x}" y="{y}"/>' for x, y in ((h, h), (0, 0), (size, 0), (0, size), (size, size)))
    diamonds = "".join(_diamond(x, y, size * 0.09, stroke, 1.0) for x, y in ((h, 0), (h, size), (0, h), (size, h)))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<defs><g id="r">{_rosette(0, 0, r, 12, stroke, 1.1)}</g></defs>'
            f'<g opacity="{opacity}">{uses}{diamonds}{_diamond(h, h, size * 0.46, stroke, 0.8)}</g></svg>')


def jaali_tile(stroke=GOLD, opacity=0.35, size=44):
    """ลายตาข่ายแบบ Jaali (หน้าต่างฉลุแบบมุกัล) ใช้เป็นพื้นแถบสีเข้ม"""
    h = size / 2.0
    d = (f'<path d="M{h} 2 L{size - 2} {h} L{h} {size - 2} L2 {h} Z" fill="none" stroke="{stroke}" stroke-width="1"/>'
         f'<circle cx="{h}" cy="{h}" r="{size * 0.12}" fill="none" stroke="{stroke}" stroke-width="1"/>'
         f'<path d="M0 0 L{h} 2 M{size} 0 L{h} 2 M0 {size} L{h} {size - 2} M{size} {size} L{h} {size - 2}" '
         f'stroke="{stroke}" stroke-width="0.8" fill="none"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<g opacity="{opacity}">{d}</g></svg>')


# ---------------------------------------------------------------- เพสลีย์
def paisley(fill=GOLD, stroke=MAROON_DARK, opacity=0.9, size=120):
    """ลายเพสลีย์เดี่ยว ใช้ตกแต่งมุมแบนเนอร์"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 100 100">'
            f'<g opacity="{opacity}">'
            f'<path d="M50 6 C82 8 96 42 80 70 C68 92 38 98 22 78 C10 62 26 44 42 50 C54 55 52 70 42 68 '
            f'C36 66 38 60 42 61" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>'
            f'<path d="M52 20 C72 24 80 44 70 62 C62 76 44 80 34 70" fill="none" stroke="{stroke}" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-dasharray="1 4"/>'
            f'<circle cx="62" cy="40" r="4" fill="{stroke}"/><circle cx="52" cy="58" r="2.6" fill="{stroke}"/>'
            f'</g></svg>')


# ---------------------------------------------------------------- โทรัน / เส้นคั่น
def toran_tile(c1=SAFFRON, c2=GOLD, c3=PEACOCK):
    """ธงแขวนหน้าประตูแบบอินเดีย (Toran) 3 สี สลับกัน ความกว้างหนึ่งชุด = 3 ธง"""
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="90" height="16" viewBox="0 0 90 16">'
            f'<path d="M0 0H30L15 16Z" fill="{c1}"/><path d="M30 0H60L45 16Z" fill="{c2}"/>'
            f'<path d="M60 0H90L75 16Z" fill="{c3}"/>'
            f'<circle cx="15" cy="4" r="1.6" fill="{CREAM}"/><circle cx="45" cy="4" r="1.6" fill="{MAROON_DARK}"/>'
            f'<circle cx="75" cy="4" r="1.6" fill="{CREAM}"/></svg>')


def divider(color=GOLD, width=320):
    """เส้นคั่นหัวข้อ มีดอกบัวตรงกลาง"""
    mid = width / 2.0
    petals = ""
    for ang in (-60, -30, 0, 30, 60):
        petals += (f'<ellipse cx="{mid}" cy="9" rx="3.2" ry="8" transform="rotate({ang} {mid} 18)" '
                   f'fill="{color}" opacity="0.95"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="22" viewBox="0 0 {width} 22">'
            f'<line x1="4" y1="14" x2="{mid - 26}" y2="14" stroke="{color}" stroke-width="1.4"/>'
            f'<line x1="{mid + 26}" y1="14" x2="{width - 4}" y2="14" stroke="{color}" stroke-width="1.4"/>'
            f'<circle cx="{mid - 32}" cy="14" r="2" fill="{color}"/><circle cx="{mid + 32}" cy="14" r="2" fill="{color}"/>'
            f'{petals}<circle cx="{mid}" cy="17" r="2.6" fill="{MAROON}"/></svg>')


# ---------------------------------------------------------------- โลโก้ในตัว
def logo_svg(ring=GOLD, body=MAROON, art=CREAM, accent=SAFFRON):
    """โลโก้ร้าน: ตราวงกลมสีทอง ข้างในเป็นโดมหัวหอมแบบอินเดียและดอกบัว
    (ถ้าอยากใช้โลโก้ของร้านเอง ไปที่แอดมิน > ตั้งค่า > โลโก้ แล้วอัปโหลดได้เลย)"""
    petals = ""
    for ang in (-70, -42, -14, 14, 42, 70):
        petals += (f'<ellipse cx="60" cy="93" rx="5" ry="13" transform="rotate({ang} 60 100)" '
                   f'fill="{accent}" stroke="{ring}" stroke-width="1"/>')
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">'
        f'<circle cx="60" cy="60" r="57" fill="{ring}"/>'
        f'<circle cx="60" cy="60" r="52" fill="{body}"/>'
        f'<circle cx="60" cy="60" r="47" fill="none" stroke="{ring}" stroke-width="1.2" stroke-dasharray="2 3"/>'
        # ยอดโดม
        f'<line x1="60" y1="12" x2="60" y2="24" stroke="{ring}" stroke-width="2.2" stroke-linecap="round"/>'
        f'<circle cx="60" cy="11" r="2.6" fill="{ring}"/>'
        # โดมหัวหอม
        f'<path d="M60 24 C58 33 51 36 45 44 C39 52 38 60 39 70 L81 70 C82 60 81 52 75 44 '
        f'C69 36 62 33 60 24 Z" fill="{art}"/>'
        # ซุ้มโค้ง
        f'<path d="M52 70 L52 56 C52 49 68 49 68 56 L68 70 Z" fill="{body}"/>'
        f'<path d="M34 70 H86 V76 H34 Z" fill="{ring}"/>'
        # หออะไหล่สองข้าง
        f'<rect x="30" y="50" width="6" height="20" fill="{art}"/><rect x="84" y="50" width="6" height="20" fill="{art}"/>'
        f'<path d="M30 50 L33 42 L36 50 Z" fill="{ring}"/><path d="M84 50 L87 42 L90 50 Z" fill="{ring}"/>'
        f'{petals}'
        f'<circle cx="60" cy="100" r="4" fill="{ring}"/>'
        '</svg>')


# ---------------------------------------------------------------- ไอคอนโซเชียล
def social_icon(name, fg=CREAM, bg=MAROON_DARK):
    """ไอคอนโซเชียลขนาด 24x24 (โปร่งใส) คืนค่าเป็นข้อความ SVG"""
    w = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">', "</svg>")
    shapes = {
        "instagram": (f'<rect x="3.5" y="3.5" width="17" height="17" rx="5" fill="none" stroke="{fg}" stroke-width="2"/>'
                      f'<circle cx="12" cy="12" r="4" fill="none" stroke="{fg}" stroke-width="2"/>'
                      f'<circle cx="17.2" cy="6.8" r="1.2" fill="{fg}"/>'),
        "facebook": (f'<path d="M13.5 21v-8h2.7l.4-3.2h-3.1V7.8c0-.9.3-1.5 1.6-1.5h1.7V3.4c-.3 0-1.3-.1-2.4-.1'
                     f'-2.4 0-4.1 1.5-4.1 4.2v2.3H7.5V13h2.8v8z" fill="{fg}"/>'),
        "line": (f'<path d="M12 3C6.8 3 3 6.2 3 10.2c0 3.6 3.2 6.5 7.5 7 .3.1.7.2.8.5.1.3 0 .7 0 1l-.1.8'
                 f'c0 .3-.2 1 .9.6s5.8-3.4 7.9-5.8C20.4 12.9 21 11.6 21 10.2 21 6.2 17.2 3 12 3z" fill="{fg}"/>'
                 f'<text x="12" y="11.6" font-size="4.8" font-weight="700" text-anchor="middle" fill="{bg}" '
                 f'font-family="Arial, sans-serif">LINE</text>'),
        "tiktok": (f'<path d="M16.5 3c.3 2.2 1.6 3.6 3.8 3.8v3c-1.4 0-2.7-.4-3.8-1.2v6.1c0 3.2-2.6 5.3-5.5 5.3'
                   f'-3 0-5.2-2.3-5.2-5.1 0-3.2 2.7-5.5 6-5v3.1c-1.4-.4-2.9.5-2.9 2 0 1.1.9 2 2 2 1.2 0 2.1-.8 2.1-2.2V3z" '
                   f'fill="{fg}"/>'),
        "youtube": (f'<rect x="2.5" y="5.5" width="19" height="13" rx="4" fill="{fg}"/>'
                    f'<path d="M10 9l5 3-5 3z" fill="{bg}"/>'),
        "x_twitter": (f'<path d="M5 4.5l14 15M19 4.5L5 19.5" stroke="{fg}" stroke-width="2.4" stroke-linecap="round"/>'),
    }
    return w[0] + shapes.get(name, "") + w[1]


SOCIAL_ORDER = [
    ("instagram", "Instagram"), ("facebook", "Facebook"), ("line", "LINE"),
    ("tiktok", "TikTok"), ("youtube", "YouTube"), ("x_twitter", "X"),
]


# ---------------------------------------------------------------- หมวดหมู่รูปภาพ
import os

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")

CATEGORY_IMAGE = {
    "ของทานเล่น": "starters.jpg",
    "ทันดูรี": "tandoori.jpg",
    "แกงอินเดีย": "curry.jpg",
    "ข้าวและขนมปัง": "rice_bread.jpg",
    "ของหวานและเครื่องดื่ม": "desserts.jpg",
}


def category_image(cat):
    """คืนค่า path ของรูปภาพประจำหมวด ถ้าไม่มีรูปให้คืน None"""
    filename = CATEGORY_IMAGE.get(cat)

    if not filename:
        return None

    path = os.path.join(IMAGE_DIR, filename)

    if os.path.isfile(path):
        return path

    return None



# ---------------------------------------------------------------- ไอคอนเส้น (แทนอิโมจิในส่วนที่ไม่ใช่รูปอาหาร)
_ICONS = {
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    "pin": '<path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "truck": '<path d="M3 7h11v9H3zM14 10h4l3 3v3h-7z"/><circle cx="7" cy="17.5" r="2"/><circle cx="17" cy="17.5" r="2"/>',
    "store": '<path d="M4 10v10h16V10M3 10l2-6h14l2 6zM9 20v-6h6v6"/>',
    "utensils": '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M17 3c-2 2-2.5 5-2.5 8H17v10"/>',
    "leaf": '<path d="M5 19c0-9 6-14 15-14 0 9-5 15-14 15M5 19l8-8"/>',
    "star": '<path d="M12 3l2.8 6 6.2.7-4.7 4.3 1.4 6.5-5.7-3.3-5.7 3.3 1.4-6.5L3 9.7 9.2 9z"/>',
    "flame": '<path d="M12 3c1 4 5 5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 2 2 2 0-3-1-5 1-8z"/>',
    "gift": '<path d="M4 11h16v9H4zM3 8h18v3H3zM12 8v12M12 8c-2-4-6-3-4 0M12 8c2-4 6-3 4 0"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
}


def line_icon(name, color=CREAM, width=1.8):
    """ไอคอนเส้นขนาด 24x24 สีตามที่กำหนด (คืนข้อความ SVG)"""
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">'
            f'{_ICONS.get(name, "")}</svg>')
