"""receipt_pdf.py - สร้างใบเสร็จรับเงินเป็นไฟล์ PDF (A5) พร้อมแยกภาษีมูลค่าเพิ่ม (VAT)

ใช้งาน:  pdf_bytes = build_receipt_pdf(order, items, shop)
  order : แถวออเดอร์จากฐานข้อมูล (id, receipt_no, customer_name, phone, subtotal, discount, points_used,
          delivery_fee, total, order_type, table_no, payment_method, created_at, updated_at)
  items : รายการอาหาร (name, qty, price)
  shop  : dict ข้อมูลร้าน {"name","tagline","address","phone","hours","tax_id"}

VAT : ราคาในเว็บถือเป็นราคาที่ "รวม VAT แล้ว" (ยอดที่ลูกค้าจ่ายไม่เปลี่ยน)
      ใบเสร็จจะแยกให้เห็น ราคาก่อน VAT และ VAT ตามอัตรา VAT_RATE ใน config.py (7%)
ฟอนต์ไทย : ใช้ fonts/Loma.ttf ที่แนบมา ถ้าไม่มีจะลองหาฟอนต์ไทยในเครื่อง (Leelawadee UI / Tahoma / TLWG)
"""
import io
import os
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle)

try:
    from config import TAX_ID, VAT_RATE
except ImportError:  # รันแยกไฟล์ได้
    VAT_RATE, TAX_ID = 0.07, ""

# ---------------- สี (โทนเดียวกับเว็บ) ----------------
PLUM = colors.HexColor("#1A0F26")
PLUM2 = colors.HexColor("#2E1A45")
GOLD = colors.HexColor("#E9B949")
GOLD_L = colors.HexColor("#FFE08A")
SAFFRON = colors.HexColor("#F07A00")
RANI = colors.HexColor("#D81B60")
PEACOCK = colors.HexColor("#1FA8A0")
PAPER = colors.HexColor("#FFFBF3")
ZEBRA = colors.HexColor("#FFF1D6")
LINE = colors.HexColor("#EBD9B4")
INK = colors.HexColor("#2A1B12")
MUTED = colors.HexColor("#85746A")
GREEN = colors.HexColor("#17935A")
RED = colors.HexColor("#C0392B")

W, H = A5
M = 30                 # ขอบซ้ายขวา
HDR = 108              # ความสูงหัวกระดาษหน้าแรก
HDR2 = 38              # ความสูงหัวกระดาษหน้าต่อไป
FOOT = 50

# ---------------- ฟอนต์ ----------------
_HERE = Path(__file__).resolve().parent
_CANDIDATES = [
    (_HERE / "fonts" / "Loma.ttf", _HERE / "fonts" / "Loma-Bold.ttf"),
    (Path(r"C:\Windows\Fonts\LeelawUI.ttf"), Path(r"C:\Windows\Fonts\LeelaUIb.ttf")),
    (Path(r"C:\Windows\Fonts\tahoma.ttf"), Path(r"C:\Windows\Fonts\tahomabd.ttf")),
    (Path("/usr/share/fonts/truetype/tlwg/Loma.ttf"), Path("/usr/share/fonts/truetype/tlwg/Loma-Bold.ttf")),
    (Path("/usr/share/fonts/truetype/tlwg/Garuda.ttf"), Path("/usr/share/fonts/truetype/tlwg/Garuda-Bold.ttf")),
]
_FONTS = None


def _fonts():
    """ลงทะเบียนฟอนต์ไทยครั้งแรกที่เรียกใช้ คืนค่า (ชื่อฟอนต์ปกติ, ชื่อฟอนต์ตัวหนา)"""
    global _FONTS
    if _FONTS:
        return _FONTS
    for reg, bold in _CANDIDATES:
        if reg.exists():
            pdfmetrics.registerFont(TTFont("RcReg", str(reg)))
            pdfmetrics.registerFont(TTFont("RcBold", str(bold if bold.exists() else reg)))
            _FONTS = ("RcReg", "RcBold")
            return _FONTS
    raise RuntimeError("ไม่พบฟอนต์ภาษาไทยสำหรับสร้าง PDF (ต้องมี fonts/Loma.ttf)")


# ---------------- ตัวช่วยจัดรูปแบบ ----------------
def _g(o, key, default=""):
    try:
        v = o[key]
    except (KeyError, IndexError):
        return default
    return default if v is None else v


def _money(x):
    return f"฿{float(x):,.2f}"


def vat_split(total, rate=None):
    """แยก VAT ออกจากยอดรวมที่รวม VAT แล้ว -> (ราคาก่อน VAT, VAT) ปัดเศษ 2 ตำแหน่ง"""
    rate = VAT_RATE if rate is None else rate
    base = round(float(total) / (1 + rate), 2)
    return base, round(float(total) - base, 2)


