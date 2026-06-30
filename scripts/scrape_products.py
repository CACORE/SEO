#!/usr/bin/env python3
import requests
import sys
import time
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}

PRODUCTS = [
    ("西谷米", 5271, "https://www.huitong1929.com/products/%E8%A5%BF%E8%B0%B7%E7%B1%B3-%E8%A5%BF%E7%B1%B3%E9%9C%B2-300g-%E6%B3%B0%E5%9C%8B"),
    ("麵茶粉", 3970, "https://www.huitong1929.com/products/%E7%94%A2%E5%93%81-%E5%8F%A4%E6%97%A9%E5%91%B3%E9%BA%B5%E8%8C%B6%E7%B2%89-300g"),
    ("味露魚露", 921, "https://www.huitong1929.com/products/-%E5%91%B3%E9%9C%B2%E7%89%8C%E9%AD%9A%E9%9C%B2-%E6%B3%B0%E5%9C%8B%E9%80%B2%E5%8F%A3%E6%9D%B1%E5%8D%97%E4%BA%9E%E8%AA%BF%E5%91%B3%E6%96%99-700ml"),
    ("迪化街堅果", 832, "https://www.huitong1929.com/products/dihua-street-roasted-nuts-mixed"),
    ("黑米糙米", 770, "https://www.huitong1929.com/products/taiwan-low-gi-black-brown-rice-600g"),
    ("山核桃", 682, "https://www.huitong1929.com/products/original-roasted-pecans"),
    ("玉米碎", 624, "https://www.huitong1929.com/products/%E7%8E%89%E7%B1%B3%E7%A2%8E-600g-%E7%B4%94%E7%8E%89%E7%B1%B3%E7%A0%94%E7%A3%A8-%E7%94%A2%E5%9C%B0%E7%BE%8E%E5%9C%8B"),
    ("泰國長米", 595, "https://www.huitong1929.com/products/-%E6%B3%B0%E5%9C%8B%E7%89%B9a%E7%B4%9A%E9%A6%99%E7%B1%B3-%E7%9C%9F%E7%A9%BA%E9%95%B7%E7%B1%B3-600g"),
    ("長糙米", 592, "https://www.huitong1929.com/products/%E5%9C%A8%E4%BE%86%E7%B3%99%E7%B1%B3-%E9%95%B7%E7%B3%AF%E7%B1%B3-600g-%E7%94%A2%E5%9C%B0%E5%8F%B0%E7%81%A3%E8%A5%BF%E8%9E%BA"),
    ("白高粱", 545, "https://www.huitong1929.com/products/%E5%8D%B0%E5%BA%A6-%E7%99%BD%E9%AB%98%E7%B2%B1-600g-%E9%AB%98%E7%B2%B1%E7%B1%B3"),
    ("三色糙米", 512, "https://www.huitong1929.com/products/taiwan-tri-color-brown-rice"),
    ("澳洲麥片", 479, "https://www.huitong1929.com/products/%E5%A4%A7%E9%BA%A5%E7%89%87-600g-%E9%BA%A5%E8%A7%92-%E6%BE%B3%E6%B4%B2"),
    ("紅扁豆", 478, "https://www.huitong1929.com/products/-%E6%BE%B3%E6%B4%B2%E7%B4%85%E6%89%81%E8%B1%86-%E9%AB%98%E8%9B%8B%E7%99%BD%E9%A4%8A%E7%94%9F%E7%A9%80%E7%89%A9-600g"),
    ("眉豆", 429, "https://www.huitong1929.com/products/%E7%B1%B3%E8%B1%86-%E7%9C%89%E8%B1%86-%E9%BB%91%E7%9C%BC%E8%B1%86-600g-%E7%94%A2%E5%9C%B0%E7%B7%AC%E5%9C%B8"),
]


def scrape(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("title")
    meta = soup.find("meta", attrs={"name": "description"})
    h1 = soup.find("h1")
    return {
        "title": title.get_text(strip=True) if title else "",
        "meta": meta["content"] if meta and meta.get("content") else "",
        "h1": h1.get_text(strip=True) if h1 else "",
    }


for name, imp, url in PRODUCTS:
    try:
        d = scrape(url)
        print("=" * 60)
        print(f"[{name}] 曝光:{imp}")
        print(f"TITLE: {d['title']}")
        print(f"META : {d['meta']}")
        print(f"H1   : {d['h1']}")
        time.sleep(0.5)
    except Exception as e:
        print(f"[{name}] ERROR: {e}")
