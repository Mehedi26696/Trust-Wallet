"""
Fraud detection utilities for transaction monitoring.
Implements rules to detect suspicious activities and prevent fraud.

Adds an optional ML-based pre-send anomaly check that uses trained artifacts
under `ai_models/`. If artifacts or PyCaret are unavailable, the check fails-open
(does not block a transaction).
"""

from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select
from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID

from ..models.transaction import Transaction
from ..models.fraud_alert import FraudAlert
from ..config import settings
from .autoencoder_model import predict_raw_autoencoder


def autoencoder_fraud_check(
    session: Session,
    user_id: UUID,
    amount: float,
    receiver_id: Optional[UUID] = None,
    *,
    context: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, float, Dict[str, Any]]:
    """Run autoencoder-based fraud check on a send transaction.
    
    Builds a feature vector from transaction history and context, then
    scores with the autoencoder model. Returns (is_anomaly, recon_error, details).
    Fails open if model or artifacts are unavailable.
    
    Args:
        session: DB session
        user_id: Sender user ID
        amount: Transaction amount
        receiver_id: Receiver user ID (optional, for merchant features)
        context: Additional context dict (product_category, merchant_name, etc.)
    
    Returns:
        Tuple[bool, float, dict]: (is_anomaly, reconstruction_error, details)
    """
    try:
        now_ts = datetime.now(timezone.utc)
        ctx = context or {}
        
        # Fetch sender's recent transaction history
        recent_stmt = (
            select(Transaction)
            .where(Transaction.sender_id == user_id, Transaction.status == "completed")
            .order_by(Transaction.timestamp.desc())
            .limit(100)
        )
        recent = list(session.exec(recent_stmt))
        
        # Compute user-level stats
        user_tx_count = float(len(recent))
        amounts = [float(t.amount) for t in recent if t.amount is not None]
        user_avg_amount = float(sum(amounts) / len(amounts)) if amounts else 0.0
        # user_freq: transactions per day (simplified)
        if recent and len(recent) > 1:
            time_span = (recent[0].timestamp - recent[-1].timestamp).total_seconds() / 86400.0
            user_freq = user_tx_count / max(time_span, 1.0)
        else:
            user_freq = 0.0
        
        # Merchant-level stats (if receiver_id provided)
        merch_tx_count = 0.0
        merch_avg_amount = 0.0
        merchant_freq = 0.0
        if receiver_id:
            merch_stmt = (
                select(Transaction)
                .where(
                    Transaction.sender_id == user_id,
                    Transaction.receiver_id == receiver_id,
                    Transaction.status == "completed",
                )
                .order_by(Transaction.timestamp.desc())
                .limit(50)
            )
            merch_txns = list(session.exec(merch_stmt))
            merch_tx_count = float(len(merch_txns))
            merch_amounts = [float(t.amount) for t in merch_txns if t.amount is not None]
            merch_avg_amount = float(sum(merch_amounts) / len(merch_amounts)) if merch_amounts else 0.0
            if merch_txns and len(merch_txns) > 1:
                merch_span = (merch_txns[0].timestamp - merch_txns[-1].timestamp).total_seconds() / 86400.0
                merchant_freq = merch_tx_count / max(merch_span, 1.0)
        
        # Build raw transaction dict for autoencoder
        raw_tx = {
            "product_category": ctx.get("product_category", "transfer"),
            "product_name": ctx.get("product_name", "money_transfer"),
            "merchant_name": ctx.get("merchant_name", "unknown"),
            "payment_method": ctx.get("payment_method", "wallet"),
            "transaction_status": "completed",
            "device_type": ctx.get("device_type", "web"),
            "location": ctx.get("location", "BD"),
            "product_amount": float(amount),
            "transaction_fee": float(ctx.get("transaction_fee", 0.0)),
            "cashback": float(ctx.get("cashback", 0.0)),
            "loyalty_points": float(ctx.get("loyalty_points", 0.0)),
            "user_tx_count": user_tx_count,
            "user_avg_amount": user_avg_amount,
            "user_freq": user_freq,
            "merch_tx_count": merch_tx_count,
            "merch_avg_amount": merch_avg_amount,
            "merchant_freq": merchant_freq,
            "hour": now_ts.hour,
            "day": now_ts.day,
            "month": now_ts.month,
        }
        
        # Score with autoencoder
        result = predict_raw_autoencoder(raw_tx)
        is_anomaly = result["is_anomaly"] == 1
        recon_error = result["reconstruction_error"]
        
        details = {
            "features": raw_tx,
            "timestamp": now_ts.isoformat(),
            "threshold": result["threshold"],
        }
        
        return is_anomaly, recon_error, details
        
    except Exception as e:
        # Fail open: do not block transaction on ML errors
        return False, 0.0, {"ml_error": str(e)}


