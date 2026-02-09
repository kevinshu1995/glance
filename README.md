# Glance Dashboard x Homepage

個人化的 Glance dashboard 配置，整合新聞、市場、天氣、影片訂閱等資訊流，並搭配 [Homepage](https://gethomepage.dev) 作為服務監控面板。支援 GitHub Webhook 自動部署至 Raspberry Pi，搭配 Telegram 通知。

## 專案簡介

這是基於 [Glance](https://github.com/glanceapp/glance) 與 [Homepage](https://gethomepage.dev) 建立的個人儀表板配置，提供：

- **四頁面設計**：Home（資訊匯集）、Start Page（快速啟動頁）、Reddit（社群瀏覽）、Services（服務監控）
- **Homepage 整合**：Services 分頁透過 iframe 嵌入 Homepage，監控自架服務狀態
- **自定義主題**：Tucan 配色方案
- **容器化部署**：Docker Compose 一鍵啟動 Glance + Homepage 雙服務
- **自動部署**：GitHub Webhook + Cloudflare Tunnel + Telegram 通知
- **自定義 Widgets**：Raindrop 書籤管理、每日英文單字

## 架構

```
GitHub push (pi branch)
  → Cloudflare Tunnel
    → webhook-server.py (:5000)
      → deploy.sh → docker compose down / up → health-check.sh
      → Telegram 通知（觸發 / 成功 / 失敗）
```

詳細部署文件請參考：[Webhook Deploy 文件](docs/webhook-deploy.md)

## 自定義 Widgets

### 1. Raindrop Bookmarks Widget

完整的 Raindrop.io 書籤管理 widget，支援三層階層式結構顯示。

**特色功能：**

- 三層階層：Groups → Collections → Sub-collections
- 自訂排序：遵循 Raindrop.io 的群組與收藏夾順序
- 書籤詳情：封面圖片、標題、標籤、建立日期
- 收藏夾色彩：視覺化色彩指示器
- 自動刷新：24 小時快取
- 自動展開選項：可設定預設展開的群組與收藏夾
- 響應式設計：支援桌面到行動裝置的自適應佈局

**配置位置：** `config/widget/raindrop-bookmarks/`

詳細說明請參考：[Raindrop Bookmarks Widget README](config/widget/raindrop-bookmarks/README.md)

### 2. Word of the Day Widget

每日英文單字學習 widget，使用 Wordnik API 提供當日單字、定義、例句與發音日期。

**特色功能：**

- 每日單字與詳細定義
- 多個例句與來源連結
- 快速 Google 搜尋連結
- 顯示單字發音日期

**配置位置：** `config/widget/widget-word-of-the-day.yml`

## 專案結構

```
glance/
├── config/
│   ├── glance.yml              # 主配置檔案
│   ├── page-home.yml           # Home 頁面配置
│   ├── page-start-page.yml     # Start Page 配置
│   ├── page-reddit.yml         # Reddit 頁面配置
│   ├── page-services.yml       # Services 頁面（嵌入 Homepage）
│   └── widget/                 # 自定義 widget
├── homepage/
│   ├── config/                 # Homepage 配置（services, widgets 等）
│   └── data/                   # Homepage 資料
├── assets/
│   ├── user.css                # 自定義 CSS 樣式
│   └── wallpapers/             # 背景桌布
├── scripts/
│   ├── deploy.sh               # 自動部署腳本
│   ├── build-all.sh            # 全量建構腳本
│   └── health-check.sh         # 健康檢查腳本
├── docs/
│   └── webhook-deploy.md       # Webhook 部署詳細文件
├── webhook-server.py           # GitHub Webhook 接收伺服器
├── docker-compose.yml          # Docker Compose 配置（Glance + Homepage）
├── .env.example                # 環境變數範例
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

編輯 `.env` 檔案，填入必要的設定值：

```env
# Glance Widgets
WORDNIK_API_KEY=your_wordnik_api_key_here
RAINDROP_TOKEN=your_raindrop_token_here

# Homepage
HOMEPAGE_URL=http://homepage:3000

# 自動部署（選用）
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
GITHUB_WEBHOOK_SECRET=your_webhook_secret
DEPLOY_BRANCH=pi
```

完整的環境變數列表請參考 `.env.example`。

**取得 API Keys：**

- **Wordnik API Key**:
    1. 前往 [Wordnik Developer](https://developer.wordnik.com/)
    2. 註冊帳號並申請 API key

- **Raindrop Token**:
    1. 前往 [Raindrop.io Settings - Integrations](https://app.raindrop.io/settings/integrations)
    2. 建立新 app 或使用既有 app
    3. 生成測試 token

3. **啟動服務**

```bash
docker-compose up -d
```

4. **存取 Dashboard**

| 服務 | 網址 | 說明 |
|------|------|------|
| Homepage | `http://localhost:8080` | 服務監控面板 |
| Glance | `http://localhost:8081` | 主儀表板 |

## 頁面說明

### Home 頁面

資訊匯集頁面，整合各類即時資訊流：

- **左欄**：行事曆、Twitch 頻道、全球與台灣市場
- **中欄**：Hacker News、新聞 RSS（公視、中央社、報導者、BBC）、英文新聞、遊戲新聞、技術文章、YouTube 影片
- 快取時間：10 分鐘

### Start Page 頁面

快速啟動頁面，專注於搜尋與書籤管理：

- **左欄**：天氣、每日單字
- **中欄**：Google 搜尋（支援 bangs）、Raindrop 書籤
- **右欄**：時鐘（多時區）、行事曆

### Reddit 頁面

Reddit 社群瀏覽，匯集多個 subreddit：

- Frontend、apexlegends、SonyAlpha、Steam、badminton
- 支援縮圖預覽與 flair 標籤

### Services 頁面

透過 iframe 嵌入 [Homepage](https://gethomepage.dev) 服務監控面板，包含：

- **行事曆**：iCal 整合（月曆與議程視圖）
- **Self Hosted 服務**：Uptime Kuma、AdGuard Home、Speedtest Tracker、Tailscale、Nginx Proxy Manager
- **網路設備**：路由器、WiFi Router

Homepage 配置位於 `homepage/config/`，詳細說明請參考 [Homepage README](homepage/README.md)。

## 自動部署

支援透過 GitHub Webhook 自動部署至 Raspberry Pi：

1. Push 到 `pi` branch 觸發 GitHub Webhook
2. Cloudflare Tunnel 將請求轉發至 Pi 上的 `webhook-server.py`
3. 驗證 HMAC-SHA256 簽名後執行 `deploy.sh`
4. 部署結果透過 Telegram Bot 通知

詳細設定步驟請參考：[Webhook Deploy 文件](docs/webhook-deploy.md)

## 主題配色

### 當前主題：Tucan

```yaml
background-color: 10 10 10
primary-color: 24 97 58
negative-color: 56.8 58.2 1
```

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

### 更新服務

```bash
docker-compose pull
docker-compose up -d
```

### 查看 logs

```bash
# Glance
docker-compose logs -f glance

# Homepage
docker-compose logs -f homepage
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
- [Homepage 官方文件](https://gethomepage.dev)
- [Community Widgets](https://github.com/glanceapp/community-widgets)
- [Raindrop.io API](https://developer.raindrop.io)
- [Wordnik API](https://developer.wordnik.com/)
