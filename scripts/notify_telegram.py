"""
notify_telegram.py - 傳送 Telegram 通知
用法：python scripts/notify_telegram.py "訊息內容"
token 統一放在 weekly_monitor 的 .env，這裡不寫死（避免外流）
"""
import sys
from pathlib import Path

import requests

ENV_FILE = Path(r"C:\Users\HT-01\Desktop\AI agent\weekly_monitor\.env")

def load_env(path: Path) -> dict:
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env

_env = load_env(ENV_FILE)
BOT_TOKEN = _env.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID   = _env.get("TELEGRAM_CHAT_ID", "")

if not BOT_TOKEN or not CHAT_ID:
    sys.exit(f"讀不到 Telegram 設定，請確認 {ENV_FILE} 裡有 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID")

def send(text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=15)
    resp.raise_for_status()
    return True

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "SEO 專案通知"
    send(msg)
    print("Telegram 發送成功")
