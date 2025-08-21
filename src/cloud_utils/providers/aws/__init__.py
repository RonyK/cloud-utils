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
    from .secrets_client import SecretsManagerClient
    from .aio.s3_client import AioS3Client
    from .aio.sqs_client import AioSQSClient, AioSQSHandler
    from .aio.cloudwatch_client import AsyncCloudWatchMetricsClient
    from .aio.secrets_client import AsyncSecretsManagerClient
    
    __all__.extend([
        "S3Client",
        "SQSClient",
        "SQSHandler",
        "CloudWatchMetricsClient",
        "MetricDimension",
        "MetricQuery",
        "MetricDataPoint",
        "SecretsManagerClient",
        "AioS3Client",
        "AioSQSClient",
        "AioSQSHandler",
        "AsyncCloudWatchMetricsClient",
        "AsyncSecretsManagerClient",
    ])
except ImportError:
    # AWS dependencies not installed
    pass
