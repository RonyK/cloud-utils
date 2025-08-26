"""
AWS SQS Asynchronous Client

Provides asynchronous operations for AWS SQS service.
"""

import logging
import json
from typing import Any, Dict, List, Optional, Union

import aioboto3
from botocore.config import Config

from ...exceptions import AWSConfigError, AWSConnectionError, AWSResourceNotFoundError

logger = logging.getLogger(__name__)


class AioSQSClient:
    """AWS SQS asynchronous operations class"""
    
    def __init__(
        self,
        region_name: Optional[str] = None,
        profile_name: Optional[str] = None,
        config: Optional[Config] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize SQS Async class
        
        Args:
            region_name: AWS region name
            profile_name: AWS profile name
            config: boto3 configuration object
            **kwargs: Additional boto3 session parameters
        """
        self.region_name = region_name or 'us-east-1'
        self.profile_name = profile_name
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
    
    async def create_queue(
        self,
        queue_name: str,
        attributes: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create SQS queue asynchronously
        
        Args:
            queue_name: Name of the queue to create
            attributes: Queue attributes (e.g., visibility timeout, message retention)
            tags: Tags to associate with the queue
            
        Returns:
            str: Queue URL
            
        Raises:
            AWSConnectionError: If queue creation fails
        """
        try:
            params = {
                'QueueName': queue_name
            }
            
            if attributes:
                params['Attributes'] = attributes
            if tags:
                params['tags'] = tags
            
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                response = await sqs_client.create_queue(**params)
                queue_url = response['QueueUrl']
                
                logger.info(f"Successfully created SQS queue: {queue_name}")
                return queue_url
                
        except Exception as e:
            logger.error(f"Failed to create SQS queue {queue_name}: {e}")
            raise AWSConnectionError(f"Failed to create SQS queue {queue_name}: {e}") from e
    
    async def delete_queue(self, queue_url: str) -> bool:
        """
        Delete SQS queue asynchronously
        
        Args:
            queue_url: URL of the queue to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            AWSConnectionError: If queue deletion fails
        """
        try:
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                await sqs_client.delete_queue(QueueUrl=queue_url)
                logger.info(f"Successfully deleted SQS queue: {queue_url}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete SQS queue {queue_url}: {e}")
            raise AWSConnectionError(f"Failed to delete SQS queue {queue_url}: {e}") from e
    
    async def get_queue_url(self, queue_name: str, account_id: Optional[str] = None) -> str:
        """
        Get queue URL by name asynchronously
        
        Args:
            queue_name: Name of the queue
            account_id: AWS account ID (optional)
            
        Returns:
            str: Queue URL
            
        Raises:
            AWSResourceNotFoundError: If queue not found
            AWSConnectionError: If operation fails
        """
        try:
            params = {'QueueName': queue_name}
            if account_id:
                params['QueueOwnerAWSAccountId'] = account_id
            
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                response = await sqs_client.get_queue_url(**params)
                return response['QueueUrl']
                
        except Exception as e:
            logger.error(f"Failed to get queue URL for {queue_name}: {e}")
            raise AWSConnectionError(f"Failed to get queue URL for {queue_name}: {e}") from e
    
    async def list_queues(
        self,
        queue_name_prefix: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> List[str]:
        """
        List SQS queues asynchronously
        
        Args:
            queue_name_prefix: Prefix to filter queue names
            max_results: Maximum number of results to return
            
        Returns:
            List[str]: List of queue URLs
            
        Raises:
            AWSConnectionError: If listing fails
        """
        try:
            params = {}
            if queue_name_prefix:
                params['QueueNamePrefix'] = queue_name_prefix
            if max_results:
                params['MaxResults'] = max_results
            
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                response = await sqs_client.list_queues(**params)
                queue_urls = response.get('QueueUrls', [])
                
                logger.info(f"Found {len(queue_urls)} SQS queues")
                return queue_urls
                
        except Exception as e:
            logger.error(f"Failed to list SQS queues: {e}")
            raise AWSConnectionError(f"Failed to list SQS queues: {e}") from e
    
    async def send_message(
        self,
        queue_url: str,
        message_body: Union[str, Dict[str, Any]],
        delay_seconds: Optional[int] = None,
        message_attributes: Optional[Dict[str, Dict[str, Any]]] = None,
        message_group_id: Optional[str] = None,
        message_deduplication_id: Optional[str] = None
    ) -> str:
        """
        Send message to SQS queue asynchronously
        
        Args:
            queue_url: URL of the target queue
            message_body: Message content (string or dictionary - dict will be converted to JSON)
            delay_seconds: Delay before message becomes visible (0-900 seconds)
            message_attributes: Additional message attributes
            message_group_id: Message group ID for FIFO queues
            message_deduplication_id: Deduplication ID for FIFO queues
            
        Returns:
            str: Message ID
            
        Raises:
            AWSConnectionError: If message sending fails
        """
        try:
            # Convert dict to JSON string if necessary
            if isinstance(message_body, dict):
                message_body = json.dumps(message_body, ensure_ascii=False, default=str)
            
            params = {
                'QueueUrl': queue_url,
                'MessageBody': message_body
            }
            
            if delay_seconds is not None:
                params['DelaySeconds'] = delay_seconds
            if message_attributes:
                params['MessageAttributes'] = message_attributes
            if message_group_id:
                params['MessageGroupId'] = message_group_id
            if message_deduplication_id:
                params['MessageDeduplicationId'] = message_deduplication_id
            
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                response = await sqs_client.send_message(**params)
                message_id = response['MessageId']
                
                logger.info(f"Successfully sent message {message_id} to queue {queue_url}")
                return message_id
                
        except Exception as e:
            logger.error(f"Failed to send message to queue {queue_url}: {e}")
            raise AWSConnectionError(f"Failed to send message to queue {queue_url}: {e}") from e
    
    async def send_message_batch(
        self,
        queue_url: str,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Send multiple messages to SQS queue in batch asynchronously
        
        Args:
            queue_url: URL of the target queue
            messages: List of message dictionaries with keys:
                     - 'Id': Unique identifier for the message
                     - 'MessageBody': Message content (string or dictionary - dict will be converted to JSON)
                     - 'DelaySeconds': Optional delay
                     - 'MessageAttributes': Optional attributes
                     - 'MessageGroupId': Optional group ID for FIFO
                     - 'MessageDeduplicationId': Optional deduplication ID for FIFO
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Results with 'Successful' and 'Failed' lists
            
        Raises:
            AWSConnectionError: If batch sending fails
        """
        try:
            # Process messages to convert dict MessageBody to JSON string
            processed_messages = []
            for message in messages:
                processed_message = message.copy()
                
                # Convert dict MessageBody to JSON string if necessary
                if isinstance(processed_message.get('MessageBody'), dict):
                    processed_message['MessageBody'] = json.dumps(
                        processed_message['MessageBody'], 
                        ensure_ascii=False, 
                        default=str
                    )
                
                processed_messages.append(processed_message)
            
            # SQS batch limit is 10 messages
            batch_size = 10
            all_results = {'Successful': [], 'Failed': []}
            
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                for i in range(0, len(processed_messages), batch_size):
                    batch = processed_messages[i:i + batch_size]
                    
                    params = {
                        'QueueUrl': queue_url,
                        'Entries': batch
                    }
                    
                    response = await sqs_client.send_message_batch(**params)
                    
                    if 'Successful' in response:
                        all_results['Successful'].extend(response['Successful'])
                    if 'Failed' in response:
                        all_results['Failed'].extend(response['Failed'])
            
            logger.info(f"Batch sent {len(all_results['Successful'])} messages to queue {queue_url}")
            return all_results
            
        except Exception as e:
            logger.error(f"Failed to send message batch to queue {queue_url}: {e}")
            raise AWSConnectionError(f"Failed to send message batch to queue {queue_url}: {e}") from e
    
    async def receive_messages(
        self,
        queue_url: str,
        max_number_of_messages: int = 10,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: int = 20,
        message_attribute_names: Optional[List[str]] = None,
        attribute_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Receive messages from SQS queue asynchronously
        
        Args:
            queue_url: URL of the source queue
            max_number_of_messages: Maximum number of messages to receive (1-10)
            visibility_timeout: Visibility timeout in seconds
            wait_time_seconds: Long polling wait time (0-20 seconds)
            message_attribute_names: Names of message attributes to retrieve
            attribute_names: Names of queue attributes to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of received messages
            
        Raises:
            AWSConnectionError: If message receiving fails
        """
        try:
            params = {
                'QueueUrl': queue_url,
                'MaxNumberOfMessages': max_number_of_messages,
                'WaitTimeSeconds': wait_time_seconds
            }
            
            if visibility_timeout is not None:
                params['VisibilityTimeout'] = visibility_timeout
            if message_attribute_names:
                params['MessageAttributeNames'] = message_attribute_names
            if attribute_names:
                params['AttributeNames'] = attribute_names
            
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                response = await sqs_client.receive_message(**params)
                messages = response.get('Messages', [])
                
                logger.info(f"Received {len(messages)} messages from queue {queue_url}")
                return messages
                
        except Exception as e:
            logger.error(f"Failed to receive messages from queue {queue_url}: {e}")
            raise AWSConnectionError(f"Failed to receive messages from queue {queue_url}: {e}") from e
    
    async def delete_message(self, queue_url: str, receipt_handle: str) -> bool:
        """
        Delete message from SQS queue asynchronously
        
        Args:
            queue_url: URL of the queue
            receipt_handle: Receipt handle from received message
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            AWSConnectionError: If message deletion fails
        """
        try:
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                await sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle
                )
                
                logger.info(f"Successfully deleted message with receipt handle {receipt_handle}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete message from queue {queue_url}: {e}")
            raise AWSConnectionError(f"Failed to delete message from queue {queue_url}: {e}") from e
    
    async def delete_message_batch(
        self,
        queue_url: str,
        messages: List[Dict[str, str]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Delete multiple messages from SQS queue in batch asynchronously
        
        Args:
            queue_url: URL of the queue
            messages: List of message dictionaries with keys:
                     - 'Id': Unique identifier for the message
                     - 'ReceiptHandle': Receipt handle from received message
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Results with 'Successful' and 'Failed' lists
            
        Raises:
            AWSConnectionError: If batch deletion fails
        """
        try:
            # SQS batch limit is 10 messages
            batch_size = 10
            all_results = {'Successful': [], 'Failed': []}
            
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                for i in range(0, len(messages), batch_size):
                    batch = messages[i:i + batch_size]
                    
                    params = {
                        'QueueUrl': queue_url,
                        'Entries': batch
                    }
                    
                    response = await sqs_client.delete_message_batch(**params)
                    
                    if 'Successful' in response:
                        all_results['Successful'].extend(response['Successful'])
                    if 'Failed' in response:
                        all_results['Failed'].extend(response['Failed'])
            
            logger.info(f"Batch deleted {len(all_results['Successful'])} messages from queue {queue_url}")
            return all_results
            
        except Exception as e:
            logger.error(f"Failed to delete message batch from queue {queue_url}: {e}")
            raise AWSConnectionError(f"Failed to delete message batch from queue {queue_url}: {e}") from e
    
    async def change_message_visibility(
        self,
        queue_url: str,
        receipt_handle: str,
        visibility_timeout: int
    ) -> bool:
        """
        Change message visibility timeout asynchronously
        
        Args:
            queue_url: URL of the queue
            receipt_handle: Receipt handle from received message
            visibility_timeout: New visibility timeout in seconds
            
        Returns:
            bool: True if operation successful
            
        Raises:
            AWSConnectionError: If operation fails
        """
        try:
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                await sqs_client.change_message_visibility(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle,
                    VisibilityTimeout=visibility_timeout
                )
                
                logger.info(f"Changed visibility timeout to {visibility_timeout} seconds for message {receipt_handle}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to change message visibility for queue {queue_url}: {e}")
            raise AWSConnectionError(f"Failed to change message visibility for queue {queue_url}: {e}") from e
    
    async def purge_queue(self, queue_url: str) -> bool:
        """
        Purge all messages from SQS queue asynchronously
        
        Args:
            queue_url: URL of the queue to purge
            
        Returns:
            bool: True if operation successful
            
        Raises:
            AWSConnectionError: If operation fails
        """
        try:
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                await sqs_client.purge_queue(QueueUrl=queue_url)
                logger.info(f"Successfully purged queue {queue_url}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to purge queue {queue_url}: {e}")
            raise AWSConnectionError(f"Failed to purge queue {queue_url}: {e}") from e
    
    async def get_queue_attributes(
        self,
        queue_url: str,
        attribute_names: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Get queue attributes asynchronously
        
        Args:
            queue_url: URL of the queue
            attribute_names: List of attribute names to retrieve
            
        Returns:
            Dict[str, str]: Queue attributes
            
        Raises:
            AWSConnectionError: If operation fails
        """
        try:
            params = {'QueueUrl': queue_url}
            if attribute_names:
                params['AttributeNames'] = attribute_names
            
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                response = await sqs_client.get_queue_attributes(**params)
                attributes = response.get('Attributes', {})
                
                logger.info(f"Retrieved {len(attributes)} attributes for queue {queue_url}")
                return attributes
                
        except Exception as e:
            logger.error(f"Failed to get attributes for queue {queue_url}: {e}")
            raise AWSConnectionError(f"Failed to get attributes for queue {queue_url}: {e}") from e
    
    async def long_poll_receive(
        self,
        queue_url: str,
        max_number_of_messages: int = 10,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: int = 20,
        message_attribute_names: Optional[List[str]] = None,
        attribute_names: Optional[List[str]] = None,
        max_poll_time: int = 300  # 5 minutes
    ) -> List[Dict[str, Any]]:
        """
        Long poll receive messages with extended timeout
        
        Args:
            queue_url: URL of the source queue
            max_number_of_messages: Maximum number of messages to receive (1-10)
            visibility_timeout: Visibility timeout in seconds
            wait_time_seconds: Long polling wait time (0-20 seconds)
            message_attribute_names: Names of message attributes to retrieve
            attribute_names: Names of queue attributes to retrieve
            max_poll_time: Maximum total polling time in seconds
            
        Returns:
            List[Dict[str, Any]]: List of received messages
            
        Raises:
            AWSConnectionError: If message receiving fails
        """
        try:
            import asyncio
            import time
            
            start_time = time.time()
            all_messages = []
            
            async with (await self._get_session()).client('sqs', config=self.config) as sqs_client:
                while (time.time() - start_time) < max_poll_time:
                    params = {
                        'QueueUrl': queue_url,
                        'MaxNumberOfMessages': max_number_of_messages,
                        'WaitTimeSeconds': wait_time_seconds
                    }
                    
                    if visibility_timeout is not None:
                        params['VisibilityTimeout'] = visibility_timeout
                    if message_attribute_names:
                        params['MessageAttributeNames'] = message_attribute_names
                    if attribute_names:
                        params['AttributeNames'] = attribute_names
                    
                    response = await sqs_client.receive_message(**params)
                    messages = response.get('Messages', [])
                    
                    if messages:
                        all_messages.extend(messages)
                        logger.info(f"Received {len(messages)} messages from queue {queue_url}")
                        break
                    
                    # If no messages and we're still within time limit, continue polling
                    if (time.time() - start_time) < max_poll_time:
                        await asyncio.sleep(1)  # Small delay before next poll
            
            logger.info(f"Long poll completed, total messages received: {len(all_messages)}")
            return all_messages
            
        except Exception as e:
            logger.error(f"Failed to long poll receive messages from queue {queue_url}: {e}")
            raise AWSConnectionError(f"Failed to long poll receive messages from queue {queue_url}: {e}") from e


class AioSQSHandler:
    """Asynchronous SQS handler for specific queue operations"""
    
    def __init__(
        self,
        queue_name: Optional[str] = None,
        queue_url: Optional[str] = None,
        region_name: Optional[str] = None,
        profile_name: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize async SQS handler for specific queue
        
        Args:
            queue_name: Name of the queue (will be used to get URL if queue_url not provided)
            queue_url: Direct URL of the queue
            region_name: AWS region name
            profile_name: AWS profile name
            **kwargs: Additional SQS client parameters
        """
        if not queue_name and not queue_url:
            raise ValueError("Either queue_name or queue_url must be provided")
        
        self.sqs_client = AioSQSClient(region_name=region_name, profile_name=profile_name, **kwargs)
        self._queue_name = None
        self._queue_url = None
        self._is_fifo = None
        
        # Store initial values for async initialization
        self._initial_queue_name = queue_name
        self._initial_queue_url = queue_url
    
    async def _initialize_queue_info(self) -> None:
        """Initialize and validate queue information asynchronously"""
        if self._initial_queue_name and self._initial_queue_url:
            # Both provided - validate consistency
            await self._validate_queue_consistency(self._initial_queue_name, self._initial_queue_url)
            self._queue_name = self._initial_queue_name
            self._queue_url = self._initial_queue_url
        elif self._initial_queue_url:
            # Only queue_url provided - extract queue_name
            self._queue_url = self._initial_queue_url
            self._queue_name = self._extract_queue_name_from_url(self._initial_queue_url)
        else:
            # Only queue_name provided - get queue_url
            self._queue_name = self._initial_queue_name
            self._queue_url = await self.sqs_client.get_queue_url(self._initial_queue_name)
    
    def _extract_queue_name_from_url(self, queue_url: str) -> str:
        """Extract queue name from queue URL"""
        # SQS URL format: https://sqs.{region}.amazonaws.com/{account_id}/{queue_name}
        # or for FIFO: https://sqs.{region}.amazonaws.com/{account_id}/{queue_name}.fifo
        try:
            # Split by '/' and get the last part
            parts = queue_url.rstrip('/').split('/')
            queue_name = parts[-1]
            
            # Remove .fifo suffix if present for name extraction
            if queue_name.endswith('.fifo'):
                queue_name = queue_name[:-5]  # Remove '.fifo'
            
            return queue_name
        except (IndexError, AttributeError):
            raise ValueError(f"Invalid queue URL format: {queue_url}")
    
    async def _validate_queue_consistency(self, queue_name: str, queue_url: str) -> None:
        """Validate that queue_name and queue_url are consistent"""
        extracted_name = self._extract_queue_name_from_url(queue_url)
        
        if extracted_name != queue_name:
            raise ValueError(
                f"Queue name mismatch: provided '{queue_name}' but URL contains '{extracted_name}'. "
                f"URL: {queue_url}"
            )
        
        # Additional validation: check if the queue actually exists and matches
        try:
            actual_url = await self.sqs_client.get_queue_url(queue_name)
            if actual_url != queue_url:
                raise ValueError(
                    f"Queue URL mismatch: provided '{queue_url}' but AWS returned '{actual_url}' "
                    f"for queue name '{queue_name}'"
                )
        except Exception as e:
            raise ValueError(f"Failed to validate queue consistency: {e}")
    
    @property
    def queue_name(self) -> str:
        """Get queue name"""
        if self._queue_name is None:
            raise RuntimeError("Queue information not yet initialized. Call an async method first.")
        return self._queue_name
    
    @property
    def queue_url(self) -> str:
        """Get queue URL"""
        if self._queue_url is None:
            raise RuntimeError("Queue information not yet initialized. Call an async method first.")
        return self._queue_url
    
    async def _ensure_initialized(self) -> None:
        """Ensure queue information is initialized"""
        if self._queue_url is None:
            await self._initialize_queue_info()
    
    async def _is_fifo(self) -> bool:
        """Check if the queue is a FIFO queue"""
        if self._is_fifo is None:
            await self._ensure_initialized()
            # FIFO queues end with .fifo
            self._is_fifo = self.queue_url.endswith('.fifo')
        return self._is_fifo
    
    def _generate_deduplication_id(self, message_body: str) -> str:
        """Generate deduplication ID for FIFO queue messages"""
        import hashlib
        import time
        
        # Create a hash based on message body and timestamp
        content = f"{message_body}_{int(time.time() * 1000)}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _generate_group_id(self) -> str:
        """Generate group ID for FIFO queue messages"""
        import time
        
        # Use timestamp as group ID for simple grouping
        return f"group_{int(time.time() * 1000)}"
    
    async def send_message(
        self,
        message_body: Union[str, Dict[str, Any]],
        delay_seconds: Optional[int] = None,
        message_attributes: Optional[Dict[str, Dict[str, Any]]] = None,
        message_group_id: Optional[str] = None,
        message_deduplication_id: Optional[str] = None
    ) -> str:
        """Send message to the specific queue"""
        await self._ensure_initialized()
        
        # For FIFO queues, ensure required parameters are set
        if await self._is_fifo():
            if message_deduplication_id is None:
                # Convert dict to string for deduplication ID generation if necessary
                if isinstance(message_body, dict):
                    message_body_str = json.dumps(message_body, ensure_ascii=False, default=str)
                else:
                    message_body_str = message_body
                message_deduplication_id = self._generate_deduplication_id(message_body_str)
            if message_group_id is None:
                message_group_id = self._generate_group_id()
            
            # FIFO queues don't support delay_seconds
            delay_seconds = None
        
        return await self.sqs_client.send_message(
            queue_url=self.queue_url,
            message_body=message_body,
            delay_seconds=delay_seconds,
            message_attributes=message_attributes,
            message_group_id=message_group_id,
            message_deduplication_id=message_deduplication_id
        )
    
    async def send_message_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Send batch messages to the specific queue"""
        await self._ensure_initialized()
        
        # For FIFO queues, ensure required parameters are set for each message
        if await self._is_fifo():
            processed_messages = []
            for message in messages:
                processed_message = message.copy()
                
                # Ensure Id is present
                if 'Id' not in processed_message:
                    processed_message['Id'] = f"msg_{len(processed_messages)}"
                
                # Ensure MessageDeduplicationId is present
                if 'MessageDeduplicationId' not in processed_message:
                    message_body = processed_message.get('MessageBody', '')
                    processed_message['MessageDeduplicationId'] = self._generate_deduplication_id(message_body)
                
                # Ensure MessageGroupId is present
                if 'MessageGroupId' not in processed_message:
                    processed_message['MessageGroupId'] = self._generate_group_id()
                
                processed_messages.append(processed_message)
            
            messages = processed_messages
        
        return await self.sqs_client.send_message_batch(
            queue_url=self.queue_url,
            messages=messages
        )
    
    async def send_messages(
        self,
        message_bodies: List[Union[str, Dict[str, Any]]],
        delay_seconds: Optional[int] = None,
        message_attributes: Optional[Dict[str, Dict[str, Any]]] = None,
        message_group_id: Optional[str] = None,
        message_deduplication_id: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Send multiple message bodies to the specific queue in batch
        
        Args:
            message_bodies: List of message body strings or dictionaries (dicts will be converted to JSON)
            delay_seconds: Delay before messages become visible (0-900 seconds, not supported for FIFO)
            message_attributes: Additional message attributes to apply to all messages
            message_group_id: Message group ID for FIFO queues (applied to all messages)
            message_deduplication_id: Deduplication ID for FIFO queues (auto-generated if not provided)
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Results with 'Successful' and 'Failed' lists
            
        Note:
            For FIFO queues, if message_deduplication_id is not provided, 
            it will be auto-generated for each message to ensure uniqueness.
        """
        await self._ensure_initialized()
        
        # Convert message bodies to proper message format
        messages = []
        for i, message_body in enumerate(message_bodies):
            # Convert dict to JSON string if necessary
            if isinstance(message_body, dict):
                message_body_str = json.dumps(message_body, ensure_ascii=False, default=str)
            else:
                message_body_str = message_body
            
            message = {
                'Id': f"msg_{i}",
                'MessageBody': message_body_str
            }
            
            # Add optional parameters if provided
            if delay_seconds is not None and not await self._is_fifo():
                message['DelaySeconds'] = delay_seconds
            if message_attributes:
                message['MessageAttributes'] = message_attributes
            if message_group_id and await self._is_fifo():
                message['MessageGroupId'] = message_group_id
            if message_deduplication_id and await self._is_fifo():
                message['MessageDeduplicationId'] = message_deduplication_id
            
            messages.append(message)
        
        # For FIFO queues, ensure required parameters are set for each message
        if await self._is_fifo():
            processed_messages = []
            for message in messages:
                processed_message = message.copy()
                
                # Ensure MessageDeduplicationId is present (auto-generate if not provided)
                if 'MessageDeduplicationId' not in processed_message:
                    message_body = processed_message.get('MessageBody', '')
                    processed_message['MessageDeduplicationId'] = self._generate_deduplication_id(message_body)
                
                # Ensure MessageGroupId is present (auto-generate if not provided)
                if 'MessageGroupId' not in processed_message:
                    processed_message['MessageGroupId'] = self._generate_group_id()
                
                processed_messages.append(processed_message)
            
            messages = processed_messages
        
        return await self.sqs_client.send_message_batch(
            queue_url=self.queue_url,
            messages=messages
        )
    
    async def receive_messages(
        self,
        max_number_of_messages: int = 10,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: int = 20,
        message_attribute_names: Optional[List[str]] = None,
        attribute_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Receive messages from the specific queue"""
        await self._ensure_initialized()
        return await self.sqs_client.receive_messages(
            queue_url=self.queue_url,
            max_number_of_messages=max_number_of_messages,
            visibility_timeout=visibility_timeout,
            wait_time_seconds=wait_time_seconds,
            message_attribute_names=message_attribute_names,
            attribute_names=attribute_names
        )
    
    async def delete_message(self, receipt_handle: str) -> bool:
        """Delete message from the specific queue"""
        await self._ensure_initialized()
        return await self.sqs_client.delete_message(
            queue_url=self.queue_url,
            receipt_handle=receipt_handle
        )
    
    async def delete_message_batch(self, messages: List[Dict[str, str]]) -> Dict[str, List[Dict[str, Any]]]:
        """Delete batch messages from the specific queue"""
        await self._ensure_initialized()
        return await self.sqs_client.delete_message_batch(
            queue_url=self.queue_url,
            messages=messages
        )
    
    async def change_message_visibility(self, receipt_handle: str, visibility_timeout: int) -> bool:
        """Change message visibility timeout for the specific queue"""
        await self._ensure_initialized()
        return await self.sqs_client.change_message_visibility(
            queue_url=self.queue_url,
            receipt_handle=receipt_handle,
            visibility_timeout=visibility_timeout
        )
    
    async def purge_queue(self) -> bool:
        """Purge all messages from the specific queue"""
        await self._ensure_initialized()
        return await self.sqs_client.purge_queue(queue_url=self.queue_url)
    
    async def get_queue_attributes(self, attribute_names: Optional[List[str]] = None) -> Dict[str, str]:
        """Get attributes of the specific queue"""
        await self._ensure_initialized()
        return await self.sqs_client.get_queue_attributes(
            queue_url=self.queue_url,
            attribute_names=attribute_names
        )
    
    async def get_queue_info(self) -> Dict[str, Any]:
        """Get comprehensive queue information"""
        await self._ensure_initialized()
        attributes = await self.sqs_client.get_queue_attributes(
            queue_url=self.queue_url,
            attribute_names=[
                'QueueArn',
                'ApproximateNumberOfMessages',
                'ApproximateNumberOfMessagesNotVisible',
                'ApproximateNumberOfMessagesDelayed',
                'CreatedTimestamp',
                'LastModifiedTimestamp',
                'VisibilityTimeout',
                'MessageRetentionPeriod',
                'MaximumMessageSize',
                'DelaySeconds',
                'ReceiveMessageWaitTimeSeconds'
            ]
        )
        
        return {
            'queue_name': self.queue_name,
            'queue_url': self.queue_url,
            'is_fifo': await self._is_fifo(),
            'attributes': attributes
        }
    
    async def long_poll_receive(
        self,
        max_number_of_messages: int = 10,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: int = 20,
        message_attribute_names: Optional[List[str]] = None,
        attribute_names: Optional[List[str]] = None,
        max_poll_time: int = 300
    ) -> List[Dict[str, Any]]:
        """Long poll receive messages from the specific queue"""
        await self._ensure_initialized()
        return await self.sqs_client.long_poll_receive(
            queue_url=self.queue_url,
            max_number_of_messages=max_number_of_messages,
            visibility_timeout=visibility_timeout,
            wait_time_seconds=wait_time_seconds,
            message_attribute_names=message_attribute_names,
            attribute_names=attribute_names,
            max_poll_time=max_poll_time
        )
