from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from app.models.document import Document, DocumentCreate, DocumentSign
from app.core.security import get_current_active_user, get_admin_user
from app.database import get_database
from app.core.config import settings
from bson import ObjectId
from datetime import datetime
import os
import shutil
import uuid
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    current_user = Depends(get_admin_user)
):
    """上傳 PDF 文件（僅管理員）"""
    db = await get_database()
    
    # 檢查檔案類型
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只允許上傳 PDF 檔案"
        )
    
    # 檢查檔案大小
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="檔案大小超過限制"
        )
    
    # 生成唯一檔名
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.doc_to_sign_path, filename)
    
    # 確保目錄存在
    os.makedirs(settings.doc_to_sign_path, exist_ok=True)
    
    # 儲存檔案
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # 儲存到資料庫
    document_doc = {
        "filename": filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_size": file_size,
        "status": "uploaded",
        "uploaded_by": current_user["username"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.documents.insert_one(document_doc)
    
    return {
        "id": str(result.inserted_id),
        "filename": filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_size": file_size,
        "status": "uploaded",
        "uploaded_by": current_user["username"],
        "created_at": document_doc["created_at"],
        "updated_at": document_doc["updated_at"]
    }

@router.get("/", response_model=List[Document])
async def get_documents(current_user = Depends(get_current_active_user)):
    """獲取所有文件列表（包括已簽署和未簽署的文件）"""
    db = await get_database()
    
    # 顯示所有文件
    query = {}
    
    documents = []
    async for doc in db.documents.find(query).sort("created_at", -1):
        documents.append({
            "id": str(doc["_id"]),
            "filename": doc["filename"],
            "original_filename": doc["original_filename"],
            "file_path": doc["file_path"],
            "file_size": doc["file_size"],
            "status": doc["status"],
            "uploaded_by": doc["uploaded_by"],
            "signed_by": doc.get("signed_by"),
            "signed_at": doc.get("signed_at"),
            "signed_filename": doc.get("signed_filename"),
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"]
        })
    
    return documents

@router.get("/available", response_model=List[Document])
async def get_available_documents(current_user = Depends(get_current_active_user)):
    """獲取可簽署文件列表（未簽署的文件）"""
    db = await get_database()
    
    # 只顯示未簽署的文件
    query = {"status": "uploaded"}
    
    documents = []
    async for doc in db.documents.find(query).sort("created_at", -1):
        documents.append({
            "id": str(doc["_id"]),
            "filename": doc["filename"],
            "original_filename": doc["original_filename"],
            "file_path": doc["file_path"],
            "file_size": doc["file_size"],
            "status": doc["status"],
            "uploaded_by": doc["uploaded_by"],
            "signed_by": doc.get("signed_by"),
            "signed_at": doc.get("signed_at"),
            "signed_filename": doc.get("signed_filename"),
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"]
        })
    
    return documents

@router.get("/signed", response_model=List[Document])
async def get_signed_documents(current_user = Depends(get_current_active_user)):
    """獲取已簽署文件列表"""
    db = await get_database()
    
    # 管理員可以看到所有已簽署文件，一般用戶只能看到自己簽署的文件
    if current_user["role"] == "admin":
        query = {"status": "signed"}
    else:
        query = {"status": "signed", "signed_by": current_user["username"]}
    
    documents = []
    async for doc in db.documents.find(query).sort("created_at", -1):
        documents.append({
            "id": str(doc["_id"]),
            "filename": doc["filename"],
            "original_filename": doc["original_filename"],
            "file_path": doc["file_path"],
            "file_size": doc["file_size"],
            "status": doc["status"],
            "uploaded_by": doc["uploaded_by"],
            "signed_by": doc.get("signed_by"),
            "signed_at": doc.get("signed_at"),
            "signed_filename": doc.get("signed_filename"),
            "signed_file_path": doc.get("signed_file_path"),
            "signature_data": doc.get("signature_data"),
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"]
        })
    
    return documents

@router.get("/all-signed", response_model=List[Document])
async def get_all_signed_documents(current_user = Depends(get_current_active_user)):
    """獲取所有已簽署文件列表（管理員和一般用戶都可以看到所有已簽署文件）"""
    db = await get_database()
    
    # 所有用戶都可以看到所有已簽署文件
    query = {"status": "signed"}
    
    documents = []
    async for doc in db.documents.find(query).sort("created_at", -1):
        documents.append({
            "id": str(doc["_id"]),
            "filename": doc["filename"],
            "original_filename": doc["original_filename"],
            "file_path": doc["file_path"],
            "file_size": doc["file_size"],
            "status": doc["status"],
            "uploaded_by": doc["uploaded_by"],
            "signed_by": doc.get("signed_by"),
            "signed_at": doc.get("signed_at"),
            "signed_filename": doc.get("signed_filename"),
            "signed_file_path": doc.get("signed_file_path"),
            "signature_data": doc.get("signature_data"),
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"]
        })
    
    return documents

@router.get("/{document_id}")
async def get_document(document_id: str, current_user = Depends(get_current_active_user)):
    """獲取單個文件信息"""
    db = await get_database()
    
    document = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 檢查權限
    if current_user["role"] != "admin":
        # 一般用戶只能查看可簽署文件或自己簽署的文件
        if document["status"] == "uploaded":
            # 可以查看可簽署文件
            pass
        elif document["status"] == "signed" and document.get("signed_by") == current_user["username"]:
            # 可以查看自己簽署的文件
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限查看此文件"
            )
    
    return {
        "id": str(document["_id"]),
        "filename": document["filename"],
        "original_filename": document["original_filename"],
        "file_path": document["file_path"],
        "file_size": document["file_size"],
        "status": document["status"],
        "uploaded_by": document["uploaded_by"],
        "signed_by": document.get("signed_by"),
        "signed_filename": document.get("signed_filename"),
        "signed_file_path": document.get("signed_file_path"),
        "signature_data": document.get("signature_data"),
        "created_at": document["created_at"],
        "updated_at": document["updated_at"]
    }

@router.get("/{document_id}/preview")
async def preview_document(document_id: str, token: str = None):
    """預覽文件"""
    db = await get_database()
    
    # 驗證 token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要認證令牌"
        )
    
    from app.core.security import verify_token
    try:
        token_data = verify_token(token)
        current_user = await db.users.find_one({"username": token_data.username})
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用戶不存在"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證令牌"
        )
    
    document = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 檢查權限
    if current_user["role"] != "admin":
        # 一般用戶只能預覽可簽署文件或自己簽署的文件
        if document["status"] == "uploaded":
            # 可以預覽可簽署文件
            pass
        elif document["status"] == "signed" and document.get("signed_by") == current_user["username"]:
            # 可以預覽自己簽署的文件
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限預覽此文件"
            )
    
    # 根據文件狀態選擇預覽文件
    if document["status"] == "signed" and document.get("signed_file_path"):
        # 已簽署文件，預覽已簽署的文件
        file_path = document["signed_file_path"]
        filename = document.get("signed_filename", document["original_filename"])
    else:
        # 未簽署文件，預覽原始文件
        file_path = document["file_path"]
        filename = document["original_filename"]
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件檔案不存在"
        )
    
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": "inline"}  # 設置為 inline 以支持 iframe 預覽
    )

