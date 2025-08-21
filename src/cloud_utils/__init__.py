"""
Cloud Utils - Unified cloud utilities for AWS, Google Cloud, and Azure

A comprehensive library for easy access to various cloud services with both
synchronous and asynchronous support.
"""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.1.0"
__author__ = "Cloud Utils Team"
__email__ = "team@cloud-utils.com"

# Common exceptions
from .exceptions import (
    CloudUtilsError,
    AuthError,
    ConfigError,
    ConnectionError,
    RetryableError,
    ValidationError,
    ResourceNotFoundError,
    PermissionError,
    RateLimitError,
    TimeoutError,
    ServiceUnavailableError,
)

# AWS specific exceptions
from .exceptions import (
    AWSError,
    AWSConfigError,
    AWSConnectionError,
    AWSResourceNotFoundError,
    AWSPermissionError,
)

# Main clients - conditionally import based on available dependencies
try:
    from .providers.aws.s3_client import S3Client
    from .providers.aws.sqs_client import SQSClient, SQSHandler
    from .providers.aws.secrets_client import SecretsManagerClient
    from .providers.aws.aio.s3_client import AioS3Client
    from .providers.aws.aio.sqs_client import AioSQSClient, AioSQSHandler
    from .providers.aws.aio.secrets_client import AsyncSecretsManagerClient
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

__all__ = [
    # Common exceptions
    "CloudUtilsError",
    "AuthError",
    "ConfigError",
    "ConnectionError",
    "RetryableError",
    "ValidationError",
    "ResourceNotFoundError",
    "PermissionError",
    "RateLimitError",
    "TimeoutError",
    "ServiceUnavailableError",
    
    # AWS exceptions
    "AWSError",
    "AWSConfigError",
    "AWSConnectionError",
    "AWSResourceNotFoundError",
    "AWSPermissionError",
]

# Conditionally add AWS clients if available
if AWS_AVAILABLE:
    __all__.extend([
        "S3Client",
        "SQSClient",
        "SQSHandler",
        "SecretsManagerClient",
        "AioS3Client",
        "AioSQSClient",
        "AioSQSHandler",
        "AsyncSecretsManagerClient",
    ])
