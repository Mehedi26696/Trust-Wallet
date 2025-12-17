from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # Token expiry in seconds
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class TokenData(BaseModel):
    """Schema for token data."""
    phone_number: Optional[str] = None
    user_id: Optional[UUID] = None