def _fmt_dt(s):
    """'2026-10-25 14:35:10' -> '25/10/2569 14:35 น.' (พ.ศ.)"""
    s = str(s or "").replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s[:len(datetime.now().strftime(fmt))], fmt)
            return d.strftime("%d/%m/") + str(d.year + 543) + (d.strftime(" %H:%M น.") if "%H" in fmt else "")
        except ValueError:
            continue
    return s[:16]


def _mask_phone(p):
    d = "".join(ch for ch in str(p or "") if ch.isdigit())
    return f"{d[:3]}-xxx-{d[-4:]}" if len(d) >= 9 else (str(p or "") or "-")


def _p(text, style):
    return Paragraph(escape(str(text)), style)


# ---------------- ตราประทับ PAID ----------------
class _Stamp(Flowable):
    def __init__(self, bold, w=150, h=84):
        super().__init__()
        self.bold, self.width, self.height = bold, w, h

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.translate(self.width / 2, self.height / 2)
        c.rotate(9)
        c.setStrokeColor(GREEN); c.setFillColor(GREEN)
        c.setStrokeAlpha(.85); c.setFillAlpha(.9)
        c.setLineWidth(2.4); c.roundRect(-56, -27, 112, 54, 9, stroke=1, fill=0)
        c.setLineWidth(.7); c.roundRect(-52, -23, 104, 46, 6, stroke=1, fill=0)
        c.setFont(self.bold, 25); c.drawCentredString(0, -3, "PAID")
        c.setFont(self.bold, 9.5); c.drawCentredString(0, -17, "ชำระเงินแล้ว")
        c.restoreState()


# ---------------- หัว/ท้ายกระดาษ ----------------
def _tri_bar(c, y, h=4):
    third = W / 3
    for i, col in enumerate((RANI, SAFFRON, GOLD)):
        c.setFillColor(col); c.rect(i * third, y, third + 1, h, stroke=0, fill=1)


def _crest(c, cx, cy, r, bold):
    c.saveState()
    c.setStrokeColor(GOLD); c.setLineWidth(1.6); c.setFillColor(PLUM2); c.circle(cx, cy, r, stroke=1, fill=1)
    c.setLineWidth(.5); c.circle(cx, cy, r - 3.2, stroke=1, fill=0)
    c.setFillColor(GOLD)
    p = c.beginPath()                       # โดมอินเดีย
    p.moveTo(cx - 12, cy - 9)
    p.curveTo(cx - 13, cy + 5, cx - 5, cy + 10, cx, cy + 17)
    p.curveTo(cx + 5, cy + 10, cx + 13, cy + 5, cx + 12, cy - 9)
    p.close(); c.drawPath(p, stroke=0, fill=1)
    c.rect(cx - 15, cy - 13, 30, 3.2, stroke=0, fill=1)
    c.setFillColor(PLUM2); c.roundRect(cx - 3.2, cy - 9, 6.4, 9, 3, stroke=0, fill=1)  # ประตู
    c.restoreState()


def _page_first(shop, rc_no):
    reg, bold = _fonts()

    def draw(c, doc):
        c.saveState()
        c.setFillColor(PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)
        c.setFillColor(PLUM); c.rect(0, H - HDR, W, HDR, stroke=0, fill=1)
        c.saveState()                       # ลายวงกลมมันดาลาจางๆ มุมขวาบน
        clip = c.beginPath(); clip.rect(0, H - HDR, W, HDR); c.clipPath(clip, stroke=0, fill=0)
        c.setStrokeColor(GOLD); c.setLineWidth(.8)
        for i, r in enumerate((26, 44, 62, 80, 98, 116)):
            c.setStrokeAlpha(.22 - i * .028); c.circle(W - 22, H - 18, r, stroke=1, fill=0)
        c.restoreState()
        _tri_bar(c, H - HDR - 4)
        _crest(c, M + 23, H - 44, 23, bold)
        c.setFillColor(GOLD_L); c.setFont(bold, 20); c.drawString(M + 57, H - 42, shop["name"])
        c.setFillColor(colors.HexColor("#CDBFD6")); c.setFont(reg, 7.4)
        c.drawString(M + 57, H - 55, shop.get("tagline", ""))
        c.setFillColor(colors.white); c.setFont(bold, 15); c.drawRightString(W - M, H - 40, "ใบเสร็จรับเงิน")
        c.setFillColor(GOLD); c.setFont(bold, 8); c.drawRightString(W - M, H - 53, "R E C E I P T")
        c.setStrokeColor(GOLD); c.setStrokeAlpha(.35); c.setLineWidth(.6); c.line(M, H - 70, W - M, H - 70)
        c.setStrokeAlpha(1)
        c.setFillColor(colors.HexColor("#E6DAEE")); c.setFont(reg, 7.6)
        line = " · ".join(x for x in (shop.get("address"), f"โทร {shop['phone']}" if shop.get("phone") else "",
                                      f"เปิด {shop['hours']}" if shop.get("hours") else "") if x)
        c.drawString(M, H - 83, line[:110])
        if shop.get("tax_id"):
            c.drawString(M, H - 95, f"เลขประจำตัวผู้เสียภาษี {shop['tax_id']}")
        _footer(c, doc, shop, rc_no)
        c.restoreState()
    return draw


