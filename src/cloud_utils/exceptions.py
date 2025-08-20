"""
Cloud Utils Common Exception Classes

Defines common exceptions used across all cloud utilities.
"""

from typing import Any, Dict, Optional


class CloudUtilsError(Exception):
    """Base exception class for Cloud Utils"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthError(CloudUtilsError):
    """Authentication related errors"""
    pass


class ConfigError(CloudUtilsError):
    """Configuration related errors"""
    pass


class ConnectionError(CloudUtilsError):
    """Connection related errors"""
    pass


class RetryableError(CloudUtilsError):
    """Retryable errors"""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        max_retries: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)
        self.retry_after = retry_after
        self.max_retries = max_retries


class ValidationError(CloudUtilsError):
    """Data validation errors"""
    pass


class ResourceNotFoundError(CloudUtilsError):
    """Resource not found errors"""
    pass


class PermissionError(CloudUtilsError):
    """Permission denied errors"""
    pass


class RateLimitError(RetryableError):
    """Rate limit errors"""
    pass


class TimeoutError(RetryableError):
    """Timeout errors"""
    pass


class ServiceUnavailableError(RetryableError):
    """Service unavailable errors"""
    pass


# AWS specific exceptions
class AWSError(CloudUtilsError):
    """Base AWS error"""
    pass


class AWSConfigError(AWSError, ConfigError):
    """AWS configuration error"""
    pass


class AWSConnectionError(AWSError, ConnectionError):
    """AWS connection error"""
    pass


class AWSResourceNotFoundError(AWSError, ResourceNotFoundError):
    """AWS resource not found error"""
    pass


class AWSPermissionError(AWSError, PermissionError):
    """AWS permission denied error"""
    pass

