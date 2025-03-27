"""
Authentication utilities.
"""
import secrets
import string
from typing import Dict
from datetime import datetime, timedelta
from jose import jwt
from config.settings import settings
from config.logging import logger


class AuthUtils:
    """Authentication utility functions."""
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """
        Generate a random API key.
        
        Args:
            length: Length of the API key
            
        Returns:
            Random API key string
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def create_access_token(data: Dict, expires_delta: timedelta = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional token expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode, 
                settings.SECRET_KEY, 
                algorithm="HS256"
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise 