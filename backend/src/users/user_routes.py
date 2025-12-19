"""
User API routes for registration, login, and profile management.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from uuid import UUID
import json

from ..auth.auth_service import (
    authenticate_user, 
    create_access_token, 
    get_current_user
)
from ..models.user import User
from ..schemas.user_schemas import UserCreate, UserLogin, UserResponse, UserProfile, UnblockAccountResponse
from ..schemas.auth_schemas import Token
from ..services.user_service import UserService
from ..utils.database import get_session
from ..utils.fraud_detector import clear_user_fraud_block
from ..config import settings


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new user.
    
    - **full_name**: User's full name
    - **phone_number**: User's phone number (Bangladesh format: +8801XXXXXXXXX)
    - **password**: User's password (min 8 characters with uppercase, lowercase, digit)
    - **nid**: National ID (10, 13, or 17 digits with year validation)
    
    Returns user information with default wallet balance of 0.0 BDT.
    """
    try:
        user = UserService.create_user(session, user_data)
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and return JWT token.
    
    - **phone_number**: User's phone number (Bangladesh format)
    - **password**: User's password
    
    Returns JWT access token for authenticated requests.
    """
    print(f"Login attempt - Phone: {user_credentials.phone_number}")
    
    user = authenticate_user(
        session, 
        user_credentials.phone_number, 
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone_number, "user_id": str(user.id)},  # Use phone_number instead of email
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )





@router.get("/me", response_model=UserProfile)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's basic info (for greeting, etc).
    Same as /profile but with clearer naming.
    """
    return UserProfile.model_validate(current_user)


@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get user information by ID (public information only).
    
    Requires authentication. Returns basic user information without sensitive data.
    """
    user = UserService.get_user_by_id(session, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.post("/dev/unblock-account/{phone_number}", response_model=UnblockAccountResponse)
async def developer_unblock_account(
    phone_number: str,
    session: Session = Depends(get_session)
):
    """
    [DEVELOPER ENDPOINT] Unblock a user account that has been temporarily blocked due to fraud.
    
    This endpoint clears all unresolved fraud alerts for the specified user, allowing them
    to make transactions again. Use this for testing or to manually override fraud blocks.
    
    - **phone_number**: Phone number of the user to unblock (Bangladesh format: 01XXXXXXXXX)
    
    Returns the number of fraud alerts cleared.
    
    ⚠️ WARNING: This is a developer-only endpoint and should be removed or protected in production.
    """
    try:
        # Verify user exists by phone number
        user = UserService.get_user_by_phone(session, phone_number)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with phone number {phone_number} not found"
            )
        
        # Clear all unresolved fraud alerts for the user
        alerts_cleared = 0
        from ..models.fraud_alert import FraudAlert
        from sqlmodel import select
        
        statement = select(FraudAlert).where(
            FraudAlert.user_id == user.id,
            FraudAlert.resolved == False
        )
        
        unresolved_alerts = session.exec(statement).all()
        alerts_cleared = len(unresolved_alerts)
        
        # Mark all as resolved
        for alert in unresolved_alerts:
            alert.resolved = True
            session.add(alert)
        
        session.commit()
        
        return UnblockAccountResponse(
            user_id=user.id,
            success=True,
            message=f"Successfully unblocked account for {phone_number}. Cleared {alerts_cleared} fraud alert(s).",
            alerts_cleared=alerts_cleared
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unblock account: {str(e)}"
        )