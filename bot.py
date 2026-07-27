import os
import time
import json
import requests
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "https://rest.ft.42.space/api/v1/markets"

def to_vn_time(utc_str):
    if not utc_str:
        return "N/A"
    try:
        clean = utc_str[:19].replace("T", " ")
        dt = datetime.strptime(clean, "%Y-%m-%d %H:%M:%S")
        vn = dt + timedelta(hours=7)
        return vn.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return utc_str

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("Telegram status:", r.status_code)
    except Exception as e:
        print("Telegram error:", e)

def fetch_markets():
    try:
        r = requests.get(API_URL, params={
            "order": "created_at",
            "ascending": "false",
            "limit": 5
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
    created = to_vn_time(m.get("createdAt", ""))
    start = to_vn_time(m.get("startDate", ""))
    volume = m.get("volume", 0)
    cats = ", ".join(m.get("categories", [])) or "N/A"

    return (
        f"New market on 42\n\n"
        f"{question}\n\n"
        f"Status: {status}\n"
        f"Created: {created} (VN)\n"
        f"Live luc: {start} (VN)\n"
        f"Volume: {volume:.1f}\n"
        f"Category: {cats}\n\n"
        f"{address}"
    )

def main():
    print("TEST MODE: Sending latest market...")
    markets = fetch_markets()

    if markets:
        latest = markets[0]
        print("Sending:", latest.get("question")[:60])
        send_telegram(format_msg(latest))
        print("Done. Check your Telegram.")
    else:
        print("No markets found")

    # Giữ process sống
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
