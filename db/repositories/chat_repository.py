"""
Repository for chat-related database operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from db.mongodb import MongoDB
from db.models.chat import ChatMessage, ConversationSummary
from config.logging import logger


class ChatRepository:
    """Repository for chat message operations."""
    
    @staticmethod
    async def create_message(message: ChatMessage) -> ChatMessage:
        """
        Store a new chat message in the database.
        
        Args:
            message: The chat message to store
            
        Returns:
            The stored chat message with ID
        """
        try:
            result = await MongoDB.db.chat_messages.insert_one(
                message.model_dump(by_alias=True)  # Updated from dict()
            )
            message.id = result.inserted_id
            return message
        except Exception as e:
            logger.error(f"Failed to create chat message: {e}")
            raise
    
    @staticmethod
    async def get_conversation(
        conversation_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[ChatMessage]:
        """
        Retrieve messages from a conversation with pagination.
        
        Args:
            conversation_id: The ID of the conversation
            skip: Number of messages to skip (for pagination)
            limit: Maximum number of messages to return
            
        Returns:
            List of chat messages
        """
        try:
            cursor = MongoDB.db.chat_messages.find(
                {"conversation_id": conversation_id}
            ).sort("timestamp", 1).skip(skip).limit(limit)
            
            messages = []
            async for document in cursor:
                messages.append(ChatMessage(**document))
            
            return messages
        except Exception as e:
            logger.error(f"Failed to retrieve conversation: {e}")
            raise
    
    @staticmethod
    async def get_user_conversations(
        user_id: str,
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get paginated list of conversations for a user.
        
        Args:
            user_id: The ID of the user
            page: Page number (starting from 1)
            limit: Number of conversations per page
            
        Returns:
            Dictionary with conversations and pagination info
        """
        try:
            skip = (page - 1) * limit
            
            # Get distinct conversation IDs for this user
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$conversation_id"}},
                {"$sort": {"_id": -1}},  # Sort by conversation_id desc
                {"$skip": skip},
                {"$limit": limit}
            ]
            
            cursor = MongoDB.db.chat_messages.aggregate(pipeline)
            
            conversation_ids = []
            async for doc in cursor:
                conversation_ids.append(doc["_id"])
            
            # Get the total count
            total = await MongoDB.db.chat_messages.distinct(
                "conversation_id", {"user_id": user_id}
            )
            total_count = len(total)
            
            # Get the most recent message from each conversation for preview
            conversations = []
            for conv_id in conversation_ids:
                # Get the most recent message
                latest_msg = await MongoDB.db.chat_messages.find_one(
                    {"conversation_id": conv_id},
                    sort=[("timestamp", -1)]
                )
                
                if latest_msg:
                    # Get the total messages in this conversation
                    msg_count = await MongoDB.db.chat_messages.count_documents(
                        {"conversation_id": conv_id}
                    )
                    
                    conversations.append({
                        "conversation_id": conv_id,
                        "last_message": ChatMessage(**latest_msg),
                        "message_count": msg_count
                    })
            
            return {
                "conversations": conversations,
                "pagination": {
                    "total": total_count,
                    "page": page,
                    "limit": limit,
                    "pages": (total_count + limit - 1) // limit  # Ceiling division
                }
            }
        except Exception as e:
            logger.error(f"Failed to retrieve user conversations: {e}")
            raise
    
    @staticmethod
    async def delete_conversation(conversation_id: str) -> bool:
        """
        Delete a conversation and its summary.
        
        Args:
            conversation_id: The ID of the conversation to delete
            
        Returns:
            True if anything was deleted, False otherwise
        """
        try:
            # Delete all messages in the conversation
            result_msgs = await MongoDB.db.chat_messages.delete_many(
                {"conversation_id": conversation_id}
            )
            
            # Delete the summary if it exists
            result_summary = await MongoDB.db.conversation_summaries.delete_one(
                {"conversation_id": conversation_id}
            )
            
            deleted = result_msgs.deleted_count > 0 or result_summary.deleted_count > 0
            logger.info(f"Deleted conversation {conversation_id}: {deleted}")
            
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            raise