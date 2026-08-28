import json
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# รายการสติกเกอร์ทั้งหมดที่ต้องการติดตาม (ใส่ ID และชื่อให้ครบถ้วน)
MY_STICKERS = [
    {"id": "36148588", "name": "มินนี่ขออ้อนหน่อย"},
    {"id": "36091152", "name": "วีวี่ช่วงเวลาดีๆ (DukDik)"},
    {"id": "35952291", "name": "โยเกิร์ตแชททุกวัน (DukDik)"},
    {"id": "36003212", "name": "ถ้วยฟูทำงานที่เรารัก (DukDik)"},
    {"id": "35827838", "name": "ถ้วยฟูวันที่คิดถึง (ดุ๊กดิ๊ก)"},
    {"id": "35302312", "name": "วีวี่คิดถึงทุกวัน"},
    # หากมีสติกเกอร์ตัวอื่น สามารถเพิ่มต่อตรงนี้ได้เลยครับ เช่น:
    # {"id": "ID_3", "name": "ถ้วยฟูทำงานที่เรารัก"},
]

BASE_URL = (
    "https://store.line.me/stickershop/showcase/top_creators/th?taste=3&page="
)
MAX_PAGES = 15  # ค้นหาลึกสุด 15 หน้า (ประมาณ Top 540)


def fetch_ranks():
    found_ranks = {s["id"]: None for s in MY_STICKERS}
    items_per_page = 36

    for page in range(1, MAX_PAGES + 1):
        url = f"{BASE_URL}{page}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }

        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select("a[href*='/stickershop/product/']")

            for index, item in enumerate(items):
                href = item.get("href", "")
                match = re.search(r"/product/(\d+)", href)
                if match:
                    sticker_id = match.group(1)
                    if (
                        sticker_id in found_ranks
                        and found_ranks[sticker_id] is None
                    ):
                        rank = ((page - 1) * items_per_page) + (index + 1)
                        found_ranks[sticker_id] = rank

            # ถ้าเจอครบทุกตัวแล้ว ให้หยุดค้นหาทันที
            if all(r is not None for r in found_ranks.values()):
                break

        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการดึงข้อมูลหน้า {page}: {e}")

    return found_ranks


def update_data():
    print("กำลังเช็กอันดับสติกเกอร์และอัปเดตไฟล์ data.json...")
    ranks = fetch_ranks()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # อ่านข้อมูลประวัติเก่า (ถ้ามี)
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            history_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history_data = {"stickers": MY_STICKERS, "history": []}

    # อัปเดตรายชื่อสติกเกอร์ให้ตรงกับปัจจุบันเสมอ
    history_data["stickers"] = MY_STICKERS

    # เพิ่มบันทึกประวัติอันดับรอบใหม่
    entry = {"timestamp": timestamp, "ranks": ranks}
    history_data["history"].append(entry)

    # บันทึกลงไฟล์ data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

    print(f"บันทึกข้อมูลเรียบร้อยเมื่อเวลา {timestamp}")


if __name__ == "__main__":
    update_data()