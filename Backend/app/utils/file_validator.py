"""
File validation utilities for the AI Data Analyst platform.
"""

import os
import pandas as pd
from fastapi import UploadFile
from typing import List, Optional

from app.core.exceptions import (
    UnsupportedFileTypeError, 
    FileSizeError, 
    FileProcessingError,
    DataParsingError
)

# Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json'}
ALLOWED_CONTENT_TYPES = {
    'text/csv',
    'application/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/json'
}


def validate_file_type(filename: str, content_type: Optional[str] = None) -> None:
    """
    Validate file type based on extension and content type.
    
    Args:
        filename: Name of the file
        content_type: MIME type of the file
        
    Raises:
        UnsupportedFileTypeError: If file type is not supported
    """
    if not filename:
        raise UnsupportedFileTypeError("Filename is required")
    
    # Check file extension
    file_ext = os.path.splitext(filename.lower())[1]
    if file_ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{file_ext}'. "
            f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check content type if provided
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise UnsupportedFileTypeError(
            f"Unsupported content type '{content_type}'. "
            f"File extension '{file_ext}' suggests a supported format, "
            f"but content type doesn't match."
        )


def validate_file_size(file_size: int) -> None:
    """
    Validate file size.
    
    Args:
        file_size: Size of the file in bytes
        
    Raises:
        FileSizeError: If file is too large
    """
    if file_size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        actual_size_mb = file_size / (1024 * 1024)
        raise FileSizeError(
            f"File too large: {actual_size_mb:.1f}MB. "
            f"Maximum allowed size: {max_size_mb}MB"
        )


def validate_upload_file(file: UploadFile) -> None:
    """
    Validate an uploaded file.
    
    Args:
        file: FastAPI UploadFile object
        
    Raises:
        UnsupportedFileTypeError: If file type is not supported
        FileSizeError: If file is too large
        FileProcessingError: If file cannot be processed
    """
    if not file.filename:
        raise FileProcessingError("No file provided")
    
    # Validate file type
    validate_file_type(file.filename, file.content_type)
    
    # Get file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    # Validate file size
    validate_file_size(file_size)


def validate_dataframe_content(df: pd.DataFrame, min_rows: int = 1, min_cols: int = 1) -> None:
    """
    Validate DataFrame content.
    
    Args:
        df: Pandas DataFrame to validate
        min_rows: Minimum number of rows required
        min_cols: Minimum number of columns required
        
    Raises:
        DataParsingError: If DataFrame doesn't meet requirements
    """
    if df is None:
        raise DataParsingError("Failed to parse data from file")
    
    if df.empty:
        raise DataParsingError("File contains no data")
    
    if len(df) < min_rows:
        raise DataParsingError(f"File must contain at least {min_rows} rows of data")
    
    if len(df.columns) < min_cols:
        raise DataParsingError(f"File must contain at least {min_cols} columns")
    
    # Check for completely empty columns
    empty_cols = df.columns[df.isnull().all()].tolist()
    if empty_cols:
        raise DataParsingError(f"File contains completely empty columns: {empty_cols}")


def get_file_info(file_path: str) -> dict:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    if not os.path.exists(file_path):
        raise FileProcessingError(f"File not found: {file_path}")
    
    file_stat = os.stat(file_path)
    file_ext = os.path.splitext(file_path.lower())[1]
    
    return {
        'filename': os.path.basename(file_path),
        'extension': file_ext,
        'size_bytes': file_stat.st_size,
        'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
        'created': file_stat.st_ctime,
        'modified': file_stat.st_mtime
    }
