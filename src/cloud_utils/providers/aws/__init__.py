"""
AWS Provider Module

Provides AWS service clients.
"""

from .s3_client import S3Client
from .sqs_client import SQSClient, SQSHandler
from .aio.s3_client import AioS3Client
from .aio.sqs_client import AioSQSClient, AioSQSHandler

__all__ = [
    "S3Client",
    "SQSClient",
    "SQSHandler",
    "AioS3Client",
    "AioSQSClient",
    "AioSQSHandler",
]
