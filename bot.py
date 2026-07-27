import os
import time
import json
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
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
        print("Telegram sent successfully")
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
    print("Bot is running... (TEST MODE - will send latest market once)")
    
    markets = fetch_markets()
    
    if markets:
        latest = markets[0]  # market mới nhất
        print("Sending latest market:", latest.get("question")[:60])
        send_telegram(format_msg(latest))
    else:
        print("No markets found")

    print("Test finished. Bot will now sleep.")
    
    # Giữ bot sống để không bị Railway tắt
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
