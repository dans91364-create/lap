"""Helper utility functions."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import time
from functools import wraps

from src.utils.constants import PNCP_DATE_FORMAT, DISPLAY_DATE_FORMAT

logger = logging.getLogger(__name__)


def format_date_for_pncp(date: datetime) -> str:
    """
    Format date for PNCP API (YYYYMMDD).
    
    Args:
        date: Date to format
        
    Returns:
        Formatted date string
    """
    return date.strftime(PNCP_DATE_FORMAT)


def parse_pncp_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse datetime string from PNCP API.
    
    Args:
        date_str: Date string from API
        
    Returns:
        Parsed datetime or None
    """
    if not date_str:
        return None
    
    try:
        # Try ISO format first
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        try:
            # Try other common formats
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.warning(f"Could not parse date: {date_str}")
            return None


def format_cnpj(cnpj: str) -> str:
    """
    Format CNPJ to standard format (XX.XXX.XXX/XXXX-XX).
    
    Args:
        cnpj: CNPJ string (with or without formatting)
        
    Returns:
        Formatted CNPJ
    """
    # Remove any non-digit characters
    cnpj = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj) != 14:
        return cnpj
    
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def format_cpf(cpf: str) -> str:
    """
    Format CPF to standard format (XXX.XXX.XXX-XX).
    
    Args:
        cpf: CPF string (with or without formatting)
        
    Returns:
        Formatted CPF
    """
    # Remove any non-digit characters
    cpf = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf) != 11:
        return cpf
    
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def clean_cnpj_cpf(doc: str) -> str:
    """
    Remove formatting from CNPJ/CPF.
    
    Args:
        doc: CNPJ or CPF string
        
    Returns:
        Cleaned document number
    """
    return ''.join(filter(str.isdigit, doc))


def get_date_range(years: int = 2) -> tuple[datetime, datetime]:
    """
    Get date range for data collection.
    
    Args:
        years: Number of years to go back
        
    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)
    return start_date, end_date


def retry_on_failure(max_attempts: int = 3, delay: int = 5):
    """
    Decorator to retry function on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    logger.warning(f"Attempt {attempts} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


def safe_get(data: Dict[str, Any], *keys, default=None):
    """
    Safely get nested dictionary values.
    
    Args:
        data: Dictionary to search
        *keys: Nested keys to access
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data


def truncate_string(text: Optional[str], max_length: int = 255) -> Optional[str]:
    """
    Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if not text:
        return text
    
    return text[:max_length] if len(text) > max_length else text


def calculate_percentage(value: float, total: float) -> float:
    """
    Calculate percentage safely.
    
    Args:
        value: Value
        total: Total
        
    Returns:
        Percentage
    """
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)
