"""
API routes for importing data.
"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, BackgroundTasks
import os
import tempfile
import shutil
from typing import Dict, Any
from db.models.user import User
from utils.csv_importer import CSVImporter
from api.dependencies import get_current_user
from config.logging import logger


router = APIRouter(prefix="/import", tags=["import"])


@router.post("/csv", response_model=Dict[str, Any])
async def import_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Import chat data from a CSV file.
    
    Args:
        background_tasks: FastAPI background tasks
        file: The CSV file to upload
        current_user: The authenticated user
        
    Returns:
        Import statistics
    """
    # Check file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    
    try:
        # Write uploaded file to temp file
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()
        
        # Import the CSV data
        stats = await CSVImporter.import_from_file(temp_file.name)
        
        return {
            "filename": file.filename,
            "status": "success",
            "stats": stats
        }
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CSV file not found"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error importing CSV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing CSV: {str(e)}"
        )
    finally:
        # Clean up the temp file
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


@router.post("/csv/file", response_model=Dict[str, Any])
async def import_csv_from_path(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """
    Import chat data from a CSV file on the server.
    
    Args:
        file_path: The path to the CSV file on the server
        current_user: The authenticated user
        
    Returns:
        Import statistics
    """
    try:
        # Import the CSV data
        stats = await CSVImporter.import_from_file(file_path)
        
        return {
            "filename": os.path.basename(file_path),
            "status": "success",
            "stats": stats
        }
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CSV file not found: {file_path}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error importing CSV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing CSV: {str(e)}"
        ) 