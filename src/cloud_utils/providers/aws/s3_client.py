"""
AWS S3 Synchronous Client

Provides synchronous operations for AWS S3 service.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from ...exceptions import AWSConfigError, AWSConnectionError, AWSResourceNotFoundError
from ...utils.backoff import RetryConfig

logger = logging.getLogger(__name__)


class S3Client:
    """AWS S3 synchronous operations class"""
    
    def __init__(
        self,
        region_name: Optional[str] = None,
        profile_name: Optional[str] = None,
        config: Optional[Config] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize S3 client
        
        Args:
            region_name: AWS region name
            profile_name: AWS profile name
            config: boto3 configuration object
            **kwargs: Additional boto3 session parameters
        """
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.profile_name = profile_name or os.getenv('AWS_PROFILE')
        self.config = config or Config(
            retries={'max_attempts': 3, 'mode': 'standard'},
            max_pool_connections=50
        )
        self.kwargs = kwargs
        self._session = None
        self._client = None
        self._resource = None
        
        # Retry configuration
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=30.0,
            factor=2.0,
            jitter=True
        )
    
    @property
    def session(self):
        """Return boto3 session"""
        if self._session is None:
            try:
                self._session = boto3.Session(
                    profile_name=self.profile_name,
                    region_name=self.region_name,
                    **self.kwargs
                )
            except Exception as e:
                logger.error(f"Failed to create AWS session: {e}")
                raise AWSConfigError(f"Failed to create AWS session: {e}") from e
        return self._session
    
    @property
    def client(self):
        """Return S3 client"""
        if self._client is None:
            try:
                self._client = self.session.client('s3', config=self.config)
            except Exception as e:
                logger.error(f"Failed to create S3 client: {e}")
                raise AWSConfigError(f"Failed to create S3 client: {e}") from e
        return self._client
    
    @property
    def resource(self):
        """Return S3 resource"""
        if self._resource is None:
            try:
                self._resource = self.session.resource('s3', config=self.config)
            except Exception as e:
                logger.error(f"Failed to create S3 resource: {e}")
                raise AWSConfigError(f"Failed to create S3 resource: {e}") from e
        return self._resource
    
    def create_bucket(
        self,
        bucket_name: str,
        region: Optional[str] = None,
        **kwargs: Any
    ) -> bool:
        """
        Create S3 bucket
        
        Args:
            bucket_name: Bucket name
            region: Region to create bucket in (default: current region)
            **kwargs: Additional bucket options
            
        Returns:
            bool: True if creation successful
            
        Raises:
            AWSConnectionError: If bucket creation fails
        """
        def _create_bucket():
            try:
                params = {
                    'Bucket': bucket_name,
                    **kwargs
                }
                
                # Set LocationConstraint if region specified
                if region and region != 'us-east-1':
                    params['CreateBucketConfiguration'] = {
                        'LocationConstraint': region
                    }
                
                self.client.create_bucket(**params)
                logger.info(f"Successfully created S3 bucket: {bucket_name}")
                return True
                
            except Exception as e:
                self._handle_aws_error(e, f"create bucket {bucket_name}")
        
        return self.retry_config.retry(_create_bucket)
    
    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Delete S3 bucket
        
        Args:
            bucket_name: Bucket name to delete
            force: Force delete (delete contents even if bucket has objects)
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            AWSConnectionError: If bucket deletion fails
        """
        def _delete_bucket():
            try:
                if force:
                    # Delete all objects in bucket
                    bucket = self.resource.Bucket(bucket_name)
                    bucket.objects.all().delete()
                    logger.info(f"Deleted all objects from bucket: {bucket_name}")
                
                self.client.delete_bucket(Bucket=bucket_name)
                logger.info(f"Successfully deleted S3 bucket: {bucket_name}")
                return True
                
            except Exception as e:
                self._handle_aws_error(e, f"delete bucket {bucket_name}")
        
        return self.retry_config.retry(_delete_bucket)
    
    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Check if bucket exists
        
        Args:
            bucket_name: Bucket name to check
            
        Returns:
            bool: True if bucket exists
            
        Raises:
            AWSConnectionError: If check fails
        """
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                self._handle_aws_error(e, f"check bucket existence {bucket_name}")
        except Exception as e:
            self._handle_aws_error(e, f"check bucket existence {bucket_name}")
    
    def upload_file(
        self,
        file_path: str,
        bucket_name: str,
        object_key: str,
        **kwargs: Any
    ) -> bool:
        """
        Upload local file to S3
        
        Args:
            file_path: Local file path to upload
            bucket_name: Target bucket name
            object_key: S3 object key
            **kwargs: Additional upload options
            
        Returns:
            bool: True if upload successful
            
        Raises:
            AWSConnectionError: If file upload fails
        """
        def _upload_file():
            try:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                self.client.upload_file(
                    file_path,
                    bucket_name,
                    object_key,
                    **kwargs
                )
                
                logger.info(f"Successfully uploaded {file_path} to s3://{bucket_name}/{object_key}")
                return True
                
            except Exception as e:
                if isinstance(e, FileNotFoundError):
                    raise e
                else:
                    self._handle_aws_error(e, f"upload file {file_path} to bucket {bucket_name}")
        
        return self.retry_config.retry(_upload_file)
    
    def download_file(
        self,
        bucket_name: str,
        object_key: str,
        file_path: str,
        **kwargs: Any
    ) -> bool:
        """
        Download S3 object to local file
        
        Args:
            bucket_name: Source bucket name
            object_key: S3 object key
            file_path: Local file path to download to
            **kwargs: Additional download options
            
        Returns:
            bool: True if download successful
            
        Raises:
            AWSConnectionError: If file download fails
        """
        def _download_file():
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                self.client.download_file(
                    bucket_name,
                    object_key,
                    file_path,
                    **kwargs
                )
                
                logger.info(f"Successfully downloaded s3://{bucket_name}/{object_key} to {file_path}")
                return True
                
            except Exception as e:
                self._handle_aws_error(e, f"download file from bucket {bucket_name}")
        
        return self.retry_config.retry(_download_file)
    
    def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        List objects in bucket
        
        Args:
            bucket_name: Bucket name
            prefix: Object key prefix (optional)
            delimiter: Delimiter (optional)
            **kwargs: Additional list options
            
        Returns:
            List[Dict[str, Any]]: List of object information
            
        Raises:
            AWSConnectionError: If object listing fails
        """
        def _list_objects():
            try:
                params = {
                    'Bucket': bucket_name,
                    **kwargs
                }
                
                if prefix:
                    params['Prefix'] = prefix
                if delimiter:
                    params['Delimiter'] = delimiter
                
                response = self.client.list_objects_v2(**params)
                objects = response.get('Contents', [])
                
                logger.info(f"Found {len(objects)} objects in bucket {bucket_name}")
                return objects
                
            except Exception as e:
                self._handle_aws_error(e, f"list objects in bucket {bucket_name}")
        
        return self.retry_config.retry(_list_objects)
    
    def delete_object(self, bucket_name: str, object_key: str) -> bool:
        """
        Delete S3 object
        
        Args:
            bucket_name: Bucket name
            object_key: Object key to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            AWSConnectionError: If object deletion fails
        """
        def _delete_object():
            try:
                self.client.delete_object(
                    Bucket=bucket_name,
                    Key=object_key
                )
                
                logger.info(f"Successfully deleted s3://{bucket_name}/{object_key}")
                return True
                
            except Exception as e:
                self._handle_aws_error(e, f"delete object from bucket {bucket_name}")
        
        return self.retry_config.retry(_delete_object)
    
    def _handle_aws_error(self, error: Exception, operation: str) -> None:
        """
        Handle AWS errors and raise appropriate exceptions
        
        Args:
            error: AWS error that occurred
            operation: Description of operation being performed
            
        Raises:
            AWSConnectionError: For connection related errors
            AWSConfigError: For configuration related errors
        """
        if isinstance(error, ClientError):
            error_code = error.response['Error']['Code']
            error_message = error.response['Error']['Message']
            
            logger.error(f"AWS {operation} failed: {error_code} - {error_message}")
            
            if error_code in ['UnauthorizedOperation', 'AccessDenied']:
                raise AWSConfigError(f"Access denied for {operation}: {error_message}")
            elif error_code in ['InvalidParameterValue', 'ValidationException']:
                raise AWSConfigError(f"Invalid parameter for {operation}: {error_message}")
            elif error_code == 'NoSuchBucket':
                raise AWSResourceNotFoundError(f"Bucket not found for {operation}: {error_message}")
            else:
                raise AWSConnectionError(f"AWS {operation} failed: {error_code} - {error_message}")
        
        else:
            logger.error(f"Unexpected error during {operation}: {error}")
            raise AWSConnectionError(f"Unexpected error during {operation}: {error}")
