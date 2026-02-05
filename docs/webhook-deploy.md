# Webhook Deploy Service

Raspberry Pi 上的自動部署服務。當 GitHub 收到 push 事件時，透過 Cloudflare Tunnel 觸發 Pi 上的 `webhook-server.py`，執行 `deploy.sh` 並推送 Telegram 通知。

## 架構

```
GitHub push (pi branch)
  → Cloudflare Tunnel (p-webhook.hsiu.soy)
    → webhook-server.py (:5000)
      → 驗證 HMAC-SHA256 簽名
      → 篩選 branch
      → 馬上回傳 202 Accepted
      → 背景執行 deploy.sh
        → git pull
        → docker compose down / up
        → health-check.sh
        → 重啟 glance-webhook.service（延遲 3 秒）
      → 推送 Telegram 通知（觸發 / 成功 / 失敗）
```

## 環境變數

全部寫在 `/home/pie/glance/.env` 裡，由 systemd `EnvironmentFile` 讀取。

| 變數                    | 說明                                  | 預設值 |
| ----------------------- | ------------------------------------- | ------ |
| `TELEGRAM_TOKEN`        | Telegram Bot token                    | —      |
| `TELEGRAM_CHAT_ID`      | Telegram chat ID                      | —      |
| `GITHUB_WEBHOOK_SECRET` | GitHub webhook secret（用於簽名驗證） | —      |
| `DEPLOY_BRANCH`         | 觸發部署的 branch 名                  | `pi`   |

參考 `.env.example` 確認全部需要填入的欄位。

---

## 手動處理事項

以下動作**無法自動完成**，需要在 Pi 或瀏覽器裡手動操作。

### 1. 安裝 Flask

```bash
sudo apt-get update && sudo apt-get install -y python3-pip
sudo pip3 install flask --break-system-packages
```

若 `apt` 找不到 `cloudflared`（見下節），改用直接下載的方式安裝。

### 2. 安裝 cloudflared

```bash
ARCH=$(dpkg --print-architecture)
wget "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}.deb"
sudo dpkg -i cloudflared-linux-${ARCH}.deb
```

安裝後可以刪掉 `.deb` 檔，或加進 `.gitignore`（`*.deb`）。

### 3. Cloudflare Tunnel 登入

SSH 環境無法直接開瀏覽器，需要把 URL 貼到本機瀏覽器裡授權：

```bash
cloudflared tunnel login
```

終端會輸出一個 `https://login.cloudflare.com/...` 的 URL，複製後貼到本機瀏覽器開啟，授權完成後 Pi 上會自動下載 `cert.pem`。

### 4. 建立 Tunnel 並設定 config

```bash
cloudflared tunnel create glance
```

記下輸出的 **Tunnel ID**，然後建立 config：

```bash
sudo mkdir -p /etc/cloudflared
sudo tee /etc/cloudflared/config.yml <<EOF
tunnel: <TUNNEL-ID>
credentials-file: /home/pie/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: dashboard.hsiu.soy
    service: http://localhost:8001
  - hostname: p-webhook.hsiu.soy
    service: http://localhost:5000
  - service: http_status:404
EOF
```

後面新增服務時，在 `- service: http_status:404` 之前加入新的 hostname 規則即可。

### 5. Route DNS

每個 hostname 都要跑一次，否則從外網打進來會 404：

```bash
cloudflared tunnel route dns glance dashboard.hsiu.soy
cloudflared tunnel route dns glance p-webhook.hsiu.soy
```

新增服務時別忘了對應多跑一個這個命令。

### 6. 安裝 cloudflared 為 systemd service

```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

修改 `/etc/cloudflared/config.yml` 之後，需要重啟才會生效：

```bash
sudo systemctl restart cloudflared
```

### 7. GitHub Webhook 設定

進入 GitHub repo → **Settings → Webhooks → Add webhook**

| 欄位         | 填入                                                         |
| ------------ | ------------------------------------------------------------ |
| Payload URL  | `https://p-webhook.hsiu.soy/deploy`                          |
| Content type | `application/json`                                           |
| Secret       | 隨便打一串隨機字，同時填進 `.env` 的 `GITHUB_WEBHOOK_SECRET` |
| Events       | Just the push event                                          |

### 8. webhook-server systemd 設定

先確認 `.env` 已經填好，然後設定 systemd 從 `.env` 讀取環境變數：

