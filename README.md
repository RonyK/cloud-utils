# Cloud-Utils

A unified utility module for easy access to various cloud services in Python.

## 🚀 Key Features

- **AWS**: S3, SQS, DynamoDB, OpenSearch, etc. (synchronous/asynchronous)
- **Google Cloud**: Storage, Pub/Sub, etc. (planned for future development)
- **Azure**: Blob Storage, Service Bus, etc. (planned for future development)
- **Common Features**: Configuration management, logging, retry logic, error handling

## 📋 Requirements

- Python 3.11+
- Cloud service-specific credential setup

## 🛠️ Installation

### Basic Installation
```bash
pip install cloud-utils
```

### Optional Dependency Installation
```bash
# AWS related (synchronous only)
pip install "cloud-utils[aws]"

# AWS related (synchronous + asynchronous)
pip install "cloud-utils[aws,aws-aio]"

# OpenSearch support
pip install "cloud-utils[opensearch]"

# Development tools
pip install "cloud-utils[dev]"
```

### Development Environment Installation
```bash
git clone https://github.com/RonyK/cloud-utils.git
cd cloud-utils
pip install -e ".[dev]"
```

## 🔧 Configuration

### AWS Configuration
```bash
# Set via environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Or use AWS profile
export AWS_PROFILE=your_profile
```

## 📖 Usage Examples

### AWS S3 Usage

#### Synchronous Mode
```python
from cloud_utils.providers.aws import S3Client

# Initialize S3 client
s3 = S3Client(region_name='us-east-1')

# Create bucket
s3.create_bucket('my-bucket')

# Upload file
s3.upload_file('local-file.txt', 'my-bucket', 'remote-file.txt')

# Download file
s3.download_file('my-bucket', 'remote-file.txt', 'downloaded-file.txt')

# List objects
objects = s3.list_objects('my-bucket', prefix='docs/')

# Delete object
s3.delete_object('my-bucket', 'remote-file.txt')
```

#### Asynchronous Mode
```python
import asyncio
from cloud_utils.providers.aws import AioS3Client

async def main():
    # Initialize S3 asynchronous client
    s3_async = AioS3Client(region_name='us-east-1')
    
    # Create bucket
    await s3_async.create_bucket('my-async-bucket')
    
    # Upload file
    await s3_async.upload_file('local-file.txt', 'my-async-bucket', 'remote-file.txt')
```

### AWS CloudWatch Metrics Usage

#### Synchronous Mode
```python
from cloud_utils.providers.aws import CloudWatchMetricsClient, MetricDimension, MetricQuery
import datetime

# Initialize CloudWatch client
cw = CloudWatchMetricsClient(region_name='ap-northeast-2')

# Define metric dimensions
dimensions = [
    MetricDimension("Service", "processor"),
    MetricDimension("Stage", "prod"),
    MetricDimension("Environment", "production")
]

# Create metric queries
queries = [
    MetricQuery(
        namespace="MyApp/Metrics",
        metric_name="ResourcesProcessed",
        dimensions=dimensions,
        period=60,
        stat="Sum",
        unit="Count"
    ),
    # Calculate per-second processing rate using Metric Math
    MetricQuery(
        namespace="MyApp/Metrics",
        metric_name="ResourcesProcessed",
        dimensions=dimensions,
        period=60,
        stat="Sum",
        expression="query_0 / PERIOD(query_0)",  # per-minute sum / 60 seconds = per-second
        label="ResourcesProcessed per second"
    )
]

# Set time range
end_time = datetime.datetime.now(datetime.timezone.utc)
start_time = end_time - datetime.timedelta(hours=24)

# Get multiple metrics at once (recommended)
series = cw.get_metric_data(queries, start_time, end_time)

# Process results
for query_id, data_points in series.items():
    print(f"{query_id}: {len(data_points)} data points")
```

#### Asynchronous Mode
```python
import asyncio
from cloud_utils.providers.aws import AsyncCloudWatchMetricsClient, MetricDimension, MetricQuery

async def main():
    # Initialize async CloudWatch client
    cw = AsyncCloudWatchMetricsClient(region_name='ap-northeast-2')
    
    # Define dimensions and queries (same as sync version)
    dimensions = [MetricDimension("Service", "api-gateway")]
    queries = [
        MetricQuery(
            namespace="AWS/ApiGateway",
            metric_name="Count",
            dimensions=dimensions,
            period=300,
            stat="Sum"
        )
    ]
    
    # Set time range
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=6)
    
    # Get metrics asynchronously
    series = await cw.get_metric_data(queries, start_time, end_time)
    
    # Process results
    for query_id, data_points in series.items():
        print(f"{query_id}: {len(data_points)} data points")

# Run async function
asyncio.run(main())
```
    # Multipart upload (for large files)
    await s3_async.upload_multipart('large-file.zip', 'my-async-bucket', 'large-file.zip')

# Execute
asyncio.run(main())
```

### AWS SQS Usage

#### Synchronous Mode
```python
from cloud_utils.providers.aws import SQSClient, SQSHandler

# Method 1: Using SQSClient directly
sqs = SQSClient(region_name='us-east-1')

