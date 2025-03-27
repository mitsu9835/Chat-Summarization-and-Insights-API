"""
Script to import cleaned_data.csv into the database.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.csv_importer import CSVImporter
from db.mongodb import MongoDB
from config.settings import settings
from config.logging import logger


async def import_cleaned_data():
    """Import the cleaned_data.csv file into the database."""
    # Connect to database
    logger.info("Connecting to MongoDB...")
    await MongoDB.connect_to_database()
    
    # Path to CSV file
    csv_path = "cleaned_data.csv"
    
    # Check if file exists
    if not os.path.exists(csv_path):
        logger.error(f"File not found: {csv_path}")
        print(f"File not found: {csv_path}")
        return
    
    # Import data
    try:
        logger.info(f"Starting import of {csv_path}...")
        stats = await CSVImporter.import_from_file(csv_path)
        
        # Print results
        print(f"Import completed:")
        print(f"- Total rows: {stats['total_rows']}")
        print(f"- Processed: {stats['processed']}")
        print(f"- Successful: {stats['successful']}")
        print(f"- Failed: {stats['failed']}")
        print(f"- Conversations: {stats['conversation_count']}")
        
    except Exception as e:
        logger.error(f"Error importing data: {e}")
        print(f"Error importing data: {e}")
    
    # Close database connection
    await MongoDB.close_database_connection()


if __name__ == "__main__":
    asyncio.run(import_cleaned_data()) 