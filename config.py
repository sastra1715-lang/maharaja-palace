"""config.py - ค่าตั้งต้นที่แก้ได้ง่ายของร้าน (แก้ที่นี่ที่เดียว)

รหัสแอดมิน : ตั้งผ่านตัวแปรแวดล้อม ADMIN_PASSWORD (ค่าเริ่มต้น admin1234 - ควรเปลี่ยนก่อนใช้งานจริง)
QR ชำระเงิน : เซฟรูป QR ของร้านเป็น qr.png วางไว้โฟลเดอร์เดียวกับ app.py หรือใส่ลิงก์รูปแทนก็ได้
              เช่น QR_IMAGE = "https://example.com/my-qr.png"
โลโก้      : 3 วิธี (เลือกวิธีใดก็ได้)
              1) แอดมิน > ตั้งค่า > โลโก้ร้าน > อัปโหลดรูป  (แนะนำ เปลี่ยนได้ทันทีโดยไม่ต้องแก้โค้ด)
              2) วางไฟล์ logo.png (หรือ logo.jpg / logo.webp / logo.svg) ไว้โฟลเดอร์เดียวกับ app.py
              3) ไม่ทำอะไร = ใช้โลโก้โดมอินเดียที่สร้างไว้ในตัว
"""
import os

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin1234")
QR_IMAGE = "qr.png"

LOGO_SIDE = "right"        # "right" = โลโก้มุมขวาบน (ตามตัวอย่าง) · "left" = มุมซ้ายบน
LOGO_FILES = ("logo.png", "logo.jpg", "logo.jpeg", "logo.webp", "logo.svg")

PAGE_TITLE = "Maharaja Palace · Royal Indian Cuisine"
PAGE_ICON = "👑"

# ใบเสร็จ: อัตราภาษีมูลค่าเพิ่ม (VAT) ราคาในเว็บถือเป็นราคาที่รวม VAT แล้ว ใบเสร็จจะแยกยอดให้ดู
VAT_RATE = 0.07
# เลขประจำตัวผู้เสียภาษี 13 หลักของร้าน (ว่างไว้ = ไม่แสดงบนใบเสร็จ) หรือตั้งผ่านตัวแปรแวดล้อม TAX_ID
TAX_ID = os.environ.get("TAX_ID", "")
