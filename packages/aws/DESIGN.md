# AWS Module Design Document

## Overview
Module that provides synchronous and asynchronous clients for AWS services.

## Currently Supported Services
- **S3**: Object storage (synchronous/asynchronous)
- **SQS**: Message queue (synchronous/asynchronous) - planned for future development
- **DynamoDB**: NoSQL database (synchronous) - planned for future development
- **OpenSearch**: Search service (synchronous) - planned for future development

## Architecture Principles
1. **Synchronous/Asynchronous Symmetry**: Maintain identical method names, but use `Aio` prefix for asynchronous
2. **Error Handling**: Use common exception classes for consistent error handling
3. **Retry Logic**: Automatic retry using backoff strategies
4. **Configuration Management**: Flexible configuration through environment variables and configuration files

## Class Structure
```
S3Client (Synchronous)
├── session: boto3.Session
├── client: boto3.client('s3')
├── resource: boto3.resource('s3')
└── retry_config: RetryConfig

AioS3Client (Asynchronous)
├── session: aioboto3.Session
├── config: botocore.config.Config
└── _get_session(): async method
```

## Main Methods
### S3Client
- `create_bucket()`: Create bucket
- `delete_bucket()`: Delete bucket
- `upload_file()`: Upload file
- `download_file()`: Download file
- `list_objects()`: List objects
- `delete_object()`: Delete object

### AioS3Client
- `create_bucket()`: Asynchronously create bucket
- `delete_bucket()`: Asynchronously delete bucket
- `upload_file()`: Asynchronously upload file
- `download_file()`: Asynchronously download file
- `list_objects()`: Asynchronously list objects
- `delete_object()`: Asynchronously delete object
- `upload_multipart()`: Multipart upload

## Error Handling
- `AWSConfigError`: Configuration related errors
- `AWSConnectionError`: Connection related errors
- `AWSResourceNotFoundError`: Resource not found errors

## Retry Strategy
- Exponential backoff (default)
- Maximum 3 retries
- Jitter (randomness) included

## Configuration Options
- `AWS_DEFAULT_REGION`: Default region
- `AWS_PROFILE`: AWS profile
- `AWS_ACCESS_KEY_ID`: Access key ID
- `AWS_SECRET_ACCESS_KEY`: Secret access key

## Usage Examples
```python
from cloud_utils.providers.aws import S3Client, AioS3Client

# Synchronous usage
s3 = S3Client(region_name='us-east-1')
s3.create_bucket('my-bucket')
s3.upload_file('local.txt', 'my-bucket', 'remote.txt')

# Asynchronous usage
async def main():
    s3_async = AioS3Client(region_name='us-east-1')
    await s3_async.create_bucket('my-async-bucket')
    await s3_async.upload_file('local.txt', 'my-async-bucket', 'remote.txt')
```

## Future Development Plans
1. Add SQS client
2. Add DynamoDB client
3. Add OpenSearch client
4. Add more S3 features (version management, encryption, etc.)
5. Performance optimization and monitoring
