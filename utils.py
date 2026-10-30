"""utils.py - ตัวช่วยตรวจข้อมูลที่กรอกจากฟอร์ม (ไม่เปลี่ยนค่าที่เก็บ แค่ตรวจความถูกต้องเบื้องต้น)"""
import re
from datetime import datetime

_DIGITS = re.compile(r"\d")


def digits_only(text):
    """ดึงเฉพาะตัวเลขจากข้อความ เช่น '081-234-5678' -> '0812345678'"""
    return "".join(_DIGITS.findall(text or ""))


def valid_phone(text):
    """เบอร์โทรที่ยอมรับ: มีตัวเลข 8-15 หลัก (รองรับเบอร์บ้าน มือถือ และรหัสประเทศ +66)
    ตั้งใจให้หลวมเพื่อไม่กระทบเบอร์เดิมที่เคยบันทึกไว้ในระบบ"""
    n = len(digits_only(text))
    return 8 <= n <= 15


def clean_text(text, maxlen=200):
    """ตัดช่องว่างหัวท้าย ยุบช่องว่างซ้ำ และจำกัดความยาว"""
    t = re.sub(r"\s+", " ", (text or "")).strip()
    return t[:maxlen]



_HOURS = re.compile(r"(\d{1,2})[:.](\d{2})\D+?(\d{1,2})[:.](\d{2})")


def parse_hours(text):
    """แปลงข้อความเวลาเปิด-ปิด เช่น '10:00–22:00 น.' เป็น (นาทีเริ่ม, นาทีปิด) · อ่านไม่ได้คืน None"""
    m = _HOURS.search(text or "")
    if not m:
        return None
    h1, m1, h2, m2 = (int(x) for x in m.groups())
    if h1 > 23 or h2 > 24 or m1 > 59 or m2 > 59:
        return None
    return h1 * 60 + m1, h2 * 60 + m2


def is_open_now(text, now=None):
    """ร้านเปิดอยู่ไหมตามเวลาที่ตั้งไว้ (รองรับร้านที่ปิดหลังเที่ยงคืน) · อ่านเวลาไม่ได้คืน None"""
    span = parse_hours(text)
    if span is None:
        return None
    now = now or datetime.now()
    cur = now.hour * 60 + now.minute
    start, end = span
    if start == end:
        return True                      # เปิดตลอด 24 ชั่วโมง
    if start < end:
        return start <= cur < end
    return cur >= start or cur < end     # ข้ามเที่ยงคืน เช่น 18:00-02:00
