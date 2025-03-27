"""
Base class for LLM service integration.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from db.models.chat import ChatMessage, ConversationSummary


class LLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    async def generate_summary(self, messages: List[ChatMessage]) -> str:
        """
        Generate a summary of a conversation.
        
        Args:
            messages: List of chat messages
            
        Returns:
            A summary of the conversation
        """
        pass
    
    @abstractmethod
    async def extract_action_items(self, messages: List[ChatMessage]) -> List[str]:
        """
        Extract action items from a conversation.
        
        Args:
            messages: List of chat messages
            
        Returns:
            List of action items
        """
        pass
    
    @abstractmethod
    async def extract_decisions(self, messages: List[ChatMessage]) -> List[str]:
        """
        Extract decisions from a conversation.
        
        Args:
            messages: List of chat messages
            
        Returns:
            List of decisions
        """
        pass
    
    @abstractmethod
    async def extract_questions(self, messages: List[ChatMessage]) -> List[str]:
        """
        Extract questions from a conversation.
        
        Args:
            messages: List of chat messages
            
        Returns:
            List of questions
        """
        pass
    
    @abstractmethod
    async def analyze_sentiment(self, messages: List[ChatMessage]) -> str:
        """
        Analyze the sentiment of a conversation.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Sentiment classification (positive, negative, neutral, mixed)
        """
        pass
    
    @abstractmethod
    async def determine_outcome(self, messages: List[ChatMessage]) -> str:
        """
        Determine the outcome of a conversation.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Outcome classification (yes, no, maybe, curious)
        """
        pass
    
    @abstractmethod
    async def extract_keywords(self, messages: List[ChatMessage]) -> List[str]:
        """
        Extract keywords from a conversation.
        
        Args:
            messages: List of chat messages
            
        Returns:
            List of keywords
        """
        pass
    
    @abstractmethod
    async def generate_full_insights(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """
        Generate all insights for a conversation in a single call.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Dictionary with all insights
        """
        pass 