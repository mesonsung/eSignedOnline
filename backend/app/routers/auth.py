from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from app.models.user import UserCreate, UserLogin, Token, User
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    generate_activation_code,
    get_current_active_user
)
from app.core.email import send_activation_email
from app.core.config import settings
from app.database import get_database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """用戶註冊"""
    try:
        logger.info(f"收到註冊請求，用戶名: {user_data.username}, 郵箱: {user_data.email}")
        db = await get_database()
        
        # 檢查用戶名是否已存在
        existing_user = await db.users.find_one({"username": user_data.username})
        if existing_user:
            logger.warning(f"註冊失敗：用戶名 {user_data.username} 已存在")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用戶名已存在"
            )
        
        # 檢查郵箱是否已存在
        existing_email = await db.users.find_one({"email": user_data.email})
        if existing_email:
            logger.warning(f"註冊失敗：郵箱 {user_data.email} 已被使用")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="郵箱已被使用"
            )
        
        # 生成啟用碼
        activation_code = generate_activation_code()
        
        # 創建用戶
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "role": user_data.role,
            "password": get_password_hash(user_data.password),
            "is_active": False,
            "activation_code": activation_code,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user_doc)
        logger.info(f"用戶 {user_data.username} 創建成功，ID: {result.inserted_id}")
        
        # 發送啟用郵件
        email_sent = await send_activation_email(user_data.email, activation_code)
        if email_sent:
            logger.info(f"啟用郵件已發送到 {user_data.email}")
        else:
            logger.warning(f"啟用郵件發送失敗，但用戶已創建。啟用碼: {activation_code}")
        
        return {
            "message": "註冊成功，請檢查您的郵箱以獲取啟用碼",
            "user_id": str(result.inserted_id)
        }
        
    except HTTPException:
        # 重新拋出 HTTP 異常
        raise
    except Exception as e:
        logger.error(f"註冊過程中發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="註冊過程中發生錯誤，請稍後重試"
        )

@router.post("/activate", response_model=dict)
async def activate_account(activation_data: dict):
    """啟用帳號"""
    db = await get_database()
    
    username = activation_data.get("username")
    activation_code = activation_data.get("activation_code")
    
    if not username or not activation_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用戶名和啟用碼都是必需的"
        )
    
    user = await db.users.find_one({
        "username": username,
        "activation_code": activation_code
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="啟用碼無效或用戶不存在"
        )
    
    # 更新用戶狀態
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "is_active": True,
                "activation_code": None,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "帳號啟用成功"}

@router.post("/login", response_model=Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    """用戶登入"""
    db = await get_database()
    
    # 查找用戶
    user = await db.users.find_one({"username": user_credentials.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤"
        )
    
    # 驗證密碼
    if not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤"
        )
    
    # 檢查帳號是否已啟用
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="帳號未啟用，請先啟用您的帳號"
        )
    
    # 創建訪問令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

async def get_current_user(credentials = Depends(security)):
    """獲取當前用戶（用於依賴注入）"""
    from app.core.security import verify_token
    token = credentials.credentials
    token_data = verify_token(token)
    
    db = await get_database()
    user = await db.users.find_one({"username": token_data.username})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶不存在"
        )
    return user

@router.get("/me", response_model=User)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """獲取當前用戶信息"""
    return {
        "id": str(current_user["_id"]),
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user.get("full_name"),
        "role": current_user["role"],
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"],
        "updated_at": current_user["updated_at"]
    }

@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: dict,
    current_user = Depends(get_current_active_user)
):
    """修改密碼"""
    try:
        old_password = password_data.get("old_password")
        new_password = password_data.get("new_password")
        
        if not old_password or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="舊密碼和新密碼都是必需的"
            )
        
        # 驗證舊密碼
        if not verify_password(old_password, current_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="舊密碼錯誤"
            )
        
        # 檢查新密碼長度
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密碼至少需要6個字符"
            )
        
        # 更新密碼
        db = await get_database()
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {
                "$set": {
                    "password": get_password_hash(new_password),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"用戶 {current_user['username']} 成功修改密碼")
        return {"message": "密碼修改成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密碼時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密碼時發生錯誤"
        )

@router.post("/forgot-password", response_model=dict)
async def forgot_password(request_data: dict):
    """忘記密碼 - 發送重設密碼郵件"""
    try:
        email = request_data.get("email")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="郵箱地址是必需的"
            )
        
        db = await get_database()
        user = await db.users.find_one({"email": email})
        
        if not user:
            # 為了安全起見，即使郵箱不存在也返回成功訊息
            return {"message": "如果該郵箱地址存在於系統中，重設密碼連結已發送"}
        
        # 生成重設密碼令牌
        reset_token = generate_activation_code()
        reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1小時後過期
        
        # 更新用戶記錄
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "reset_token": reset_token,
                    "reset_token_expires": reset_expires,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # 發送重設密碼郵件
        from app.core.email import send_password_reset_email
        email_sent = await send_password_reset_email(user["email"], reset_token)
        
        if email_sent:
            logger.info(f"重設密碼郵件已發送到 {email}")
        else:
            logger.warning(f"重設密碼郵件發送失敗到 {email}, 重設令牌: {reset_token}")
        
        return {"message": "如果該郵箱地址存在於系統中，重設密碼連結已發送"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"處理忘記密碼請求時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="處理請求時發生錯誤"
        )

@router.post("/reset-password", response_model=dict)
async def reset_password(reset_data: dict):
    """重設密碼"""
    try:
        token = reset_data.get("token")
        new_password = reset_data.get("new_password")
        
        if not token or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="重設令牌和新密碼都是必需的"
            )
        
        # 檢查新密碼長度
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密碼至少需要6個字符"
            )
        
        db = await get_database()
        user = await db.users.find_one({
            "reset_token": token,
            "reset_token_expires": {"$gt": datetime.utcnow()}
        })
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="重設令牌無效或已過期"
            )
        
        # 更新密碼並清除重設令牌
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "password": get_password_hash(new_password),
                    "updated_at": datetime.utcnow()
                },
                "$unset": {
                    "reset_token": "",
                    "reset_token_expires": ""
                }
            }
        )
        
        logger.info(f"用戶 {user['username']} 成功重設密碼")
        return {"message": "密碼重設成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重設密碼時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重設密碼時發生錯誤"
        )
