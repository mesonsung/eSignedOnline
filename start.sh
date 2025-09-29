#!/bin/bash

# eSignedOnline 啟動腳本

echo "正在啟動 eSignedOnline 系統..."

# 檢查證書是否存在
if [ ! -f "storage/frontend/letsencrypt" ]; then
    echo "證書不存在，正在生成..."
    docker run -it --rm \
    -v "$(pwd)/storage/frontend/letsencrypt:/etc/letsencrypt" \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    -d esigned.serveblog.net\
    --email meson.sung@gmail.com \
    --agree-tos \
    --non-interactive
  fi

if [ ! -f "storage/backend/certs/cert.pem" ] || [ ! -f "storage/backend/certs/key.pem" ]; then
    echo "後端證書不存在，正在生成..."
    ./generate-certs.sh
fi

# 建立必要的目錄
mkdir -p storage/backend/uploads/DocToSign
mkdir -p storage/backend/uploads/SignedDoc

# 啟動 Docker Compose
echo "正在啟動 Docker 容器..."
docker-compose up -d

echo "系統啟動完成！"
echo "前端: https://localhost"
echo "後端 API: https://localhost:8443/api/docs"
echo ""
echo "預設管理員帳號:"
echo "用戶名: ADMIN"
echo "密碼: 1qaz@WSX"
echo "Email: ADMIN@esigned.local"
