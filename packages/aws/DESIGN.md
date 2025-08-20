# AWS Module Design Document

## Overview
Module that provides synchronous and asynchronous clients for AWS services.

## Currently Supported Services
- **S3**: Object storage (synchronous/asynchronous)
- **SQS**: Message queue (synchronous/asynchronous)
- **DynamoDB**: NoSQL database (synchronous) - planned for future development
- **OpenSearch**: Search service (synchronous) - planned for future development

## Architecture Principles
1. **Synchronous/Asynchronous Symmetry**: Maintain identical method names, but use `Aio` prefix for asynchronous
2. **Error Handling**: Use common exception classes for consistent error handling
3. **Configuration Management**: Flexible configuration through environment variables and configuration files
4. **Queue-Specific Handlers**: Provide specialized handlers for working with specific SQS queues

## Class Structure
```
S3Client (Synchronous)
├── session: boto3.Session
├── client: boto3.client('s3')
├── resource: boto3.resource('s3')
└── config: botocore.config.Config

AioS3Client (Asynchronous)
├── session: aioboto3.Session
├── config: botocore.config.Config
└── _get_session(): async method

SQSClient (Synchronous)
├── session: boto3.Session
├── client: boto3.client('sqs')
└── config: botocore.config.Config

SQSHandler (Synchronous Queue-Specific)
├── queue_name: str
├── queue_url: str
├── sqs_client: SQSClient
└── queue_url_resolved: property

AioSQSClient (Asynchronous)
├── session: aioboto3.Session
├── config: botocore.config.Config
└── _get_session(): async method

AioSQSHandler (Asynchronous Queue-Specific)
├── queue_name: str
├── queue_url: str
├── sqs_client: AioSQSClient
└── _get_queue_url_resolved(): async method
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

### SQSClient
- `create_queue()`: Create queue
- `delete_queue()`: Delete queue
- `get_queue_url()`: Get queue URL by name
- `list_queues()`: List queues
- `send_message()`: Send single message
- `send_message_batch()`: Send multiple messages in batch
- `receive_messages()`: Receive messages
- `delete_message()`: Delete single message
- `delete_message_batch()`: Delete multiple messages in batch
- `change_message_visibility()`: Change message visibility timeout
- `purge_queue()`: Purge all messages
- `get_queue_attributes()`: Get queue attributes

### SQSHandler
- `send_message()`: Send message to specific queue
- `send_message_batch()`: Send batch messages to specific queue
- `send_messages()`: Send multiple message bodies as batch (auto-converts to message format)
- `receive_messages()`: Receive messages from specific queue
- `delete_message()`: Delete message from specific queue
- `delete_message_batch()`: Delete batch messages from specific queue
- `change_message_visibility()`: Change message visibility timeout for specific queue
- `purge_queue()`: Purge all messages from specific queue
- `get_queue_attributes()`: Get attributes of specific queue
- `get_queue_info()`: Get comprehensive queue information

### AioSQSClient
- `create_queue()`: Asynchronously create queue
- `delete_queue()`: Asynchronously delete queue
- `get_queue_url()`: Asynchronously get queue URL by name
- `list_queues()`: Asynchronously list queues
- `send_message()`: Asynchronously send single message
- `send_message_batch()`: Asynchronously send multiple messages in batch
- `receive_messages()`: Asynchronously receive messages
- `delete_message()`: Asynchronously delete single message
- `delete_message_batch()`: Asynchronously delete multiple messages in batch
- `change_message_visibility()`: Asynchronously change message visibility timeout
- `purge_queue()`: Asynchronously purge all messages
- `get_queue_attributes()`: Asynchronously get queue attributes
- `long_poll_receive()`: Extended long polling with configurable timeout

### AioSQSHandler
- `send_message()`: Asynchronously send message to specific queue
- `send_message_batch()`: Asynchronously send batch messages to specific queue
- `send_messages()`: Asynchronously send multiple message bodies as batch (auto-converts to message format)
- `receive_messages()`: Asynchronously receive messages from specific queue
- `delete_message()`: Asynchronously delete message from specific queue
- `delete_message_batch()`: Asynchronously delete batch messages from specific queue
- `change_message_visibility()`: Asynchronously change message visibility timeout for specific queue
- `purge_queue()`: Asynchronously purge all messages from specific queue
- `get_queue_attributes()`: Asynchronously get attributes of specific queue
- `get_queue_info()`: Asynchronously get comprehensive queue information
- `long_poll_receive()`: Asynchronously long poll receive messages from specific queue

## Error Handling
- `AWSConfigError`: Configuration related errors
- `AWSConnectionError`: Connection related errors
- `AWSResourceNotFoundError`: Resource not found errors

## Configuration Options
- `AWS_DEFAULT_REGION`: Default region
- `AWS_PROFILE`: AWS profile
- `AWS_ACCESS_KEY_ID`: Access key ID
- `AWS_SECRET_ACCESS_KEY`: Secret access key

## Usage Examples
```python
from cloud_utils.providers.aws import S3Client, SQSClient, SQSHandler, AioS3Client, AioSQSClient, AioSQSHandler

