import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

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
    except Exception as e:
        print("Lỗi gửi Telegram:", e)

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
        print("Lỗi API:", e)
        return []

def format_msg(m):
    address = m.get("address", "")
    question = m.get("question", "No title")
    status = m.get("status", "").upper()
    created = m.get("createdAt", "")[:19].replace("T", " ")
    volume = m.get("volume", 0)
    cats = ", ".join(m.get("categories", [])) or "N/A"

    return (
        f"🆕 <b>Market mới trên 42!</b>\n\n"
        f"<b>{question}</b>\n\n"
        f"Status: <code>{status}</code>\n"
        f"Created: <code>{created} UTC</code>\n"
        f"Volume: <code>{volume:.1f}</code>\n"
        f"Category: <code>{cats}</code>\n\n"
        f"<code>{address}</code>"
    )

def main():
    print("Bot đang chạy... (đ
