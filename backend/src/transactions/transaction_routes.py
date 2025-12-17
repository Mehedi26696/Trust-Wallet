"""
Transaction API routes for managing money transfers and transaction history.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List
from uuid import UUID

from ..auth.auth_service import get_current_user
from ..models.user import User
from ..models.transaction import Transaction
from ..schemas.transaction_schemas import (
    TransactionResponse,
    TransactionListResponse,
    TransactionResponseWithWarning,
    AnomalyWarning,
)
from ..schemas.wallet_schemas import (
    WalletSendRequest, 
    WalletResponse,
    RiskCheckRequest,
    RiskCheckResponse,
    TransactionPreviewRequest,
    TransactionPreviewResponse,
    TransactionConfirmRequest,
)
from ..services.wallet_service import WalletService
from ..services.user_service import UserService
from ..utils.database import get_session
from ..utils.xgboost_fraud_detector import xgboost_fraud_check
from ..config import settings
from ..schemas.anomaly_schemas import RawTransaction, RawPredictionResponse
from datetime import datetime


router = APIRouter()




@router.get("/wallet", response_model=WalletResponse)
async def get_wallet_balance(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's wallet balance.
    
    Requires valid JWT token. Returns current wallet balance in BDT.
    """
    balance = WalletService.get_balance(current_user)
    
    return WalletResponse(
        user_id=current_user.id,
        balance=balance
    )


# Removed old autoencoder endpoint - now using XGBoost for fraud detection


