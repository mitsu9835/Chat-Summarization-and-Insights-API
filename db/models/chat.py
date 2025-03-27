"""
Database models for chat messages and related data.
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId class that works with Pydantic models."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class ChatMessage(BaseModel):
    """Model representing a single chat message."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    conversation_id: str
    message_id: str
    message_content: str
    user_id: str
    user_type: Literal["customer", "support_agent"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic model configuration."""
        populate_by_name = True  # Updated from allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "conversation_id": "conv123",
                "message_id": "msg456",
                "message_content": "Hello, I need help with my order.",
                "user_id": "customer123",
                "user_type": "customer",
                "timestamp": "2023-10-15T14:30:00"
            }
        }


class ConversationSummary(BaseModel):
    """Model representing a conversation summary with insights."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    conversation_id: str
    summary: str
    action_items: List[str] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    outcome: Literal["yes", "no", "maybe", "curious"]
    keywords: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic model configuration."""
        populate_by_name = True  # Updated from allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "conversation_id": "conv123",
                "summary": "Customer had an issue with order #12345 and requested a refund.",
                "action_items": ["Process refund for order #12345", "Update customer profile"],
                "decisions": ["Refund approved"],
                "questions": ["When will the refund be processed?"],
                "sentiment": "neutral",
                "outcome": "yes",
                "keywords": ["refund", "order", "shipping"],
                "created_at": "2023-10-15T14:45:00",
                "updated_at": "2023-10-15T14:45:00"
            }
        }