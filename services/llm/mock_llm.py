"""
Mock LLM service for development and testing.
"""
from typing import List, Dict, Any
import asyncio
import random
from services.llm.base import LLMService
from db.models.chat import ChatMessage
from config.logging import logger


class MockLLMService(LLMService):
    """Mock LLM service that returns predefined responses."""
    
    async def generate_summary(self, messages: List[ChatMessage]) -> str:
        """Generate a mock summary."""
        logger.info("Generating mock summary")
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        return (
            "This is a mock summary of the conversation. "
        ) 