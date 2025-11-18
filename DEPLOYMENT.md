# Glance 部署指南

本專案支援兩種運行模式：**本地開發**（docker-compose）和**生產部署**（Dockerfile）。

## 📦 專案結構

```
.
├── Dockerfile           # 生產環境映像定義
├── docker-compose.yml   # 本地開發配置
├── .env                 # 環境變數（不會被加入版本控制）
├── config/              # Glance 配置檔案
│   ├── glance.yml
│   └── home.yml
└── assets/              # 自定義樣式資源
    └── user.css
```

---

## 🛠️ 本地開發模式（推薦）

### 啟動服務

```bash
# 構建並啟動（首次運行或 Dockerfile 變更後）
docker-compose up --build

# 背景運行
docker-compose up -d

# 查看日誌
docker-compose logs -f glance
```

### 停止服務

```bash
docker-compose down
```

### 特點

- ✅ 配置檔案即時生效（透過 volume 掛載）
- ✅ 環境變數自動從 `.env` 載入
- ✅ 使用本地 Dockerfile 構建，確保與生產環境一致
- ✅ 可隨時修改 `config/` 和 `assets/` 目錄內容

---

## 🚀 生產環境部署

### 方案 A：直接使用 Dockerfile（配置透過 Volume 掛載）

適合需要動態調整配置的場景。

```bash
# 1. 構建映像
docker build -t glance-prod .

# 2. 運行容器（掛載配置）
docker run -d \
  --name glance \
  --restart unless-stopped \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/assets:/app/assets \
  -v /etc/localtime:/etc/localtime:ro \
  -p 8080:8080 \
  --env-file .env \
  glance-prod
```

### 方案 B：配置打包進映像（完全自包含）

適合固定配置的部署（例如 Render、Fly.io 等平台）。

```bash
# 1. 修改 Dockerfile，取消以下兩行的註解：
#    COPY config/ /app/config/
#    COPY assets/ /app/assets/

# 2. 構建映像（傳入環境變數）
docker build \
  --build-arg MY_SECRET_TOKEN=your_token \
  --build-arg WORDNIK_API_KEY=your_key \
  -t glance-prod .

# 3. 運行容器（無需掛載配置）
docker run -d \
  --name glance \
  --restart unless-stopped \
  -p 8080:8080 \
  glance-prod
```

### 方案 C：部署到雲平台

大部分支援 Dockerfile 的平台（如 Render、Railway、Fly.io）都會自動：

1. 偵測專案根目錄的 `Dockerfile`
2. 執行 `docker build`
3. 運行容器

**注意事項：**
- 如果平台不支援 volume 掛載，請使用**方案 B**將配置打包進映像
- 環境變數可透過平台的環境變數設置界面配置
- 確保在平台設置以下環境變數：
  - `MY_SECRET_TOKEN`
  - `WORDNIK_API_KEY`

---

## 🔧 環境變數管理

### 本地開發

編輯 `.env` 檔案：

```env
MY_SECRET_TOKEN=123456
WORDNIK_API_KEY=your_api_key_here
```

### 生產環境

根據部署方式選擇：

- **Docker run**：使用 `--env-file .env` 或 `-e KEY=VALUE`
- **Docker build**：使用 `--build-arg KEY=VALUE`
- **雲平台**：透過平台的環境變數設置頁面

---

## 📝 常見問題

### Q: 修改配置後需要重啟嗎？

- **開發環境**：配置檔案透過 volume 掛載，部分修改可能需要重啟容器
- **生產環境（方案 A）**：同開發環境
- **生產環境（方案 B）**：需要重新構建映像並部署

### Q: 如何切換開發/生產模式？

- 開發：使用 `docker-compose up`
- 生產：依據上述三種方案選擇適合的部署方式

### Q: Dockerfile 跟 docker-compose.yml 的關係？

- `docker-compose.yml` 會自動使用 `Dockerfile` 構建映像
- 兩者共用相同的映像定義，確保環境一致性
- 差異在於配置管理方式（volume vs. COPY）

---

## 🔗 相關資源

- [Glance 官方文件](https://github.com/glanceapp/glance)
- [Docker Compose 文件](https://docs.docker.com/compose/)
- [Dockerfile 最佳實踐](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
