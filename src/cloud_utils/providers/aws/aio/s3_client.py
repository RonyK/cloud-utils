"""
AWS S3 Asynchronous Client

Provides asynchronous operations for AWS S3 service.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

import aioboto3
from botocore.config import Config

from ...exceptions import AWSConfigError, AWSConnectionError, AWSResourceNotFoundError

logger = logging.getLogger(__name__)


class AioS3Client:
    """AWS S3 asynchronous operations class"""
    
    def __init__(
        self,
        region_name: Optional[str] = None,
        profile_name: Optional[str] = None,
        config: Optional[Config] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize S3 Async class
        
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
    
    async def _get_session(self):
        """Return aioboto3 session"""
        if self._session is None:
            self._session = aioboto3.Session(
                profile_name=self.profile_name,
                region_name=self.region_name,
                **self.kwargs
            )
        return self._session
    
    async def create_bucket(
        self,
        bucket_name: str,
        region: Optional[str] = None,
        **kwargs: Any
    ) -> bool:
        """
        Create S3 bucket asynchronously
        
        Args:
            bucket_name: Bucket name
            region: Region to create bucket in (default: current region)
            **kwargs: Additional bucket options
            
        Returns:
            bool: True if creation successful
            
        Raises:
            AWSConnectionError: If bucket creation fails
        """
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
            
            async with (await self._get_session()).client('s3', config=self.config) as s3_client:
                await s3_client.create_bucket(**params)
                
                logger.info(f"Successfully created S3 bucket: {bucket_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create S3 bucket {bucket_name}: {e}")
            raise AWSConnectionError(f"Failed to create S3 bucket {bucket_name}: {e}") from e
    
    async def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Delete S3 bucket asynchronously
        
        Args:
            bucket_name: Bucket name to delete
            force: Force delete (delete contents even if bucket has objects)
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            AWSConnectionError: If bucket deletion fails
        """
        try:
            async with (await self._get_session()).client('s3', config=self.config) as s3_client:
                if force:
                    # Delete all objects in bucket
                    paginator = s3_client.get_paginator('list_objects_v2')
                    async for page in paginator.paginate(Bucket=bucket_name):
                        if 'Contents' in page:
                            objects = [{'Key': obj['Key']} for obj in page['Contents']]
                            if objects:
                                await s3_client.delete_objects(
                                    Bucket=bucket_name,
                                    Delete={'Objects': objects}
                                )
                    
                    logger.info(f"Deleted all objects from bucket: {bucket_name}")
                
                await s3_client.delete_bucket(Bucket=bucket_name)
                
                logger.info(f"Successfully deleted S3 bucket: {bucket_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete S3 bucket {bucket_name}: {e}")
            raise AWSConnectionError(f"Failed to delete S3 bucket {bucket_name}: {e}") from e
    
    async def bucket_exists(self, bucket_name: str) -> bool:
        """
        Check if bucket exists asynchronously
        
        Args:
            bucket_name: Bucket name to check
            
        Returns:
            bool: True if bucket exists
            
        Raises:
            AWSConnectionError: If check fails
        """
        try:
            async with (await self._get_session()).client('s3', config=self.config) as s3_client:
                await s3_client.head_bucket(Bucket=bucket_name)
                return True
                
        except Exception as e:
            if '404' in str(e) or 'NoSuchBucket' in str(e):
                return False
            else:
                logger.error(f"Failed to check bucket existence {bucket_name}: {e}")
                raise AWSConnectionError(f"Failed to check bucket existence {bucket_name}: {e}") from e
    
    async def upload_file(
        self,
        file_path: str,
        bucket_name: str,
        object_key: str,
        **kwargs: Any
    ) -> bool:
        """
        Upload local file to S3 asynchronously
        
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
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            async with (await self._get_session()).client('s3', config=self.config) as s3_client:
                await s3_client.upload_file(
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
                logger.error(f"Failed to upload file {file_path} to bucket {bucket_name}: {e}")
                raise AWSConnectionError(f"Failed to upload file {file_path} to bucket {bucket_name}: {e}") from e
    
    async def download_file(
        self,
        bucket_name: str,
        object_key: str,
        file_path: str,
        **kwargs: Any
    ) -> bool:
        """
        Download S3 object to local file asynchronously
        
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
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            async with (await self._get_session()).client('s3', config=self.config) as s3_client:
                await s3_client.download_file(
                    bucket_name,
                    object_key,
                    file_path,
                    **kwargs
                )
                
                logger.info(f"Successfully downloaded s3://{bucket_name}/{object_key} to {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to download file from bucket {bucket_name}: {e}")
            raise AWSConnectionError(f"Failed to download file from bucket {bucket_name}: {e}") from e
    
    async def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        delimiter: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        List objects in bucket asynchronously
        
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
        try:
            params = {
                'Bucket': bucket_name,
                **kwargs
            }
            
            if prefix:
                params['Prefix'] = prefix
            if delimiter:
                params['Delimiter'] = delimiter
            
            async with (await self._get_session()).client('s3', config=self.config) as s3_client:
                response = await s3_client.list_objects_v2(**params)
                objects = response.get('Contents', [])
                
                logger.info(f"Found {len(objects)} objects in bucket {bucket_name}")
                return objects
                
        except Exception as e:
            logger.error(f"Failed to list objects in bucket {bucket_name}: {e}")
            raise AWSConnectionError(f"Failed to list objects in bucket {bucket_name}: {e}") from e
    
    async def delete_object(self, bucket_name: str, object_key: str) -> bool:
        """
        Delete S3 object asynchronously
        
        Args:
            bucket_name: Bucket name
            object_key: Object key to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            AWSConnectionError: If object deletion fails
        """
        try:
            async with (await self._get_session()).client('s3', config=self.config) as s3_client:
                await s3_client.delete_object(
                    Bucket=bucket_name,
                    Key=object_key
                )
                
                logger.info(f"Successfully deleted s3://{bucket_name}/{object_key}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete object from bucket {bucket_name}: {e}")
            raise AWSConnectionError(f"Failed to delete object from bucket {bucket_name}: {e}") from e
    
    async def upload_multipart(
        self,
        file_path: str,
        bucket_name: str,
        object_key: str,
        chunk_size: int = 8 * 1024 * 1024,  # 8MB
        **kwargs: Any
    ) -> bool:
        """
        Upload large file using multipart upload asynchronously
        
        Args:
            file_path: Local file path to upload
            bucket_name: Target bucket name
            object_key: S3 object key
            chunk_size: Chunk size (bytes)
            **kwargs: Additional upload options
            
        Returns:
            bool: True if upload successful
            
        Raises:
            AWSConnectionError: If multipart upload fails
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            async with (await self._get_session()).client('s3', config=self.config) as s3_client:
                # Start multipart upload
                response = await s3_client.create_multipart_upload(
                    Bucket=bucket_name,
                    Key=object_key,
                    **kwargs
                )
                
                upload_id = response['UploadId']
                parts = []
                
                try:
                    with open(file_path, 'rb') as f:
                        part_number = 1
                        
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            
                            # Upload part
                            part_response = await s3_client.upload_part(
                                Bucket=bucket_name,
                                Key=object_key,
                                PartNumber=part_number,
                                UploadId=upload_id,
                                Body=chunk
                            )
                            
                            parts.append({
                                'ETag': part_response['ETag'],
                                'PartNumber': part_number
                            })
                            
                            part_number += 1
                    
                    # Complete multipart upload
                    await s3_client.complete_multipart_upload(
                        Bucket=bucket_name,
                        Key=object_key,
                        UploadId=upload_id,
                        MultipartUpload={'Parts': parts}
                    )
                    
                    logger.info(f"Successfully uploaded {file_path} to s3://{bucket_name}/{object_key} using multipart upload")
                    return True
                    
                except Exception as e:
                    # Clean up on upload failure
                    await s3_client.abort_multipart_upload(
                        Bucket=bucket_name,
                        Key=object_key,
                        UploadId=upload_id
                    )
                    raise e
                    
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise e
            else:
                logger.error(f"Failed to multipart upload file {file_path} to bucket {bucket_name}: {e}")
                raise AWSConnectionError(f"Failed to multipart upload file {file_path} to bucket {bucket_name}: {e}") from e