# Synchronous S3 usage
s3 = S3Client(region_name='us-east-1')
s3.create_bucket('my-bucket')
s3.upload_file('local.txt', 'my-bucket', 'remote.txt')

# Synchronous SQS usage
sqs = SQSClient(region_name='us-east-1')
queue_url = sqs.create_queue('my-queue')
message_id = sqs.send_message(queue_url, 'Hello, World!')
messages = sqs.receive_messages(queue_url)

# Synchronous SQSHandler usage (queue-specific)
sqs_handler = SQSHandler(queue_name='my-queue', region_name='us-east-1')
message_id = sqs_handler.send_message('Hello from handler!')
messages = sqs_handler.receive_messages()
queue_info = sqs_handler.get_queue_info()

# Asynchronous S3 usage
async def main():
    s3_async = AioS3Client(region_name='us-east-1')
    await s3_async.create_bucket('my-async-bucket')
    await s3_async.upload_file('local.txt', 'my-async-bucket', 'remote.txt')

# Asynchronous SQS usage
async def main():
    sqs_async = AioSQSClient(region_name='us-east-1')
    queue_url = await sqs_async.create_queue('my-async-queue')
    message_id = await sqs_async.send_message(queue_url, 'Async Hello!')
    messages = await sqs_async.receive_messages(queue_url)

# Asynchronous SQSHandler usage (queue-specific)
async def main():
    sqs_handler = AioSQSHandler(queue_name='my-async-queue', region_name='us-east-1')
    message_id = await sqs_handler.send_message('Hello from async handler!')
    messages = await sqs_handler.long_poll_receive(max_poll_time=120)
    queue_info = await sqs_handler.get_queue_info()
```

## SQS Specific Features

### Queue Types Support
- **Standard Queues**: At-least-once delivery, best-effort ordering
- **FIFO Queues**: Exactly-once processing, strict ordering (via message_group_id and message_deduplication_id)

### Message Handling
- **Batch Operations**: Send/delete up to 10 messages at once
- **Long Polling**: Configurable wait time (0-20 seconds) for efficient message retrieval
- **Visibility Timeout**: Configurable timeout for message processing
- **Message Attributes**: Support for custom metadata

### Advanced Features
- **Extended Long Polling**: Custom implementation for longer polling periods
- **Message Deduplication**: Automatic deduplication for FIFO queues
- **Message Grouping**: Group messages for ordered processing in FIFO queues

### Handler Benefits
- **Queue-Specific Operations**: No need to specify queue URL for each operation
- **Automatic URL Resolution**: Automatically resolves queue URL from name if needed
- **Simplified API**: Cleaner interface for working with specific queues
- **Queue Information**: Easy access to comprehensive queue metadata
- **FIFO Queue Auto-Detection**: Automatically detects FIFO queues and handles required parameters
- **Smart Parameter Generation**: Auto-generates MessageDeduplicationId and MessageGroupId for FIFO queues

## FIFO Queue Handling

### Automatic Detection
Both `SQSHandler` and `AioSQSHandler` automatically detect FIFO queues by checking if the queue URL ends with `.fifo`.

### Required Parameter Auto-Generation
For FIFO queues, the handlers automatically generate required parameters if not provided:

- **MessageDeduplicationId**: Generated using MD5 hash of message content + timestamp
- **MessageGroupId**: Generated using timestamp-based group identifier
- **Id**: For batch operations, ensures unique message identifiers

### FIFO-Specific Behavior
- **Delay Seconds**: Automatically disabled (not supported by FIFO queues)
- **Batch Processing**: All required FIFO parameters are auto-generated for each message
- **Compliance**: Ensures AWS SQS FIFO requirements are met automatically

### Usage Example
```python
# FIFO queue handler automatically detects queue type
fifo_handler = SQSHandler(queue_name='my-fifo-queue.fifo')