@router.post("/ml/predict-fraud")
async def predict_fraud(
    transaction_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Direct API endpoint to predict fraud for a transaction using XGBoost.
    
    Expects transaction data with the following fields:
    - type: Transaction type (e.g., "TRANSFER")
    - amount: Transaction amount
    - payerdebited: Amount debited from payer
    - recievercredited: Amount credited to receiver
    - payer_type: Type of payer (e.g., "CUSTOMER")
    - reciever_type: Type of receiver (e.g., "CUSTOMER")
    - hour: Hour of day (0-23)
    - day_of_week: Day of week (0-6)
    - date: Day of month (1-31)
    
    Returns:
    - isFraud: 0 or 1
    - fraud_probability: Probability of fraud (0.0 to 1.0)
    """
    from ..utils.xgboost_fraud_detector import predict_single_transaction
    
    try:
        result = predict_single_transaction(transaction_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud prediction failed: {str(e)}"
        )


@router.post("/wallet/check-risk", response_model=RiskCheckResponse)
async def check_transaction_risk(
    risk_request: RiskCheckRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Check risk level for a potential transaction without executing it.
    
    This endpoint provides live risk assessment for the frontend.
    No database changes are made; it only analyzes the risk.
    
    - **receiver_phone**: Phone number of the receiver
    - **amount**: Amount to send in BDT
    
    Returns:
    - risk_level: "low", "medium", or "high"
    - risk_score: Reconstruction error from autoencoder
    - threshold: Threshold used for anomaly detection
    - can_proceed: Whether transaction should be allowed
    - warnings: List of warning messages
    """
    try:
        # Find receiver by phone
        receiver = UserService.get_user_by_phone(session, risk_request.receiver_phone)
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver not found"
            )
        
        # Check if receiver is active
        if not receiver.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Receiver account is inactive"
            )
        
        # Can't send to yourself
        if current_user.id == receiver.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send money to yourself"
            )
        
        # Run XGBoost fraud check
        is_fraud, fraud_prob, details = xgboost_fraud_check(
            session,
            str(current_user.id),
            str(receiver.id),
            float(risk_request.amount),
            transaction_type="TRANSFER"
        )
        
        # Determine risk level based on fraud probability
        if fraud_prob < 0.3:
            risk_level = "low"
        elif fraud_prob < 0.7:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Build warnings list
        warnings = []
        if is_fraud:
            warnings.append("Transaction flagged as potentially fraudulent")
        if fraud_prob > 0.7:
            warnings.append("High fraud risk detected")
        elif fraud_prob > 0.5:
            warnings.append("Moderate fraud risk detected")
        
        # Determine if transaction can proceed
        can_proceed = not is_fraud or not settings.BLOCK_ML_ANOMALY
        
        return RiskCheckResponse(
            risk_level=risk_level,
            risk_score=fraud_prob,
            threshold=0.5,
            can_proceed=can_proceed,
            warnings=warnings,
            details=details
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Fail open: if risk check fails, allow transaction with warning
        return RiskCheckResponse(
            risk_level="low",
            risk_score=0.0,
            threshold=0.5,
            can_proceed=True,
            warnings=["Risk check unavailable"],
            details={"error": str(e)}
        )


@router.post("/wallet/preview-send", response_model=TransactionPreviewResponse)
async def preview_transaction(
    preview_request: TransactionPreviewRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Preview a transaction before confirming it.
    
    This endpoint validates the transaction and shows what will happen,
    including fees, risk analysis, and final balances, WITHOUT executing it.
    
    - **receiver_phone**: Phone number of the receiver
    - **amount**: Amount to send in BDT
    
    Returns full preview including:
    - Current balance
    - Receiver information
    - Amount and fees
    - Risk assessment
    - Final balance after transaction
    """
    try:
        # Find receiver by phone
        receiver = UserService.get_user_by_phone(session, preview_request.receiver_phone)
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver not found"
            )
        
        # Check if receiver is active
        if not receiver.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Receiver account is inactive"
            )
        
        # Can't send to yourself
        if current_user.id == receiver.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send money to yourself"
            )
        
        # Check sender balance
        if current_user.wallet_balance < preview_request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        
        # Run XGBoost fraud check
        is_fraud, fraud_prob, details = xgboost_fraud_check(
            session,
            str(current_user.id),
            str(receiver.id),
            float(preview_request.amount),
            transaction_type="TRANSFER"
        )
        
        # Determine risk level based on fraud probability
        # Low: < 30%, Medium: 30-70%, High: > 70%
        if fraud_prob < 0.3:
            risk_level = "low"
        elif fraud_prob < 0.7:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Build warnings
        warnings = []
        if is_fraud:
            warnings.append("Transaction flagged as potentially fraudulent")
        if fraud_prob > 0.7:
            warnings.append("High fraud risk detected")
        elif fraud_prob > 0.5:
            warnings.append("Moderate fraud risk detected")
        
        # Determine if can proceed
        can_proceed = not is_fraud or not settings.BLOCK_ML_ANOMALY
        
        # Calculate fees (currently 0, but structured for future)
        fee = 0.0
        total_deducted = preview_request.amount + fee
        new_balance = current_user.wallet_balance - total_deducted
        
        # Build risk check response
        risk_check = RiskCheckResponse(
            risk_level=risk_level,
            risk_score=fraud_prob,  # Use fraud probability as risk score
            threshold=0.5,  # Standard threshold for binary classification
            can_proceed=can_proceed,
            warnings=warnings,
            details=details
        )
        
        return TransactionPreviewResponse(
            sender_balance=current_user.wallet_balance,
            receiver_name=receiver.full_name,
            receiver_phone=receiver.phone_number or preview_request.receiver_phone,
            amount=preview_request.amount,
            fee=fee,
            total_deducted=total_deducted,
            new_balance=new_balance,
            risk_check=risk_check,
            can_proceed=can_proceed
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview failed: {str(e)}"
        )


@router.post("/wallet/confirm-send", response_model=TransactionResponseWithWarning, status_code=status.HTTP_201_CREATED)
async def confirm_transaction(
    confirm_request: TransactionConfirmRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Execute a transaction after preview and confirmation.
    
    This is the second step of the two-step confirmation flow.
    The user should call /wallet/preview-send first to see the preview,
    then call this endpoint to execute the actual transfer.
    
    - **receiver_phone**: Phone number of the receiver
    - **amount**: Amount to send in BDT
    
    Returns transaction details with optional anomaly warning.
    """
    try:
        # Convert to WalletSendRequest format
        send_request = WalletSendRequest(
            receiver_phone=confirm_request.receiver_phone,
            amount=confirm_request.amount
        )
        
        # Find receiver by phone
        receiver = UserService.get_user_by_phone(session, send_request.receiver_phone)
        receiver_id = receiver.id if receiver else None
        
        # XGBoost ML pre-check
        is_fraud, fraud_prob, details = xgboost_fraud_check(
            session,
            str(current_user.id),
            str(receiver_id) if receiver_id else "",
            float(send_request.amount),
            transaction_type="TRANSFER"
        )
        
        if is_fraud and settings.BLOCK_ML_ANOMALY:
            # Block transaction
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "warning": {
                        "flagged": True,
                        "reason": "Transaction flagged as potentially fraudulent by ML model",
                        "fraud_probability": fraud_prob,
                        "threshold": 0.5,
                        "details": details,
                    }
                },
            )
        
        # Execute the transaction
        transaction = WalletService.send_money(session, current_user, send_request)
        
        # Build warning if fraud detected but not blocking
        warning = None
        if is_fraud and not settings.BLOCK_ML_ANOMALY:
            warning = AnomalyWarning(
                flagged=True,
                reason="Transaction flagged as potentially fraudulent by XGBoost model",
                reconstruction_error=fraud_prob,  # Using fraud_prob as score
                threshold=0.5,
                details=details,
            )
        
        return TransactionResponseWithWarning(
            transaction=TransactionResponse.model_validate(transaction),
            warning=warning,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction failed: {str(e)}"
        )


