"""
Utility for extracting chat data from CSV files.
"""
import csv
import os
from typing import List, Optional
from datetime import datetime
import uuid
from db.models.chat import ChatMessage
from config.logging import logger


class ChatExtractor:
    """Class for extracting chat data from various sources."""
    
    @staticmethod
    def extract_from_csv(file_path: str, conversation_id: Optional[str] = None) -> List[ChatMessage]:
        """
        Extract chat messages from a CSV file.
        
        Expected CSV format:
        timestamp,user_id,user_type,message_content
        
        Args:
            file_path: Path to the CSV file
            conversation_id: Optional ID for the conversation (generated if not provided)
            
        Returns:
            List of ChatMessage objects
        """
        if not os.path.exists(file_path):
            logger.error(f"CSV file not found: {file_path}")
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        messages = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                # Skip header row
                next(reader, None)
                
                for row in reader:
                    if len(row) < 4:
                        logger.warning(f"Skipping invalid row: {row}")
                        continue
                    
                    timestamp_str, user_id, user_type, message_content = row
                    
                    try:
                        # Parse timestamp (assuming ISO format)
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except ValueError:
                        # Fallback to current time if parsing fails
                        logger.warning(f"Invalid timestamp format: {timestamp_str}, using current time")
                        timestamp = datetime.utcnow()
                    
                    # Validate user_type
                    if user_type not in ["customer", "support_agent"]:
                        logger.warning(f"Invalid user_type: {user_type}, defaulting to customer")
                        user_type = "customer"
                    
                    # Create message
                    message = ChatMessage(
                        conversation_id=conversation_id,
                        message_id=str(uuid.uuid4()),
                        message_content=message_content,
                        user_id=user_id,
                        user_type=user_type,
                        timestamp=timestamp
                    )
                    
                    messages.append(message)
        
        except Exception as e:
            logger.error(f"Error extracting chat data from CSV: {e}")
            raise
        
        logger.info(f"Extracted {len(messages)} messages from CSV file")
        return messages 