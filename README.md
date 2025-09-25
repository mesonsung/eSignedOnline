# eSignedOnline - 電子檔簽署系統

## 系統概述
eSignedOnline 是一個基於 Web 的電子檔簽署系統，支援 PDF 文件的數位簽署和管理。

## 技術架構
- **前端**: Vue.js 3 (Composition API) + Material Design + RWD
- **後端**: Python 3.12 + FastAPI
- **資料庫**: MongoDB 4.4
- **容器化**: Docker + Docker Compose
- **安全性**: HTTPS (前端: 8443, 後端: 7443)

## 主要功能
1. 使用者管理 (註冊、登入、啟用)
2. PDF 文件管理 (上傳、預覽、刪除)
3. 電子簽署功能
4. 多語言支援 (繁體中文/英文/越南文)
5. 文件下載和管理

## 快速開始
```bash
# 啟動系統
docker-compose up -d

# 訪問前端
https://localhost:8443

# 訪問後端 API
https://localhost:7443/docs
```

## 預設管理員帳號
- 帳號: ADMIN
- 密碼: 1qaz@WSX
- Email: ADMIN@esigned.local