# Create queue
queue_url = sqs.create_queue('my-queue')

# Send message
message_id = sqs.send_message(queue_url, 'Hello, World!')

# Send batch messages
messages = [
    {'Id': '1', 'MessageBody': 'First message'},
    {'Id': '2', 'MessageBody': 'Second message'}
]
results = sqs.send_message_batch(queue_url, messages)

# Receive messages
messages = sqs.receive_messages(queue_url, max_number_of_messages=10)

# Process and delete messages
for message in messages:
    print(f"Received: {message['Body']}")
    sqs.delete_message(queue_url, message['ReceiptHandle'])

# Method 2: Using SQSHandler for specific queue
sqs_handler = SQSHandler(queue_name='my-queue', region_name='us-east-1')

# Send message (no need to specify queue URL)
message_id = sqs_handler.send_message('Hello from handler!')

# Receive messages
messages = sqs_handler.receive_messages(max_number_of_messages=5)

# Get queue information
queue_info = sqs_handler.get_queue_info()
print(f"Queue has {queue_info['attributes']['ApproximateNumberOfMessages']} messages")
print(f"Is FIFO queue: {queue_info['is_fifo']}")

# Method 3: FIFO Queue with automatic parameter handling
fifo_handler = SQSHandler(queue_name='my-fifo-queue.fifo', region_name='us-east-1')

# For FIFO queues, group_id and deduplication_id are automatically generated if not provided
message_id = fifo_handler.send_message('FIFO message')  # Auto-generates required FIFO parameters

# Send batch messages to FIFO queue
fifo_messages = [
    {'MessageBody': 'FIFO message 1'},
    {'MessageBody': 'FIFO message 2'}
]
# All required FIFO parameters (Id, MessageDeduplicationId, MessageGroupId) are auto-generated
results = fifo_handler.send_message_batch(fifo_messages)

# Method 4: Simple message body list for batch sending
# Just provide a list of message strings - much simpler!
simple_messages = [
    'Hello from message 1',
    'Hello from message 2',
    'Hello from message 3'
]
# Automatically converts to proper message format and handles FIFO requirements
results = fifo_handler.send_messages(simple_messages)

# With custom attributes for all messages
custom_attributes = {
    'MessageType': {'StringValue': 'notification', 'DataType': 'String'},
    'Priority': {'StringValue': 'high', 'DataType': 'String'}
}
results = fifo_handler.send_messages(simple_messages, message_attributes=custom_attributes)

# Method 5: Send dictionary data (automatically converted to JSON)
user_data = {
    'user_id': 12345,
    'name': 'John Doe',
    'email': 'john@example.com',
    'preferences': {'theme': 'dark', 'notifications': True}
}

# Send single dictionary message
message_id = fifo_handler.send_message(user_data)

# Send multiple dictionary messages
user_messages = [
    {'user_id': 1, 'action': 'login', 'timestamp': '2024-01-01T10:00:00Z'},
    {'user_id': 2, 'action': 'logout', 'timestamp': '2024-01-01T11:00:00Z'},
    {'user_id': 3, 'action': 'purchase', 'amount': 99.99, 'timestamp': '2024-01-01T12:00:00Z'}
]
# All dictionaries are automatically converted to JSON strings
results = fifo_handler.send_messages(user_messages)
```

#### Asynchronous Mode
```python
import asyncio
from cloud_utils.providers.aws import AioSQSClient, AioSQSHandler

async def main():
    # Method 1: Using AioSQSClient directly
    sqs_async = AioSQSClient(region_name='us-east-1')
    
    # Create queue
    queue_url = await sqs_async.create_queue('my-async-queue')
    
    # Send message
    message_id = await sqs_async.send_message(queue_url, 'Async Hello!')
    
    # Long poll receive messages
    messages = await sqs_async.long_poll_receive(
        queue_url, 
        max_poll_time=60  # Poll for up to 1 minute
    )
    
    # Process and delete messages
    for message in messages:
        print(f"Received: {message['Body']}")
        await sqs_async.delete_message(queue_url, message['ReceiptHandle'])
    
    # Method 2: Using AioSQSHandler for specific queue
    sqs_handler = AioSQSHandler(queue_name='my-async-queue', region_name='us-east-1')
    
    # Send message (no need to specify queue URL)
    message_id = await sqs_handler.send_message('Hello from async handler!')
    
    # Long poll receive messages
    messages = await sqs_handler.long_poll_receive(max_poll_time=120)
    
    # Get queue information
    queue_info = await sqs_handler.get_queue_info()
    print(f"Queue has {queue_info['attributes']['ApproximateNumberOfMessages']} messages")
    print(f"Is FIFO queue: {queue_info['is_fifo']}")
    
    # Method 3: FIFO Queue with automatic parameter handling
    fifo_handler = AioSQSHandler(queue_name='my-async-fifo-queue.fifo', region_name='us-east-1')
    
    # For FIFO queues, group_id and deduplication_id are automatically generated if not provided
    message_id = await fifo_handler.send_message('Async FIFO message')
    
    # Send batch messages to FIFO queue
    fifo_messages = [
        {'MessageBody': 'Async FIFO message 1'},
        {'MessageBody': 'Async FIFO message 2'}
    ]
    # All required FIFO parameters are auto-generated
    results = await fifo_handler.send_message_batch(fifo_messages)

    # Method 4: Simple message body list for batch sending
    # Just provide a list of message strings - much simpler!
    simple_messages = [
        'Async Hello from message 1',
        'Async Hello from message 2',
        'Async Hello from message 3'
    ]
    # Automatically converts to proper message format and handles FIFO requirements
    results = await fifo_handler.send_messages(simple_messages)

    # With custom attributes for all messages
    custom_attributes = {
        'MessageType': {'StringValue': 'async_notification', 'DataType': 'String'},
        'Priority': {'StringValue': 'high', 'DataType': 'String'}
    }
    results = await fifo_handler.send_messages(simple_messages, message_attributes=custom_attributes)

    # Method 5: Send dictionary data (automatically converted to JSON)
    async_user_data = {
        'user_id': 67890,
        'name': 'Jane Smith',
        'email': 'jane@example.com',
        'preferences': {'theme': 'light', 'notifications': False}
    }

    # Send single dictionary message
    message_id = await fifo_handler.send_message(async_user_data)

    # Send multiple dictionary messages
    async_user_messages = [
        {'user_id': 4, 'action': 'async_login', 'timestamp': '2024-01-01T13:00:00Z'},
        {'user_id': 5, 'action': 'async_logout', 'timestamp': '2024-01-01T14:00:00Z'},
        {'user_id': 6, 'action': 'async_purchase', 'amount': 149.99, 'timestamp': '2024-01-01T15:00:00Z'}
    ]
    # All dictionaries are automatically converted to JSON strings
    results = await fifo_handler.send_messages(async_user_messages)

