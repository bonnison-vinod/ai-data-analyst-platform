"""
Custom exception classes for the AI Data Analyst platform.
"""

class DataAnalystException(Exception):
    """Base exception class for the AI Data Analyst platform."""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FileProcessingError(DataAnalystException):
    """Raised when file processing fails."""
    pass


class UnsupportedFileTypeError(DataAnalystException):
    """Raised when an unsupported file type is uploaded."""
    pass


class FileSizeError(DataAnalystException):
    """Raised when file size exceeds limits."""
    pass


class DataParsingError(DataAnalystException):
    """Raised when data parsing fails."""
    pass


class QueryExecutionError(DataAnalystException):
    """Raised when query execution fails."""
    pass


class ValidationError(DataAnalystException):
    """Raised when input validation fails."""
    pass


class ExternalServiceError(DataAnalystException):
    """Raised when external service (OpenAI, etc.) fails."""
    pass


class DataAnalysisError(DataAnalystException):
    """Raised when data analysis operations fail."""
    pass


class FileValidationError(DataAnalystException):
    """Raised when file validation fails."""
    pass


class QueryProcessingError(DataAnalystException):
    """Raised when query processing operations fail."""
    pass
