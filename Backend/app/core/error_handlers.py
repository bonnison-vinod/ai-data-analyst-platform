"""
Centralized error handling for the AI Data Analyst platform.
"""

import logging
import traceback
from typing import Dict, Any, Optional

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE
)

from app.core.exceptions import (
    DataAnalystException,
    FileProcessingError,
    UnsupportedFileTypeError,
    FileSizeError,
    DataParsingError,
    QueryExecutionError,
    ValidationError,
    ExternalServiceError
)

# Configure logging
logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling class."""
    
    @staticmethod
    def create_error_response(
        status_code: int,
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """
        Create a standardized error response.
        
        Args:
            status_code: HTTP status code
            error_type: Type of error for categorization
            message: Human-readable error message
            details: Additional error details
            request_id: Request ID for tracking
            
        Returns:
            JSONResponse with standardized error format
        """
        error_data = {
            "error": {
                "type": error_type,
                "message": message,
                "timestamp": logger.name,  # Will be set by middleware
            }
        }
        
        if details:
            error_data["error"]["details"] = details
            
        if request_id:
            error_data["error"]["request_id"] = request_id
            
        return JSONResponse(
            status_code=status_code,
            content=error_data
        )

    @staticmethod
    def log_error(
        error: Exception,
        request: Optional[Request] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log error with context information.
        
        Args:
            error: The exception that occurred
            request: FastAPI request object
            context: Additional context information
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        
        if request:
            error_info.update({
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host if request.client else None
            })
        
        if context:
            error_info["context"] = context
            
        logger.error("Application error occurred", extra=error_info)


# Exception handlers for FastAPI
async def data_analyst_exception_handler(
    request: Request, 
    exc: DataAnalystException
) -> JSONResponse:
    """Handle custom DataAnalyst exceptions."""
    ErrorHandler.log_error(exc, request)
    
    # Map exception types to HTTP status codes
    status_map = {
        UnsupportedFileTypeError: HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        FileSizeError: HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        FileProcessingError: HTTP_422_UNPROCESSABLE_ENTITY,
        DataParsingError: HTTP_422_UNPROCESSABLE_ENTITY,
        QueryExecutionError: HTTP_400_BAD_REQUEST,
        ValidationError: HTTP_400_BAD_REQUEST,
        ExternalServiceError: HTTP_503_SERVICE_UNAVAILABLE,
    }
    
    status_code = status_map.get(type(exc), HTTP_500_INTERNAL_SERVER_ERROR)
    
    return ErrorHandler.create_error_response(
        status_code=status_code,
        error_type=type(exc).__name__,
        message=str(exc),
        details=getattr(exc, 'details', None)
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    ErrorHandler.log_error(exc, request)
    
    return ErrorHandler.create_error_response(
        status_code=exc.status_code,
        error_type="HTTPException",
        message=exc.detail
    )


async def validation_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle validation errors."""
    ErrorHandler.log_error(exc, request)
    
    return ErrorHandler.create_error_response(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        error_type="ValidationError",
        message=str(exc)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    ErrorHandler.log_error(exc, request)
    
    # Don't expose internal error details in production
    message = "An internal server error occurred. Please try again later."
    
    return ErrorHandler.create_error_response(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="InternalServerError",
        message=message
    )


# Utility functions for common error scenarios
def raise_file_validation_error(filename: str, issue: str) -> None:
    """Raise a standardized file validation error."""
    raise ValidationError(f"File validation failed for '{filename}': {issue}")


def raise_data_processing_error(operation: str, details: str) -> None:
    """Raise a standardized data processing error."""
    raise FileProcessingError(f"Data processing failed during {operation}: {details}")


def raise_query_error(query: str, error_details: str) -> None:
    """Raise a standardized query execution error."""
    raise QueryExecutionError(f"Query execution failed: {error_details}")


def raise_external_service_error(service: str, error_details: str) -> None:
    """Raise a standardized external service error."""
    raise ExternalServiceError(f"External service '{service}' error: {error_details}")


# Error context managers
class ErrorContext:
    """Context manager for handling operations with specific error context."""
    
    def __init__(self, operation: str, context: Optional[Dict[str, Any]] = None):
        self.operation = operation
        self.context = context or {}
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, Exception):
            ErrorHandler.log_error(
                exc_val, 
                context={
                    "operation": self.operation,
                    **self.context
                }
            )
        return False  # Don't suppress the exception


def register_error_handlers(app):
    """
    Register all error handlers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    from fastapi import HTTPException
    
    # Register custom exception handlers
    app.add_exception_handler(DataAnalystException, data_analyst_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ValueError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
