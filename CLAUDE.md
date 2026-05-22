# SEO 專案

網站：huitong1929.com（惠通行）
GSC：sc-domain:huitong1929.com

## 工作流程

每次進入專案，依序執行：

1. `/fetch` — 拉最新 GSC 資料
2. `/analyze` — 分析機會，產出優先清單
3. `/act` — 依優先清單執行：改 meta、寫文章、或更新現有內容

## 指令

### /fetch
```
python scripts/fetch_gsc_data.py --days 90
```
資料存入 `data/gsc_<start>_<end>.json`

### /analyze
```
python scripts/analyze.py
```
讀取 `data/` 最新一份 GSC 資料，輸出三份清單：
- **A 類**：高曝光低 CTR（title/meta 問題，立刻可改）
- **B 類**：排名 6-15（再推一把就上第一頁）
- **C 類**：新文章機會（有搜尋量但現在沒頁面承接）

報告存入 `reports/analysis_<date>.md`

### /act
讀取最新 `reports/analysis_<date>.md`，從 A 類開始：
- 針對每個 A 類項目，給出具體的 title 和 meta description 修改建議
- 針對每個 C 類項目，產出完整文章草稿

## 資料說明

- GSC 資料延遲 2-3 天
- 每次 /fetch 會覆蓋 data/ 中同日期範圍的檔案
- 維度：query + page（可看每個關鍵字對應到哪個頁面）
