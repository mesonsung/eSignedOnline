from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """連接到 MongoDB"""
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client.esigned
        
        # 測試連接
        await db.client.admin.command('ping')
        logger.info("成功連接到 MongoDB")
        
    except Exception as e:
        logger.error(f"無法連接到 MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """關閉 MongoDB 連接"""
    if db.client:
        db.client.close()
        logger.info("已關閉 MongoDB 連接")
