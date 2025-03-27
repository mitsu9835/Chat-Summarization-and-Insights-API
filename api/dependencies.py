"""
FastAPI dependencies for route handlers.
"""
from fastapi import Header, HTTPException, status, Depends, Query
from typing import Optional
from db.repositories.user_repository import UserRepository
from db.models.user import User
from services.llm.factory import LLMServiceFactory
from services.llm.base import LLMService
from config.logging import logger


async def get_current_user(x_api_key: Optional[str] = Header(None)) -> User:
    """
    Dependency to get the current user from API key.
    
    Args:
        x_api_key: API key from header
        
    Returns:
        User object
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    user = await UserRepository.get_user_by_api_key(x_api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return user


def get_llm_service(provider: Optional[str] = Query(None, description="LLM provider to use")) -> LLMService:
    """
    Dependency to get the LLM service.
    
    Args:
        provider: Optional LLM provider name (grok, gemini, mock)
        
    Returns:
        LLM service instance
    """
    return LLMServiceFactory.create_llm_service(provider) 