"""
Utility for importing chat data from CSV files.
"""
import csv
import os
from typing import List, Optional
from datetime import datetime
import uuid
import pandas as pd
from db.models.chat import ChatMessage
from db.repositories.chat_repository import ChatRepository
from config.logging import logger


class CSVImporter:
    """Class to import chat data from CSV files."""
    
    @staticmethod
    async def import_from_file(
        file_path: str, 
        conversation_id_column: str = "conversation_id",
        message_id_column: str = "message_id",
        message_content_column: str = "message_content",
        user_id_column: str = "user_id",
        user_type_column: str = "user_type",
        timestamp_column: str = "timestamp"
    ) -> dict:
        """
        Import chat data from a CSV file into the database.
        
        Args:
            file_path: Path to the CSV file
            conversation_id_column: Column name for conversation IDs
            message_id_column: Column name for message IDs
            message_content_column: Column name for message content
            user_id_column: Column name for user IDs
            user_type_column: Column name for user types
            timestamp_column: Column name for timestamps
            
        Returns:
            Dictionary with import statistics
        """
        if not os.path.exists(file_path):
            logger.error(f"CSV file not found: {file_path}")
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        try:
            # Read CSV using pandas for better handling of various formats
            df = pd.read_csv(file_path)
            logger.info(f"Read {len(df)} rows from CSV file")
            
            # Validate columns
            required_columns = [
                conversation_id_column,
                message_id_column,
                message_content_column,
                user_id_column,
                user_type_column,
                timestamp_column
            ]
            
            for column in required_columns:
                if column not in df.columns:
                    logger.error(f"Required column '{column}' not found in CSV")
                    raise ValueError(f"Required column '{column}' not found in CSV")
            
            # Import statistics
            stats = {
                "total_rows": len(df),
                "processed": 0,
                "successful": 0,
                "failed": 0,
                "conversations": set()
            }
            
            # Process each row
            for index, row in df.iterrows():
                stats["processed"] += 1
                
                try:
                    # Get values
                    conversation_id = str(row[conversation_id_column])
                    message_id = str(row[message_id_column])
                    message_content = str(row[message_content_column])
                    user_id = str(row[user_id_column])
                    user_type = str(row[user_type_column])
                    
                    # Handle timestamp
                    try:
                        timestamp = pd.to_datetime(row[timestamp_column])
                    except:
                        # Default to current time if timestamp is invalid
                        logger.warning(f"Invalid timestamp in row {index}, using current time")
                        timestamp = datetime.utcnow()
                    
                    # Validate user_type
                    if user_type not in ["customer", "support_agent"]:
                        logger.warning(f"Invalid user_type '{user_type}' in row {index}, defaulting to 'customer'")
                        user_type = "customer"
                    
                    # Create message object
                    message = ChatMessage(
                        conversation_id=conversation_id,
                        message_id=message_id,
                        message_content=message_content,
                        user_id=user_id,
                        user_type=user_type,
                        timestamp=timestamp
                    )
                    
                    # Store in database
                    await ChatRepository.create_message(message)
                    
                    # Update statistics
                    stats["successful"] += 1
                    stats["conversations"].add(conversation_id)
                    
                except Exception as e:
                    logger.error(f"Error processing row {index}: {str(e)}")
                    stats["failed"] += 1
            
            # Convert set to list for easier serialization
            stats["conversations"] = list(stats["conversations"])
            stats["conversation_count"] = len(stats["conversations"])
            
            logger.info(f"CSV import completed: {stats['successful']} messages imported, "
                       f"{stats['failed']} failed, {stats['conversation_count']} conversations")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error importing CSV: {str(e)}")
            raise 