@router.post("/wallet/send", response_model=TransactionResponseWithWarning, status_code=status.HTTP_201_CREATED)
async def send_money(
    send_request: WalletSendRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Send money to another user.
    
    - **receiver_phone**: Phone number of the receiver
    - **amount**: Amount to send in BDT (must be positive, max 1,000,000)
    
    Validates:
    - Sender has sufficient balance
    - Receiver exists and is active
    - Amount is positive
    - Fraud detection rules
    
    Returns transaction details upon successful transfer.
    If ML detects an anomaly and BLOCK_ML_ANOMALY is false, returns the transaction with a warning payload.
    """
    try:
        # XGBoost ML pre-check (fails open if artifacts missing)
        receiver = UserService.get_user_by_phone(session, send_request.receiver_phone)
        receiver_id = receiver.id if receiver else None

        is_fraud, fraud_prob, details = xgboost_fraud_check(
            session,
            str(current_user.id),
            str(receiver_id) if receiver_id else "",
            float(send_request.amount),
            transaction_type="TRANSFER"
        )

        if is_fraud and settings.BLOCK_ML_ANOMALY:
            # Block transaction with clear 409 response
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "warning": {
                        "flagged": True,
                        "reason": "Transaction flagged as potentially fraudulent by ML model",
                        "fraud_probability": fraud_prob,
                        "threshold": 0.5,
                        "details": details,
                    }
                },
            )

        transaction = WalletService.send_money(session, current_user, send_request)
        
        # Wrap response and include a warning (non-blocking) when flagged
        warning = None
        if is_fraud and not settings.BLOCK_ML_ANOMALY:
            warning = AnomalyWarning(
                flagged=True,
                reason="Transaction flagged as potentially fraudulent by XGBoost model",
                reconstruction_error=fraud_prob,  # Using fraud_prob as score
                threshold=0.5,
                details=details,
            )

        return TransactionResponseWithWarning(
            transaction=TransactionResponse.model_validate(transaction),
            warning=warning,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction failed"
        )


@router.get("/transactions", response_model=TransactionListResponse)
async def get_user_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of transactions per page"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get user's transaction history with pagination.
    
    - **page**: Page number (starts from 1)
    - **page_size**: Number of transactions per page (1-100)
    
    Returns paginated list of transactions where user is either sender or receiver.
    Transactions are ordered by timestamp (most recent first).
    """
    offset = (page - 1) * page_size
    
    transactions = WalletService.get_transactions(
        session, 
        current_user.id, 
        limit=page_size, 
        offset=offset
    )
    
    total_count = WalletService.get_transaction_count(session, current_user.id)
    
    transaction_responses = [
        TransactionResponse.model_validate(transaction) 
        for transaction in transactions
    ]
    
    return TransactionListResponse(
        items=transaction_responses,  # Changed from 'transactions' to 'items'
        total_count=total_count,
        page=page,
        page_size=page_size
    )


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_details(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get details of a specific transaction.
    
    User can only view transactions where they are either sender or receiver.
    """
    from sqlmodel import select
    
    statement = select(Transaction).where(
        Transaction.id == transaction_id,
        (Transaction.sender_id == current_user.id) | 
        (Transaction.receiver_id == current_user.id)
    )
    
    transaction = session.exec(statement).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionResponse.model_validate(transaction)