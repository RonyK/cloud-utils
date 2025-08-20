# Cloud-Utils

A unified utility module for easy access to various cloud services in Python.

## 🚀 Key Features

- **AWS**: S3, SQS, DynamoDB, OpenSearch, etc. (synchronous/asynchronous)
- **Google Cloud**: Storage, Pub/Sub, etc. (planned for future development)
- **Azure**: Blob Storage, Service Bus, etc. (planned for future development)
- **Common Features**: Configuration management, logging, retry logic, error handling

## 📋 Requirements

- Python 3.12+
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
git clone https://github.com/your-org/cloud-utils.git
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
    
    # Multipart upload (for large files)
    await s3_async.upload_multipart('large-file.zip', 'my-async-bucket', 'large-file.zip')

# Execute
asyncio.run(main())
```

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
│       │   └── aio/         # Asynchronous clients
│       │       └── s3_client.py
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

- **Issues**: [GitHub Issues](https://github.com/your-org/cloud-utils/issues)
- **Documentation**: [ReadTheDocs](https://cloud-utils.readthedocs.io)
- **Email**: team@cloud-utils.com

## 🗺️ Roadmap

### v0.2.0 (Future)
- [ ] Add AWS SQS client
- [ ] Add AWS DynamoDB client
- [ ] Add AWS OpenSearch client

### v0.3.0 (Future)
- [ ] Google Cloud Storage client
- [ ] Google Cloud Pub/Sub client

### v0.4.0 (Future)
- [ ] Azure Blob Storage client
- [ ] Azure Service Bus client

### v1.0.0 (Future)
- [ ] Support for all major cloud services
- [ ] Performance optimization
- [ ] Monitoring and metrics
- [ ] CLI tools