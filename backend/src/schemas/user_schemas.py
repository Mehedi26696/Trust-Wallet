from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, AliasChoices
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    """Schema for user registration."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "phone_number": "01712345678",
                "email": "john.doe@example.com",
                "password": "SecurePass123",
                "nid": "2000357398",
            }
        }
    )
    full_name: str = Field(..., min_length=2, max_length=255, description="User's full name")
    phone_number: str = Field(
        ...,
        description="User's phone number (11 digits)",
        validation_alias=AliasChoices("phone_number", "phone"),
    )
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="User's password")
    nid: str = Field(..., min_length=10, max_length=17, description="National ID (10, 13, or 17 digits)")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number (must be exactly 11 digits)."""
        import re
        # Remove spaces, dashes, and any non-digit characters except +
        phone = re.sub(r'[\s\-()]', '', v)
        
        # Remove leading + and any country code (1-3 digits after +)
        if phone.startswith('+'):
            phone = re.sub(r'^\+\d{1,3}', '', phone)
        
        # Remove leading 88 or 880 (Bangladesh country code without +)
        if phone.startswith('88'):
            phone = phone[2:] if phone.startswith('880') else phone[2:]
        
        # Extract only digits
        phone = re.sub(r'\D', '', phone)
        
        # Check if it's exactly 11 digits
        if len(phone) != 11:
            raise ValueError(f'Phone number must be exactly 11 digits (got {len(phone)} digits)')
        
        return phone
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase for uniqueness checks (Pydantic v2)."""
        return str(v).strip().lower()
    
    # Config moved to model_config above


class UserLogin(BaseModel):
    """Schema for user login."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phone_number": "01712345678",
                "password": "SecurePass123",
            }
        }
    )
    phone_number: str = Field(
        ..., description="User's phone number (11 digits)", validation_alias=AliasChoices("phone_number", "phone")
    )
    password: str = Field(..., description="User's password")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number (must be exactly 11 digits)."""
        import re
        # Remove spaces, dashes, and any non-digit characters except +
        phone = re.sub(r'[\s\-()]', '', v)
        
        # Remove leading + and any country code (1-3 digits after +)
        if phone.startswith('+'):
            phone = re.sub(r'^\+\d{1,3}', '', phone)
        
        # Remove leading 88 or 880 (Bangladesh country code without +)
        if phone.startswith('88'):
            phone = phone[2:] if phone.startswith('880') else phone[2:]
        
        # Extract only digits
        phone = re.sub(r'\D', '', phone)
        
        # Check if it's exactly 11 digits
        if len(phone) != 11:
            raise ValueError(f'Phone number must be exactly 11 digits (got {len(phone)} digits)')
        
        return phone
    
    # Config moved to model_config above


class UserResponse(BaseModel):
    """Schema for user response (public information)."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    full_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    wallet_balance: float
    created_at: datetime
    is_active: bool


class UserProfile(BaseModel):
    """Schema for user profile information."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    full_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    nid: str
    wallet_balance: float
    created_at: datetime
    is_active: bool
    # Config moved to model_config above