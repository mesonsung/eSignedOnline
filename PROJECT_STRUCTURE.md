# eSignedOnline 專案結構

## 專案概述
eSignedOnline 是一個基於 Web 的電子檔簽署系統，支援 PDF 文件的數位簽署和管理。

## 技術架構
- **前端**: Vue.js 3 (Composition API) + Vuetify + Material Design
- **後端**: Python 3.12 + FastAPI
- **資料庫**: MongoDB 4.4
- **容器化**: Docker + Docker Compose
- **安全性**: HTTPS (前端: 8443, 後端: 7443)

## 專案結構

```
eSignedOnline/
├── README.md                          # 專案說明文件
├── PROJECT_STRUCTURE.md               # 專案結構說明
├── docker-compose.yml                 # Docker Compose 配置
├── start.sh                          # 啟動腳本
├── stop.sh                           # 停止腳本
├── generate-certs.sh                 # 證書生成腳本
├── mongo-init/                       # MongoDB 初始化
│   └── init.js                       # 初始化腳本
├── backend/                          # 後端應用程式
│   ├── Dockerfile                    # 後端 Docker 配置
│   ├── requirements.txt              # Python 依賴
│   ├── env.example                   # 環境變數範例
│   └── app/                          # 應用程式代碼
│       ├── main.py                   # 主應用程式入口
│       ├── database.py               # 資料庫連接
│       ├── core/                     # 核心模組
│       │   ├── config.py             # 配置設定
│       │   ├── security.py           # 安全相關
│       │   └── email.py              # 郵件服務
│       ├── models/                   # 資料模型
│       │   ├── user.py               # 用戶模型
│       │   └── document.py           # 文件模型
│       └── routers/                  # API 路由
│           ├── auth.py               # 認證路由
│           ├── users.py              # 用戶管理路由
│           └── documents.py          # 文件管理路由
└── frontend/                         # 前端應用程式
    ├── Dockerfile                    # 前端 Docker 配置
    ├── package.json                  # Node.js 依賴
    ├── vite.config.js                # Vite 配置
    ├── index.html                    # HTML 入口
    └── src/                          # 源代碼
        ├── main.js                   # Vue 應用程式入口
        ├── App.vue                   # 主應用程式組件
        ├── router/                   # 路由配置
        │   └── index.js              # 路由定義
        ├── stores/                   # Pinia 狀態管理
        │   └── auth.js               # 認證狀態
        ├── services/                 # API 服務
        │   └── api.js                # API 客戶端
        ├── plugins/                  # Vue 插件
        │   ├── vuetify.js            # Vuetify 配置
        │   └── i18n.js               # 國際化配置
        └── views/                    # 頁面組件
            ├── Login.vue             # 登入頁面
            ├── Register.vue          # 註冊頁面
            ├── Activate.vue          # 啟用頁面
            ├── Dashboard.vue         # 儀表板
            ├── Documents.vue         # 文件管理
            ├── Upload.vue            # 文件上傳
            ├── Users.vue             # 用戶管理
            ├── MySigned.vue          # 我的簽署
            └── Sign.vue               # 文件簽署
```

## 主要功能

### 1. 使用者管理
- 預設管理員: ADMIN / 1qaz@WSX / ADMIN@esigned.local
- 一般用戶註冊和郵箱啟用
- 角色權限管理 (管理員/一般用戶)

### 2. 文件管理 (管理員功能)
- PDF 文件上傳
- 文件預覽
- 文件刪除
- 文件列表管理

### 3. 電子簽署 (一般用戶功能)
- 選擇待簽署的 PDF 文件
- 文件預覽
- 數位簽署
- 簽署後文件下載
- 簽署記錄管理

### 4. 多語言支援
- 繁體中文 (zh-TW)
- 英文 (en)
- 越南文 (vi)

### 5. 安全性
- HTTPS 加密傳輸
- JWT 認證
- 密碼加密存儲
- 檔案類型驗證

## 快速開始

### 1. 啟動系統
```bash
./start.sh
```

### 2. 訪問應用程式
- 前端: https://localhost:8443
- 後端 API: https://localhost:7443/docs

### 3. 預設管理員帳號
- 用戶名: ADMIN
- 密碼: 1qaz@WSX
- Email: ADMIN@esigned.local

### 4. 停止系統
```bash
./stop.sh
```

## 開發說明

### 後端開發
- 使用 FastAPI 框架
- 支援自動 API 文檔生成
- 使用 MongoDB 作為資料庫
- 支援非同步操作

### 前端開發
- 使用 Vue.js 3 Composition API
- 使用 Vuetify 作為 UI 框架
- 支援響應式設計
- 使用 Pinia 進行狀態管理

### 部署
- 使用 Docker 容器化
- 支援 Docker Compose 一鍵部署
- 自動生成 HTTPS 證書
- 支援環境變數配置

## 注意事項

1. **SMTP 配置**: 需要配置真實的 SMTP 服務以發送啟用郵件
2. **證書安全**: 生產環境請使用正式的 SSL 證書
3. **資料庫安全**: 生產環境請修改預設密碼
4. **檔案存儲**: 生產環境建議使用雲端存儲服務
5. **日誌記錄**: 生產環境請配置適當的日誌記錄
