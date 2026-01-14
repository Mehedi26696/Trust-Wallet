"""
Transaction API routes for managing money transfers and transaction history.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List
from uuid import UUID

import sys
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
    AddFundsRequest,
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
from ..utils.fraud_detector import check_fraudulent_activity
from ..utils.groq_message_enhancer import enhance_risk_message
from ..config import settings
from ..schemas.anomaly_schemas import RawTransaction, RawPredictionResponse
from datetime import datetime, timezone, timedelta


def is_face_verified_recently(user: User, window_minutes: int = 5) -> bool:
    """Check if the user has successfully verified their face in the last X minutes."""
    if not user.last_face_verified_at:
        return False
    
    now = datetime.now(timezone.utc)
    last_verified = user.last_face_verified_at
    
    # Ensure TZ-aware comparison
    if last_verified.tzinfo is None:
        last_verified = last_verified.replace(tzinfo=timezone.utc)
    
    diff = (now - last_verified)
    is_recent = diff < timedelta(minutes=window_minutes)
    
    print(f"DEBUG [FACE-CHECK] user={user.id}, now={now}, last={last_verified}, diff={diff}, is_recent={is_recent}", file=sys.stderr)
    return is_recent


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


@router.post("/wallet/add-funds", response_model=WalletResponse)
async def add_funds(
    add_funds_request: AddFundsRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Add funds to user's wallet account.
    
    - **amount**: Amount to deposit in BDT (max 10,000,000)
    - **description**: Optional note about the deposit
    
    Returns updated wallet balance.
    Requires valid JWT token for authentication.
    """
    try:
        # Update user's wallet balance
        new_balance = current_user.wallet_balance + add_funds_request.amount
        
        # Update in database
        current_user.wallet_balance = new_balance
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        
        return WalletResponse(
            user_id=current_user.id,
            balance=current_user.wallet_balance
        )
    
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add funds: {str(e)}"
        )


