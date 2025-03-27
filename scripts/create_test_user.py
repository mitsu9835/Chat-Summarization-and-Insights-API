"""
Script to create a test user with API key in the database.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.models.user import User
from db.repositories.user_repository import UserRepository
from db.mongodb import MongoDB
from utils.auth import AuthUtils
from config.settings import settings


async def create_test_user():
    """Create a test user with API key."""
    # Connect to database
    print("Connecting to MongoDB...")
    await MongoDB.connect_to_database()
    
    # Generate API key
    api_key = AuthUtils.generate_api_key()
    
    # Create user
    user = User(api_key=api_key)
    
    # Save user to database
    await UserRepository.create_user(user)
    
    print(f"Test user created successfully. API key: {api_key}")


if __name__ == "__main__":
    asyncio.run(create_test_user()) 