# ============================================
# Base Stage - 共用基礎配置
# ============================================
FROM glanceapp/glance:latest AS base

# 設置工作目錄
WORKDIR /app

# 設置環境變數（可在 docker build 或 docker run 時覆蓋）
ARG MY_SECRET_TOKEN
ARG WORDNIK_API_KEY

ENV MY_SECRET_TOKEN=${MY_SECRET_TOKEN} \
    WORDNIK_API_KEY=${WORDNIK_API_KEY}

# 暴露端口
EXPOSE 8080

# ============================================
# Development Stage - 開發環境
# ============================================
FROM base AS development

# 開發環境不複製配置，使用 docker-compose volume 掛載
# 容器啟動命令（繼承自基礎映像）

# ============================================
# Production Stage - 生產環境
# ============================================
FROM base AS production

# 生產環境將配置打包到映像中
COPY config/ /app/config/
COPY assets/ /app/assets/

# 容器啟動命令（繼承自基礎映像）
