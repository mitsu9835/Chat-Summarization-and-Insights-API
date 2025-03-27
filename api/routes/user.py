"""
API routes for user operations.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from typing import Dict, Any
from db.models.user import User
from db.repositories.chat_repository import ChatRepository
from api.dependencies import get_current_user
from config.logging import logger


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}/chats", response_model=Dict[str, Any])
async def get_user_chats(
    user_id: str = Path(..., description="The ID of the user"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve paginated chat history for a specific user.
    
    Args:
        user_id: The ID of the user
        page: Page number (starting from 1)
        limit: Number of conversations per page
        current_user: The authenticated user
        
    Returns:
        Dictionary with conversations and pagination info
    """
    # Simple authorization check
    if current_user.role != "admin" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's chats"
        )
    
    try:
        return await ChatRepository.get_user_conversations(
            user_id=user_id,
            page=page,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error retrieving user chats: {e}") 