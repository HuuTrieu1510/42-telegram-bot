import os
import time
import json
import requests

TELEGRAM_TOKEN = "8978048324:AAHqBq0yFuSK-bfE-wYa3R71Jpd5s5AWYFs"
CHAT_ID = "1627350578"
POLL_INTERVAL = 60
STATE_FILE = "last_markets.json"
API_URL = "https://rest.ft.42.space/api/v1/markets"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_state(known):
    with open(STATE_FILE, "w") as f:
        json.dump(list(known), f)

def fetch_markets():
    try:
        r = requests.get(API_URL, params={
            "order": "created_at",
            "ascending": "false",
            "limit": 15
        }, timeout=15)
        data = r.json()
        return data.get("markets", data.get("data", []))
    except Exception as e:
        print("API error:", e)
        return []

def format_msg(m):
    address = m.get("address", "")
    question = m.get("question", "No title")
    status = m.get("status", "").upper()
    created = m.get("createdAt", "")[:19].replace("T", " ")
    volume = m.get("volume", 0)
    cats = ", ".join(m.get("categories", [])) or "N/A"

    return (
        f"🆕 <b>New market on 42!</b>\n\n"
        f"<b>{question}</b>\n\n"
        f"Status: <code>{status}</code>\n"
        f"Created: <code>{created} UTC</code>\n"
        f"Volume: <code>{volume:.1f}</code>\n"
        f"Category: <code>{cats}</code>\n\n"
        f"<code>{address}</code>"
    )

def main():
    print("Bot is running...")
    known = load_state()
    first_run = len(known) == 0

    while True:
        markets = fetch_markets()
        new_ones = []

        for m in markets:
            addr = m.get("address")
            if addr and addr not in known:
                new_ones.append(m)
                known.add(addr)

        if new_ones and not first_run:
            for m in reversed(new_ones):
                send_telegram(format_msg(m))
                print("Sent:", m.get("question")[:50])
                time.sleep(1)

        if new_ones:
            save_state(known)

        first_run = False
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()

