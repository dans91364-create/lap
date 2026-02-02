"""Base collector class for data collection."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
import httpx
from datetime import datetime

from config.settings import settings
from src.utils.helpers import retry_on_failure

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Base class for all data collectors."""
    
    def __init__(self):
        """Initialize collector."""
        self.base_url = settings.PNCP_BASE_URL
        self.timeout = settings.PNCP_TIMEOUT
        self.max_retries = settings.PNCP_MAX_RETRIES
        self.retry_delay = settings.PNCP_RETRY_DELAY
        
    @retry_on_failure(max_attempts=3, delay=5)
    async def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API.
        
        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response JSON data
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.info(f"Making request to: {url}")
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
    
    def _make_sync_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make synchronous HTTP request to API.
        
        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response JSON data
        """
        with httpx.Client(timeout=self.timeout) as client:
            try:
                logger.info(f"Making request to: {url}")
                response = client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
    
    @abstractmethod
    async def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect data from source.
        
        Returns:
            List of collected data items
        """
        pass
    
    def log_collection_stats(self, total: int, success: int, errors: int):
        """
        Log collection statistics.
        
        Args:
            total: Total items processed
            success: Successful items
            errors: Failed items
        """
        logger.info(f"""
        Collection Statistics:
        - Total: {total}
        - Success: {success}
        - Errors: {errors}
        - Success Rate: {(success/total*100) if total > 0 else 0:.2f}%
        """)
