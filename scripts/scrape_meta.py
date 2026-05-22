#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("請先執行: pip install requests beautifulsoup4")
    sys.exit(1)

SITE = "https://www.huitong1929.com"
OUTPUT = Path(__file__).parent.parent / "data" / "site_meta.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}

# 已知文章 URL（從部落格首頁抓到的）
KNOWN_URLS = [
    "/blogs/rice-and-grains/how-to-cook-chickpeas-guide",
    "/blogs/rice-and-grains/rice-weevils-handling-storage",
    "/blogs/rice-and-grains/black-rice-vs-purple-rice-difference",
    "/blogs/rice-and-grains/what-is-resistant-starch-benefits-foods",
    "/blogs/rice-and-grains/how-to-cook-rice-water-ratio",
    "/blogs/rice-and-grains/high-protein-beans-vs-starch-beans",
    "/blogs/rice-and-grains/五穀米推薦-選購指南",
    "/blogs/rice-and-grains/whole-grains-complete-guide",
    "/blogs/rice-and-grains/惠通行-燕麥片-健康早餐-10分鐘",
    "/blogs/kitchen-seasoning-ingredients/cooking-oil-smoke-point-guide",
    "/blogs/kitchen-seasoning-ingredients/light-vs-dark-soy-sauce-difference-guide",
]


def get_all_urls():
    return [SITE + path for path in KNOWN_URLS]


def scrape_meta(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("title")
        meta = soup.find("meta", attrs={"name": "description"})
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        return {
            "url": url,
            "title": title.get_text(strip=True) if title else "",
            "meta_description": meta["content"] if meta and meta.get("content") else "",
            "og_description": og_desc["content"] if og_desc and og_desc.get("content") else "",
        }
    except Exception as e:
        return {"url": url, "title": "", "meta_description": "", "og_description": "", "error": str(e)}


def main():
    all_urls = get_all_urls()
    print(f"共 {len(all_urls)} 篇文章")

    print(f"\n共 {len(all_urls)} 篇，開始抓 meta...")
    results = []
    for i, url in enumerate(all_urls, 1):
        print(f"  [{i}/{len(all_urls)}] {url}")
        data = scrape_meta(url)
        results.append(data)
        time.sleep(0.3)

    OUTPUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n完成，存入：{OUTPUT}")

    print("\n--- 結果摘要 ---")
    print(f"{'URL':<60} {'有Meta':^6} {'有OG':^6}")
    print("─" * 75)
    for r in results:
        has_meta = "✓" if r["meta_description"] else "✗"
        has_og = "✓" if r["og_description"] else "✗"
        short_url = r["url"].replace(SITE, "")[:58]
        print(f"{short_url:<60} {has_meta:^6} {has_og:^6}")


if __name__ == "__main__":
    main()
