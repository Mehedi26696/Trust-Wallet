from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
import math


class RawTransaction(BaseModel):
    product_category: str
    product_name: str
    merchant_name: str
    payment_method: str
    transaction_status: str
    device_type: str
    location: str
    product_amount: float
    transaction_fee: float
    cashback: float
    loyalty_points: float
    user_tx_count: float
    user_avg_amount: float
    user_freq: float
    merch_tx_count: float
    merch_avg_amount: float
    merchant_freq: float
    hour: int
    day: int
    month: int


class RawPredictionResponse(BaseModel):
    is_anomaly: int = Field(description="1 if anomaly, else 0")
    reconstruction_error: float
    threshold: float
    details: Optional[dict] = None
