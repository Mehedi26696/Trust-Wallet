"""
Authentication service for JWT token management and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from ..models.user import User
from ..schemas.auth_schemas import TokenData
from ..utils.database import get_session
from ..utils.password_utils import verify_password
from ..config import settings


# JWT Configuration - Use settings from config
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Security scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data (dict): Data to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token.
    
    Args:
        token (str): JWT token to verify
        
    Returns:
        TokenData: Decoded token data
        
    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        user_id: str = payload.get("user_id")  # UUID comes as string from JWT
        
        if phone_number is None or user_id is None:
            raise credentials_exception
        
        # Convert string UUID back to UUID object
        token_data = TokenData(phone_number=phone_number, user_id=UUID(user_id))
        return token_data
    
    except JWTError:
        raise credentials_exception


def authenticate_user(session: Session, phone_number: str, password: str) -> Optional[User]:
    """
    Authenticate a user by phone number and password.
    
    Args:
        session: Database session
        phone_number (str): User phone number
        password (str): User password
        
    Returns:
        Optional[User]: User object if authentication successful, None otherwise
    """
    statement = select(User).where(User.phone_number == phone_number)
    user = session.exec(statement).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Get the current authenticated user.
    
    Args:
        credentials: HTTP authorization credentials
        session: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If user is not authenticated or not found
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    statement = select(User).where(User.phone_number == token_data.phone_number)
    user = session.exec(statement).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user