```bash
sudo mkdir -p /etc/systemd/system/glance-webhook.service.d
sudo tee /etc/systemd/system/glance-webhook.service.d/override.conf <<EOF
[Service]
EnvironmentFile=/home/pie/glance/.env
EOF

sudo systemctl daemon-reload
sudo systemctl restart glance-webhook.service
```

### 9. 腳本執行權限

```bash
chmod +x /home/pie/glance/scripts/deploy.sh
chmod +x /home/pie/glance/scripts/health-check.sh
```

### 10. sudoers 設定（deploy 後自動重啟 webhook service）

`deploy.sh` 末尾會重啟 `glance-webhook.service`，但該服務以 `pie` user 來跑，預設沒有 `sudo` 權限。需要開放這一個命令：

```bash
sudo visudo -f /etc/sudoers.d/pie-webhook
```

進去後貼入以下內容，存出來：

```
pie ALL=(root) NOPASSWD: /usr/bin/systemctl restart glance-webhook.service
```

驗證：

```bash
sudo -u pie sudo systemctl restart glance-webhook.service --dry-run
```

不報錯即可。

---

## API Endpoints

所有 endpoint 從外網經 `https://p-webhook.hsiu.soy` 存取。

### `POST /deploy`

由 GitHub webhook 觸發，非手動打的。為避免 GitHub 的 10 秒 timeout，收到請求後馬上回傳 `202`，實際部署在背景執行，結果透過 Telegram 通知。

- 驗證 `X-Hub-Signature-256` 簽名，失敗回傳 `401`
- 檢查 `ref` 是否符合 `DEPLOY_BRANCH`，不符回傳 `200` + `skipped`
- 驗證通過後馬上回傳 `202`，`deploy.sh` 在背景執行

**回傳：**

| Status Code | 含義                               |
| ----------- | ---------------------------------- |
| `202`       | 部署已排佇，看 Telegram 通知等結果 |
| `200`       | branch 不符，跳過                  |
| `401`       | 簽名驗證失敗                       |

**部署結果**（透過 Telegram 通知，或看 `GET /logs`）：

- 成功：Telegram 推送成功訊息
- 失敗：Telegram 推送失敗訊息 + exit code + deploy.log 內容
- 超時（>5分鐘）：Telegram 推送超時訊息

### `GET /health`

健康檢查，單純確認服務有沒有起來。

```json
{ "status": "ok" }
```

### `GET /status`

回傳目前 Docker 容器狀態。

### `GET /logs`

回傳 `deploy.log` 最後 30 行。

---

## Telegram 通知

以下事件會推送通知：

| 事件     | 訊息內容                           |
| -------- | ---------------------------------- |
| 部署觸發 | 時間戳                             |
| 部署成功 | 時間戳                             |
| 部署失敗 | 時間戳、exit code、deploy.log 內容 |
| 部署超時 | 時間戳（超過 5 分鐘）              |

`TELEGRAM_TOKEN` 或 `TELEGRAM_CHAT_ID` 沒填的話，通知單純跳過，不會影響部署流程。

---

## 常見問題

**Q: GitHub webhook 回傳 404**
Config 可能沒有同步。確認 `/etc/cloudflared/config.yml` 裡有該 hostname，然後 `sudo systemctl restart cloudflared`。別忘了 `cloudflared tunnel route dns` 也要跑過。

**Q: 部署失敗但 error 是空的**
`deploy.sh` 的輸出被重定向進了 `deploy.log`，`stderr` 本身會是空的。看回傳的 `deploy_log` 欄位或直接去看 `/home/pie/glance/logs/deploy.log`。

**Q: Telegram 通知收不到**
先確認 `.env` 裡的 `TELEGRAM_TOKEN` 和 `TELEGRAM_CHAT_ID` 填得對不對，然後看 `webhook.log` 裡有沒有 "Telegram 通知失敗" 的訊息。

**Q: Permission denied: deploy.sh**
`chmod +x /home/pie/glance/scripts/deploy.sh`

**Q: Deploy 後 webhook service 沒有重啟**
確認 sudoers 已經設定（見手動處理事項 #10）。可以手動測試：`sudo -u pie sudo systemctl restart glance-webhook.service`

**Q: 換網域時 `cloudflared tunnel route dns` 報「record already exists」**
目標網域已經有 A / CNAME record。進 Cloudflare Dashboard → DNS → Records，找到該subdomain 的記錄刪掉後，再跑 `route dns`。舊網域的 CNAME record 也記得進去清理。

