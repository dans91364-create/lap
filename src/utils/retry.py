"""Retry decorator with exponential backoff for handling transient failures."""

import time
import logging
import asyncio
import inspect
from functools import wraps
from typing import Callable, Type, Tuple, Optional
from src.exceptions import ExternalAPIError

logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator that retries a function with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function called on each retry
        
    Returns:
        Decorated function with retry logic
        
    Example:
        @retry_with_exponential_backoff(max_attempts=5, initial_delay=2.0)
        async def fetch_data():
            # This will retry up to 5 times with exponential backoff
            response = await client.get(url)
            return response.json()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            """Async wrapper for retry logic."""
            attempt = 0
            delay = initial_delay
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    current_delay = min(delay, max_delay)
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    
                    # Call on_retry callback if provided
                    if on_retry:
                        on_retry(attempt, e, current_delay)
                    
                    # Wait before retrying
                    await asyncio.sleep(current_delay)
                    
                    # Increase delay for next attempt
                    delay *= exponential_base
            
            # This should never be reached, but just in case
            raise Exception(f"Max retries ({max_attempts}) exceeded")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Sync wrapper for retry logic."""
            attempt = 0
            delay = initial_delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    current_delay = min(delay, max_delay)
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    
                    # Call on_retry callback if provided
                    if on_retry:
                        on_retry(attempt, e, current_delay)
                    
                    # Wait before retrying
                    time.sleep(current_delay)
                    
                    # Increase delay for next attempt
                    delay *= exponential_base
            
            # This should never be reached, but just in case
            raise Exception(f"Max retries ({max_attempts}) exceeded")
        
        # Detect if function is async or sync
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_on_http_error(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    status_codes: Tuple[int, ...] = (500, 502, 503, 504, 429)
):
    """
    Decorator that retries HTTP requests on specific status codes.
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        status_codes: HTTP status codes to retry on
        
    Returns:
        Decorated function with retry logic
        
    Example:
        @retry_on_http_error(max_attempts=5, status_codes=(429, 500, 502, 503))
        async def fetch_from_api():
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    """
    def should_retry(e: Exception) -> bool:
        """Check if exception should trigger a retry."""
        # Check for httpx HTTPStatusError
        if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
            return e.response.status_code in status_codes
        # Check for ExternalAPIError
        if isinstance(e, ExternalAPIError) and e.status_code:
            return e.status_code in status_codes
        return False
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            """Async wrapper for HTTP retry logic."""
            attempt = 0
            delay = initial_delay
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if not should_retry(e):
                        raise
                    
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        logger.error(
                            f"HTTP request {func.__name__} failed after {max_attempts} attempts"
                        )
                        raise
                    
                    current_delay = delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"HTTP error on attempt {attempt}/{max_attempts}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    
                    await asyncio.sleep(current_delay)
            
            raise Exception(f"Max retries ({max_attempts}) exceeded")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Sync wrapper for HTTP retry logic."""
            attempt = 0
            delay = initial_delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if not should_retry(e):
                        raise
                    
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        logger.error(
                            f"HTTP request {func.__name__} failed after {max_attempts} attempts"
                        )
                        raise
                    
                    current_delay = delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"HTTP error on attempt {attempt}/{max_attempts}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    
                    time.sleep(current_delay)
            
            raise Exception(f"Max retries ({max_attempts}) exceeded")
        
        # Detect if function is async or sync
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
