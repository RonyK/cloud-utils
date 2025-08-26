"""
Async AWS Secrets Manager Client

Provides asynchronous functionality to retrieve secrets from AWS Secrets Manager.
"""

import json
import logging
from typing import Any, Dict, Optional, Union

try:
    import aioboto3
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

from ...exceptions import (
    CloudUtilsError,
    AuthError,
    ConnectionError,
    ResourceNotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class AsyncSecretsManagerError(CloudUtilsError):
    """Base exception for async Secrets Manager operations."""
    pass


class AsyncSecretsManagerAuthError(AuthError):
    """Authentication error for async Secrets Manager."""
    pass


class AsyncSecretsManagerConnectionError(ConnectionError):
    """Connection error for async Secrets Manager."""
    pass


class AsyncSecretsManagerNotFoundError(ResourceNotFoundError):
    """Secret not found error for async operations."""
    pass


class AsyncSecretsManagerValidationError(ValidationError):
    """Validation error for async Secrets Manager operations."""
    pass


class AsyncSecretsManagerClient:
    """
    Async AWS Secrets Manager client for retrieving secrets.
    
    This client provides asynchronous methods to retrieve secrets from AWS Secrets Manager
    with proper error handling and logging.
    """
    
    def __init__(
        self,
        region_name: Optional[str] = None,
        profile_name: Optional[str] = None,
        session: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize the async Secrets Manager client.
        
        Args:
            region_name: AWS region name (e.g., 'us-east-1')
            profile_name: AWS profile name to use
            session: Boto3 session object
            **kwargs: Additional arguments passed to boto3.client
        """
        if not AWS_AVAILABLE:
            raise ImportError(
                "aioboto3 and boto3 are required for async AWS Secrets Manager operations. "
                "Install with: pip install 'cloud-utils[aws-aio]'"
            )
        
        self.region_name = region_name
        self.profile_name = profile_name
        self.session = session
        self.kwargs = kwargs
        
        # Create aioboto3 session
        if session:
            self.aiosession = aioboto3.Session(boto_session=session)
        else:
            self.aiosession = aioboto3.Session()
            
        logger.info(f"Async Secrets Manager client initialized for region: {region_name or 'default'}")
    
    async def get_secret(
        self,
        secret_id: str,
        version_stage: Optional[str] = None,
        version_id: Optional[str] = None,
        as_dict: bool = True
    ) -> Union[str, Dict[str, Any]]:
        """
        Retrieve a secret from AWS Secrets Manager asynchronously.
        
        Args:
            secret_id: The identifier for the secret
            version_stage: The staging label of the version of the secret to retrieve
            version_id: The unique identifier of the version of the secret to retrieve
            as_dict: If True, return as dictionary; if False, return as string
            
        Returns:
            The secret value as string or dictionary
            
        Raises:
            AsyncSecretsManagerError: For general errors
            AsyncSecretsManagerAuthError: For authentication errors
            AsyncSecretsManagerConnectionError: For connection errors
            AsyncSecretsManagerNotFoundError: When secret is not found
            AsyncSecretsManagerValidationError: For validation errors
        """
        if not secret_id or not secret_id.strip():
            raise AsyncSecretsManagerValidationError("secret_id cannot be empty")
        
        try:
            async with self.aiosession.client('secretsmanager', **self.kwargs) as client:
                # Prepare parameters
                params = {'SecretId': secret_id}
                if version_stage:
                    params['VersionStage'] = version_stage
                if version_id:
                    params['VersionId'] = version_id
                
                logger.info(f"Retrieving secret: {secret_id}")
                response = await client.get_secret_value(**params)
                
                # Extract the secret value
                secret_value = response.get('SecretString')
                if secret_value is None:
                    # Handle binary secrets
                    secret_value = response.get('SecretBinary')
                    if secret_value is None:
                        raise AsyncSecretsManagerError("Secret has no value")
                
                # Parse JSON if requested and possible
                if as_dict and isinstance(secret_value, str):
                    try:
                        return json.loads(secret_value)
                    except json.JSONDecodeError:
                        logger.warning(f"Secret {secret_id} is not valid JSON, returning as string")
                        return secret_value
                
                return secret_value
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ResourceNotFoundException':
                raise AsyncSecretsManagerNotFoundError(f"Secret {secret_id} not found") from e
            elif error_code == 'InvalidParameterException':
                raise AsyncSecretsManagerValidationError(f"Invalid parameter: {error_message}") from e
            elif error_code == 'AccessDeniedException':
                raise AsyncSecretsManagerAuthError(f"Access denied to secret {secret_id}") from e
            elif error_code == 'DecryptionFailureException':
                raise AsyncSecretsManagerError(f"Failed to decrypt secret {secret_id}") from e
            elif error_code == 'InternalServiceErrorException':
                raise AsyncSecretsManagerConnectionError(f"Internal service error: {error_message}") from e
            elif error_code == 'InvalidRequestException':
                raise AsyncSecretsManagerValidationError(f"Invalid request: {error_message}") from e
            else:
                raise AsyncSecretsManagerError(f"Failed to retrieve secret {secret_id}: {error_message}") from e
                
        except Exception as e:
            raise AsyncSecretsManagerError(f"Unexpected error retrieving secret {secret_id}: {e}") from e
    
    async def get_secret_string(self, secret_id: str, **kwargs) -> str:
        """
        Retrieve a secret as a string asynchronously.
        
        Args:
            secret_id: The identifier for the secret
            **kwargs: Additional arguments passed to get_secret
            
        Returns:
            The secret value as a string
        """
        result = await self.get_secret(secret_id, as_dict=False, **kwargs)
        if isinstance(result, bytes):
            return result.decode('utf-8')
        return str(result)
    
    async def get_secret_dict(self, secret_id: str, **kwargs) -> Dict[str, Any]:
        """
        Retrieve a secret as a dictionary asynchronously.
        
        Args:
            secret_id: The identifier for the secret
            **kwargs: Additional arguments passed to get_secret
            
        Returns:
            The secret value as a dictionary
            
        Raises:
            AsyncSecretsManagerValidationError: If secret cannot be parsed as JSON
        """
        result = await self.get_secret(secret_id, as_dict=True, **kwargs)
        if not isinstance(result, dict):
            raise AsyncSecretsManagerValidationError(f"Secret {secret_id} is not a valid JSON object")
        return result
    
    async def list_secrets(
        self,
        max_results: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        List available secrets asynchronously.
        
        Args:
            max_results: Maximum number of results to return
            filters: Filters to apply to the list
            
        Returns:
            List of secret metadata
            
        Raises:
            AsyncSecretsManagerError: For general errors
            AsyncSecretsManagerAuthError: For authentication errors
        """
        try:
            async with self.aiosession.client('secretsmanager', **self.kwargs) as client:
                params = {}
                if max_results:
                    params['MaxResults'] = max_results
                if filters:
                    params['Filters'] = filters
                
                logger.info("Listing secrets")
                response = await client.list_secrets(**params)
                return response.get('SecretList', [])
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'AccessDeniedException':
                raise AsyncSecretsManagerAuthError("Access denied to list secrets") from e
            else:
                raise AsyncSecretsManagerError(f"Failed to list secrets: {error_message}") from e
                
        except Exception as e:
            raise AsyncSecretsManagerError(f"Unexpected error listing secrets: {e}") from e
    
    async def describe_secret(self, secret_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a secret asynchronously.
        
        Args:
            secret_id: The identifier for the secret
            
        Returns:
            Secret metadata
            
        Raises:
            AsyncSecretsManagerError: For general errors
            AsyncSecretsManagerNotFoundError: When secret is not found
        """
        try:
            async with self.aiosession.client('secretsmanager', **self.kwargs) as client:
                logger.info(f"Describing secret: {secret_id}")
                response = await client.describe_secret(SecretId=secret_id)
                return response
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ResourceNotFoundException':
                raise AsyncSecretsManagerNotFoundError(f"Secret {secret_id} not found") from e
            else:
                raise AsyncSecretsManagerError(f"Failed to describe secret {secret_id}: {error_message}") from e
                
        except Exception as e:
            raise AsyncSecretsManagerError(f"Unexpected error describing secret {secret_id}: {e}") from e
