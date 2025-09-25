#!/bin/bash

# eSignedOnline 停止腳本

echo "正在停止 eSignedOnline 系統..."

# 停止 Docker Compose
docker-compose down

echo "系統已停止！"
