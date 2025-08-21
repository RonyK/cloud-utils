# AWS Secrets Manager

This module provides functionality to retrieve secrets from AWS Secrets Manager with both synchronous and asynchronous support.

## Features

- **Synchronous Client**: `SecretsManagerClient` for traditional blocking operations
- **Asynchronous Client**: `AsyncSecretsManagerClient` for non-blocking operations
- **Comprehensive Error Handling**: Specific exception types for different error scenarios
- **Flexible Output**: Support for both JSON and string secret values
- **Version Management**: Support for specific secret versions and stages
- **Metadata Access**: Retrieve secret metadata and descriptions

## Installation

```bash
# For synchronous operations
pip install 'cloud-utils[aws]'

# For asynchronous operations
pip install 'cloud-utils[aws-aio]'
```

## Basic Usage

### Synchronous Client

```python
from cloud_utils.providers.aws import SecretsManagerClient

# Initialize client
client = SecretsManagerClient(region_name='us-east-1')

# Get secret as dictionary (default)
secret_dict = client.get_secret('my-database-secret')
print(f"Database host: {secret_dict['host']}")

# Get secret as string
api_key = client.get_secret_string('my-api-key')
print(f"API Key: {api_key}")

# Get specific version
previous_secret = client.get_secret('my-secret', version_stage='AWSPREVIOUS')
```

### Asynchronous Client

```python
import asyncio
from cloud_utils.providers.aws import AsyncSecretsManagerClient

async def get_secrets():
    client = AsyncSecretsManagerClient(region_name='us-east-1')
    
    # Get multiple secrets concurrently
    secret_ids = ['secret1', 'secret2', 'secret3']
    tasks = [client.get_secret(secret_id) for secret_id in secret_ids]
    results = await asyncio.gather(*tasks)
    
    return results

# Run the async function
secrets = asyncio.run(get_secrets())
```

## API Reference

### SecretsManagerClient

#### Constructor

```python
SecretsManagerClient(
    region_name: Optional[str] = None,
    profile_name: Optional[str] = None,
    session: Optional[Any] = None,
    **kwargs
)
```

**Parameters:**
- `region_name`: AWS region name (e.g., 'us-east-1')
- `profile_name`: AWS profile name to use
- `session`: Boto3 session object
- `**kwargs`: Additional arguments passed to boto3.client

#### Methods

##### get_secret()

```python
get_secret(
    secret_id: str,
    version_stage: Optional[str] = None,
    version_id: Optional[str] = None,
    as_dict: bool = True
) -> Union[str, Dict[str, Any]]
```

Retrieve a secret from AWS Secrets Manager.

**Parameters:**
- `secret_id`: The identifier for the secret
- `version_stage`: The staging label of the version (e.g., 'AWSCURRENT', 'AWSPREVIOUS')
- `version_id`: The unique identifier of the version
- `as_dict`: If True, return as dictionary; if False, return as string

**Returns:** The secret value as string or dictionary

##### get_secret_string()

```python
get_secret_string(secret_id: str, **kwargs) -> str
```

Retrieve a secret as a string.

##### get_secret_dict()

```python
get_secret_dict(secret_id: str, **kwargs) -> Dict[str, Any]
```

Retrieve a secret as a dictionary.

##### list_secrets()

```python
list_secrets(
    max_results: Optional[int] = None,
    filters: Optional[Dict[str, Any]] = None
) -> list
```

List available secrets.

##### describe_secret()

```python
describe_secret(secret_id: str) -> Dict[str, Any]
```

Get detailed information about a secret.

### AsyncSecretsManagerClient

The async client provides the same methods as the synchronous client but with async/await syntax.

## Error Handling

The module provides specific exception types for different error scenarios:

```python
from cloud_utils.providers.aws import (
    SecretsManagerError,
    SecretsManagerAuthError,
    SecretsManagerConnectionError,
    SecretsManagerNotFoundError,
    SecretsManagerValidationError
)

try:
    secret = client.get_secret('my-secret')
except SecretsManagerNotFoundError:
    print("Secret not found")
except SecretsManagerAuthError:
    print("Authentication failed")
except SecretsManagerValidationError:
    print("Invalid parameters")
except SecretsManagerError:
    print("General error occurred")
```

## Examples

### Database Connection Configuration

```python
from cloud_utils.providers.aws import SecretsManagerClient

def get_database_config():
    client = SecretsManagerClient(region_name='us-east-1')
    
    try:
        config = client.get_secret_dict('database-credentials')
        return {
            'host': config['host'],
            'port': config['port'],
            'database': config['database'],
            'username': config['username'],
            'password': config['password']
        }
    except Exception as e:
        logger.error(f"Failed to retrieve database config: {e}")
        raise
```

### API Key Management

```python
from cloud_utils.providers.aws import SecretsManagerClient

def get_api_key(service_name: str):
    client = SecretsManagerClient(region_name='us-east-1')
    
    try:
        api_key = client.get_secret_string(f'{service_name}-api-key')
        return api_key
    except Exception as e:
        logger.error(f"Failed to retrieve API key for {service_name}: {e}")
        raise
```

### Concurrent Secret Retrieval

```python
import asyncio
from cloud_utils.providers.aws import AsyncSecretsManagerClient

async def get_multiple_secrets(secret_ids: list):
    client = AsyncSecretsManagerClient(region_name='us-east-1')
    
    tasks = [client.get_secret(secret_id) for secret_id in secret_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    secrets = {}
    for secret_id, result in zip(secret_ids, results):
        if isinstance(result, Exception):
            logger.error(f"Failed to retrieve {secret_id}: {result}")
        else:
            secrets[secret_id] = result
    
    return secrets
```

## Best Practices

1. **Error Handling**: Always handle exceptions appropriately for your use case
2. **Caching**: Consider caching frequently accessed secrets to reduce API calls
3. **Logging**: Use appropriate logging levels for debugging and monitoring
4. **Concurrent Access**: Use the async client for retrieving multiple secrets concurrently
5. **Version Management**: Use version stages for safe secret rotation

## Configuration

The client uses standard AWS credential resolution:

1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS credentials file (`~/.aws/credentials`)
3. IAM roles (when running on EC2, ECS, Lambda, etc.)
4. AWS profiles

## Troubleshooting

### Common Issues

1. **Credentials Not Found**: Ensure AWS credentials are properly configured
2. **Access Denied**: Verify IAM permissions for Secrets Manager
3. **Region Mismatch**: Ensure the client region matches your secret's region
4. **Network Issues**: Check VPC configuration and security groups

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
