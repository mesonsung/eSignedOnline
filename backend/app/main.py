from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.database import get_database, connect_to_mongo
from app.routers import auth, documents, users
from app.core.config import settings

logger = logging.getLogger(__name__)

# 全域變數
database = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時執行
    global database
    await connect_to_mongo()
    database = await get_database()
    yield
    # 關閉時執行
    if database:
        database.client.close()

app = FastAPI(
    title="eSignedOnline API",
    description="電子檔簽署系統 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:8443", 
        "https://127.0.0.1:8443",
        "http://localhost:8443", 
        "http://127.0.0.1:8443",
        "https://esigned_frontend:8443",
        "http://esigned_frontend:8443"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全設定
security = HTTPBearer()

# 異常處理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"驗證錯誤在 {request.method} {request.url}: {exc.errors()}")
    logger.error(f"請求體: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "請求資料驗證失敗",
            "errors": exc.errors()
        }
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Pydantic 驗證錯誤在 {request.method} {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "資料驗證失敗",
            "errors": exc.errors()
        }
    )

# 包含路由
app.include_router(auth.router, prefix="/api/auth", tags=["認證"])
app.include_router(users.router, prefix="/api/users", tags=["使用者"])
app.include_router(documents.router, prefix="/api/documents", tags=["文件"])

@app.get("/")
async def root():
    return {"message": "eSignedOnline API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    # 檢查是否有 SSL 證書
    ssl_keyfile = "/app/certs/key.pem"
    ssl_certfile = "/app/certs/cert.pem"
    
    if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
        # 使用 HTTPS
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=7443,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            reload=True
        )
    else:
        # 使用 HTTP
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=7443,
            reload=True
        )
