"""
Cloud Utils Backoff Utilities

Provides various backoff strategies for retry logic.
"""

import random
import time
from typing import Callable, Optional, TypeVar, Union

from ..exceptions import RetryableError

T = TypeVar('T')


def exponential_backoff(
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    factor: float = 2.0,
    jitter: bool = True
) -> Callable[[int], float]:
    """
    Create exponential backoff function
    
    Args:
        base_delay: Base delay time (seconds)
        max_delay: Maximum delay time (seconds)
        factor: Exponential increase factor
        jitter: Whether to add jitter (randomness)
        
    Returns:
        Backoff function
    """
    def backoff(attempt: int) -> float:
        delay = min(base_delay * (factor ** attempt), max_delay)
        if jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        return delay
    
    return backoff


def linear_backoff(
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    increment: float = 1.0,
    jitter: bool = True
) -> Callable[[int], float]:
    """
    Create linear backoff function
    
    Args:
        base_delay: Base delay time (seconds)
        max_delay: Maximum delay time (seconds)
        increment: Increment amount
        jitter: Whether to add jitter (randomness)
        
    Returns:
        Backoff function
    """
    def backoff(attempt: int) -> float:
        delay = min(base_delay + (increment * attempt), max_delay)
        if jitter:
            delay = delay * (0.8 + random.random() * 0.4)
        return delay
    
    return backoff


def constant_backoff(
    delay: float = 1.0,
    jitter: bool = True
) -> Callable[[int], float]:
    """
    Create constant backoff function
    
    Args:
        delay: Delay time (seconds)
        jitter: Whether to add jitter (randomness)
        
    Returns:
        Backoff function
    """
    def backoff(attempt: int) -> float:
        if jitter:
            return delay * (0.8 + random.random() * 0.4)
        return delay
    
    return backoff


def retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 3,
    backoff_strategy: Optional[Callable[[int], float]] = None,
    exceptions: Union[type, tuple] = Exception,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None
) -> T:
    """
    Retry function with backoff strategy
    
    Args:
        func: Function to execute
        max_attempts: Maximum number of attempts
        backoff_strategy: Backoff strategy function
        exceptions: Exception types to retry on
        on_retry: Callback function called on retry
        
    Returns:
        Function execution result
        
    Raises:
        Last exception that occurred
    """
    if backoff_strategy is None:
        backoff_strategy = exponential_backoff()
    
    last_exception: Optional[Exception] = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            
            if attempt == max_attempts - 1:
                # Last attempt, raise exception
                raise last_exception
            
            # Wait before retry
            delay = backoff_strategy(attempt)
            
            if on_retry:
                on_retry(attempt, e, delay)
            
            time.sleep(delay)
    
    # This should not be reached
    raise last_exception


def async_retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 3,
    backoff_strategy: Optional[Callable[[int], float]] = None,
    exceptions: Union[type, tuple] = Exception,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None
) -> T:
    """
    Retry async function with backoff strategy
    
    Args:
        func: Function to execute (coroutine)
        max_attempts: Maximum number of attempts
        backoff_strategy: Backoff strategy function
        exceptions: Exception types to retry on
        on_retry: Callback function called on retry
        
    Returns:
        Function execution result
        
    Raises:
        Last exception that occurred
    """
    if backoff_strategy is None:
        backoff_strategy = exponential_backoff()
    
    last_exception: Optional[Exception] = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            
            if attempt == max_attempts - 1:
                # Last attempt, raise exception
                raise last_exception
            
            # Wait before retry
            delay = backoff_strategy(attempt)
            
            if on_retry:
                on_retry(attempt, e, delay)
            
            # Async wait (using time.sleep instead of asyncio.sleep)
            time.sleep(delay)
    
    # This should not be reached
    raise last_exception


class RetryConfig:
    """Retry configuration class"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        factor: float = 2.0,
        jitter: bool = True,
        exceptions: Union[type, tuple] = Exception
    ) -> None:
        """
        Initialize retry configuration
        
        Args:
            max_attempts: Maximum number of attempts
            base_delay: Base delay time (seconds)
            max_delay: Maximum delay time (seconds)
            factor: Exponential increase factor
            jitter: Whether to add jitter (randomness)
            exceptions: Exception types to retry on
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.factor = factor
        self.jitter = jitter
        self.exceptions = exceptions
    
    def create_backoff_strategy(self) -> Callable[[int], float]:
        """Create backoff strategy"""
        return exponential_backoff(
            base_delay=self.base_delay,
            max_delay=self.max_delay,
            factor=self.factor,
            jitter=self.jitter
        )
    
    def retry(self, func: Callable[[], T]) -> T:
        """Execute retry"""
        return retry_with_backoff(
            func=func,
            max_attempts=self.max_attempts,
            backoff_strategy=self.create_backoff_strategy(),
            exceptions=self.exceptions
        )
