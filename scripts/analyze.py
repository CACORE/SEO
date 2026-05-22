#!/usr/bin/env python3
import json
import sys
from datetime import date
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_DIR = Path(__file__).parent.parent / "data"
REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# 每個頁面取點擊最高的關鍵字代表
MIN_IMPRESSIONS_A = 2000   # A 類：高曝光低 CTR
MAX_CTR_A = 0.03
MIN_IMPRESSIONS_B = 500    # B 類：排名 6-15
MIN_IMPRESSIONS_C = 800    # C 類：新機會（搜尋量夠但排名差）
MAX_POSITION_B = 15
MIN_POSITION_B = 6
MIN_POSITION_C = 15


def load_latest():
    files = sorted(DATA_DIR.glob("gsc_*.json"))
    if not files:
        print("找不到資料，請先執行 /fetch")
        sys.exit(1)
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


def aggregate_by_query(rows):
    """每個關鍵字加總所有頁面的 clicks/impressions"""
    agg = {}
    for r in rows:
        keys = r.get("keys", [])
        if not keys:
            continue
        query = keys[0]
        page = keys[1] if len(keys) > 1 else ""
        clicks = r.get("clicks", 0)
        impressions = r.get("impressions", 0)
        ctr = r.get("ctr", 0)
        position = r.get("position", 0)

        if query not in agg or clicks > agg[query]["clicks"]:
            agg[query] = {
                "query": query,
                "page": page,
                "clicks": clicks,
                "impressions": impressions,
                "ctr": ctr,
                "position": position,
            }
    return list(agg.values())


def classify(items):
    a, b, c = [], [], []
    for item in items:
        imp = item["impressions"]
        ctr = item["ctr"]
        pos = item["position"]

        if imp >= MIN_IMPRESSIONS_A and ctr <= MAX_CTR_A:
            a.append(item)
        elif imp >= MIN_IMPRESSIONS_B and MIN_POSITION_B <= pos <= MAX_POSITION_B:
            b.append(item)
        elif imp >= MIN_IMPRESSIONS_C and pos > MIN_POSITION_C:
            c.append(item)

    a.sort(key=lambda x: x["impressions"], reverse=True)
    b.sort(key=lambda x: x["impressions"], reverse=True)
    c.sort(key=lambda x: x["impressions"], reverse=True)
    return a, b, c


def fmt_row(item):
    kw = item["query"][:28]
    return (f"| {kw:<28} | {item['impressions']:>7,} | {item['clicks']:>6} "
            f"| {item['ctr']*100:>5.1f}% | {item['position']:>5.1f} | {item['page'][:50]} |")


def render_table(items):
    header = "| 關鍵字                       |    曝光 |   點擊 |   CTR |  排名 | 頁面                                               |"
    sep    = "|------------------------------|---------|--------|-------|-------|-----------------------------------------------------|"
    rows = [fmt_row(i) for i in items[:30]]
    return "\n".join([header, sep] + rows)


def main():
    data = load_latest()
    rows = data["rows"]
    period = f"{data['start_date']} ～ {data['end_date']}"
    print(f"分析期間：{period}（{len(rows)} 筆）")

    items = aggregate_by_query(rows)
    a, b, c = classify(items)

    report_date = date.today().isoformat()
    report_path = REPORTS_DIR / f"analysis_{report_date}.md"

    report = f"""# SEO 分析報告 {report_date}

期間：{period} ｜ 總筆數：{len(rows):,}

---

## A 類：高曝光低 CTR（title/meta 立刻可改）

> 曝光 >{MIN_IMPRESSIONS_A:,}、CTR <{MAX_CTR_A*100:.0f}%

{render_table(a)}

---

## B 類：排名 {MIN_POSITION_B}-{MAX_POSITION_B}（再推一把進第一頁）

> 曝光 >{MIN_IMPRESSIONS_B:,}、排名 {MIN_POSITION_B}-{MAX_POSITION_B}

{render_table(b)}

---

## C 類：新文章機會（有量但沒有好頁面承接）

> 曝光 >{MIN_IMPRESSIONS_C:,}、排名 >{MIN_POSITION_C}

{render_table(c)}
"""

    report_path.write_text(report, encoding="utf-8")
    print(f"\nA 類 {len(a)} 項 ｜ B 類 {len(b)} 項 ｜ C 類 {len(c)} 項")
    print(f"報告：{report_path}")
    print("\n下一步：/act")


if __name__ == "__main__":
    main()
