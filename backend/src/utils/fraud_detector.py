"""
Fraud detection utilities for transaction monitoring.
Implements rules to detect suspicious activities and prevent fraud.

Adds an optional ML-based pre-send anomaly check that uses trained artifacts
under `ai_models/`. If artifacts or PyCaret are unavailable, the check fails-open
(does not block a transaction).
"""

import sys
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


def check_fraudulent_activity(session: Session, user_id: UUID, amount: float, receiver_id: Optional[UUID] = None, record_alert: bool = True) -> Tuple[bool, str, str]:
    """
    Check if a transaction should be flagged as fraudulent.
    
    Fraud detection rules with severity levels:
    - critical (0.98): Multiple high-value in short time
    - high (0.90): Exceeds max amount, 2x historical max
    - medium-high (0.80): Rapid successive transactions, testing pattern
    - medium (0.70): Amount > average, first-time high-value receiver
    - low (0.35): Late night, weekend high-value
    
    Args:
        session: Database session
        user_id (UUID): User ID making the transaction
        amount (float): Transaction amount in BDT
        receiver_id (Optional[UUID]): Receiver user ID for additional checks
        
    Returns:
        Tuple[bool, str, str]: (is_fraudulent, reason, severity)
    """
    
    # Fetch user's transaction history for multiple rules
    time_30d_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_stmt = select(Transaction).where(
        Transaction.sender_id == user_id,
        Transaction.status == "completed",
        Transaction.timestamp >= time_30d_ago,
    ).order_by(Transaction.timestamp.desc())
    recent_txns = list(session.exec(recent_stmt))
    
    # Rule 1: Absolute maximum transaction amount (high severity)
    if amount > settings.MAX_TRANSACTION_AMOUNT:
        reason = f"Transaction amount {amount:,.2f} BDT exceeds maximum limit {settings.MAX_TRANSACTION_AMOUNT:,.2f} BDT"
        if record_alert:
            _create_fraud_alert(session, user_id, reason, "high")
        return True, reason, "high"

    # Rule 2: Amount exceeds 2x historical maximum (high severity)
    if recent_txns:
        amounts = [float(t.amount) for t in recent_txns if t.amount is not None]
        if amounts:
            max_historical = max(amounts)
            if amount > max_historical * 2:
                reason = f"Transaction amount {amount:,.2f} BDT is more than 2x your historical maximum {max_historical:,.2f} BDT"
                if record_alert:
                    _create_fraud_alert(session, user_id, reason, "high")
                return True, reason, "high"
    
    # Rule 3: Amount above recent average (medium severity)
    if recent_txns:
        amounts = [float(t.amount) for t in recent_txns if t.amount is not None]
        if amounts:
            avg_amount = sum(amounts) / len(amounts)
            if avg_amount > 0 and amount > avg_amount * 1.5:
                reason = f"Transaction amount {amount:,.2f} BDT significantly exceeds recent average {avg_amount:,.2f} BDT"
                if record_alert:
                    _create_fraud_alert(session, user_id, reason, "medium")
                return True, reason, "medium"
    
    # Rule 4: Multiple high-value transactions in short time (critical severity)
    if amount >= settings.HIGH_VALUE_THRESHOLD:
        time_window_ago = datetime.now(timezone.utc) - timedelta(minutes=settings.HIGH_VALUE_TIME_WINDOW_MINUTES)
        high_value_stmt = select(Transaction).where(
            Transaction.sender_id == user_id,
            Transaction.timestamp >= time_window_ago,
            Transaction.amount >= settings.HIGH_VALUE_THRESHOLD,
            Transaction.status == "completed"
        )
        recent_high_value = list(session.exec(high_value_stmt))
        
        if len(recent_high_value) >= settings.MAX_HIGH_VALUE_TRANSACTIONS:
            reason = f"Multiple high-value transactions: {len(recent_high_value) + 1} transactions ≥{settings.HIGH_VALUE_THRESHOLD:,.2f} BDT in {settings.HIGH_VALUE_TIME_WINDOW_MINUTES} minutes"
            if record_alert:
                _create_fraud_alert(session, user_id, reason, "critical")
            return True, reason, "critical"
    
    # Rule 5: Rapid successive transactions - velocity check (medium-high severity)
    time_5min_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
    velocity_stmt = select(Transaction).where(
        Transaction.sender_id == user_id,
        Transaction.timestamp >= time_5min_ago,
        Transaction.status == "completed"
    )
    recent_velocity = list(session.exec(velocity_stmt))
    if len(recent_velocity) >= 3:
        # Relax velocity rule for simple/small transactions (e.g. < 500 BDT)
        # Only block if either the current amount is high OR the previous ones were high
        is_high_velocity = amount >= 500 or any(float(t.amount) >= 500 for t in recent_velocity)
        
        if is_high_velocity:
            reason = f"Rapid transaction velocity: {len(recent_velocity) + 1} transactions in 5 minutes"
            if record_alert:
                _create_fraud_alert(session, user_id, reason, "medium-high")
            return True, reason, "medium-high"
        else:
            print(f"ℹ️ [INFO] Velocity check ignored for low-value transaction sequence ({amount} BDT)", file=sys.stderr)
    
    # Rule 6: First transaction to receiver with high amount (medium severity)
    if receiver_id and amount >= settings.HIGH_VALUE_THRESHOLD * 0.5:
        receiver_stmt = select(Transaction).where(
            Transaction.sender_id == user_id,
            Transaction.receiver_id == receiver_id,
            Transaction.status == "completed"
        )
        receiver_history = list(session.exec(receiver_stmt))
        if len(receiver_history) == 0:
            reason = f"First transaction to new receiver with amount {amount:,.2f} BDT"
            if record_alert:
                _create_fraud_alert(session, user_id, reason, "medium")
            return True, reason, "medium"
    
    # Rule 7: Testing pattern - small amount followed by large (medium-high severity)
    time_1hr_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    recent_1hr_stmt = select(Transaction).where(
        Transaction.sender_id == user_id,
        Transaction.timestamp >= time_1hr_ago,
        Transaction.status == "completed"
    ).order_by(Transaction.timestamp.desc())
    recent_1hr = list(session.exec(recent_1hr_stmt))
    
    if recent_1hr and amount >= settings.HIGH_VALUE_THRESHOLD:
        recent_amounts = [float(t.amount) for t in recent_1hr if t.amount is not None]
        # Check if any recent transaction was very small (<100 BDT) followed by this large one
        if any(amt < 100 for amt in recent_amounts[:3]):
            reason = f"Suspicious pattern: Small test transaction followed by large amount {amount:,.2f} BDT"
            if record_alert:
                _create_fraud_alert(session, user_id, reason, "medium-high")
            return True, reason, "medium-high"
    
    # Rule 8: Late night transaction (low severity - warning only)
    current_hour = datetime.now(timezone.utc).hour
    if (current_hour >= 22 or current_hour <= 6) and amount >= settings.HIGH_VALUE_THRESHOLD:
        reason = f"High-value transaction {amount:,.2f} BDT during late night hours (22:00-06:00)"
        if record_alert:
            _create_fraud_alert(session, user_id, reason, "low")
        return True, reason, "low"
    
    # Rule 9: Weekend high-value transaction (low severity - warning only)
    current_weekday = datetime.now(timezone.utc).weekday()
    if current_weekday >= 5 and amount >= settings.HIGH_VALUE_THRESHOLD * 1.5:
        reason = f"High-value weekend transaction {amount:,.2f} BDT"
        if record_alert:
            _create_fraud_alert(session, user_id, reason, "low")
        return True, reason, "low"
    
    return False, "", ""


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
        FraudAlert.timestamp >= thirty_days_ago,
        FraudAlert.resolved == False
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


def clear_user_fraud_block(session: Session, user_id: UUID) -> bool:
    """
    Clear all unresolved fraud alerts for a user to unblock their account.
    
    Args:
        session: Database session
        user_id (UUID): User ID to unblock
        
    Returns:
        bool: True if alerts were cleared, False if no pending alerts
    """
    statement = select(FraudAlert).where(
        FraudAlert.user_id == user_id,
        FraudAlert.resolved == False
    )
    
    unresolved_alerts = session.exec(statement).all()
    
    if not unresolved_alerts:
        return False
    
    # Mark all unresolved alerts as resolved
    for alert in unresolved_alerts:
        alert.resolved = True
        session.add(alert)
    
    session.commit()
    return True