"""
Gemini API integration for LLM services.
"""
import json
import aiohttp
from typing import List, Dict, Any, Optional
from services.llm.base import LLMService
from db.models.chat import ChatMessage
from config.settings import settings
from config.logging import logger


class GeminiLLMService(LLMService):
    """LLM service implementation using Google's Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini LLM service."""
        self.api_key = settings.GEMINI_API_KEY
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
        if not self.api_key:
            logger.warning("No Gemini API key provided. LLM features will not work properly.")
    
    def _format_chat_history(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """
        Format chat messages for Gemini API.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Formatted messages for Gemini API
        """
        formatted_messages = []
        
        for msg in messages:
            role = "user" if msg.user_type == "customer" else "model"
            formatted_messages.append({
                "role": role,
                "parts": [{"text": msg.message_content}]
            })
        
        return formatted_messages
    
    async def _call_gemini_api(self, messages: List[Dict[str, Any]], 
                              system_prompt: str) -> Optional[str]:
        """
        Call the Gemini API with the given messages.
        
        Args:
            messages: Formatted messages for Gemini API
            system_prompt: System prompt for Gemini
            
        Returns:
            The response content or None if error
        """
        if not self.api_key:
            logger.error("Cannot call Gemini API: No API key provided")
            return None
        
        # Insert system prompt as first user message if provided
        if system_prompt:
            messages.insert(0, {
                "role": "user",
                "parts": [{"text": f"System: {system_prompt}\n\nUser: "}]
            })
        
        # Create the request payload
        payload = {
            "contents": messages,
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.8,
                "topK": 40,
                "maxOutputTokens": 1000
            }
        }
        
        # Make the API request
        try:
            url = f"{self.api_url}?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    headers=headers, 
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Gemini API error: {response.status}, {error_text}")
                        return None
                    
                    result = await response.json()
                    try:
                        return result["candidates"][0]["content"]["parts"][0]["text"]
                    except (KeyError, IndexError) as e:
                        logger.error(f"Unexpected Gemini API response structure: {e}")
                        return None
        
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None
    
    async def generate_summary(self, messages: List[ChatMessage]) -> str:
        """Generate a summary of a conversation."""
        formatted_messages = self._format_chat_history(messages)
        
        system_prompt = (
            "You are a helpful assistant that summarizes customer service conversations. "
            "Provide a concise summary of the main points discussed, issues raised, "
            "and resolutions reached. Focus on facts and avoid personal opinions."
        )
        
        response = await self._call_gemini_api(formatted_messages, system_prompt)
        
        if not response:
            return "Failed to generate summary."
        
        return response
    
    async def extract_action_items(self, messages: List[ChatMessage]) -> List[str]:
        """Extract action items from a conversation."""
        formatted_messages = self._format_chat_history(messages)
        
        system_prompt = (
            "Extract a list of action items from this customer service conversation. "
            "Action items are specific tasks that need to be completed by either party. "
            "Format your response as a JSON array of strings, each representing one action item."
        )
        
        response = await self._call_gemini_api(formatted_messages, system_prompt)
        
        if not response:
            return []
        
        try:
            # Try to parse the response as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If not valid JSON, try to extract lines as action items
            lines = [line.strip() for line in response.split('\n')]
            # Remove empty lines and lines that seem to be headers
            return [line for line in lines if line and not line.endswith(':')]
    
    async def extract_decisions(self, messages: List[ChatMessage]) -> List[str]:
        """Extract decisions from a conversation."""
        formatted_messages = self._format_chat_history(messages)
        
        system_prompt = (
            "Extract a list of decisions made during this customer service conversation. "
            "Decisions are choices or determinations that were agreed upon. "
            "Format your response as a JSON array of strings, each representing one decision."
        )
        
        response = await self._call_gemini_api(formatted_messages, system_prompt)
        
        if not response:
            return []
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            lines = [line.strip() for line in response.split('\n')]
            return [line for line in lines if line and not line.endswith(':')]
    
    async def extract_questions(self, messages: List[ChatMessage]) -> List[str]:
        """Extract questions from a conversation."""
        formatted_messages = self._format_chat_history(messages)
        
        system_prompt = (
            "Extract a list of questions raised during this customer service conversation. "
            "Include both answered and unanswered questions. "
            "Format your response as a JSON array of strings, each representing one question."
        )
        
        response = await self._call_gemini_api(formatted_messages, system_prompt)
        
        if not response:
            return []
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            lines = [line.strip() for line in response.split('\n')]
            return [line for line in lines if line and line.endswith('?')]
    
    async def analyze_sentiment(self, messages: List[ChatMessage]) -> str:
        """Analyze the sentiment of a conversation."""
        formatted_messages = self._format_chat_history(messages)
        
        system_prompt = (
            "Analyze the overall sentiment of this customer service conversation. "
            "Respond with exactly one word: 'positive', 'negative', 'neutral', or 'mixed'."
        )
        
        response = await self._call_gemini_api(formatted_messages, system_prompt)
        
        if not response:
            return "neutral"
        
        # Normalize the response
        response = response.lower().strip()
        valid_sentiments = ["positive", "negative", "neutral", "mixed"]
        
        # Check if response is already a valid sentiment
        if response in valid_sentiments:
            return response
        
        # Otherwise map to closest valid sentiment
        if "positive" in response:
            return "positive"
        elif "negative" in response:
            return "negative"
        elif "mixed" in response:
            return "mixed"
        else:
            return "neutral"
    
    async def determine_outcome(self, messages: List[ChatMessage]) -> str:
        """Determine the outcome of a conversation."""
        formatted_messages = self._format_chat_history(messages)
        
        system_prompt = (
            "Determine the outcome of this customer service conversation. "
            "Respond with exactly one word: "
            "'yes' (issue resolved), "
            "'no' (issue not resolved), "
            "'maybe' (unclear if resolved), or "
            "'curious' (question was asked but not answered)."
        )
        
        response = await self._call_gemini_api(formatted_messages, system_prompt)
        
        if not response:
            return "maybe"
        
        # Normalize the response
        response = response.lower().strip()
        valid_outcomes = ["yes", "no", "maybe", "curious"]
        
        # Check if response is already a valid outcome
        if response in valid_outcomes:
            return response
        
        # Otherwise map to closest valid outcome
        if "yes" in response or "resolved" in response:
            return "yes"
        elif "no" in response or "not resolved" in response:
            return "no"
        elif "curious" in response or "question" in response:
            return "curious"
        else:
            return "maybe"
    
    async def extract_keywords(self, messages: List[ChatMessage]) -> List[str]:
        """Extract keywords from a conversation."""
        formatted_messages = self._format_chat_history(messages)
        
        system_prompt = (
            "Extract the 5-10 most important keywords or phrases from this customer service conversation. "
            "Focus on terms that capture the main topics, products, or issues discussed. "
            "Format your response as a JSON array of strings."
        )
        
        response = await self._call_gemini_api(formatted_messages, system_prompt)
        
        if not response:
            return []
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # If not valid JSON, look for keywords separated by commas
            keywords = [k.strip() for k in response.split(',')]
            return [k for k in keywords if k and len(k) > 1]
    
    async def generate_full_insights(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """Generate all insights for a conversation in a single call."""
        formatted_messages = self._format_chat_history(messages)
        
        system_prompt = (
            "Analyze this customer service conversation and provide the following insights in JSON format:\n"
            "1. summary: A concise summary of the conversation\n"
            "2. action_items: Array of action items to be completed\n"
            "3. decisions: Array of decisions made during the conversation\n"
            "4. questions: Array of questions raised during the conversation\n"
            "5. sentiment: Overall sentiment as 'positive', 'negative', 'neutral', or 'mixed'\n"
            "6. outcome: Conversation outcome as 'yes', 'no', 'maybe', or 'curious'\n"
            "7. keywords: Array of 5-10 important keywords or phrases\n\n"
            "Respond with valid JSON only."
        )
        
        response = await self._call_gemini_api(formatted_messages, system_prompt)
        
        if not response:
            # Return default values if API call fails
            return {
                "summary": "Failed to generate summary.",
                "action_items": [],
                "decisions": [],
                "questions": [],
                "sentiment": "neutral",
                "outcome": "maybe",
                "keywords": []
            }
        
        try:
            # Try to parse the response as JSON
            insights = json.loads(response)
            
            # Ensure all expected fields are present
            default_insights = {
                "summary": "Failed to generate summary.",
                "action_items": [],
                "decisions": [],
                "questions": [],
                "sentiment": "neutral",
                "outcome": "maybe",
                "keywords": []
            }
            
            for key in default_insights:
                if key not in insights:
                    insights[key] = default_insights[key]
            
            return insights
        
        except json.JSONDecodeError:
            logger.error("Failed to parse Gemini API response as JSON")
            
            # If we can't parse JSON, fall back to individual API calls
            return {
                "summary": await self.generate_summary(messages),
                "action_items": await self.extract_action_items(messages),
                "decisions": await self.extract_decisions(messages),
                "questions": await self.extract_questions(messages),
                "sentiment": await self.analyze_sentiment(messages),
                "outcome": await self.determine_outcome(messages),
                "keywords": await self.extract_keywords(messages)
            }