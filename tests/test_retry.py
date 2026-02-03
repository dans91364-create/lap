"""Tests for retry utilities."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.utils.retry import (
    retry_with_exponential_backoff,
    retry_on_http_error
)
from src.exceptions import ExternalAPIError


class TestRetryWithExponentialBackoff:
    """Tests for retry with exponential backoff."""
    
    @pytest.mark.asyncio
    async def test_successful_call_no_retry(self):
        """Test that successful calls don't retry."""
        mock_func = AsyncMock(return_value="success")
        
        @retry_with_exponential_backoff(max_attempts=3)
        async def test_func():
            return await mock_func()
        
        result = await test_func()
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_then_success(self):
        """Test retry on failure then success."""
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        @retry_with_exponential_backoff(
            max_attempts=5,
            initial_delay=0.01,
            exponential_base=2.0
        )
        async def test_func():
            return await failing_func()
        
        result = await test_func()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_max_attempts_exceeded(self):
        """Test that max attempts raises exception."""
        mock_func = AsyncMock(side_effect=Exception("Permanent failure"))
        
        @retry_with_exponential_backoff(max_attempts=3, initial_delay=0.01)
        async def test_func():
            return await mock_func()
        
        with pytest.raises(Exception) as exc_info:
            await test_func()
        
        assert "Permanent failure" in str(exc_info.value)
        assert mock_func.call_count == 3
    
    @pytest.mark.asyncio
    async def test_specific_exception_types(self):
        """Test retry only on specific exception types."""
        call_count = 0
        
        async def specific_error_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Should retry")
            elif call_count == 2:
                raise TypeError("Should not retry")
            return "success"
        
        @retry_with_exponential_backoff(
            max_attempts=5,
            initial_delay=0.01,
            exceptions=(ValueError,)
        )
        async def test_func():
            return await specific_error_func()
        
        with pytest.raises(TypeError):
            await test_func()
        
        assert call_count == 2
    
    def test_sync_function_retry(self):
        """Test retry with synchronous function."""
        call_count = 0
        
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        @retry_with_exponential_backoff(max_attempts=5, initial_delay=0.01)
        def test_func():
            return failing_func()
        
        result = test_func()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_on_retry_callback(self):
        """Test on_retry callback is called."""
        retry_attempts = []
        
        def on_retry_callback(attempt, error, delay):
            retry_attempts.append((attempt, str(error), delay))
        
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception(f"Failure {call_count}")
            return "success"
        
        @retry_with_exponential_backoff(
            max_attempts=5,
            initial_delay=0.5,
            on_retry=on_retry_callback
        )
        async def test_func():
            return await failing_func()
        
        result = await test_func()
        
        assert result == "success"
        assert len(retry_attempts) == 2
        assert retry_attempts[0][0] == 1  # First retry
        assert retry_attempts[1][0] == 2  # Second retry


class TestRetryOnHTTPError:
    """Tests for retry on HTTP error."""
    
    @pytest.mark.asyncio
    async def test_retry_on_specific_status_codes(self):
        """Test retry on specific HTTP status codes."""
        call_count = 0
        
        async def http_error_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                error = ExternalAPIError("Server error", status_code=503)
                raise error
            return "success"
        
        @retry_on_http_error(
            max_attempts=5,
            initial_delay=0.01,
            status_codes=(503,)
        )
        async def test_func():
            return await http_error_func()
        
        result = await test_func()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_no_retry_on_other_status_codes(self):
        """Test no retry on status codes not in list."""
        call_count = 0
        
        async def http_error_func():
            nonlocal call_count
            call_count += 1
            error = ExternalAPIError("Bad request", status_code=400)
            raise error
        
        @retry_on_http_error(
            max_attempts=5,
            initial_delay=0.01,
            status_codes=(500, 502, 503)
        )
        async def test_func():
            return await http_error_func()
        
        with pytest.raises(ExternalAPIError) as exc_info:
            await test_func()
        
        assert exc_info.value.status_code == 400
        assert call_count == 1  # Should not retry
    
    @pytest.mark.asyncio
    async def test_no_retry_on_success(self):
        """Test no retry when request succeeds."""
        mock_func = AsyncMock(return_value={"data": "success"})
        
        @retry_on_http_error(max_attempts=3)
        async def test_func():
            return await mock_func()
        
        result = await test_func()
        
        assert result == {"data": "success"}
        assert mock_func.call_count == 1
