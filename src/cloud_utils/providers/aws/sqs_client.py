"""
AWS SQS Synchronous Client

Provides synchronous operations for AWS SQS service.
"""

import logging
import json
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from ...exceptions import AWSConfigError, AWSConnectionError, AWSResourceNotFoundError

logger = logging.getLogger(__name__)


class SQSClient:
    """AWS SQS synchronous operations class"""
    
    def __init__(
        self,
        region_name: Optional[str] = None,
        profile_name: Optional[str] = None,
        config: Optional[Config] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize SQS client
        
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
        self._client = None
    
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
        """Return SQS client"""
        if self._client is None:
            try:
                self._client = self.session.client('sqs', config=self.config)
            except Exception as e:
                logger.error(f"Failed to create SQS client: {e}")
                raise AWSConfigError(f"Failed to create SQS client: {e}") from e
        return self._client
    
    def create_queue(
        self,
        queue_name: str,
        attributes: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create SQS queue
        
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
            
            response = self.client.create_queue(**params)
            queue_url = response['QueueUrl']
            
            logger.info(f"Successfully created SQS queue: {queue_name}")
            return queue_url
            
        except Exception as e:
            self._handle_aws_error(e, f"create queue {queue_name}")
    
    def delete_queue(self, queue_url: str) -> bool:
        """
        Delete SQS queue
        
        Args:
            queue_url: URL of the queue to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            AWSConnectionError: If queue deletion fails
        """
        try:
            self.client.delete_queue(QueueUrl=queue_url)
            logger.info(f"Successfully deleted SQS queue: {queue_url}")
            return True
            
        except Exception as e:
            self._handle_aws_error(e, f"delete queue {queue_url}")
    
    def get_queue_url(self, queue_name: str, account_id: Optional[str] = None) -> str:
        """
        Get queue URL by name
        
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
            
            response = self.client.get_queue_url(**params)
            return response['QueueUrl']
            
        except Exception as e:
            self._handle_aws_error(e, f"get queue URL for {queue_name}")
    
    def list_queues(
        self,
        queue_name_prefix: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> List[str]:
        """
        List SQS queues
        
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
            
            response = self.client.list_queues(**params)
            queue_urls = response.get('QueueUrls', [])
            
            logger.info(f"Found {len(queue_urls)} SQS queues")
            return queue_urls
            
        except Exception as e:
            self._handle_aws_error(e, "list queues")
    
    def send_message(
        self,
        queue_url: str,
        message_body: Union[str, Dict[str, Any]],
        delay_seconds: Optional[int] = None,
        message_attributes: Optional[Dict[str, Dict[str, Any]]] = None,
        message_group_id: Optional[str] = None,
        message_deduplication_id: Optional[str] = None
    ) -> str:
        """
        Send message to SQS queue
        
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
            
            response = self.client.send_message(**params)
            message_id = response['MessageId']
            
            logger.info(f"Successfully sent message {message_id} to queue {queue_url}")
            return message_id
            
        except Exception as e:
            self._handle_aws_error(e, f"send message to queue {queue_url}")
    
    def send_message_batch(
        self,
        queue_url: str,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Send multiple messages to SQS queue in batch
        
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
            
            for i in range(0, len(processed_messages), batch_size):
                batch = processed_messages[i:i + batch_size]
                
                params = {
                    'QueueUrl': queue_url,
                    'Entries': batch
                }
                
                response = self.client.send_message_batch(**params)
                
                if 'Successful' in response:
                    all_results['Successful'].extend(response['Successful'])
                if 'Failed' in response:
                    all_results['Failed'].extend(response['Failed'])
            
            logger.info(f"Batch sent {len(all_results['Successful'])} messages to queue {queue_url}")
            return all_results
            
        except Exception as e:
            self._handle_aws_error(e, f"send message batch to queue {queue_url}")
    
    def receive_messages(
        self,
        queue_url: str,
        max_number_of_messages: int = 10,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: int = 20,
        message_attribute_names: Optional[List[str]] = None,
        attribute_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Receive messages from SQS queue
        
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
            
            response = self.client.receive_message(**params)
            messages = response.get('Messages', [])
            
            logger.info(f"Received {len(messages)} messages from queue {queue_url}")
            return messages
            
        except Exception as e:
            self._handle_aws_error(e, f"receive messages from queue {queue_url}")
    
    def delete_message(self, queue_url: str, receipt_handle: str) -> bool:
        """
        Delete message from SQS queue
        
        Args:
            queue_url: URL of the queue
            receipt_handle: Receipt handle from received message
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            AWSConnectionError: If message deletion fails
        """
        try:
            self.client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            
            logger.info(f"Successfully deleted message with receipt handle {receipt_handle}")
            return True
            
        except Exception as e:
            self._handle_aws_error(e, f"delete message from queue {queue_url}")
    
    def delete_message_batch(
        self,
        queue_url: str,
        messages: List[Dict[str, str]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Delete multiple messages from SQS queue in batch
        
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
            
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                
                params = {
                    'QueueUrl': queue_url,
                    'Entries': batch
                }
                
                response = self.client.delete_message_batch(**params)
                
                if 'Successful' in response:
                    all_results['Successful'].extend(response['Successful'])
                if 'Failed' in response:
                    all_results['Failed'].extend(response['Failed'])
            
            logger.info(f"Batch deleted {len(all_results['Successful'])} messages from queue {queue_url}")
            return all_results
            
        except Exception as e:
            self._handle_aws_error(e, f"delete message batch from queue {queue_url}")
    
    def change_message_visibility(
        self,
        queue_url: str,
        receipt_handle: str,
        visibility_timeout: int
    ) -> bool:
        """
        Change message visibility timeout
        
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
            self.client.change_message_visibility(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
                VisibilityTimeout=visibility_timeout
            )
            
            logger.info(f"Changed visibility timeout to {visibility_timeout} seconds for message {receipt_handle}")
            return True
            
        except Exception as e:
            self._handle_aws_error(e, f"change message visibility for queue {queue_url}")
    
    def purge_queue(self, queue_url: str) -> bool:
        """
        Purge all messages from SQS queue
        
        Args:
            queue_url: URL of the queue to purge
            
        Returns:
            bool: True if operation successful
            
        Raises:
            AWSConnectionError: If operation fails
        """
        try:
            self.client.purge_queue(QueueUrl=queue_url)
            logger.info(f"Successfully purged queue {queue_url}")
            return True
            
        except Exception as e:
            self._handle_aws_error(e, f"purge queue {queue_url}")
    
    def get_queue_attributes(
        self,
        queue_url: str,
        attribute_names: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Get queue attributes
        
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
            
            response = self.client.get_queue_attributes(**params)
            attributes = response.get('Attributes', {})
            
            logger.info(f"Retrieved {len(attributes)} attributes for queue {queue_url}")
            return attributes
            
        except Exception as e:
            self._handle_aws_error(e, f"get attributes for queue {queue_url}")
    
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
            elif error_code == 'QueueDoesNotExist':
                raise AWSResourceNotFoundError(f"Queue not found for {operation}: {error_message}")
            else:
                raise AWSConnectionError(f"AWS {operation} failed: {error_code} - {error_message}")
        
        else:
            logger.error(f"Unexpected error during {operation}: {error}")
            raise AWSConnectionError(f"Unexpected error during {operation}: {error}")


class SQSHandler:
    """SQS handler for specific queue operations"""
    
    def __init__(
        self,
        queue_name: Optional[str] = None,
        queue_url: Optional[str] = None,
        region_name: Optional[str] = None,
        profile_name: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize SQS handler for specific queue
        
        Args:
            queue_name: Name of the queue (will be used to get URL if queue_url not provided)
            queue_url: Direct URL of the queue
            region_name: AWS region name
            profile_name: AWS profile name
            **kwargs: Additional SQS client parameters
        """
        if not queue_name and not queue_url:
            raise ValueError("Either queue_name or queue_url must be provided")
        
        self.queue_name = queue_name
        self.queue_url = queue_url
        self.sqs_client = SQSClient(region_name=region_name, profile_name=profile_name, **kwargs)
        self._resolved_queue_url = None
        self._is_fifo = None
    
    @property
    def queue_url_resolved(self) -> str:
        """Get resolved queue URL"""
        if self._resolved_queue_url is None:
            if self.queue_url:
                self._resolved_queue_url = self.queue_url
            else:
                self._resolved_queue_url = self.sqs_client.get_queue_url(self.queue_name)
        return self._resolved_queue_url
    
    @property
    def is_fifo(self) -> bool:
        """Check if the queue is a FIFO queue"""
        if self._is_fifo is None:
            # FIFO queues end with .fifo
            self._is_fifo = self.queue_url_resolved.endswith('.fifo')
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
    
    def send_message(
        self,
        message_body: Union[str, Dict[str, Any]],
        delay_seconds: Optional[int] = None,
        message_attributes: Optional[Dict[str, Dict[str, Any]]] = None,
        message_group_id: Optional[str] = None,
        message_deduplication_id: Optional[str] = None
    ) -> str:
        """Send message to the specific queue"""
        # For FIFO queues, ensure required parameters are set
        if self.is_fifo:
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
        
        return self.sqs_client.send_message(
            queue_url=self.queue_url_resolved,
            message_body=message_body,
            delay_seconds=delay_seconds,
            message_attributes=message_attributes,
            message_group_id=message_group_id,
            message_deduplication_id=message_deduplication_id
        )
    
    def send_message_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Send batch messages to the specific queue"""
        # For FIFO queues, ensure required parameters are set for each message
        if self.is_fifo:
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
        
        return self.sqs_client.send_message_batch(
            queue_url=self.queue_url_resolved,
            messages=messages
        )
    
    def send_messages(
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
            if delay_seconds is not None and not self.is_fifo:
                message['DelaySeconds'] = delay_seconds
            if message_attributes:
                message['MessageAttributes'] = message_attributes
            if message_group_id and self.is_fifo:
                message['MessageGroupId'] = message_group_id
            if message_deduplication_id and self.is_fifo:
                message['MessageDeduplicationId'] = message_deduplication_id
            
            messages.append(message)
        
        # For FIFO queues, ensure required parameters are set for each message
        if self.is_fifo:
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
        
        return self.sqs_client.send_message_batch(
            queue_url=self.queue_url_resolved,
            messages=messages
        )
    
    def receive_messages(
        self,
        max_number_of_messages: int = 10,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: int = 20,
        message_attribute_names: Optional[List[str]] = None,
        attribute_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Receive messages from the specific queue"""
        return self.sqs_client.receive_messages(
            queue_url=self.queue_url_resolved,
            max_number_of_messages=max_number_of_messages,
            visibility_timeout=visibility_timeout,
            wait_time_seconds=wait_time_seconds,
            message_attribute_names=message_attribute_names,
            attribute_names=attribute_names
        )
    
    def delete_message(self, receipt_handle: str) -> bool:
        """Delete message from the specific queue"""
        return self.sqs_client.delete_message(
            queue_url=self.queue_url_resolved,
            receipt_handle=receipt_handle
        )
    
    def delete_message_batch(self, messages: List[Dict[str, str]]) -> Dict[str, List[Dict[str, Any]]]:
        """Delete batch messages from the specific queue"""
        return self.sqs_client.delete_message_batch(
            queue_url=self.queue_url_resolved,
            messages=messages
        )
    
    def change_message_visibility(self, receipt_handle: str, visibility_timeout: int) -> bool:
        """Change message visibility timeout for the specific queue"""
        return self.sqs_client.change_message_visibility(
            queue_url=self.queue_url_resolved,
            receipt_handle=receipt_handle,
            visibility_timeout=visibility_timeout
        )
    
    def purge_queue(self) -> bool:
        """Purge all messages from the specific queue"""
        return self.sqs_client.purge_queue(queue_url=self.queue_url_resolved)
    
    def get_queue_attributes(self, attribute_names: Optional[List[str]] = None) -> Dict[str, str]:
        """Get attributes of the specific queue"""
        return self.sqs_client.get_queue_attributes(
            queue_url=self.queue_url_resolved,
            attribute_names=attribute_names
        )
    
    def get_queue_info(self) -> Dict[str, Any]:
        """Get comprehensive queue information"""
        attributes = self.get_queue_attributes([
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
        ])
        
        return {
            'queue_name': self.queue_name,
            'queue_url': self.queue_url_resolved,
            'is_fifo': self.is_fifo,
            'attributes': attributes
        }