@router.post("/{document_id}/sign", response_model=Document)
async def sign_document(
    document_id: str,
    request_data: dict,
    current_user = Depends(get_current_active_user)
):
    """簽署文件"""
    db = await get_database()
    
    document = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 檢查文件狀態
    if document["status"] != "uploaded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件已被簽署"
        )
    
    # 生成簽署後的檔名
    signed_filename = f"{current_user['username']}-{document['original_filename']}"
    signed_file_path = os.path.join(settings.signed_doc_path, signed_filename)
    
    # 確保目錄存在
    os.makedirs(settings.signed_doc_path, exist_ok=True)
    
    # 解析簽名數據
    import json
    signature_data = json.loads(request_data.get("signature_data", "{}"))
    signature_image = signature_data.get("signature_image")
    
    if signature_image:
        # 使用 PDF 工具添加簽名
        from app.utils.pdf_utils import add_signature_to_pdf
        
        success = add_signature_to_pdf(
            original_pdf_path=document["file_path"],
            signature_image_data=signature_image,
            signature_info=signature_data,
            output_path=signed_file_path
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="PDF 簽名處理失敗"
            )
    else:
        # 如果沒有簽名圖像，只複製文件
        shutil.copy2(document["file_path"], signed_file_path)
    
    # 創建新的已簽署文件記錄
    signed_document_data = {
        "filename": document["filename"],  # 保持原始文件名
        "original_filename": document["original_filename"],
        "file_path": document["file_path"],  # 原始文件路徑
        "file_size": document["file_size"],
        "status": "signed",
        "uploaded_by": document["uploaded_by"],
        "signed_by": current_user["username"],
        "signed_at": datetime.utcnow(),
        "signed_filename": signed_filename,
        "signed_file_path": signed_file_path,
        "signature_data": request_data.get("signature_data"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    doc_exists = await db.documents.find_one({"signed_filename": signed_filename})
    if doc_exists:
        result = await db.documents.update_one({"_id": doc_exists["_id"]}, {"$set": signed_document_data})
    else:
        result = await db.documents.insert_one(signed_document_data)
    new_document = await db.documents.find_one({"_id": result.inserted_id})
    
    return {
        "id": str(new_document["_id"]),
        "filename": new_document["filename"],
        "original_filename": new_document["original_filename"],
        "file_path": new_document["file_path"],
        "file_size": new_document["file_size"],
        "status": new_document["status"],
        "uploaded_by": new_document["uploaded_by"],
        "signed_by": new_document.get("signed_by"),
        "signed_filename": new_document.get("signed_filename"),
        "created_at": new_document["created_at"],
        "updated_at": new_document["updated_at"]
    }

@router.get("/{document_id}/download")
async def download_signed_document(document_id: str, current_user = Depends(get_current_active_user)):
    """下載簽署後的文件"""
    db = await get_database()
    
    document = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 檢查權限
    if (document.get("signed_by","") != current_user["username"] and current_user["role"] != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限下載此文件"
        )
    
    # 檢查文件狀態
    if document["status"] != "signed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件尚未簽署"
        )
    
    file_path = document["signed_file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="簽署文件不存在"
        )
    
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=document["signed_filename"]
    )

