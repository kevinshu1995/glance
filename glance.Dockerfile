# ============================================
# Production Dockerfile for Zeabur/Cloud Deployment
# ============================================
# 使用 glance 官方映像作為基礎
FROM glanceapp/glance:latest

# 設置工作目錄
WORKDIR /app

# 設置環境變數（可在 docker build 或 docker run 時覆蓋）
ARG MY_SECRET_TOKEN
ARG WORDNIK_API_KEY

ENV MY_SECRET_TOKEN=${MY_SECRET_TOKEN} \
    WORDNIK_API_KEY=${WORDNIK_API_KEY}

# 生產環境將配置打包到映像中
COPY config/ /app/config/
COPY assets/ /app/assets/

# 暴露端口
EXPOSE 8080

# 容器啟動命令（繼承自基礎映像）
