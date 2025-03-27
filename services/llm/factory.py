"""
Factory for creating LLM service instances.
"""
from typing import Optional
from services.llm.base import LLMService
from services.llm.mock_llm import MockLLMService
from services.llm.grok import GrokLLMService
from services.llm.gemini import GeminiLLMService
from config.settings import settings
from config.logging import logger


class LLMServiceFactory:
    """Factory for creating appropriate LLM service instances."""
    
    @staticmethod
    def create_llm_service(provider: Optional[str] = None) -> LLMService:
        """
        Create and return an LLM service instance.
        
        Args:
            provider: Optional provider name ('grok', 'gemini', or 'mock')
                     If None, uses the best available provider
                     
        Returns:
            LLM service instance
        """
        # If provider is specified, use that
        if provider:
            if provider.lower() == "grok":
                if settings.GROK_API_KEY:
                    logger.info("Using Grok LLM service")
                    return GrokLLMService()
                else:
                    logger.warning("Grok API key not available, falling back to mock")
                    return MockLLMService()
            
            elif provider.lower() == "gemini":
                if settings.GEMINI_API_KEY:
                    logger.info("Using Gemini LLM service")
                    return GeminiLLMService()
                else:
                    logger.warning("Gemini API key not available, falling back to mock")
                    return MockLLMService()
            
            elif provider.lower() == "mock":
                logger.info("Using Mock LLM service")
                return MockLLMService()
            
            else:
                logger.warning(f"Unknown provider '{provider}', using Mock LLM service")
                return MockLLMService()
        
        # If no provider specified, try them in priority order
        if settings.GROK_API_KEY:
            logger.info("Using Grok LLM service")
            return GrokLLMService()
        
        elif settings.GEMINI_API_KEY:
            logger.info("Using Gemini LLM service")
            return GeminiLLMService()
        
        else:
            logger.warning("No API keys available, using Mock LLM service")
            return MockLLMService() 