# Execute
asyncio.run(main())
```

### FIFO Queue Automatic Handling

The SQSHandler and AioSQSHandler automatically detect FIFO queues (queues ending with `.fifo`) and handle required parameters:

- **Automatic Detection**: Queue type is detected from the queue URL
- **Message Deduplication ID**: Automatically generated using message content hash + timestamp
- **Message Group ID**: Automatically generated using timestamp
- **Delay Seconds**: Automatically disabled for FIFO queues (not supported)
- **Batch Operations**: All required FIFO parameters are auto-generated for batch messages

This makes working with FIFO queues much simpler while ensuring compliance with AWS SQS FIFO requirements.

### Common Features Usage

#### Configuration Management
```python
from cloud_utils.config import settings

# Get configuration values
region = settings.get('AWS_DEFAULT_REGION', 'us-east-1')
debug = settings.get_bool('DEBUG', False)
timeout = settings.get_int('TIMEOUT', 30)

# Update configuration
settings.update({'LOG_LEVEL': 'DEBUG'})
```

#### Logging Configuration
```python
from cloud_utils.config.logging import setup_logging, get_logger

# Setup logging
setup_logging(level='DEBUG', log_file='app.log')

# Use logger
logger = get_logger(__name__)
logger.info('Application started')
```

#### Retry Logic
```python
from cloud_utils.utils.backoff import RetryConfig, exponential_backoff

# Retry configuration
retry_config = RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=60.0,
    factor=2.0,
    jitter=True
)

# Execute retry
def risky_operation():
    # Network request, etc.
    pass

result = retry_config.retry(risky_operation)
```

## 🏗️ Project Structure

```
cloud-utils/
├── src/cloud_utils/           # Package to be deployed
│   ├── __init__.py           # Main API
│   ├── exceptions.py         # Common exception classes
│   ├── config/               # Configuration management
│   │   ├── settings.py      # Configuration loading
│   │   └── logging.py       # Logging configuration
│   ├── utils/                # Common utilities
│   │   └── backoff.py       # Retry logic
│   └── providers/            # Cloud service-specific clients
│       ├── aws/             # AWS services
│       │   ├── s3_client.py # Synchronous S3
│       │   ├── sqs_client.py # Synchronous SQS + SQSHandler
│       │   └── aio/         # Asynchronous clients
│       │       ├── s3_client.py
│       │       └── sqs_client.py # Async SQS + AioSQSHandler
│       ├── gcp/             # Google Cloud (future)
│       └── azure/           # Azure (future)
├── packages/                 # Development/design documents
├── tests/                    # Test code
├── examples/                 # Usage examples
└── docs/                     # Documentation
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Test with coverage
pytest --cov=cloud_utils

# Test specific module
pytest tests/unit/test_aws_s3_client.py

# Integration tests
pytest tests/integration/
```

## 📚 Documentation

- **API Documentation**: `docs/api_reference.md`
- **Quick Start**: `docs/quickstart.md`
- **Provider Guide**: `docs/providers.md`
- **Design Documents**: `packages/*/DESIGN.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Environment Setup
```bash
# Install dependencies
pip install -e ".[dev]"

# Code formatting
black src/
isort src/

# Linting
flake8 src/
mypy src/

# Testing
pytest
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/RonyK/cloud-utils/issues)
- **Documentation**: [ReadTheDocs](https://github.com/RonyK/cloud-utils)
- **Email**: team@cloud-utils.com
