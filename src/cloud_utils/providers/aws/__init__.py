"""
AWS Provider Module

Provides AWS service clients.
"""

__all__ = []

try:
    from .s3_client import S3Client
    from .sqs_client import SQSClient, SQSHandler
    from .aio.s3_client import AioS3Client
    from .aio.sqs_client import AioSQSClient, AioSQSHandler
    
    __all__.extend([
        "S3Client",
        "SQSClient",
        "SQSHandler",
        "AioS3Client",
        "AioSQSClient",
        "AioSQSHandler",
    ])
except ImportError:
    # AWS dependencies not installed
    pass
