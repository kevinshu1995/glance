# Glance 部署指南

本專案使用 **Docker Multi-Stage Build** 支援兩種運行模式：**本地開發**（development stage）和**生產部署**（production stage）。

## 📦 專案結構

```
.
├── Dockerfile           # Multi-stage build（包含 base、development、production）
├── docker-compose.yml   # 本地開發配置（使用 development stage）
├── .env                 # 環境變數（不會被加入版本控制）
├── config/              # Glance 配置檔案
│   ├── glance.yml
│   └── home.yml
└── assets/              # 自定義樣式資源
    └── user.css
```

## 🏗️ Multi-Stage Build 架構

Dockerfile 包含三個 stages：

1. **`base`** - 共用基礎配置（環境變數、工作目錄等）
2. **`development`** - 開發環境（不執行 COPY，依賴 volume 掛載）
3. **`production`** - 生產環境（執行 COPY，將配置打包進映像）

---

## 🛠️ 本地開發模式（推薦）

使用 docker-compose 自動啟動 **development stage**。

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

- ✅ 自動使用 `development` stage（透過 `target: development` 指定）
- ✅ **不會執行** `COPY` 指令，配置檔案透過 volume 掛載
- ✅ 配置檔案即時生效（修改 `config/` 和 `assets/` 即時反映）
- ✅ 環境變數自動從 `.env` 載入
- ✅ 與生產環境使用相同的 Dockerfile，確保環境一致性

---

## 🚀 生產環境部署

生產環境使用 **production stage**，會自動將 `config/` 和 `assets/` 打包進映像。

### 方式一：標準部署（推薦）

Docker build 預設使用最後一個 stage（即 `production`）。

```bash
# 構建映像（自動使用 production stage）
docker build -t glance-prod:latest \
  --build-arg MY_SECRET_TOKEN=your_token \
  --build-arg WORDNIK_API_KEY=your_key \
  .

# 運行容器（無需掛載配置）
docker run -d \
  --name glance \
  --restart unless-stopped \
  -p 8080:8080 \
  glance-prod:latest
```

### 方式二：明確指定 Production Stage

```bash
# 明確指定使用 production stage
docker build --target production \
  -t glance-prod:latest \
  --build-arg MY_SECRET_TOKEN=your_token \
  --build-arg WORDNIK_API_KEY=your_key \
  .

# 運行容器
docker run -d \
  --name glance \
  --restart unless-stopped \
  -p 8080:8080 \
  glance-prod:latest
```

### 特點

- ✅ 使用 `production` stage，自動執行 `COPY` 指令
- ✅ 配置檔案打包進映像，映像完全自包含
- ✅ 部署時無需額外掛載 volumes
- ✅ 適合容器化編排環境（Kubernetes、Docker Swarm 等）
- ✅ 適合雲平台部署（Render、Railway、Fly.io 等）

### 方式三：部署到雲平台

大部分支援 Dockerfile 的平台（如 Render、Railway、Fly.io）都會自動：

1. 偵測專案根目錄的 `Dockerfile`
2. 執行 `docker build`（預設使用 `production` stage）
3. 運行容器

**注意事項：**
- 確保在平台設置以下環境變數（build-time arguments）：
  - `MY_SECRET_TOKEN`
  - `WORDNIK_API_KEY`
- 配置檔案會自動打包進映像，無需手動設定 volume

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

### Q: 如何切換開發/生產模式？

透過指定不同的 build target：

- **開發環境**：使用 `docker-compose up`（自動使用 `development` stage）
- **生產環境**：使用 `docker build`（預設使用 `production` stage）

### Q: 修改配置後需要重啟嗎？

- **開發環境（development stage）**：
  - 配置透過 volume 掛載，部分修改可能需要重啟容器：
    ```bash
    docker-compose restart
    ```

- **生產環境（production stage）**：
  - 配置已打包進映像，需要重新構建映像並重新部署：
    ```bash
    docker build -t glance-prod:latest .
    docker stop glance && docker rm glance
    docker run -d --name glance -p 8080:8080 glance-prod:latest
    ```

### Q: Multi-Stage Build 的優勢是什麼？

- ✅ **單一 Dockerfile**：維護更簡單，不需要管理多個 Dockerfile
- ✅ **環境一致性**：開發與生產使用相同的基礎配置（`base` stage）
- ✅ **靈活切換**：透過 `--target` 或 docker-compose 的 `target` 選項切換
- ✅ **最佳化映像**：開發環境保持輕量，生產環境包含完整配置

### Q: 為什麼 development stage 不執行 COPY？

開發環境透過 volume 掛載配置檔案，這樣可以：
- 即時修改配置無需重新建置映像
- 加快開發迭代速度
- 保持本地檔案與容器同步

### Q: Dockerfile 跟 docker-compose.yml 的關係？

- `docker-compose.yml` 使用 `Dockerfile` 構建映像
- 透過 `target: development` 指定使用特定 stage
- 兩者共用相同的 Dockerfile，確保環境一致性
- 差異在於 stage 選擇和配置管理方式（volume vs. COPY）

---

## 🔗 相關資源

- [Glance 官方文件](https://github.com/glanceapp/glance)
- [Docker Compose 文件](https://docs.docker.com/compose/)
- [Dockerfile 最佳實踐](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
