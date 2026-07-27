import os
import time
import json
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POLL_INTERVAL = 60
STATE_FILE = "notified_markets.json"
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
            "limit": 50
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
    start = m.get("startDate", "")[:19].replace("T", " ") if m.get("startDate") else "N/A"
    volume = m.get("volume", 0)
    cats = ", ".join(m.get("categories", [])) or "N/A"

    return (
        f"Market chua live tren 42\n\n"
        f"{question}\n\n"
        f"Status: {status}\n"
        f"Created: {created} UTC\n"
        f"Start: {start} UTC\n"
        f"Volume: {volume:.1f}\n"
        f"Category: {cats}\n\n"
        f"{address}"
    )

def main():
    print("Bot is running... (notifying not_started markets)")
    known = load_state()

    while True:
        markets = fetch_markets()
        new_ones = []

        for m in markets:
            addr = m.get("address")
            status = m.get("status", "").lower()

            if addr and status == "not_started" and addr not in known:
                new_ones.append(m)
                known.add(addr)

        if new_ones:
            for m in reversed(new_ones):
                send_telegram(format_msg(m))
                print("Sent not_started:", m.get("question")[:50])
                time.sleep(1)
            save_state(known)

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
