"""
AWS Asynchronous Client Module

Provides asynchronous clients for AWS services.
"""

from .s3_client import AioS3Client

__all__ = [
    "AioS3Client",
]
