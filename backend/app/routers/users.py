from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User, UserUpdate
from app.core.security import get_current_active_user, get_admin_user
from app.database import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[User])
async def get_users(current_user = Depends(get_admin_user)):
    """獲取所有用戶（僅管理員）"""
    db = await get_database()
    
    users = []
    async for user in db.users.find():
        users.append({
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "full_name": user.get("full_name"),
            "role": user["role"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"]
        })
    
    return users

@router.get("/me", response_model=User)
async def get_my_profile(current_user = Depends(get_current_active_user)):
    """獲取自己的資料"""
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

@router.put("/me", response_model=User)
async def update_my_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_active_user)
):
    """更新自己的資料"""
    db = await get_database()
    
    update_data = {"updated_at": datetime.utcnow()}
    
    if user_update.username is not None:
        # 檢查用戶名是否已被使用
        existing_user = await db.users.find_one({
            "username": user_update.username,
            "_id": {"$ne": current_user["_id"]}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用戶名已被使用"
            )
        update_data["username"] = user_update.username
    
    if user_update.email is not None:
        # 檢查郵箱是否已被使用
        existing_email = await db.users.find_one({
            "email": user_update.email,
            "_id": {"$ne": current_user["_id"]}
        })
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="郵箱已被使用"
            )
        update_data["email"] = user_update.email
    
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    
    if user_update.password is not None:
        from app.core.security import get_password_hash
        update_data["password_hash"] = get_password_hash(user_update.password)
    
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    # 獲取更新後的用戶資料
    updated_user = await db.users.find_one({"_id": current_user["_id"]})
    
    return {
        "id": str(updated_user["_id"]),
        "username": updated_user["username"],
        "email": updated_user["email"],
        "full_name": updated_user.get("full_name"),
        "role": updated_user["role"],
        "is_active": updated_user["is_active"],
        "created_at": updated_user["created_at"],
        "updated_at": updated_user["updated_at"]
    }

@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user = Depends(get_admin_user)):
    """刪除用戶（僅管理員）"""
    db = await get_database()
    
    # 檢查用戶是否存在
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用戶不存在"
        )
    
    # 不能刪除自己
    if str(user["_id"]) == str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能刪除自己的帳號"
        )
    
    await db.users.delete_one({"_id": ObjectId(user_id)})
    
    return {"message": "用戶已刪除"}
