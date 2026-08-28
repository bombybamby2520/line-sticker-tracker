import json
import time
from datetime import datetime, timedelta, timezone
import requests

MY_STICKERS = [
    {"id": "36148588", "name": "มินนี่ขออ้อนหน่อย"},
    {"id": "36091152", "name": "วีวี่ช่วงเวลาดีๆ (DukDik)"},
    {"id": "35952291", "name": "โยเกิร์ตแชททุกวัน (DukDik)"},
    {"id": "36003212", "name": "ถ้วยฟูทำงานที่เรารัก (DukDik)"},
    {"id": "35827838", "name": "ถ้วยฟูวันที่คิดถึง (ดุ๊กดิ๊ก)"},
    {"id": "35302312", "name": "วีวี่คิดถึงทุกวัน"},
]

# ดึงอันดับผ่าน LINE Store Showcase API โดยตรง (เลี่ยง Anti-Bot)
SHOWCASE_URL = "https://store.line.me/stickershop/showcase/top_creators/th?taste=3"


def fetch_ranks():
    found_ranks = {s["id"]: None for s in MY_STICKERS}

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "th-TH,th;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
        }
    )

    current_overall_rank = 1

    # วนลูปตรวจ 20 หน้าแรก (ครอบคลุม Top 1,000)
    for page in range(1, 21):
        url = f"{SHOWCASE_URL}&page={page}"
        try:
            res = session.get(url, timeout=15)
            if res.status_code != 200:
                print(f"หน้า {page} ติดปัญหา HTTP Status: {res.status_code}")
                continue

            # ใช้ Regex ดึง ID สติกเกอร์ตรงๆ
            import re

            page_ids = []
            matches = re.findall(r"/stickershop/product/(\d+)", res.text)
            for sid in matches:
                if not page_ids or page_ids[-1] != sid:
                    page_ids.append(sid)

            if not page_ids:
                break

            for sid in page_ids:
                if sid in found_ranks and found_ranks[sid] is None:
                    found_ranks[sid] = current_overall_rank
                current_overall_rank += 1

            if all(r is not None for r in found_ranks.values()):
                break

            time.sleep(1.5)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดหน้า {page}: {e}")

    return found_ranks


def update_data():
    print("กำลังเริ่มสแครปอันดับสติกเกอร์...")
    ranks = fetch_ranks()

    tz_th = timezone(timedelta(hours=7))
    timestamp = datetime.now(tz_th).strftime("%Y-%m-%d %H:%M")

    # กรองรอบที่มี null ทั้งหมด: หากรอบไหนสแครปไม่เจอเลย จะไม่นำลง history
    has_valid_data = any(r is not None for r in ranks.values())

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            history_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history_data = {"stickers": MY_STICKERS, "history": []}

    history_data["stickers"] = MY_STICKERS

    if has_valid_data:
        history_data["history"].append(
            {"timestamp": timestamp, "ranks": ranks}
        )
        print(f"บันทึกข้อมูลสำเร็จประจำรอบเวลา {timestamp}")
    else:
        print(
            "⚠️ สแครปไม่พบอันดับในรอบนี้ (อาจติดบล็อก IP) - ข้ามการบันทึกชั่วคราว"
        )

    # กรองประวัติเก่าที่เคยเป็น null ทั้งหมดออกจาก data.json ให้สะอาด
    clean_history = []
    for item in history_data["history"]:
        if any(r is not None for r in item.get("ranks", {}).values()):
            clean_history.append(item)

    history_data["history"] = clean_history

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    update_data()