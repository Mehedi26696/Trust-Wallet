from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    """Transaction model for recording money transfers between users."""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    sender_id: UUID = Field(foreign_key="users.id")
    receiver_id: UUID = Field(foreign_key="users.id")
    amount: float = Field(gt=0.0, description="Transaction amount in BDT")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field(default="completed", max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)
    
    class Config:
        """Pydantic configuration for the Transaction model."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "sender_id": "550e8400-e29b-41d4-a716-446655440000",
                "receiver_id": "550e8400-e29b-41d4-a716-446655440001", 
                "amount": 1000.0,
                "status": "completed",
                "description": "Payment for services"
            }
        }