from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    """User model for wallet application.
    Stores user information including NID for Bangladesh verification.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    full_name: str = Field(max_length=255)
    phone_number: str = Field(unique=True, max_length=20, index=True, description="User's phone number (11 digits)")
    password_hash: str = Field(max_length=255)
    nid: str = Field(max_length=17, description="National ID (10, 13, or 17 digits)")
    email: str = Field(unique=True, max_length=255, index=True)
    wallet_balance: float = Field(default=0.0, ge=0.0)
    # Face enrollment
    face_image_path: Optional[str] = Field(default=None, max_length=512, sa_column_kwargs={"nullable": True})
    face_hash: Optional[str] = Field(default=None, max_length=128, sa_column_kwargs={"nullable": True})
    last_face_verified_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)
    
    class Config:
        """Pydantic configuration for the User model."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "phone_number": "01712345678",
                "nid": "1234567890123",
                "wallet_balance": 1000.0
            }
        }