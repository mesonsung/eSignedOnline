#!/bin/bash

# 生成 HTTPS 證書腳本

echo "正在生成 HTTPS 證書..."

# 建立證書目錄
mkdir -p storage/backend/certs
mkdir -p storage/frontend/certs

# 生成後端證書
openssl req -x509 -newkey rsa:4096 -keyout storage/backend/certs/key.pem -out storage/backend/certs/cert.pem -days 3650 -nodes \
  -subj "/C=TW/ST=Taiwan/L=Taipei/O=eSignedOnline/OU=IT/CN=localhost"

# 生成前端證書
openssl req -x509 -newkey rsa:4096 -keyout storage/frontend/certs/key.pem -out storage/frontend/certs/cert.pem -days 3650 -nodes \
  -subj "/C=TW/ST=Taiwan/L=Taipei/O=eSignedOnline/OU=IT/CN=localhost"

echo "證書生成完成！"
echo "後端證書: storage/backend/certs/"
echo "前端證書: storage/frontend/certs/"
