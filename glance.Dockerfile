# ============================================
# Production Dockerfile for Zeabur/Cloud Deployment
# ============================================
# 使用 glance 官方映像作為基礎
FROM glanceapp/glance:latest

# 設置工作目錄
WORKDIR /app

# 生產環境將配置打包到映像中
COPY config /app/config
COPY assets /app/assets

# 驗證配置檔案是否成功複製
RUN ls -laR /app/config /app/assets

# 暴露端口
EXPOSE 8080
