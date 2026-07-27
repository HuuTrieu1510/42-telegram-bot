import os
import time
import json
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POLL_INTERVAL = 30
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
            "limit": 20
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
        f"New market on 42\n\n"
        f"{question}\n\n"
        f"Status: {status}\n"
        f"Created: {created} UTC\n"
        f"Volume: {volume:.1f}\n"
        f"Category: {cats}\n\n"
        f"{address}"
    )

def main():
    print("Bot is running... (notifying new markets every 30s)")
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
