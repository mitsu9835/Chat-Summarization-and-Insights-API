"""
Database models for users and authentication.
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from db.models.chat import PyObjectId


class User(BaseModel):
    """Model representing a user of the API."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    name: str
    auth_provider: Literal["google", "github"]
    provider_id: str
    api_key: Optional[str] = None
    role: Literal["admin", "user"] = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        """Pydantic model configuration."""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "auth_provider": "google",
                "provider_id": "123456789",
                "role": "user",
                "created_at": "2023-10-15T14:30:00"
            }
        } 