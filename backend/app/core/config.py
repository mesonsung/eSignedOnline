from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 應用程式設定
    app_name: str = "eSignedOnline"
    secret_key: str = "eSignedOnline-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 資料庫設定
    mongodb_url: str = "mongodb://admin:password123@localhost:27017/esigned?authSource=admin"
    
    # SMTP 設定
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    
    # 檔案上傳設定
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".pdf"]
    
    # 檔案路徑
    upload_path: str = "/app/uploads"
    doc_to_sign_path: str = "/app/uploads/DocToSign"
    signed_doc_path: str = "/app/uploads/SignedDoc"
    
    # 多語言設定
    default_language: str = "zh-TW"
    supported_languages: list = ["zh-TW", "en", "vi"]
    
    class Config:
        env_file = ".env"

settings = Settings()
