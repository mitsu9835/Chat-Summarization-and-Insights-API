"""
API routes for summarization and insights.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Body, Path
from typing import List, Dict, Any
from db.models.chat import ConversationSummary, ChatMessage
from db.models.user import User
from db.repositories.chat_repository import ChatRepository
from db.repositories.summary_repository import SummaryRepository
from services.llm.base import LLMService
from api.dependencies import get_current_user, get_llm_service
from config.logging import logger


router = APIRouter(prefix="/chats", tags=["summarization"])


@router.post("/summarize", response_model=ConversationSummary)
async def summarize_conversation(
    conversation_id: str = Body(..., embed=True, description="The ID of the conversation to summarize"),
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate a summary for a conversation.
    
    Args:
        conversation_id: The ID of the conversation
        current_user: The authenticated user
        llm_service: The LLM service
        
    Returns:
        The generated summary
    """
    try:
        # Check if summary already exists
        existing_summary = await SummaryRepository.get_summary(conversation_id)
        if existing_summary:
            return existing_summary
        
        # Get the conversation messages
        messages = await ChatRepository.get_conversation(conversation_id)
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        # Generate insights using LLM
        insights = await llm_service.generate_full_insights(messages)
        
        # Create the summary object
        summary = ConversationSummary(
            conversation_id=conversation_id,
            summary=insights["summary"],
            action_items=insights["action_items"],
            decisions=insights["decisions"],
            questions=insights["questions"],
            sentiment=insights["sentiment"],
            outcome=insights["outcome"],
            keywords=insights["keywords"]
        )
        
        # Store the summary
        created_summary = await SummaryRepository.create_or_update_summary(summary)
        
        return created_summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to summarize conversation"
        )


@router.get("/{conversation_id}/summary", response_model=ConversationSummary)
async def get_conversation_summary(
    conversation_id: str = Path(..., description="The ID of the conversation"),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve an existing summary for a conversation.
    
    Args:
        conversation_id: The ID of the conversation
        current_user: The authenticated user
        
    Returns:
        The conversation summary
    """
    try:
        summary = await SummaryRepository.get_summary(conversation_id)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Summary for conversation {conversation_id} not found"
            )
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve summary"
        )


@router.post("/insights", response_model=Dict[str, Any])
async def generate_insights(
    messages: List[ChatMessage] = Body(..., description="List of chat messages to analyze"),
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate insights for a list of chat messages without storing them.
    
    Args:
        messages: List of chat messages to analyze
        current_user: The authenticated user
        llm_service: The LLM service
        
    Returns:
        Dictionary with generated insights
    """
    try:
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No messages provided"
            )
        
        # Generate insights using LLM
        insights = await llm_service.generate_full_insights(messages)
        
        return insights
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate insights"
        ) 