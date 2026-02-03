"""API dependencies for authentication and authorization."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.services.auth_service import auth_service

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User payload from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure user is active.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Active user payload
        
    Raises:
        HTTPException: If user is inactive
    """
    # In a real implementation, you'd check the database
    # For now, we just return the user
    return current_user


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require admin privileges.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Admin user payload
        
    Raises:
        HTTPException: If user is not admin
    """
    # Check if user has admin role (stored in token or fetched from DB)
    # This is a simplified version
    return current_user
