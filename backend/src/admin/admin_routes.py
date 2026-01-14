"""
Admin API routes for fraud detection and system management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from datetime import datetime, timezone, timedelta
from uuid import UUID

from ..auth.auth_service import get_current_user
from ..models.user import User
from ..models.fraud_alert import FraudAlert
from ..services.wallet_service import WalletService
from ..utils.database import get_session


router = APIRouter()


# Simple admin check - in production, implement proper role-based access
def verify_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify that the current user has admin privileges.
    In production, implement proper role-based access control.
    """
    # For demo purposes, assume user with ID 1 is admin
    # In production, add an 'is_admin' field to User model or create separate roles
    if current_user.id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/fraud-alerts")
async def get_fraud_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of alerts per page"),
    severity: str = Query(None, description="Filter by severity: low, medium, high, critical"),
    resolved: bool = Query(None, description="Filter by resolution status"),
    admin_user: User = Depends(verify_admin_user),
    session: Session = Depends(get_session)
):
    """
    Get fraud alerts with optional filtering.
    
    Admin only endpoint to view fraud detection alerts.
    """
    offset = (page - 1) * page_size
    
    # Build query
    statement = select(FraudAlert)
    
    if severity:
        statement = statement.where(FraudAlert.severity == severity)
    
    if resolved is not None:
        statement = statement.where(FraudAlert.resolved == resolved)
    
    statement = statement.order_by(FraudAlert.timestamp.desc())
    statement = statement.offset(offset).limit(page_size)
    
    alerts = session.exec(statement).all()
    
    # Get total count for pagination
    count_statement = select(FraudAlert)
    if severity:
        count_statement = count_statement.where(FraudAlert.severity == severity)
    if resolved is not None:
        count_statement = count_statement.where(FraudAlert.resolved == resolved)
    
    total_alerts = session.exec(count_statement).all()
    total_count = len(total_alerts)
    
    return {
        "alerts": alerts,
        "total_count": total_count,
        "page": page,
        "page_size": page_size
    }


@router.put("/fraud-alerts/{alert_id}/resolve")
async def resolve_fraud_alert(
    alert_id: int,
    admin_user: User = Depends(verify_admin_user),
    session: Session = Depends(get_session)
):
    """
    Mark a fraud alert as resolved.
    
    Admin only endpoint to resolve fraud alerts.
    """
    statement = select(FraudAlert).where(FraudAlert.id == alert_id)
    alert = session.exec(statement).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fraud alert not found"
        )
    
    alert.resolved = True
    session.add(alert)
    session.commit()
    
    return {"message": "Fraud alert resolved successfully"}


@router.get("/users/{user_id}/fraud-score")
async def get_user_fraud_score(
    user_id: UUID,
    admin_user: User = Depends(verify_admin_user),
    session: Session = Depends(get_session)
):
    """
    Get fraud risk score for a specific user.
    
    Admin only endpoint to check user's fraud risk.
    """
    from ..utils.fraud_detector import get_user_fraud_score
    
    # Check if user exists
    from ..services.user_service import UserService
    user = UserService.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    fraud_score = get_user_fraud_score(session, user_id)
    
    return {
        "user_id": user_id,
        "fraud_score": fraud_score,
        "risk_level": (
            "low" if fraud_score < 0.3 else
            "medium" if fraud_score < 0.6 else
            "high" if fraud_score < 0.8 else
            "critical"
        )
    }


@router.post("/users/{user_id}/add-funds")
async def add_funds_to_user(
    user_id: UUID,
    amount: float = Query(..., gt=0, description="Amount to add to user's wallet"),
    admin_user: User = Depends(verify_admin_user),
    session: Session = Depends(get_session)
):
    """
    Add funds to a user's wallet (admin only).
    
    For testing and administrative purposes.
    """
    success = WalletService.add_funds(session, user_id, amount)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or invalid amount"
        )
    
    return {
        "message": f"Successfully added {amount:,.2f} BDT to user {user_id}'s wallet"
    }


@router.get("/stats/overview")
async def get_system_overview(
    admin_user: User = Depends(verify_admin_user),
    session: Session = Depends(get_session)
):
    """
    Get system overview statistics.
    
    Admin only endpoint for system monitoring.
    """
    # Count total users
    users_statement = select(User)
    all_users = session.exec(users_statement).all()
    total_users = len(all_users)
    active_users = len([u for u in all_users if u.is_active])
    
    # Count transactions in last 24 hours
    from ..models.transaction import Transaction
    twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_transactions_statement = select(Transaction).where(
        Transaction.timestamp >= twenty_four_hours_ago
    )
    recent_transactions = session.exec(recent_transactions_statement).all()
    
    # Count fraud alerts in last 24 hours
    recent_alerts_statement = select(FraudAlert).where(
        FraudAlert.timestamp >= twenty_four_hours_ago
    )
    recent_alerts = session.exec(recent_alerts_statement).all()
    
    # Calculate total wallet balance
    total_balance = sum(user.wallet_balance for user in all_users)
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_wallet_balance": total_balance,
        "transactions_24h": len(recent_transactions),
        "fraud_alerts_24h": len(recent_alerts),
        "unresolved_alerts": len([a for a in recent_alerts if not a.resolved])
    }