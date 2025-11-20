# Glance Dashboard

個人化的 Glance dashboard 配置，整合新聞、市場、天氣、影片訂閱等資訊流，並包含自定義的書籤管理與每日英文單字學習功能。

## 專案簡介

這是基於 [Glance](https://github.com/glanceapp/glance) 建立的個人儀表板配置，提供：

- **雙頁面設計**：Home（資訊匯集）與 Start Page（快速啟動頁）
- **自定義主題**：Tucan 配色與 Gruvbox Dark、Zebra 預設主題
- **容器化部署**：使用 Docker Compose 快速啟動
- **自定義 Widgets**：擴展功能以滿足個人需求

## 自定義 Widgets

### 1. Raindrop Bookmarks Widget

完整的 Raindrop.io 書籤管理 widget，支援三層階層式結構顯示。

**特色功能：**
- 📁 三層階層：Groups → Collections → Sub-collections
- 🗂️ 自訂排序：遵循 Raindrop.io 的群組與收藏夾順序
- 🔖 書籤詳情：封面圖片、標題、標籤、建立日期
- 🎨 收藏夾色彩：視覺化色彩指示器
- 🔄 自動刷新：24 小時快取
- ✨ 自動展開選項：可設定預設展開的群組與收藏夾
- 📱 響應式設計：支援桌面到行動裝置的自適應佈局

**配置位置：** `config/widget/raindrop-bookmarks/`

詳細說明請參考：[Raindrop Bookmarks Widget README](config/widget/raindrop-bookmarks/README.md)

### 2. Word of the Day Widget

每日英文單字學習 widget，使用 Wordnik API 提供當日單字、定義、例句與發音日期。

**特色功能：**
- 📖 每日單字與詳細定義
- 💬 多個例句與來源連結
- 🔍 快速 Google 搜尋連結
- 📅 顯示單字發音日期

**配置位置：** `config/widget/widget-word-of-the-day.yml`

## 專案結構

```
glance/
├── config/
│   ├── glance.yml              # 主配置檔案
│   ├── page-home.yml           # Home 頁面配置
│   ├── page-start-page.yml     # Start Page 配置
│   └── widget/
│       ├── raindrop-bookmarks/ # Raindrop 書籤 widget
│       │   ├── raindrop-bookmarks.yml
│       │   ├── README.md
│       │   ├── meta.yml
│       │   └── preview*.png
│       └── widget-word-of-the-day.yml  # 每日單字 widget
├── assets/
│   └── user.css                # 自定義 CSS 樣式
├── docker-compose.yml          # Docker Compose 配置
├── glance.Dockerfile           # Glance 映像檔建構
├── .env.example                # 環境變數範例
├── .gitignore
└── CLAUDE.md                   # 開發指南
```

## 快速開始

### 前置需求

- Docker
- Docker Compose

### 安裝步驟

1. **複製專案**

```bash
git clone <repository-url>
cd glance
```

2. **設定環境變數**

複製 `.env.example` 並重新命名為 `.env`：

```bash
cp .env.example .env
```

編輯 `.env` 檔案，填入必要的 API tokens：

```env
WORDNIK_API_KEY=your_wordnik_api_key_here
RAINDROP_TOKEN=your_raindrop_token_here
```

**取得 API Keys：**

- **Wordnik API Key**:
  1. 前往 [Wordnik Developer](https://developer.wordnik.com/)
  2. 註冊帳號並申請 API key

- **Raindrop Token**:
  1. 前往 [Raindrop.io Settings - Integrations](https://app.raindrop.io/settings/integrations)
  2. 建立新 app 或使用既有 app
  3. 生成測試 token

3. **建構 Docker 映像**

```bash
docker build -f glance.Dockerfile -t glance-local:latest .
```

4. **啟動服務**

```bash
docker-compose up -d
```

5. **存取 Dashboard**

開啟瀏覽器前往：`http://localhost:8080`

## 頁面說明

### Home 頁面

資訊匯集頁面，整合各類即時資訊流：

- **左欄**：行事曆、待辦事項、Twitch 頻道、伺服器狀態
- **中欄**：Hacker News、新聞 RSS（公視、中央社、報導者、BBC）、遊戲新聞、技術文章
- **右欄**：天氣、每日單字、全球與台灣市場

### Start Page 頁面

快速啟動頁面，專注於搜尋與書籤管理：

- **左欄**：每日單字
- **中欄**：Google 搜尋（支援 bangs）、Raindrop 書籤
- **右欄**：時鐘（多時區）、行事曆、天氣

## 主題配色

### 當前主題：Tucan

```yaml
background-color: 50 1 6
primary-color: 24 97 58
negative-color: 56.8 58.2 1
```

### 可用預設主題

- **Gruvbox Dark**：深色暖調主題
- **Zebra**：明亮對比主題

切換主題方式：修改 `config/glance.yml` 中的 `theme` 區段。

## 開發與自訂

### 修改配置

所有配置檔案位於 `config/` 目錄，修改後需重新啟動容器：

```bash
docker-compose restart
```

### 自訂 CSS

自訂樣式可加入 `assets/user.css`，並在 `config/glance.yml` 中引用：

```yaml
theme:
  custom-css-file: /assets/user.css
```

### 開發自定義 Widget

開發 `custom-api` widget 時，請參考：

- [Glance 官方文件](https://github.com/glanceapp/glance/blob/main/docs/configuration.md)
- [Custom API Widget 文件](https://github.com/glanceapp/glance/blob/main/docs/custom-api.md)
- [Community Widgets 貢獻指南](https://github.com/glanceapp/community-widgets/blob/main/CONTRIBUTING.md)
- 本專案的 `CLAUDE.md`（開發筆記與規範）

## 維護

### 更新 Glance 版本

```bash
# 重新建構映像
docker build -f glance.Dockerfile -t glance-local:latest .

# 重啟服務
docker-compose up -d
```

### 查看 logs

```bash
docker-compose logs -f glance
```

### 停止服務

```bash
docker-compose down
```

## 授權

本專案配置檔案遵循 MIT License。

Glance 本身的授權請參考：[Glance Repository](https://github.com/glanceapp/glance)

## 相關資源

- [Glance 官方儲存庫](https://github.com/glanceapp/glance)
- [Glance 配置文件](https://github.com/glanceapp/glance/blob/main/docs/configuration.md)
- [Community Widgets](https://github.com/glanceapp/community-widgets)
- [Raindrop.io API](https://developer.raindrop.io)
- [Wordnik API](https://developer.wordnik.com/)
