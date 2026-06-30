# Schema 審查報告 — huitong1929.com
**審查日期：** 2026-06-17

---

## 偵測結果

| 頁面類型 | 頁面範例 | JSON-LD | Microdata | RDFa | 狀態 |
|----------|----------|---------|-----------|------|------|
| 首頁 | / | ❌ | ❌ | ❌ | 完全缺失 |
| 產品頁 | /products/family-healthy-ten-grains-rice | ❌ | ❌ | ❌ | 完全缺失 |
| 文章頁 | /blogs/.../cooking-oil-smoke-point-guide | ❌ | ❌ | ❌ | 完全缺失 |
| 關於頁 | /pages/about-us | ❌ | ❌ | ❌ | 完全缺失 |

**結論：全站零 schema markup，是最高優先修復項。**

---

## 修復優先順序

### 優先級 1 — 產品頁 Product Schema（富結果直接影響購買轉換）
- 70 個產品頁全部缺失
- 補上後可出現 Google 購物富結果（價格、庫存狀態）
- 見 `generated-schema.json` → `product_template`

### 優先級 2 — 首頁 Organization + WebSite Schema
- 建立品牌實體，讓 Google 的知識圖譜認識「惠通行」
- WebSite schema 啟用 Sitelinks Searchbox
- 見 `generated-schema.json` → `homepage`

### 優先級 3 — 文章頁 Article Schema（E-E-A-T 信號）
- 31 篇文章全部缺失
- Article schema 讓 Google 確認作者、發布日期，強化 E-E-A-T
- 見 `generated-schema.json` → `article_template`

### 優先級 4 — BreadcrumbList（全站導覽結構）
- 產品頁和文章頁都有明確的麵包屑路徑，但未用 schema 標記
- 見 `generated-schema.json` → `breadcrumb_product` / `breadcrumb_article`

---

## EasyStore 實作方式

1. 後台 → **主題** → **編輯程式碼**
2. 找到 `theme.liquid`（全站 layout）
3. 在 `</head>` 標籤前插入：
   - 首頁 schema（用 `{% if template == 'index' %}` 包住）
   - 產品頁 schema（用 `{% if template == 'product' %}` 包住）
   - 文章頁 schema（用 `{% if template == 'article' %}` 包住）
4. 或分別在 `product.liquid`、`article.liquid` 各自插入

### 注意
- EasyStore Liquid 變數名稱請參照平台文件確認（尤其 `product.price` 單位可能是分而非元）
- `generated-schema.json` 中提供兩個版本：靜態範例（可直接測試）和 Liquid 模板
