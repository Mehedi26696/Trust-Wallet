"""
User service for handling user-related business logic.
"""

from sqlmodel import Session, select
from typing import Optional
from fastapi import HTTPException, status

from ..models.user import User
from ..schemas.user_schemas import UserCreate
from ..utils.password_utils import hash_password
from datetime import datetime, timezone
from sqlmodel import Session, select
from typing import Optional
from uuid import UUID
import bcrypt

from ..models.user import User
from ..utils.nid_validator import is_valid_nid


class UserService:
    """Service class for user operations."""
    
    @staticmethod
    def create_user(session: Session, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            session: Database session
            user_data: User creation data
            
        Returns:
            User: Created user object
            
        Raises:
            HTTPException: If validation fails or user already exists
        """
        # Validate NID format
        if not is_valid_nid(user_data.nid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid NID format"
            )
        
        # Check if phone number already exists
        existing_phone = UserService.get_user_by_phone(session, user_data.phone_number)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

        # Check if email already exists
        existing_email = UserService.get_user_by_email(session, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if NID already exists
        existing_nid = UserService.get_user_by_nid(session, user_data.nid)
        if existing_nid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NID already registered"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user
        db_user = User(
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            email=user_data.email,
            password_hash=hashed_password,
            nid=user_data.nid,
            wallet_balance=0.0
        )
        
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def get_user_by_email(session: Session, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            session: Database session
            email: User email
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_nid(session: Session, nid: str) -> Optional[User]:
        """
        Get user by NID.
        
        Args:
            session: Database session
            nid: National ID
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        statement = select(User).where(User.nid == nid)
        return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_phone(session: Session, phone_number: str) -> Optional[User]:
        """
        Get user by phone number.
        
        Args:
            session: Database session
            phone_number: User phone number
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        statement = select(User).where(User.phone_number == phone_number)
        return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_id(session: Session, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            session: Database session
            user_id: User ID
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()
    
    @staticmethod
    def update_user_balance(session: Session, user_id: UUID, new_balance: float) -> bool:
        """
        Update user wallet balance.
        
        Args:
            session: Database session
            user_id: User ID
            new_balance: New balance amount
            
        Returns:
            bool: True if update successful, False otherwise
        """
        user = UserService.get_user_by_id(session, user_id)
        if not user:
            return False
        
        user.wallet_balance = new_balance
        session.add(user)
        session.commit()
        
        return True
    
    @staticmethod
    def deactivate_user(session: Session, user_id: UUID) -> bool:
        """
        Deactivate a user account.
        
        Args:
            session: Database session
            user_id: User ID
            
        Returns:
            bool: True if deactivation successful, False otherwise
        """
        user = UserService.get_user_by_id(session, user_id)
        if not user:
            return False
        
        user.is_active = False
        session.add(user)
        session.commit()
        
        return True