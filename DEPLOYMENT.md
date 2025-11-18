# Glance 部署指南

本專案使用**兩個獨立的 Dockerfile** 分別支援：**本地開發**和**生產部署**。

## 📦 專案結構

```
.
├── Dockerfile           # 本地開發用（不含 COPY，依賴 volume 掛載）
├── glance.Dockerfile    # 生產部署用（包含 COPY，配置打包進映像）
├── docker-compose.yml   # 本地開發配置（使用 Dockerfile）
├── .env                 # 環境變數（不會被加入版本控制）
├── config/              # Glance 配置檔案
│   ├── glance.yml
│   └── home.yml
└── assets/              # 自定義樣式資源
    └── user.css
```

## 🏗️ Dockerfile 架構說明

### `Dockerfile` - 本地開發
- 用於 docker-compose 本地開發
- **不執行** `COPY` 指令
- 配置透過 volume 掛載，可即時修改

### `glance.Dockerfile` - 生產部署
- 用於 Zeabur、Render、Railway 等雲平台
- **執行** `COPY` 指令，將 config/ 和 assets/ 打包進映像
- Zeabur 會自動偵測服務名稱對應的 Dockerfile（`glance.Dockerfile`）

---

## 🛠️ 本地開發模式（推薦）

使用 docker-compose 搭配 `Dockerfile`（本地開發版本）。

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

- ✅ 使用 `Dockerfile`（本地開發版本）
- ✅ **不會執行** `COPY` 指令，配置檔案透過 volume 掛載
- ✅ 配置檔案即時生效（修改 `config/` 和 `assets/` 即時反映）
- ✅ 環境變數自動從 `.env` 載入
- ✅ 可隨時重啟容器套用配置變更

---

## 🚀 生產環境部署

生產環境使用 **`glance.Dockerfile`**，會自動將 `config/` 和 `assets/` 打包進映像。

### 方式一：部署到 Zeabur（推薦）

[Zeabur](https://zeabur.com) 會自動偵測服務名稱對應的 Dockerfile。

#### 部署步驟

1. 將專案推送到 GitHub
2. 在 Zeabur 建立新服務，服務名稱設為 **`glance`**
3. Zeabur 會自動偵測並使用 `glance.Dockerfile` 構建
4. 在服務設定中新增環境變數：
   - `MY_SECRET_TOKEN`
   - `WORDNIK_API_KEY`

#### Zeabur 自動偵測規則

Zeabur 會按照以下順序尋找 Dockerfile：
1. `glance.Dockerfile`（服務名稱.Dockerfile）
2. `Dockerfile.glance`（Dockerfile.服務名稱）
3. `Dockerfile`（預設）

因為服務名稱是 `glance`，Zeabur 會自動使用 `glance.Dockerfile`。

#### 特點

- ✅ 自動偵測並使用 `glance.Dockerfile`
- ✅ 環境變數透過 `ARG` 在構建時期傳入
- ✅ 配置檔案已打包進映像，無需額外設定
- ✅ 支援自動部署（GitHub push 觸發）

### 方式二：使用 Docker 手動部署

```bash
# 使用 glance.Dockerfile 構建映像
docker build -f glance.Dockerfile \
  -t glance-prod:latest \
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

### 方式三：部署到其他雲平台

對於 Render、Railway、Fly.io 等平台：

**選項 A：指定 Dockerfile**
- 在平台設定中指定使用 `glance.Dockerfile`
- 設定環境變數：`MY_SECRET_TOKEN`、`WORDNIK_API_KEY`

**選項 B：使用預設 Dockerfile**
- 若平台不支援指定 Dockerfile 名稱
- 可將 `glance.Dockerfile` 重新命名為 `Dockerfile`（但需先備份原本的開發用 Dockerfile）

### 特點

- ✅ 使用 `glance.Dockerfile`，自動執行 `COPY` 指令
- ✅ 配置檔案打包進映像，映像完全自包含
- ✅ 部署時無需額外掛載 volumes
- ✅ 適合容器化編排環境（Kubernetes、Docker Swarm 等）
- ✅ 適合雲平台部署（Zeabur、Render、Railway 等）

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

### Q: 為什麼要使用兩個獨立的 Dockerfile？

- **`Dockerfile`**（本地開發）：不包含 COPY，配置透過 volume 掛載，方便即時修改
- **`glance.Dockerfile`**（生產部署）：包含 COPY，配置打包進映像，適合雲平台部署
- 這種分離讓開發和部署流程更清晰，避免混淆

### Q: 如何切換開發/生產模式？

透過使用不同的 Dockerfile：

- **開發環境**：使用 `docker-compose up`（自動使用 `Dockerfile`）
- **生產環境**：使用 `docker build -f glance.Dockerfile`（明確指定 `glance.Dockerfile`）

### Q: 修改配置後需要重啟嗎？

- **開發環境（使用 Dockerfile）**：
  - 配置透過 volume 掛載，部分修改可能需要重啟容器：
    ```bash
    docker-compose restart
    ```

- **生產環境（使用 glance.Dockerfile）**：
  - 配置已打包進映像，需要重新構建映像並重新部署：
    ```bash
    docker build -f glance.Dockerfile -t glance-prod:latest .
    docker stop glance && docker rm glance
    docker run -d --name glance -p 8080:8080 glance-prod:latest
    ```

### Q: Zeabur 如何知道要使用 glance.Dockerfile？

Zeabur 會根據服務名稱自動偵測對應的 Dockerfile：
- 服務名稱：`glance`
- 偵測順序：`glance.Dockerfile` → `Dockerfile.glance` → `Dockerfile`
- 因此只要服務名稱設為 `glance`，就會自動使用 `glance.Dockerfile`

### Q: 為什麼本地開發的 Dockerfile 不執行 COPY？

開發環境透過 volume 掛載配置檔案，這樣可以：
- 即時修改配置無需重新建置映像
- 加快開發迭代速度
- 保持本地檔案與容器同步

### Q: 可以只用一個 Dockerfile 嗎？

可以，但不推薦。使用兩個獨立的 Dockerfile 的優勢：
- ✅ **職責分離**：開發與生產各有專屬配置，不會互相干擾
- ✅ **更清晰**：不需要記住 multi-stage build 的 target 參數
- ✅ **更簡單**：docker-compose 和雲平台各自使用對應的 Dockerfile，無需額外配置
- ✅ **Zeabur 友好**：自動偵測服務名稱對應的 Dockerfile

---

## 🔗 相關資源

- [Glance 官方文件](https://github.com/glanceapp/glance)
- [Docker Compose 文件](https://docs.docker.com/compose/)
- [Dockerfile 最佳實踐](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
