#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    print("請先執行: pip install -r scripts/requirements.txt")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
SCRIPTS_DIR = Path(__file__).parent
CLIENT_SECRET_FILE = SCRIPTS_DIR / "client_secret.json"
TOKEN_FILE = SCRIPTS_DIR / ".gsc_token.json"
DATA_DIR = SCRIPTS_DIR.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
SITE_URL = "sc-domain:huitong1929.com"


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("更新 token...")
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_FILE.exists():
                print(f"找不到 {CLIENT_SECRET_FILE}")
                print("請將 client_secret.json 放入 scripts/ 目錄")
                sys.exit(1)
            print("開啟瀏覽器進行 Google 授權...")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
        print(f"Token 已儲存：{TOKEN_FILE}")
    return creds


def fetch_performance(service, start_date, end_date, dimensions=None, row_limit=25000):
    if dimensions is None:
        dimensions = ["query", "page"]

    all_rows = []
    start_row = 0
    batch = 25000

    while True:
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": min(batch, row_limit - len(all_rows)),
            "startRow": start_row,
            "dataState": "final",
        }
        response = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
        rows = response.get("rows", [])
        if not rows:
            break
        all_rows.extend(rows)
        if len(all_rows) >= row_limit or len(rows) < batch:
            break
        start_row += len(rows)

    return all_rows


def save_data(rows, start_date, end_date):
    filename = DATA_DIR / f"gsc_{start_date}_{end_date}.json"
    payload = {
        "fetched_at": date.today().isoformat(),
        "site_url": SITE_URL,
        "start_date": start_date,
        "end_date": end_date,
        "row_count": len(rows),
        "rows": rows,
    }
    filename.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已儲存：{filename}（{len(rows)} 筆）")
    return filename


def print_summary(rows):
    rows_sorted = sorted(rows, key=lambda r: r.get("clicks", 0), reverse=True)
    print(f"\n{'關鍵字':<32} {'點擊':>6} {'曝光':>8} {'CTR':>6} {'排名':>6}")
    print("─" * 65)
    for r in rows_sorted[:20]:
        keys = r.get("keys", [])
        kw = (keys[0] if keys else "")[:30]
        print(f"{kw:<32} {r.get('clicks',0):>6} {r.get('impressions',0):>8} "
              f"{r.get('ctr',0)*100:>5.1f}% {r.get('position',0):>6.1f}")


def main():
    parser = argparse.ArgumentParser(description="GSC 資料抓取")
    parser.add_argument("--setup", action="store_true", help="只做授權，不拉資料")
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--start")
    parser.add_argument("--end")
    args = parser.parse_args()

    creds = get_credentials()
    print("授權成功")

    if args.setup:
        return

    service = build("searchconsole", "v1", credentials=creds)

    if args.start and args.end:
        start_date, end_date = args.start, args.end
    else:
        end = date.today() - timedelta(days=3)
        start = end - timedelta(days=args.days)
        start_date, end_date = start.isoformat(), end.isoformat()

    print(f"拉取 {start_date} ～ {end_date}...")
    rows = fetch_performance(service, start_date, end_date)

    if not rows:
        print("沒有資料，請確認 SITE_URL 設定或日期範圍")
        return

    save_data(rows, start_date, end_date)
    print_summary(rows)


if __name__ == "__main__":
    main()