def _page_later(shop, rc_no):
    reg, bold = _fonts()

    def draw(c, doc):
        c.saveState()
        c.setFillColor(PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)
        c.setFillColor(PLUM); c.rect(0, H - HDR2, W, HDR2, stroke=0, fill=1)
        _tri_bar(c, H - HDR2 - 3, 3)
        c.setFillColor(GOLD_L); c.setFont(bold, 12); c.drawString(M, H - 24, shop["name"])
        c.setFillColor(colors.white); c.setFont(reg, 8.5); c.drawRightString(W - M, H - 24, f"ใบเสร็จรับเงิน {rc_no}")
        _footer(c, doc, shop, rc_no)
        c.restoreState()
    return draw


def _footer(c, doc, shop, rc_no):
    reg, bold = _fonts()
    c.setStrokeColor(LINE); c.setLineWidth(.8); c.line(M, FOOT - 6, W - M, FOOT - 6)
    c.setFillColor(SAFFRON); c.setFont(bold, 9.5); c.drawCentredString(W / 2, FOOT - 20, "ขอบคุณที่อุดหนุน · Namaste")
    c.setFillColor(MUTED); c.setFont(reg, 6.8)
    c.drawCentredString(W / 2, FOOT - 31, f"{shop['name']} · เลขที่ {rc_no} · หน้า {doc.page}")


