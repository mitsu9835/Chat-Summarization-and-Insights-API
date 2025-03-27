"""
API routes for chat operations.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from typing import List, Dict, Any, Optional
from db.models.chat import ChatMessage
from db.models.user import User
from db.repositories.chat_repository import ChatRepository
from api.dependencies import get_current_user
from config.logging import logger


router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("/", response_model=ChatMessage, status_code=status.HTTP_201_CREATED)
async def create_chat_message(
    message: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    """
    Store a new chat message.
    
    Args:
        message: The chat message to store
        current_user: The authenticated user
        
    Returns:
        The stored chat message
    """
    try:
        return await ChatRepository.create_message(message)
    except Exception as e:
        logger.error(f"Error creating chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store chat message"
        )


@router.get("/{conversation_id}", response_model=List[ChatMessage])
async def get_conversation(
    conversation_id: str = Path(..., description="The ID of the conversation to retrieve"),
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of messages to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve messages from a conversation.
    
    Args:
        conversation_id: The ID of the conversation
        skip: Number of messages to skip (for pagination)
        limit: Maximum number of messages to return
        current_user: The authenticated user
        
    Returns:
        List of chat messages
    """
    try:
        messages = await ChatRepository.get_conversation(
            conversation_id=conversation_id,
            skip=skip,
            limit=limit
        )
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        return messages
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str = Path(..., description="The ID of the conversation to delete"),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a conversation and its summary.
    
    Args:
        conversation_id: The ID of the conversation to delete
        current_user: The authenticated user
        
    Returns:
        Nothing
    """
    try:
        deleted = await ChatRepository.delete_conversation(conversation_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conversation_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        ) 