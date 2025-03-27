"""
Repository for user-related database operations.
"""
from typing import Optional
from datetime import datetime
from db.mongodb import MongoDB
from db.models.user import User
from config.logging import logger


class UserRepository:
    """Repository for user operations."""
    
    @staticmethod
    async def create_user(user: User) -> User:
        """
        Create a new user.
        
        Args:
            user: The user to create
            
        Returns:
            The created user with ID
        """
        try:
            result = await MongoDB.db.users.insert_one(
                user.model_dump(by_alias=True)
            )
            user.id = result.inserted_id
            return user
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            The user if found, None otherwise
        """
        try:
            result = await MongoDB.db.users.find_one({"email": email})
            if result:
                return User(**result)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve user by email: {e}")
            raise
    
    @staticmethod
    async def get_user_by_api_key(api_key: str) -> Optional[User]:
        """
        Get a user by API key.
        
        Args:
            api_key: The API key to search for
            
        Returns:
            The user if found, None otherwise
        """
        try:
            result = await MongoDB.db.users.find_one({"api_key": api_key})
            if result:
                return User(**result)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve user by API key: {e}")
            raise
    
    @staticmethod
    async def update_last_login(user_id: str) -> bool:
        """
        Update the last login timestamp for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            True if updated, False otherwise
        """
        try:
            result = await MongoDB.db.users.update_one(
                {"_id": user_id},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
            raise 