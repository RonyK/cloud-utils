"""
AWS Provider Module

Provides AWS service clients.
"""

__all__ = []

try:
    from .s3_client import S3Client
    from .sqs_client import SQSClient, SQSHandler
    from .cloudwatch_client import CloudWatchMetricsClient
    from .cloudwatch_models import MetricDimension, MetricQuery, MetricDataPoint
    from .aio.s3_client import AioS3Client
    from .aio.sqs_client import AioSQSClient, AioSQSHandler
    from .aio.cloudwatch_client import AsyncCloudWatchMetricsClient
    
    __all__.extend([
        "S3Client",
        "SQSClient",
        "SQSHandler",
        "CloudWatchMetricsClient",
        "MetricDimension",
        "MetricQuery",
        "MetricDataPoint",
        "AioS3Client",
        "AioSQSClient",
        "AioSQSHandler",
        "AsyncCloudWatchMetricsClient",
    ])
except ImportError:
    # AWS dependencies not installed
    pass