# Send message without specifying FIFO parameters
message_id = fifo_handler.send_message('Hello FIFO!')
# Automatically generates:
# - MessageDeduplicationId: hash of message + timestamp
# - MessageGroupId: timestamp-based group

# Batch messages with minimal input
messages = [
    {'MessageBody': 'Message 1'},
    {'MessageBody': 'Message 2'}
]
# All required FIFO parameters are auto-generated
results = fifo_handler.send_message_batch(messages)

# Simple message body list for batch sending
message_bodies = [
    'Simple message 1',
    'Simple message 2',
    'Simple message 3'
]
# Automatically converts to proper message format and handles FIFO requirements
results = fifo_handler.send_messages(message_bodies)

# With custom attributes for all messages
custom_attributes = {
    'MessageType': {'StringValue': 'notification', 'DataType': 'String'}
}
results = fifo_handler.send_messages(message_bodies, message_attributes=custom_attributes)
```

## Message Sending Methods Comparison

### send_message_batch() vs send_messages()

| Feature | send_message_batch() | send_messages() |
|---------|---------------------|-----------------|
| **Input Format** | Full message dictionaries | Simple string list |
| **Parameter Control** | Full control over each message | Global parameters for all messages |
| **Use Case** | Complex messages with different settings | Simple messages with same settings |
| **FIFO Handling** | Manual parameter management | Automatic FIFO parameter generation |
| **Ease of Use** | More complex, more flexible | Simpler, less flexible |

### When to Use Each Method

- **Use `send_messages()` when**:
  - You have a simple list of message strings
  - All messages should have the same attributes
  - You want automatic FIFO parameter handling
  - You prefer simplicity over customization

- **Use `send_message_batch()` when**:
  - You need different settings for each message
  - You have complex message structures
  - You need fine-grained control over parameters
  - You're working with pre-formatted message dictionaries

## Data Type Support

### Message Body Types
All send functions now support both string and dictionary message bodies:

- **String Messages**: Traditional text messages
- **Dictionary Messages**: Automatically converted to JSON strings

### Automatic JSON Conversion
When a dictionary is passed as `message_body`:

```python
# Dictionary message body
user_data = {
    'user_id': 12345,
    'name': 'John Doe',
    'email': 'john@example.com',
    'preferences': {'theme': 'dark', 'notifications': True}
}

# Automatically converted to JSON string
message_id = sqs_handler.send_message(user_data)
# Result: {"user_id": 12345, "name": "John Doe", "email": "john@example.com", "preferences": {"theme": "dark", "notifications": true}}
```

### JSON Conversion Features
- **ensure_ascii=False**: Supports non-ASCII characters
- **default=str**: Handles non-serializable objects gracefully
- **FIFO Compatibility**: Deduplication ID generation works with both string and dict inputs
- **Batch Processing**: All message types supported in batch operations

### Usage Examples

#### Single Message with Dictionary
```python
# Send user data as JSON
user_info = {'id': 1, 'name': 'Alice', 'status': 'active'}
message_id = handler.send_message(user_info)
```

#### Batch Messages with Mixed Types
```python
# Mix of strings and dictionaries
mixed_messages = [
    'Simple text message',
    {'event': 'user_login', 'user_id': 123},
    'Another text message',
    {'event': 'purchase', 'amount': 99.99, 'currency': 'USD'}
]
results = handler.send_messages(mixed_messages)
```

## Future Development Plans
1. Add DynamoDB client
2. Add OpenSearch client
3. Add more S3 features (version management, encryption, etc.)
4. Add more SQS features (dead letter queues, message filtering, etc.)
5. Performance optimization and monitoring
