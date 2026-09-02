import json
import random
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
    {"id": "35319835", "name": "ถ้วยฟูวินเทจเกิร์ล"},
]

SHOWCASE_URL = "https://store.line.me/stickershop/showcase/top_creators/th?taste=3"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
]


def fetch_ranks():
    found_ranks = {s["id"]: None for s in MY_STICKERS}

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "th-TH,th;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
        }
    )

    current_overall_rank = 1

    for page in range(1, 21):
        url = f"{SHOWCASE_URL}&page={page}"
        try:
            res = session.get(url, timeout=15)
            if res.status_code != 200:
                # ถ้า LINE บล็อกจริง ส่วนใหญ่จะเจอ status พวกนี้: 403 (ห้ามเข้า),
                # 429 (ยิงถี่เกินไป), 503 (เซิร์ฟเวอร์ปฏิเสธชั่วคราว)
                print(f"หน้า {page} ติดปัญหา HTTP Status: {res.status_code}")
                continue

            import re

            page_ids = []
            matches = re.findall(r"/stickershop/product/(\d+)", res.text)
            for sid in matches:
                if not page_ids or page_ids[-1] != sid:
                    page_ids.append(sid)

            if not page_ids:
                # DEBUG: ถ้า status เป็น 200 (ปกติ) แต่หา ID ไม่เจอเลย
                # แปลว่าไม่ใช่โดนบล็อกแบบ HTTP error แต่หน้าเว็บอาจเป็นอย่างอื่น
                # เช่น หน้า captcha, หน้าเปล่า, หรือ LINE เปลี่ยนโครงสร้าง HTML
                # การพิมพ์ status + ความยาว + ตัวอย่างข้อความ ช่วยให้รู้ว่าจริงๆ ได้อะไรกลับมา
                print(f"[DEBUG] หน้า {page}: status={res.status_code}, ความยาว HTML={len(res.text)}")
                print(f"[DEBUG] ตัวอย่าง HTML 300 ตัวแรก: {res.text[:300]}")
                break

            for sid in page_ids:
                if sid in found_ranks and found_ranks[sid] is None:
                    found_ranks[sid] = current_overall_rank
                current_overall_rank += 1

            if all(r is not None for r in found_ranks.values()):
                break

            time.sleep(random.uniform(1.0, 2.5))

        except Exception as e:
            print(f"เกิดข้อผิดพลาดหน้า {page}: {e}")

    return found_ranks


def update_data():
    print("กำลังเริ่มสแครปอันดับสติกเกอร์...")
    ranks = fetch_ranks()

    tz_th = timezone(timedelta(hours=7))
    timestamp = datetime.now(tz_th).strftime("%Y-%m-%d %H:%M")

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

    clean_history = []
    for item in history_data["history"]:
        if any(r is not None for r in item.get("ranks", {}).values()):
            clean_history.append(item)

    history_data["history"] = clean_history

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    update_data()