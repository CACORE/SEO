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
BLOG_SLUGS = [
    "rice-and-grains",
    "nuts-knowledge",
    "health-lifestyle",
    "kitchen-seasoning-ingredients",
]
OUTPUT = Path(__file__).parent.parent / "data" / "site_meta.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SEO-audit/1.0)"}


def get_article_urls(blog_slug):
    urls = []
    page = 1
    while True:
        url = f"{SITE}/blogs/{blog_slug}?page={page}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            break
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select("a[href*='/blogs/" + blog_slug + "/']")
        found = set()
        for a in links:
            href = a.get("href", "")
            if f"/blogs/{blog_slug}/" in href and href != f"/blogs/{blog_slug}/":
                full = urljoin(SITE, href.split("?")[0])
                found.add(full)
        if not found:
            break
        urls.extend(found)
        page += 1
        time.sleep(0.5)
    return list(set(urls))


def scrape_meta(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
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
    all_urls = []
    for slug in BLOG_SLUGS:
        print(f"掃描 {slug}...")
        urls = get_article_urls(slug)
        print(f"  找到 {len(urls)} 篇")
        all_urls.extend(urls)

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
