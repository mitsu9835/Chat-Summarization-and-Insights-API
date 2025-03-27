"""
MongoDB connection and database operations.
"""
import motor.motor_asyncio
from typing import Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB connection handler using Motor for async operations."""
    
    client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
    db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect_to_database(cls):
        """Create database connection."""
        try:
            cls.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.DB_NAME]
            logger.info("Connected to MongoDB.")
            
            # Create indexes
            await cls.create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_database_connection(cls):
        """Close database connection."""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection.")
    
    @classmethod
    async def create_indexes(cls):
        """Create necessary indexes for optimization."""
        try:
            # Chat messages indexes
            await cls.db.chat_messages.create_index("conversation_id")
            await cls.db.chat_messages.create_index("user_id")
            await cls.db.chat_messages.create_index("timestamp")
            
            # Summaries indexes
            await cls.db.conversation_summaries.create_index("conversation_id", unique=True)
            
            logger.info("Created MongoDB indexes.")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise