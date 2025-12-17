from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class FraudAlert(SQLModel, table=True):
    __tablename__ = "fraud_alerts"

    """Fraud alert model for tracking suspicious activities."""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    reason: str = Field(max_length=500, description="Reason for fraud alert")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: str = Field(default="medium", max_length=20)  # low, medium, high, critical
    resolved: bool = Field(default=False)
    
    class Config:
        """Pydantic configuration for the FraudAlert model."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "reason": "High-value transaction exceeding 100,000 BDT",
                "severity": "high",
                "resolved": False
            }
        }