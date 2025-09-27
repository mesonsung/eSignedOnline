from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = False
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # 基本的 email 格式驗證，允許 .local 域名
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str
    role: UserRole = UserRole.USER
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('用戶名至少需要3個字符')
        if len(v.strip()) > 20:
            raise ValueError('用戶名不能超過20個字符')
        # 檢查用戶名格式 (只允許字母、數字、下劃線)
        if not re.match(r'^[a-zA-Z0-9_]+$', v.strip()):
            raise ValueError('用戶名只能包含字母、數字和下劃線')
        return v.strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('郵箱地址為必填項')
        v = v.strip().lower()
        # 基本的 email 格式驗證
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('郵箱地址格式不正確')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('密碼至少需要6個字符')
        if len(v) > 50:
            raise ValueError('密碼不能超過50個字符')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v
        # 基本的 email 格式驗證，允許 .local 域名
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v

class UserInDB(UserBase):
    id: Optional[str] = None
    password_hash: str
    activation_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class User(UserBase):
    id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
