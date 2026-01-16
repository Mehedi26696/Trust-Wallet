"""
XGBoost-based fraud detection for transactions.
Uses trained XGBoost pipeline to predict fraud probability.
"""

import os
import joblib
import pandas as pd
from typing import Dict, Any, Tuple
from datetime import datetime
from sqlmodel import Session, select
from ..models.transaction import Transaction


# Global cache for model
_xgb_pipeline = None


def load_xgboost_model():
    """Load the trained XGBoost pipeline from disk."""
    global _xgb_pipeline
    
    if _xgb_pipeline is not None:
        return _xgb_pipeline
    
    # Try to find the model in multiple locations
    model_dirs = [
        os.path.join(os.getcwd(), "models"),
        os.path.join(os.getcwd(), "ai_models"),
    ]
    
    for model_dir in model_dirs:
        model_path = os.path.join(model_dir, "xgboost_pipeline_fraud.pkl")
        if os.path.exists(model_path):
            try:
                _xgb_pipeline = joblib.load(model_path)
                print(f"✅ XGBoost model loaded from: {model_path}")
                return _xgb_pipeline
            except Exception as e:
                print(f"❌ Error loading XGBoost model from {model_path}: {e}")
                continue
    
    raise FileNotFoundError(
        f"XGBoost model not found in {model_dirs}. "
        "Please ensure 'xgboost_pipeline_fraud.pkl' exists in the models/ directory."
    )


def get_transaction_stats(session: Session, user_id: str) -> Dict[str, float]:
    """
    Get user's transaction statistics for feature engineering.
    
    Args:
        session: Database session
        user_id: User ID to get stats for
        
    Returns:
        Dictionary with transaction statistics
    """
    # Get all user's transactions
    transactions = session.exec(
        select(Transaction).where(
            (Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id)
        )
    ).all()
    
    if not transactions:
        return {
            "avg_amount": 0.0,
            "tx_count": 0,
            "frequency": 0.0,
        }
    
    amounts = [tx.amount for tx in transactions]
    avg_amount = sum(amounts) / len(amounts) if amounts else 0.0
    tx_count = len(transactions)
    frequency = tx_count / 30.0  # Average transactions per day (last 30 days)
    
    return {
        "avg_amount": avg_amount,
        "tx_count": tx_count,
        "frequency": frequency,
    }


def build_xgboost_features(
    session: Session,
    sender_id: str,
    receiver_id: str,
    amount: float,
    transaction_type: str = "TRANSFER"
) -> Dict[str, Any]:
    """
    Build feature dictionary for XGBoost model prediction.
    
    Expected features matching the trained model:
    - type: Transaction type (TRANSFER, PAYMENT, CASH_OUT, etc.)
    - amount: Transaction amount
    - payerdebited: Amount debited from payer
    - recievercredited: Amount credited to receiver (0.0 for fraudulent patterns)
    - payer_type: Type of payer account - "C" for Customer, "M" for Merchant
    - reciever_type: Type of receiver account - "C" for Customer, "M" for Merchant
    - hour: Hour of day (0-23)
    - day_of_week: Day of week (0-6, Monday=0)
    - date: Day of month (1-31)
    
    Args:
        session: Database session
        sender_id: Sender user ID
        receiver_id: Receiver user ID
        amount: Transaction amount
        transaction_type: Type of transaction (default: TRANSFER)
        
    Returns:
        Dictionary with features for XGBoost model
    """
    now = datetime.now()
    
    # For wallet transfers, both are CUSTOMER type
    # Model expects single letter: "C" for Customer, "M" for Merchant
    payer_type = "C"
    receiver_type = "C"
    
    features = {
        "type": transaction_type,
        "amount": float(amount),
        "payerdebited": float(amount),  # Amount debited from payer
        "recievercredited": float(amount),  # Amount credited to receiver (normal transaction)
        "payer_type": payer_type,  # "C" for Customer
        "reciever_type": receiver_type,  # "C" for Customer (note: typo in model training)
        "hour": now.hour,
        "day_of_week": now.weekday(),  # Monday=0, Sunday=6
        "date": now.day,
    }
    
    return features


def xgboost_fraud_check(
    session: Session,
    sender_id: str,
    receiver_id: str,
    amount: float,
    transaction_type: str = "TRANSFER"
) -> Tuple[bool, float, Dict[str, Any]]:
    """
    Check if a transaction is fraudulent using XGBoost model.
    
    Args:
        session: Database session
        sender_id: Sender user ID
        receiver_id: Receiver user ID
        amount: Transaction amount
        transaction_type: Type of transaction
        
    Returns:
        Tuple of (is_fraud, fraud_probability, details)
        - is_fraud: Boolean indicating if transaction is fraudulent
        - fraud_probability: Probability of fraud (0.0 to 1.0)
        - details: Dictionary with additional information
    """
    try:
        # Load the trained XGBoost model
        model = load_xgboost_model()
        
        # Build features for prediction
        features = build_xgboost_features(
            session, sender_id, receiver_id, amount, transaction_type
        )
        
        # Convert to DataFrame for model prediction
        df = pd.DataFrame([features])
        
        # Get prediction and probability
        is_fraud = model.predict(df)[0]
        fraud_probability = model.predict_proba(df)[0][1]  # Probability of class 1 (fraud)
        
        # Fraud threshold (configurable)
        fraud_threshold = 0.5
        
        # Build response details
        details = {
            "model": "xgboost",
            "features": features,
            "fraud_probability": float(fraud_probability),
            "threshold": fraud_threshold,
            "prediction": int(is_fraud),
        }
        
        # Return fraud decision based on threshold
        is_fraudulent = fraud_probability >= fraud_threshold
        return is_fraudulent, float(fraud_probability), details
    
    except Exception as e:
        # Fail open: if model fails, allow transaction but log error
        print(f"❌ XGBoost fraud check failed: {e}")
        return False, 0.0, {
            "model": "xgboost",
            "error": str(e),
            "fraud_probability": 0.0,
            "threshold": 0.5,
        }


def predict_single_transaction(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict fraud for a single transaction (API endpoint helper).
    
    Args:
        transaction_data: Dictionary with transaction features
        
    Returns:
        Dictionary with prediction results
    """
    try:
        model = load_xgboost_model()
        df = pd.DataFrame([transaction_data])
        
        is_fraud = model.predict(df)[0]
        fraud_prob = model.predict_proba(df)[0][1]
        
        return {
            "isFraud": int(is_fraud),
            "fraud_probability": float(fraud_prob),
        }
    except Exception as e:
        return {
            "isFraud": 0,
            "fraud_probability": 0.0,
            "error": str(e),
        }
