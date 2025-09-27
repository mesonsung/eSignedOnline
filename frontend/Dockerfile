# 構建階段
FROM node:24.9-alpine AS builder

WORKDIR /app

# 複製 package.json 和 package-lock.json
COPY package*.json ./


# 安裝依賴（優先使用鎖檔，縮減噪音與重複下載）
ENV NPM_CONFIG_UPDATE_NOTIFIER=false
RUN if [ -f package-lock.json ]; then \
      npm ci --no-audit --no-fund --loglevel=error; \
    else \
      npm install --no-audit --no-fund --loglevel=error; \
    fi

RUN npm i -D vite@latest @vitejs/plugin-vue@latest

# 複製源代碼
COPY . .

# 構建應用程式
RUN npm run build

# 生產階段
FROM nginx:alpine

# 複製構建的文件到 nginx 目錄
COPY --from=builder /app/dist /usr/share/nginx/html

# 複製 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 建立證書目錄
RUN mkdir -p /etc/nginx/certs

# 暴露端口
EXPOSE 8443

# 啟動 nginx
CMD ["nginx", "-g", "daemon off;"]