def check_fraudulent_activity(session: Session, user_id: UUID, amount: float) -> Tuple[bool, str]:
    """
    Check if a transaction should be flagged as fraudulent.
    
    Fraud detection rules:
    1. Transaction amount > MAX_TRANSACTION_AMOUNT BDT = suspicious
    2. More than MAX_HIGH_VALUE_TRANSACTIONS high-value (>=HIGH_VALUE_THRESHOLD) 
       transactions within HIGH_VALUE_TIME_WINDOW_MINUTES minutes = flag user
    
    Args:
        session: Database session
        user_id (UUID): User ID making the transaction
        amount (float): Transaction amount in BDT
        
    Returns:
        Tuple[bool, str]: (is_fraudulent, reason)
    """
    
    # Rule 1: High-value transaction check
    if amount > settings.MAX_TRANSACTION_AMOUNT:
        reason = f"High-value transaction of {amount:,.2f} BDT exceeds {settings.MAX_TRANSACTION_AMOUNT:,.2f} BDT limit"
        _create_fraud_alert(session, user_id, reason, "high")
        return True, reason
    
    # Rule 2: Multiple high-value transactions in short time
    if amount >= settings.HIGH_VALUE_THRESHOLD:
        # Check transactions in configured time window
        time_window_ago = datetime.now(timezone.utc) - timedelta(minutes=settings.HIGH_VALUE_TIME_WINDOW_MINUTES)
        
        statement = select(Transaction).where(
            Transaction.sender_id == user_id,
            Transaction.timestamp >= time_window_ago,
            Transaction.amount >= settings.HIGH_VALUE_THRESHOLD,
            Transaction.status == "completed"
        )
        
        recent_high_value_transactions = session.exec(statement).all()
        
        # If this would exceed the maximum allowed high-value transactions
        if len(recent_high_value_transactions) >= settings.MAX_HIGH_VALUE_TRANSACTIONS:
            reason = f"Multiple high-value transactions detected: {len(recent_high_value_transactions) + 1} transactions >={settings.HIGH_VALUE_THRESHOLD:,.2f} BDT in {settings.HIGH_VALUE_TIME_WINDOW_MINUTES} minutes"
            _create_fraud_alert(session, user_id, reason, "critical")
            return True, reason
    
    # Additional rules can be added here
    
    return False, ""


def _create_fraud_alert(session: Session, user_id: UUID, reason: str, severity: str = "medium") -> None:
    """
    Create a fraud alert record in the database.
    
    Args:
        session: Database session
        user_id (UUID): User ID associated with the alert
        reason (str): Reason for the fraud alert
        severity (str): Alert severity level
    """
    fraud_alert = FraudAlert(
        user_id=user_id,
        reason=reason,
        severity=severity,
        timestamp=datetime.now(timezone.utc),
        resolved=False
    )
    
    session.add(fraud_alert)
    session.commit()


def get_user_fraud_score(session: Session, user_id: UUID) -> float:
    """
    Calculate a fraud risk score for a user based on their transaction history.
    
    Args:
        session: Database session
        user_id (UUID): User ID to calculate score for
        
    Returns:
        float: Fraud risk score (0.0 - 1.0, higher = more risky)
    """
    score = 0.0
    
    # Check recent fraud alerts
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    statement = select(FraudAlert).where(
        FraudAlert.user_id == user_id,
        FraudAlert.timestamp >= thirty_days_ago
    )
    
    recent_alerts = session.exec(statement).all()
    
    # Increase score based on recent alerts
    for alert in recent_alerts:
        if alert.severity == "low":
            score += 0.1
        elif alert.severity == "medium":
            score += 0.2
        elif alert.severity == "high":
            score += 0.4
        elif alert.severity == "critical":
            score += 0.6
    
    # Check transaction patterns (velocity, amounts, etc.)
    statement = select(Transaction).where(
        Transaction.sender_id == user_id,
        Transaction.timestamp >= thirty_days_ago
    )
    
    recent_transactions = session.exec(statement).all()
    
    if recent_transactions:
        # High frequency of transactions
        if len(recent_transactions) > 100:
            score += 0.2
        
        # High average transaction amount
        avg_amount = sum(t.amount for t in recent_transactions) / len(recent_transactions)
        if avg_amount > 50000:
            score += 0.3
    
    # Cap the score at 1.0
    return min(score, 1.0)


def is_user_blocked(session: Session, user_id: UUID) -> bool:
    """
    Check if a user should be blocked from making transactions.
    
    Args:
        session: Database session
        user_id (UUID): User ID to check
        
    Returns:
        bool: True if user should be blocked
    """
    fraud_score = get_user_fraud_score(session, user_id)
    
    # Block users with high fraud scores
    if fraud_score >= 0.8:
        return True
    
    # Check for recent critical alerts
    twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    
    statement = select(FraudAlert).where(
        FraudAlert.user_id == user_id,
        FraudAlert.timestamp >= twenty_four_hours_ago,
        FraudAlert.severity == "critical",
        FraudAlert.resolved == False
    )
    
    critical_alerts = session.exec(statement).all()
    
    # Block if there are unresolved critical alerts in last 24 hours
    return len(critical_alerts) > 0