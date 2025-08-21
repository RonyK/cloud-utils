#!/usr/bin/env python3
"""
AWS Secrets Manager Usage Examples

This example demonstrates how to use the SecretsManagerClient
to retrieve secrets from AWS Secrets Manager.
"""

import asyncio
import logging
from cloud_utils.providers.aws import SecretsManagerClient, AsyncSecretsManagerClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_example():
    """Synchronous Secrets Manager usage example."""
    print("=== Synchronous Secrets Manager Example ===")
    
    try:
        # Initialize the client
        client = SecretsManagerClient(region_name='us-east-1')
        
        # Example 1: Get a secret as a dictionary (default)
        print("\n1. Getting secret as dictionary:")
        try:
            secret_dict = client.get_secret('my-database-secret')
            print(f"Database host: {secret_dict.get('host')}")
            print(f"Database port: {secret_dict.get('port')}")
            print(f"Database name: {secret_dict.get('database')}")
        except Exception as e:
            print(f"Error getting secret: {e}")
        
        # Example 2: Get a secret as a string
        print("\n2. Getting secret as string:")
        try:
            secret_string = client.get_secret_string('my-api-key')
            print(f"API Key: {secret_string[:10]}...")  # Show first 10 chars
        except Exception as e:
            print(f"Error getting secret: {e}")
        
        # Example 3: Get a specific version of a secret
        print("\n3. Getting specific version of secret:")
        try:
            secret = client.get_secret('my-secret', version_stage='AWSPREVIOUS')
            print(f"Previous version secret: {secret}")
        except Exception as e:
            print(f"Error getting previous version: {e}")
        
        # Example 4: List available secrets
        print("\n4. Listing available secrets:")
        try:
            secrets = client.list_secrets(max_results=5)
            for secret in secrets:
                print(f"- {secret['Name']} (Last modified: {secret['LastModifiedDate']})")
        except Exception as e:
            print(f"Error listing secrets: {e}")
        
        # Example 5: Get secret metadata
        print("\n5. Getting secret metadata:")
        try:
            metadata = client.describe_secret('my-secret')
            print(f"Secret description: {metadata.get('Description', 'No description')}")
            print(f"Secret tags: {metadata.get('Tags', [])}")
        except Exception as e:
            print(f"Error describing secret: {e}")
            
    except Exception as e:
        print(f"Failed to initialize client: {e}")


async def async_example():
    """Asynchronous Secrets Manager usage example."""
    print("\n=== Asynchronous Secrets Manager Example ===")
    
    try:
        # Initialize the async client
        client = AsyncSecretsManagerClient(region_name='us-east-1')
        
        # Example 1: Get multiple secrets concurrently
        print("\n1. Getting multiple secrets concurrently:")
        try:
            secret_ids = ['secret1', 'secret2', 'secret3']
            tasks = [client.get_secret(secret_id) for secret_id in secret_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for secret_id, result in zip(secret_ids, results):
                if isinstance(result, Exception):
                    print(f"Error getting {secret_id}: {result}")
                else:
                    print(f"Successfully retrieved {secret_id}")
        except Exception as e:
            print(f"Error in concurrent retrieval: {e}")
        
        # Example 2: Get secret with error handling
        print("\n2. Getting secret with error handling:")
        try:
            secret = await client.get_secret_dict('my-config-secret')
            print(f"Configuration loaded successfully: {list(secret.keys())}")
        except Exception as e:
            print(f"Error getting configuration secret: {e}")
        
        # Example 3: List secrets asynchronously
        print("\n3. Listing secrets asynchronously:")
        try:
            secrets = await client.list_secrets(max_results=3)
            print(f"Found {len(secrets)} secrets")
            for secret in secrets:
                print(f"- {secret['Name']}")
        except Exception as e:
            print(f"Error listing secrets: {e}")
            
    except Exception as e:
        print(f"Failed to initialize async client: {e}")


def error_handling_example():
    """Error handling examples."""
    print("\n=== Error Handling Examples ===")
    
    try:
        client = SecretsManagerClient(region_name='us-east-1')
        
        # Example 1: Handle secret not found
        print("\n1. Handling secret not found:")
        try:
            secret = client.get_secret('non-existent-secret')
            print(f"Secret: {secret}")
        except Exception as e:
            print(f"Expected error: {type(e).__name__}: {e}")
        
        # Example 2: Handle invalid secret ID
        print("\n2. Handling invalid secret ID:")
        try:
            secret = client.get_secret('')
            print(f"Secret: {secret}")
        except Exception as e:
            print(f"Expected error: {type(e).__name__}: {e}")
        
        # Example 3: Handle access denied
        print("\n3. Handling access denied:")
        try:
            secret = client.get_secret('restricted-secret')
            print(f"Secret: {secret}")
        except Exception as e:
            print(f"Expected error: {type(e).__name__}: {e}")
            
    except Exception as e:
        print(f"Failed to initialize client: {e}")


def main():
    """Main function to run all examples."""
    print("AWS Secrets Manager Examples")
    print("=" * 50)
    
    # Run synchronous examples
    sync_example()
    
    # Run asynchronous examples
    asyncio.run(async_example())
    
    # Run error handling examples
    error_handling_example()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
