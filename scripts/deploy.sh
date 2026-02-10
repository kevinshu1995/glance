#!/bin/bash

# 主部署腳本 - 同時更新並重啟 Glance 與 Homepage

set -e

REPO_DIR="/home/pie/glance"
LOG_DIR="/home/pie/glance/logs"
LOG_FILE="$LOG_DIR/deploy.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 建立日誌目錄（如果不存在）
mkdir -p $LOG_DIR

# 日誌函數
log() {
    echo "[$TIMESTAMP] $1" | tee -a $LOG_FILE
}

log "========== Starting Deployment =========="

# 檢查倉庫目錄
if [ ! -d "$REPO_DIR" ]; then
    log "ERROR: Repository directory not found: $REPO_DIR"
    exit 1
fi

cd $REPO_DIR

# 1. Git Pull
log "Pulling from GitHub..."
if git pull origin pi >> $LOG_FILE 2>&1; then
    log "✓ Git pull successful"
else
    log "✗ Git pull failed"
    exit 1
fi

# 2. 停止容器
log "Stopping containers..."
if docker compose down >> $LOG_FILE 2>&1; then
    log "✓ Containers stopped"
else
    log "✗ Failed to stop containers"
fi

# 3. 啟動容器
log "Starting containers..."
if docker compose up -d >> $LOG_FILE 2>&1; then
    log "✓ Containers started"
else
    log "✗ Failed to start containers"
    exit 1
fi

# 4. 等待服務啟動
log "Waiting for services to start..."
sleep 10

# 5. 健康檢查
log "Running health checks..."
bash $REPO_DIR/scripts/health-check.sh >> $LOG_FILE 2>&1

# 6. 重啟 webhook service（延遲執行，避免殺死當前程序）
# 必須重定向 stdout/stderr，否則 subprocess.run(capture_output=True) 會等待管道關閉

log "========== Deployment Completed Successfully =========="

# 明確返回成功狀態
exit 0