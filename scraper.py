import json
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

MY_STICKERS = [
    {"id": "36148588", "name": "มินนี่ขออ้อนหน่อย"},
    {"id": "36091152", "name": "วีวี่ช่วงเวลาดีๆ (DukDik)"},
    {"id": "35952291", "name": "โยเกิร์ตแชททุกวัน (DukDik)"},
    {"id": "36003212", "name": "ถ้วยฟูทำงานที่เรารัก (DukDik)"},
    {"id": "35827838", "name": "ถ้วยฟูวันที่คิดถึง (ดุ๊กดิ๊ก)"},
    {"id": "35302312", "name": "วีวี่คิดถึงทุกวัน"},
]

BASE_URL = "https://store.line.me/stickershop/showcase/top_creators/th?taste=3"


def fetch_ranks():
    found_ranks = {s["id"]: None for s in MY_STICKERS}
    current_overall_rank = 1

    # ใช้ Session เพื่อรักษา狀態 Cookie เหมือนเบราว์เซอร์จริง
    session = requests.Session()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Chromium";v="128", "Not=A?Brand";v="24", "Google Chrome";v="128"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    for page in range(1, 11):  # วนลูปตรวจ 10 หน้าแรก
        url = f"{BASE_URL}&page={page}"

        try:
            res = session.get(url, headers=headers, timeout=10)

            if res.status_code != 200:
                print(f"หน้า {page} ติดปัญหา Status Code: {res.status_code}")
                continue

            soup = BeautifulSoup(res.text, "html.parser")

            # ดึงลิงก์สติกเกอร์ทั้งหมดในหน้า
            links = soup.find_all("a", href=re.compile(r"/stickershop/product/"))

            page_ids = []
            for a in links:
                href = a.get("href", "")
                match = re.search(r"/product/(\d+)", href)
                if match:
                    sid = match.group(1)
                    # ป้องกันการเก็บ ID ซ้ำในกรอบเดียวกัน
                    if not page_ids or page_ids[-1] != sid:
                        page_ids.append(sid)

            print(f"หน้า {page}: ดึงสำเร็จ พบสติกเกอร์ {len(page_ids)} รายการ")

            if not page_ids:
                break

            for sid in page_ids:
                if sid in found_ranks and found_ranks[sid] is None:
                    found_ranks[sid] = current_overall_rank
                current_overall_rank += 1

            if all(r is not None for r in found_ranks.values()):
                break

            # หน่วงเวลาสั้นๆ ป้องกันระบบจำว่าเป็นบอทยิงถี่เกินไป
            time.sleep(1)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดหน้า {page}: {e}")

    return found_ranks


def update_data():
    print("กำลังเริ่มกระบวนการตรวจสอบอันดับสติกเกอร์...")
    ranks = fetch_ranks()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("\nผลการตรวจสอบอันดับประจำรอบ:")
    for sid, rank in ranks.items():
        name = next((s["name"] for s in MY_STICKERS if s["id"] == sid), sid)
        rank_str = f"อันดับที่ {rank}" if rank else "ไม่อยู่ใน Top Rank"
        print(f" - {name} ({sid}): {rank_str}")

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            history_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history_data = {"stickers": MY_STICKERS, "history": []}

    history_data["stickers"] = MY_STICKERS
    history_data["history"].append({"timestamp": timestamp, "ranks": ranks})

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

    print(f"\nบันทึกข้อมูลลง data.json เรียบร้อย ณ เวลา {timestamp}")


if __name__ == "__main__":
    update_data()