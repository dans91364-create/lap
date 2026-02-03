"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from src.services.auth_service import auth_service
from src.database.connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class UserResponse(BaseModel):
    """User response model."""
    id: int
    nome: str
    email: str
    perfil: str
    ativo: bool


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    user: UserResponse


class UserCreate(BaseModel):
    """User creation model."""
    nome: str
    email: EmailStr
    password: str
    perfil: str = "usuario"


def get_user_by_email(email: str):
    """Get user by email from database."""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(
            "SELECT id, nome, email, senha_hash, perfil, ativo FROM usuarios WHERE email = %s",
            (email,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'senha_hash': row[3],
                'perfil': row[4],
                'ativo': row[5]
            }
        return None
    finally:
        cursor.close()


def get_user_by_id(user_id: int):
    """Get user by ID from database."""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(
            "SELECT id, nome, email, perfil, ativo FROM usuarios WHERE id = %s",
            (user_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'perfil': row[3],
                'ativo': row[4]
            }
        return None
    finally:
        cursor.close()


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return JWT token.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        
    Returns:
        Access token and user information
    """
    # Authenticate user
    user = auth_service.authenticate_user(
        form_data.username,
        form_data.password,
        get_user_by_email
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get('ativo'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": str(user['id']), "email": user['email']}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user['id'],
            "nome": user['nome'],
            "email": user['email'],
            "perfil": user['perfil'],
            "ativo": user['ativo']
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        Current user information
    """
    # Verify token
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_id = int(payload.get("sub"))
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    return user


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        
    Returns:
        Created user information
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if user already exists
        existing_user = get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Hash password
        senha_hash = auth_service.get_password_hash(user_data.password)
        
        # Insert user
        cursor.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash, perfil)
            VALUES (%s, %s, %s, %s)
            RETURNING id, nome, email, perfil, ativo
            """,
            (user_data.nome, user_data.email, senha_hash, user_data.perfil)
        )
        
        row = cursor.fetchone()
        db.commit()
        
        return {
            'id': row[0],
            'nome': row[1],
            'email': row[2],
            'perfil': row[3],
            'ativo': row[4]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao cadastrar usuário"
        )
    finally:
        cursor.close()