@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user = Depends(get_current_active_user)):
    """刪除文件（管理員可刪除所有文件，一般用戶只能刪除自己簽署的文件）"""
    db = await get_database()
    
    document = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 權限檢查：管理員可以刪除所有文件，一般用戶只能刪除自己簽署的文件
    if current_user["role"] != "admin":
        if not document.get("signed_by") or document["signed_by"] != current_user["username"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您只能刪除自己簽署的文件"
            )
    
    try:
        if document["status"] == "signed":
            # 已簽署文件：只刪除已簽署檔案，保留原始文件
            if document.get("signed_file_path") and os.path.exists(document["signed_file_path"]):
                os.remove(document["signed_file_path"])
                logger.info(f"已刪除已簽署文件: {document['signed_file_path']}")
            
            result = await db.documents.delete_one({"_id": ObjectId(document_id)})
            
            if result.deleted_count > 0:
                user_type = "管理員" if current_user["role"] == "admin" else "用戶"
                logger.info(f"{user_type} {current_user['username']} 已刪除已簽署文件: {document['original_filename']} (ID: {document_id})，文件狀態已恢復為可簽署")
                return {"message": "已簽署文件已刪除，文件恢復為可簽署狀態"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="更新文件狀態失敗"
                )
        else:
            # 未簽署文件：刪除原始檔案和資料庫記錄
            if os.path.exists(document["file_path"]):
                os.remove(document["file_path"])
                logger.info(f"已刪除原始文件: {document['file_path']}")
            
            # 從資料庫刪除記錄
            result = await db.documents.delete_one({"_id": ObjectId(document_id)})
            
            if result.deleted_count > 0:
                user_type = "管理員" if current_user["role"] == "admin" else "用戶"
                logger.info(f"{user_type} {current_user['username']} 已刪除文件: {document['original_filename']} (ID: {document_id})")
                return {"message": "文件已刪除"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="刪除文件記錄失敗"
                )
            
    except OSError as e:
        logger.error(f"刪除實體文件時發生錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刪除實體文件失敗"
        )
    except Exception as e:
        logger.error(f"刪除文件時發生未知錯誤: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刪除文件失敗"
        )