# ---------------- สร้าง PDF ----------------
def build_receipt_pdf(o, items, shop):
    reg, bold = _fonts()
    shop = {"name": "Maharaja Palace", "tagline": "", "address": "", "phone": "", "hours": "",
            "tax_id": TAX_ID, **{k: v for k, v in (shop or {}).items() if v is not None}}
    shop["tax_id"] = shop.get("tax_id") or TAX_ID
    rc_no = str(_g(o, "receipt_no", "") or f"#{_g(o, 'id', '')}")

    lbl = ParagraphStyle("lbl", fontName=reg, fontSize=7.2, leading=9, textColor=MUTED)
    val = ParagraphStyle("val", fontName=bold, fontSize=8.8, leading=11.5, textColor=INK)
    th = ParagraphStyle("th", fontName=bold, fontSize=8.6, leading=11, textColor=GOLD_L)
    thr = ParagraphStyle("thr", parent=th, alignment=TA_RIGHT)
    thc = ParagraphStyle("thc", parent=th, alignment=TA_CENTER)
    td = ParagraphStyle("td", fontName=reg, fontSize=9.4, leading=12.5, textColor=INK, wordWrap="CJK")
    tdr = ParagraphStyle("tdr", parent=td, alignment=TA_RIGHT)
    tdc = ParagraphStyle("tdc", parent=td, alignment=TA_CENTER)
    sl = ParagraphStyle("sl", fontName=reg, fontSize=9, leading=12, textColor=INK)
    sr = ParagraphStyle("sr", parent=sl, alignment=TA_RIGHT)
    sm = ParagraphStyle("sm", fontName=reg, fontSize=7.8, leading=10.5, textColor=MUTED)
    smr = ParagraphStyle("smr", parent=sm, alignment=TA_RIGHT)
    note = ParagraphStyle("note", fontName=reg, fontSize=7.6, leading=11, textColor=MUTED, alignment=TA_CENTER)

    content_w = W - 2 * M
    story = []

    # ---- กล่องข้อมูลออเดอร์ ----
    otype = str(_g(o, "order_type", "") or "-")
    if _g(o, "table_no", ""):
        otype += f" · โต๊ะ {_g(o, 'table_no')}"

    def kv(label, value):
        return [_p(label, lbl), _p(value, val)]
    info = Table([
        [kv("เลขที่ใบเสร็จ", rc_no), kv("วันที่ออกใบเสร็จ", _fmt_dt(_g(o, "updated_at") or _g(o, "created_at"))),
         kv("ออเดอร์", f"#{_g(o, 'id')} · {otype}")],
        [kv("ลูกค้า", _g(o, "customer_name", "") or "-"), kv("เบอร์โทร", _mask_phone(_g(o, "phone", ""))),
         kv("วิธีชำระเงิน", _g(o, "payment_method", "") or "โอนเงิน")],
    ], colWidths=[content_w * .31, content_w * .35, content_w * .34])
    info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), .8, LINE), ("ROUNDEDCORNERS", [9, 9, 9, 9]),
        ("LINEBELOW", (0, 0), (-1, 0), .5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story += [Spacer(1, 4), info, Spacer(1, 9)]

    # ---- ตารางรายการอาหาร ----
    cw = [content_w - 180, 52, 62, 66]
    rows = [[_p("รายการ", th), _p("จำนวน", thc), _p("ราคา/หน่วย", thr), _p("รวม", thr)]]
    for it in items:
        q, pr = int(it["qty"]), float(it["price"])
        rows.append([_p(it["name"], td), _p(q, tdc), _p(f"{pr:,.2f}", tdr), _p(f"{pr * q:,.2f}", tdr)])
    tbl = Table(rows, colWidths=cw, repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), PLUM), ("ROUNDEDCORNERS", [8, 8, 0, 0]),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
          ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
          ("LINEBELOW", (0, -1), (-1, -1), 1.2, GOLD)]
    for r in range(1, len(rows)):
        st.append(("BACKGROUND", (0, r), (-1, r), colors.white if r % 2 else ZEBRA))
    tbl.setStyle(TableStyle(st))
    story += [tbl, Spacer(1, 9)]

    # ---- สรุปยอด + VAT ----
    total = float(_g(o, "total", 0) or 0)
    base, vat = vat_split(total)
    disc, pts, fee = float(_g(o, "discount", 0) or 0), float(_g(o, "points_used", 0) or 0), float(_g(o, "delivery_fee", 0) or 0)
    sum_rows = [[_p("ยอดอาหาร", sl), _p(_money(_g(o, "subtotal", 0) or 0), sr)]]
    if disc:
        sum_rows.append([_p("ส่วนลดคูปอง", sl), Paragraph(f'<font color="#C0392B">-{_money(disc)}</font>', sr)])
    if pts:
        sum_rows.append([_p("ใช้แต้มแลกส่วนลด", sl), Paragraph(f'<font color="#C0392B">-{_money(pts)}</font>', sr)])
    sum_rows.append([_p("ค่าจัดส่ง", sl), _p(_money(fee) if fee else "ฟรี", sr)])
    sw = 196
    sum_tbl = Table(sum_rows, colWidths=[sw - 92, 92])
    sum_tbl.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                                 ("LINEBELOW", (0, -1), (-1, -1), .6, LINE)]))
    grand = Table([[Paragraph(f'<font color="#FFE08A" size="9.5">รวมทั้งสิ้น</font><br/><font color="#CDBFD6" size="6.8">(รวม VAT แล้ว)</font>',
                              ParagraphStyle("g1", fontName=bold, leading=11)),
                    Paragraph(f'<font color="#FFE08A" size="16">{_money(total)}</font>',
                              ParagraphStyle("g2", fontName=bold, leading=19, alignment=TA_RIGHT))]],
                  colWidths=[sw - 112, 112])
    grand.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PLUM), ("ROUNDEDCORNERS", [9, 9, 9, 9]),
                               ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                               ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BOX", (0, 0), (-1, -1), 1, GOLD)]))
    pct = f"{VAT_RATE * 100:g}"
    vat_tbl = Table([[_p("ราคาก่อนภาษีมูลค่าเพิ่ม", sm), _p(_money(base), smr)],
                     [_p(f"ภาษีมูลค่าเพิ่ม {pct}%", sm), _p(_money(vat), smr)]], colWidths=[sw - 92, 92])
    vat_tbl.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    right = Table([[sum_tbl], [Spacer(1, 5)], [grand], [Spacer(1, 4)], [vat_tbl]], colWidths=[sw])
    right.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    outer = Table([[_Stamp(bold), right]], colWidths=[content_w - sw, sw])
    outer.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    outer.keepWithNext = False
    story += [outer, Spacer(1, 10)]
    story.append(_p(f"ราคาสินค้าและบริการข้างต้นรวมภาษีมูลค่าเพิ่ม {pct}% แล้ว · โปรดเก็บใบเสร็จนี้ไว้เป็นหลักฐานการชำระเงิน", note))

    # ---- ประกอบเอกสาร ----
    buf = io.BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A5, title=f"ใบเสร็จรับเงิน {rc_no}", author=shop["name"],
                          subject="Receipt", leftMargin=M, rightMargin=M)
    f1 = Frame(M, FOOT, content_w, H - HDR - FOOT - 14, id="f1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    f2 = Frame(M, FOOT, content_w, H - HDR2 - FOOT - 18, id="f2", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="first", frames=[f1], onPage=_page_first(shop, rc_no), autoNextPageTemplate="later"),
                          PageTemplate(id="later", frames=[f2], onPage=_page_later(shop, rc_no))])
    doc.build(story)
    return buf.getvalue()
