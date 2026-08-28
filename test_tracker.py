import re
import requests
from bs4 import BeautifulSoup

# รายการสติกเกอร์ที่ต้องการค้นหา (ใส่ ID และชื่อที่ต้องการแสดงผล)
MY_STICKERS = [
    {"id": "36148588", "name": "โยเกิร์ตแชททุกวัน (DukDik)"},
    {"id": "36003212", "name": "มินนี่ขออ้อนหน่อย"},
    # สามารถเพิ่มสติกเกอร์ตัวอื่นต่อตรงนี้ได้เลย เช่น:
    # {"id": "ID_ตัวที่_3", "name": "ถ้วยฟูทำงานที่เรารัก"},
]

# หน้าจัดอันดับ Top Creators (ภาษาไทย)
BASE_URL = (
    "https://store.line.me/stickershop/showcase/top_creators/th?taste=3&page="
)
MAX_PAGES = 10  # ลองค้นหาเบื้องต้น 10 หน้าแรก (360 อันดับ)

print("กำลังเริ่มค้นหาอันดับสติกเกอร์บน LINE Store...\n")

found_ranks = {s["id"]: None for s in MY_STICKERS}
items_per_page = 36

for page in range(1, MAX_PAGES + 1):
    url = f"{BASE_URL}{page}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"ไม่สามารถดึงข้อมูลหน้า {page} ได้")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("a[href*='/stickershop/product/']")

    for index, item in enumerate(items):
        href = item.get("href", "")
        match = re.search(r"/product/(\d+)", href)
        if match:
            sticker_id = match.group(1)
            if sticker_id in found_ranks and found_ranks[sticker_id] is None:
                rank = ((page - 1) * items_per_page) + (index + 1)
                found_ranks[sticker_id] = rank

    print(f"ตรวจสอบหน้า {page}/{MAX_PAGES} เรียบร้อย...")

    # ถ้าเจอครบทุกตัวแล้ว ให้หยุดค้นหาทันทีเพื่อประหยัดเวลา
    if all(r is not None for r in found_ranks.values()):
        break

print("\n--- สรุปผลการจัดอันดับ ---")
for sticker in MY_STICKERS:
    s_id = sticker["id"]
    name = sticker["name"]
    rank = found_ranks[s_id]
    if rank:
        print(f"🟢 {name} (ID: {s_id}) -> อยู่ดันดับที่ #{rank}")
    else:
        print(
            f"⚪ {name} (ID: {s_id}) -> ไม่พบใน {MAX_PAGES} หน้าแรก (> {MAX_PAGES * 36})"
        )