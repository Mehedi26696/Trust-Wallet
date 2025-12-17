from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID





class Transaction(BaseModel):
    type: str
    amount: float
    payerdebited: float
    recievercredited: float
    payer_type: str
    reciever_type: str
    hour: int
    day_of_week: int
    date: int

class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    amount: float
    timestamp: datetime
    status: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema for transaction list response."""
    items: List[TransactionResponse]  # Changed from 'transactions' to 'items'
    total_count: int
    page: int
    page_size: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total_count": 0,
                "page": 1,
                "page_size": 10
            }
        }


class AnomalyWarning(BaseModel):
    """Warning payload returned when an anomaly is detected but requests are not blocked."""
    flagged: bool
    reason: str
    reconstruction_error: Optional[float] = None
    threshold: Optional[float] = None
    details: Optional[dict] = None


class TransactionResponseWithWarning(BaseModel):
    """Response model wrapping a transaction with an optional anomaly warning."""
    transaction: TransactionResponse
    warning: Optional[AnomalyWarning] = None