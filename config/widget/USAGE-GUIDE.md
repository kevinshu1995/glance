# Raindrop Bookmarks Widget - 使用指南

## 📁 檔案說明

此目錄包含 Raindrop Bookmarks Widget 的完整配置與文件：

- `widget-raindrop-bookmarks.yml` - Widget 主要配置檔案
- `raindrop-bookmarks-README.md` - 完整的使用說明文件
- `raindrop-bookmarks-meta.yml` - Widget 的中繼資料
- `USAGE-GUIDE.md` - 本檔案，使用指南

## 🚀 快速開始

### 1. 取得 Raindrop API Token

1. 前往 [Raindrop.io Settings - Integrations](https://app.raindrop.io/settings/integrations)
2. 點擊「Create new app」或使用現有的應用程式
3. 生成 Test Token
4. 複製 Token

### 2. 設定環境變數

將 Token 設定為環境變數：

**Linux/macOS:**
```bash
export RAINDROP_TOKEN="your_token_here"
```

**Docker Compose:**
```yaml
environment:
  - RAINDROP_TOKEN=your_token_here
```

**Docker Run:**
```bash
docker run -e RAINDROP_TOKEN="your_token_here" ...
```

### 3. 在 Glance 配置中引用 Widget

在你的 `glance.yml` 中：

```yaml
pages:
  - name: Home
    columns:
      - size: full
        widgets:
          - path: config/widget/widget-raindrop-bookmarks.yml
```

或者直接複製整個 widget 配置到你的 `glance.yml` 中。

### 4. 重新啟動 Glance

```bash
# 如果使用 Docker Compose
docker-compose restart

# 如果使用 Docker
docker restart glance

# 如果直接執行
# 重新啟動 Glance 服務
```

## 📊 Widget 功能

- ✅ 顯示所有 Collections（包含子 Collections）
- ✅ 顯示最近 50 筆書籤
- ✅ 顯示封面圖片、標題、標籤、日期
- ✅ 點擊書籤在新分頁開啟
- ✅ Collection 顏色標識
- ✅ 資料夾圖示提示可展開項目
- ✅ Hover 顯示限制提示
- ✅ Token 過期自動引導至設定頁

## 🎨 自訂設定

### 調整快取時間

預設為 24 小時，可修改 `cache` 參數：

```yaml
cache: 12h  # 12 小時
cache: 30m  # 30 分鐘
cache: 1w   # 1 週
```

### 修改標題

```yaml
title: 🔖 我的書籤
title: 📚 閱讀清單
```

### 移除標題連結

如果不想點擊標題跳轉到 Raindrop，移除這行：

```yaml
title-url: https://app.raindrop.io/
```

## 🐛 故障排除

### 問題：無法載入資料

**解決方案：**
1. 檢查 `RAINDROP_TOKEN` 環境變數是否正確設定
2. 確認 Token 未過期
3. 檢查網路連線
4. 查看 Widget 顯示的 API 回應狀態碼

### 問題：Token 過期

**解決方案：**
1. Widget 會自動顯示連結至設定頁
2. 點擊連結前往 [Raindrop 設定](https://app.raindrop.io/settings/integrations)
3. 生成新的 Token
4. 更新環境變數
5. 重新啟動 Glance

### 問題：只顯示部分書籤

**說明：**
這是 Raindrop API 的限制，每次只能取得 50 筆資料。Widget 會顯示最近新增的 50 筆書籤。

**解決方案：**
如需查看完整列表，請點擊 Widget 標題或底部連結前往 Raindrop.io。

### 問題：Collection 無法展開

**解決方案：**
1. 確認你點擊的是 Collection 名稱或資料夾圖示
2. 某些 Collection 可能在最近 50 筆中沒有書籤
3. 嘗試刷新頁面（會清除快取並重新抓取資料）

## 📤 分享到 Community Widgets

如果你想將此 Widget 分享到 Glance Community Widgets：

### 1. 準備檔案

需要以下檔案：
- `README.md` - 將 `raindrop-bookmarks-README.md` 重新命名
- `meta.yml` - 將 `raindrop-bookmarks-meta.yml` 重新命名並修改 `author` 為你的 GitHub username
- `preview.png` - Widget 的截圖

### 2. 建立目錄結構

```
widgets/raindrop-bookmarks/
├── README.md
├── meta.yml
└── preview.png
```

### 3. 提交 Pull Request

1. Fork [glanceapp/community-widgets](https://github.com/glanceapp/community-widgets)
2. 建立上述目錄結構
3. 提交 Pull Request

詳細步驟請參考 [Community Widgets Contributing Guide](https://github.com/glanceapp/community-widgets/blob/main/CONTRIBUTING.md)

## 📝 版本資訊

- **版本：** 1.0.0
- **最後更新：** 2025-11-19
- **Glance 版本：** >= 0.6.0
- **API 版本：** Raindrop.io API v1

## 🔗 相關連結

- [Raindrop.io](https://raindrop.io/)
- [Raindrop API 文件](https://developer.raindrop.io/)
- [Glance 官方文件](https://github.com/glanceapp/glance)
- [Glance Community Widgets](https://github.com/glanceapp/community-widgets)

## 💡 提示

- Widget 在 hover 時會顯示「僅顯示最近 50 筆書籤」提示
- 點擊 Widget 標題可快速開啟 Raindrop.io
- Collection 和書籤都可以展開/收合
- 已訪問的書籤會改變顏色（透過 `color-primary-if-not-visited` class）

## 📧 回饋

如有問題或建議，請至 [Glance Issues](https://github.com/glanceapp/glance/issues) 或 [Community Widgets Issues](https://github.com/glanceapp/community-widgets/issues) 回報。