@router.post("/cashin", response_model=WalletResponse)
async def cashin(
    add_funds_request: AddFundsRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Cash in to user's wallet (alias for add-funds).
    
    - **amount**: Amount to deposit in BDT (max 10,000,000)
    - **description**: Optional note about the deposit
    
    Returns updated wallet balance.
    Requires valid JWT token for authentication.
    """
    try:
        # Update user's wallet balance
        new_balance = current_user.wallet_balance + add_funds_request.amount
        
        # Update in database
        current_user.wallet_balance = new_balance
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        
        return WalletResponse(
            user_id=current_user.id,
            balance=current_user.wallet_balance
        )
    
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add funds: {str(e)}"
        )


# Removed old autoencoder endpoint - now using XGBoost for fraud detection


@router.post("/cashout", response_model=WalletResponse)
async def cashout(
    cashout_request: AddFundsRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Cash out (withdraw) from user's wallet.
    
    - **amount**: Amount to withdraw in BDT (must be > 0)
    - **description**: Optional note about the withdrawal
    
    Returns updated wallet balance.
    Requires valid JWT token for authentication.
    """
    try:
        amount = cashout_request.amount
        # Validate sufficient balance
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0"
            )
        if current_user.wallet_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )

        # Subtract and persist
        current_user.wallet_balance = current_user.wallet_balance - amount
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return WalletResponse(
            user_id=current_user.id,
            balance=current_user.wallet_balance
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cash out: {str(e)}"
        )


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
        
        # Rule-based check (always execute)
        rule_flagged, rule_reason, rule_severity = check_fraudulent_activity(
            session, current_user.id, float(risk_request.amount)
        )

        # Run XGBoost fraud check
        is_fraud, fraud_prob, details = xgboost_fraud_check(
            session,
            str(current_user.id),
            str(receiver.id),
            float(risk_request.amount),
            transaction_type="TRANSFER"
        )

        warnings = []

        # If rule-based flagged, set high risk and block (can_proceed=False)
        if rule_flagged:
            # Map severity to risk score with more granular levels
            severity_scores = {
                "critical": 0.98,
                "high": 0.90,
                "medium-high": 0.80,
                "medium": 0.70,
                "medium-low": 0.55,
                "low": 0.35
            }
            rule_score = severity_scores.get(rule_severity, 0.85)
            # Only block for medium and above; allow low severity with warning
            can_proceed = rule_severity == "low"
            
            # Enhance message with Groq if available
            enhanced_reason = await enhance_risk_message(
                risk_level="high" if rule_severity != "low" else "medium",
                severity=rule_severity,
                original_reason=rule_reason,
                amount=float(risk_request.amount),
                risk_score=rule_score,
            )
            warnings.append(enhanced_reason)
            
            return RiskCheckResponse(
                risk_level="high" if rule_severity != "low" else "medium",
                risk_score=rule_score,
                threshold=0.5,
                can_proceed=can_proceed,
                warnings=warnings,
                details={"rule": rule_reason, "severity": rule_severity, "model": details},
            )

        # If model failed internally and returned fail-open defaults, use a heuristic fallback
        if isinstance(details, dict) and ("error" in details):
            amt = float(risk_request.amount)
            # Heuristic based on configured thresholds
            if amt >= settings.HIGH_VALUE_THRESHOLD:
                fraud_prob = 0.85
                risk_level = "high"
                warnings.append("ML unavailable; heuristic high risk by amount")
            elif amt >= settings.HIGH_VALUE_THRESHOLD * 0.6:
                fraud_prob = 0.55
                risk_level = "medium"
                warnings.append("ML unavailable; heuristic medium risk by amount")
            else:
                fraud_prob = 0.15
                risk_level = "low"
                warnings.append("ML unavailable; heuristic low risk")
            can_proceed = True
            return RiskCheckResponse(
                risk_level=risk_level,
                risk_score=fraud_prob,
                threshold=0.5,
                can_proceed=can_proceed,
                warnings=warnings,
                details=details,
            )

        # Determine risk level based on fraud probability
        if fraud_prob < 0.3:
            risk_level = "low"
        elif fraud_prob < 0.7:
            risk_level = "medium"
        else:
            risk_level = "high"

        # Build warnings list from model output
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
        
        # Rule-based check (always execute)
        is_face_verified = is_face_verified_recently(current_user)
        rule_flagged, rule_reason, rule_severity = check_fraudulent_activity(
            session, current_user.id, float(preview_request.amount),
            record_alert=not is_face_verified
        )

        # Run XGBoost fraud check
        is_fraud, fraud_prob, details = xgboost_fraud_check(
            session,
            str(current_user.id),
            str(receiver.id),
            float(preview_request.amount),
            transaction_type="TRANSFER"
        )

        warnings = []

        # If rule-based flagged, force high risk and disallow proceed
        if rule_flagged:
            # Map severity to risk score with more granular levels
            severity_scores = {
                "critical": 0.98,
                "high": 0.90,
                "medium-high": 0.80,
                "medium": 0.70,
                "medium-low": 0.55,
                "low": 0.35
            }
            rule_score = severity_scores.get(rule_severity, 0.85)
            # Only block for medium and above; allow low severity with warning
            # Also allow proceeding if face was verified recently (biometric bypass)
            is_face_verified = is_face_verified_recently(current_user)
            can_proceed = (rule_severity == "low") or is_face_verified
            
            if is_face_verified and rule_severity != "low":
                print(f"⚠️ [PREVIEW-BYPASS] Fraud Rule '{rule_reason}' (severity={rule_severity}) "
                      f"bypassed for user {current_user.id} during preview due to face verification", file=sys.stderr)
            
            # Enhance message with Groq if available
            enhanced_reason = await enhance_risk_message(
                risk_level="high" if rule_severity != "low" else "medium",
                severity=rule_severity,
                original_reason=rule_reason,
                amount=float(preview_request.amount),
                risk_score=rule_score,
            )
            warnings.append(enhanced_reason)
            
            risk_check = RiskCheckResponse(
                risk_level="high" if rule_severity != "low" else "medium",
                risk_score=rule_score,
                threshold=0.5,
                can_proceed=can_proceed,
                warnings=warnings,
                details={
                    "rule": rule_reason, 
                    "severity": rule_severity, 
                    "model": details,
                    "biometrics_required": rule_severity != "low" and not is_face_verified,
                    "face_enrolled": bool(current_user.face_image_path)
                },
            )
            # Even when flagged, show accurate fee/VAT so the UI reflects costs
            flagged_fee = round(float(preview_request.amount) * (10 / 1000), 2)
            flagged_vat = round(float(preview_request.amount) * (5 / 1000), 2)
            flagged_total = float(preview_request.amount) + flagged_fee + flagged_vat
            return TransactionPreviewResponse(
                sender_balance=current_user.wallet_balance,
                receiver_name=receiver.full_name,
                receiver_phone=receiver.phone_number or preview_request.receiver_phone,
                amount=preview_request.amount,
                fee=flagged_fee,
                vat=flagged_vat,
                total_deducted=flagged_total,
                new_balance=current_user.wallet_balance - flagged_total,
                risk_check=risk_check,
                can_proceed=can_proceed,
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
        if is_fraud:
            warnings.append("Transaction flagged as potentially fraudulent")
        if fraud_prob > 0.7:
            warnings.append("High fraud risk detected")
        elif fraud_prob > 0.5:
            warnings.append("Moderate fraud risk detected")
        
        # Determine if can proceed
        is_face_verified = is_face_verified_recently(current_user)
        can_proceed_ml = not is_fraud or not settings.BLOCK_ML_ANOMALY
        can_proceed = can_proceed_ml or is_face_verified
        
        if is_fraud and is_face_verified:
             print(f"⚠️ [PREVIEW-BYPASS] ML Fraud detected bypassed for user {current_user.id} during preview", file=sys.stderr)
        # Calculate fees: ৳10/1000 fee and ৳5/1000 VAT
        fee = round(float(preview_request.amount) * (10 / 1000), 2)
        vat = round(float(preview_request.amount) * (5 / 1000), 2)
        total_deducted = float(preview_request.amount) + fee + vat
        new_balance = current_user.wallet_balance - total_deducted
        
        # Build risk check response
        risk_check = RiskCheckResponse(
            risk_level=risk_level,
            risk_score=fraud_prob,  # Use fraud probability as risk score
            threshold=0.5,  # Standard threshold for binary classification
            can_proceed=can_proceed,
            warnings=warnings,
            details={
                "model_details": details,
                "biometrics_required": is_fraud and not is_face_verified,
                "face_enrolled": bool(current_user.face_image_path)
            }
        )
        
        return TransactionPreviewResponse(
            sender_balance=current_user.wallet_balance,
            receiver_name=receiver.full_name,
            receiver_phone=receiver.phone_number or preview_request.receiver_phone,
            amount=preview_request.amount,
            fee=fee,
            vat=vat,
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
        
        # Rule-based pre-check
        is_face_verified = is_face_verified_recently(current_user, window_minutes=5)
        rule_flagged, rule_reason, rule_severity = check_fraudulent_activity(
            session, current_user.id, float(send_request.amount),
            record_alert=not is_face_verified
        )
        if rule_flagged:
            # Map severity to risk score with more granular levels
            severity_scores = {
                "critical": 0.98,
                "high": 0.90,
                "medium-high": 0.80,
                "medium": 0.70,
                "medium-low": 0.55,
                "low": 0.35
            }
            rule_score = severity_scores.get(rule_severity, 0.85)
            # Only block for medium and above
            if rule_severity != "low":
                # Check for biometric bypass
                if is_face_verified:
                    print(f"⚠️ [BYPASS] Fraud Rule '{rule_reason}' (severity={rule_severity}) "
                          f"bypassed for user {current_user.id} due to recent face verification", file=sys.stderr)
                else:
                    # Enhance message with Groq if available
                    enhanced_reason = await enhance_risk_message(
                        risk_level="high",
                        severity=rule_severity,
                        original_reason=rule_reason,
                        amount=float(send_request.amount),
                        risk_score=rule_score,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={
                            "warning": {
                                "flagged": True,
                                "reason": enhanced_reason,
                                "fraud_probability": rule_score,
                                "threshold": 0.5,
                                "biometrics_required": True,
                                "face_enrolled": bool(current_user.face_image_path),
                                "details": {"rule": rule_reason, "severity": rule_severity},
                            }
                        },
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
            # Check for biometric bypass
            if is_face_verified:
                print(f"⚠️ [BYPASS] ML Fraud detected (prob={fraud_prob:.2f}) "
                      f"bypassed for user {current_user.id} due to recent face verification", file=sys.stderr)
            else:
                # Block transaction
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "warning": {
                            "flagged": True,
                            "reason": "Transaction flagged as potentially fraudulent by ML model",
                            "fraud_probability": fraud_prob,
                            "threshold": 0.5,
                            "biometrics_required": True,
                            "face_enrolled": bool(current_user.face_image_path),
                            "details": details,
                        }
                    },
                )
        
        # Execute the transaction
        transaction = WalletService.send_money(
            session, current_user, send_request, 
            face_verified=is_face_verified
        )
        
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
        # Rule-based pre-check
        is_face_verified = is_face_verified_recently(current_user, window_minutes=5)
        rule_flagged, rule_reason, rule_severity = check_fraudulent_activity(
            session, current_user.id, float(send_request.amount),
            record_alert=not is_face_verified
        )
        if rule_flagged:
            # Map severity to risk score with more granular levels
            severity_scores = {
                "critical": 0.98,
                "high": 0.90,
                "medium-high": 0.80,
                "medium": 0.70,
                "medium-low": 0.55,
                "low": 0.35
            }
            rule_score = severity_scores.get(rule_severity, 0.85)
            # Only block for medium and above
            if rule_severity != "low":
                # Check for biometric bypass
                if is_face_verified:
                    print(f"⚠️ [BYPASS] Fraud Rule '{rule_reason}' (severity={rule_severity}) "
                          f"bypassed for user {current_user.id} due to recent face verification", file=sys.stderr)
                else:
                    # Enhance message with Groq if available
                    enhanced_reason = await enhance_risk_message(
                        risk_level="high",
                        severity=rule_severity,
                        original_reason=rule_reason,
                        amount=float(send_request.amount),
                        risk_score=rule_score,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={
                            "warning": {
                                "flagged": True,
                                "reason": enhanced_reason,
                                "fraud_probability": rule_score,
                                "threshold": 0.5,
                                "biometrics_required": True,
                                "face_enrolled": bool(current_user.face_image_path),
                                "details": {"rule": rule_reason, "severity": rule_severity},
                            }
                        },
                    )

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
            # Check for biometric bypass
            if is_face_verified:
                print(f"⚠️ [BYPASS] ML Fraud detected (prob={fraud_prob:.2f}) "
                      f"bypassed for user {current_user.id} due to recent face verification", file=sys.stderr)
            else:
                # Block transaction with clear 409 response
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "warning": {
                            "flagged": True,
                            "reason": "Transaction flagged as potentially fraudulent by ML model",
                            "fraud_probability": fraud_prob,
                            "threshold": 0.5,
                            "biometrics_required": True,
                            "face_enrolled": bool(current_user.face_image_path),
                            "details": details,
                        }
                    },
                )

        transaction = WalletService.send_money(
            session, current_user, send_request,
            face_verified=is_face_verified
        )
        
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