from pydantic import BaseModel, Field, field_validator
from uuid import UUID
import re
from typing import Optional


class WalletResponse(BaseModel):
    """Schema for wallet balance response."""
    user_id: UUID
    balance: float = Field(..., ge=0, description="Current wallet balance in BDT")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "balance": 5000.0
            }
        }


class AddFundsRequest(BaseModel):
    """Schema for adding funds to user wallet."""
    amount: float = Field(..., gt=0, le=10000000, description="Amount to add in BDT (max 10M)")
    description: Optional[str] = Field(None, max_length=255, description="Optional note about the deposit")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate amount is positive and not too large."""
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 10000000:
            raise ValueError('Amount cannot exceed 10,000,000 BDT')
        return round(v, 2)
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 5000.0,
                "description": "Deposit from bank account"
            }
        }


class WalletSendRequest(BaseModel):
    """Schema for wallet send money request."""
    receiver_phone: str = Field(..., description="Phone number of the receiver (Bangladesh format)")
    amount: float = Field(..., gt=0, le=1000000, description="Amount to send in BDT (max 1M)")
    
    @field_validator('receiver_phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number (must be exactly 11 digits)."""
        # Remove spaces and dashes
        phone = re.sub(r'[\s\-]', '', v)
        # Remove any leading + or country code
        phone = re.sub(r'^\+?\d{1,3}', '', phone) if phone.startswith('+') else phone
        # Check if it's exactly 11 digits
        if not re.match(r'^\d{11}$', phone):
            raise ValueError('Phone number must be exactly 11 digits')
        return phone
    
    class Config:
        json_schema_extra = {
            "example": {
                "receiver_phone": "+8801712345678",
                "amount": 1000.0
            }
        }


class RiskCheckRequest(BaseModel):
    """Schema for risk check request (preview without executing)."""
    receiver_phone: str = Field(..., description="Phone number of the receiver")
    amount: float = Field(..., gt=0, le=1000000, description="Amount to send in BDT")
    
    @field_validator('receiver_phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number (must be exactly 11 digits)."""
        phone = re.sub(r'[\s\-]', '', v)
        # Remove any leading + or country code
        phone = re.sub(r'^\+?\d{1,3}', '', phone) if phone.startswith('+') else phone
        # Check if it's exactly 11 digits
        if not re.match(r'^\d{11}$', phone):
            raise ValueError('Phone number must be exactly 11 digits')
        return phone
    
    class Config:
        json_schema_extra = {
            "example": {
                "receiver_phone": "+8801712345678",
                "amount": 1000.0
            }
        }


class RiskCheckResponse(BaseModel):
    """Schema for risk check response."""
    risk_level: str = Field(..., description="Risk level: 'low', 'medium', or 'high'")
    risk_score: float = Field(..., description="Numerical risk score (reconstruction error)")
    threshold: float = Field(..., description="Threshold used for anomaly detection")
    can_proceed: bool = Field(..., description="Whether the transaction can proceed")
    warnings: list[str] = Field(default_factory=list, description="List of warning messages")
    details: Optional[dict] = Field(default=None, description="Additional risk details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "risk_level": "low",
                "risk_score": 1.25,
                "threshold": 1.96,
                "can_proceed": True,
                "warnings": [],
                "details": {}
            }
        }


class TransactionPreviewRequest(BaseModel):
    """Schema for transaction preview request."""
    receiver_phone: str = Field(..., description="Phone number of the receiver")
    amount: float = Field(..., gt=0, le=1000000, description="Amount to send in BDT")
    
    @field_validator('receiver_phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number (must be exactly 11 digits)."""
        phone = re.sub(r'[\s\-]', '', v)
        # Remove any leading + or country code
        phone = re.sub(r'^\+?\d{1,3}', '', phone) if phone.startswith('+') else phone
        # Check if it's exactly 11 digits
        if not re.match(r'^\d{11}$', phone):
            raise ValueError('Phone number must be exactly 11 digits')
        return phone
    
    class Config:
        json_schema_extra = {
            "example": {
                "receiver_phone": "+8801712345678",
                "amount": 1000.0
            }
        }


class TransactionPreviewResponse(BaseModel):
    """Schema for transaction preview response."""
    sender_balance: float
    receiver_name: str
    receiver_phone: str
    amount: float
    fee: float = Field(default=0.0, description="Transaction fee (currently 0)")
    total_deducted: float = Field(..., description="Total amount to be deducted from sender")
    new_balance: float = Field(..., description="Sender's balance after transaction")
    risk_check: RiskCheckResponse
    can_proceed: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "sender_balance": 5000.0,
                "receiver_name": "John Doe",
                "receiver_phone": "+8801712345678",
                "amount": 1000.0,
                "fee": 0.0,
                "total_deducted": 1000.0,
                "new_balance": 4000.0,
                "risk_check": {
                    "risk_level": "low",
                    "risk_score": 1.25,
                    "threshold": 1.96,
                    "can_proceed": True,
                    "warnings": [],
                    "details": {}
                },
                "can_proceed": True
            }
        }


class TransactionConfirmRequest(BaseModel):
    """Schema for confirming a transaction."""
    receiver_phone: str = Field(..., description="Phone number of the receiver")
    amount: float = Field(..., gt=0, le=1000000, description="Amount to send in BDT")
    
    @field_validator('receiver_phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number (must be exactly 11 digits)."""
        phone = re.sub(r'[\s\-]', '', v)
        # Remove any leading + or country code
        phone = re.sub(r'^\+?\d{1,3}', '', phone) if phone.startswith('+') else phone
        # Check if it's exactly 11 digits
        if not re.match(r'^\d{11}$', phone):
            raise ValueError('Phone number must be exactly 11 digits')
        return phone
    
    class Config:
        json_schema_extra = {
            "example": {
                "receiver_phone": "+8801712345678",
                "amount": 1000.0
            }
        }