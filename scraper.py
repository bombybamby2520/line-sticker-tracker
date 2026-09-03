import json
import random
import re
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
    {"id": "35522153", "name": "คะน้า:สโลวไลฟ์"},
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

STICKER_ID_PATTERN = re.compile(r"/stickershop/product/(\d+)")


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
                print(
                    f"Page {page} HTTP Error: {res.status_code}",
                    flush=True,
                )
                continue

            matches = STICKER_ID_PATTERN.findall(res.text)
            page_ids = []
            for sid in matches:
                if not page_ids or page_ids[-1] != sid:
                    page_ids.append(sid)

            if not page_ids:
                print(
                    f"[DEBUG] Page {page}: status={res.status_code}, HTML length={len(res.text)}",
                    flush=True,
                )
                break

            for sid in page_ids:
                if sid in found_ranks and found_ranks[sid] is None:
                    found_ranks[sid] = current_overall_rank
                current_overall_rank += 1

            if all(r is not None for r in found_ranks.values()):
                break

            time.sleep(random.uniform(1.0, 2.5))

        except Exception as e:
            print(f"Error on page {page}: {e}", flush=True)

    return found_ranks


def update_data():
    print("Fetching rankings from LINE Store...", flush=True)

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
        history_data["history"].append({"timestamp": timestamp, "ranks": ranks})
        print(f"Successfully updated data ({timestamp})", flush=True)
    else:
        print("No ranks found in this round (skipped saving)", flush=True)

    clean_history = []
    for item in history_data["history"]:
        if any(r is not None for r in item.get("ranks", {}).values()):
            clean_history.append(item)

    history_data["history"] = clean_history

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    update_data()