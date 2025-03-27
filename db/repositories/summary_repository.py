"""
Repository for conversation summary operations.
"""
from typing import Optional
from datetime import datetime
from db.mongodb import MongoDB
from db.models.chat import ConversationSummary
from config.logging import logger


class SummaryRepository:
    """Repository for conversation summary operations."""
    
    @staticmethod
    async def create_or_update_summary(summary: ConversationSummary) -> ConversationSummary:
        """
        Create or update a conversation summary.
        
        Args:
            summary: The summary to store
            
        Returns:
            The stored summary
        """
        try:
            summary.updated_at = datetime.utcnow()
            
            # Use find_one_and_replace with upsert for atomic operation
            result = await MongoDB.db.conversation_summaries.find_one_and_replace(
                {"conversation_id": summary.conversation_id},
                summary.model_dump(by_alias=True),
                upsert=True,
                return_document=True
            )
            
            return ConversationSummary(**result) if result else summary
        except Exception as e:
            logger.error(f"Failed to create/update summary: {e}")
            raise
    
    @staticmethod
    async def get_summary(conversation_id: str) -> Optional[ConversationSummary]:
        """
        Retrieve a conversation summary.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            The conversation summary if found, None otherwise
        """
        try:
            result = await MongoDB.db.conversation_summaries.find_one(
                {"conversation_id": conversation_id}
            )
            
            if result:
                return ConversationSummary(**result)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve summary: {e}")
            raise 