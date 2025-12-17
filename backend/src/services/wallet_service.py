"""
Wallet service for handling wallet and transaction operations.
"""

from sqlmodel import Session, select
from typing import List
from fastapi import HTTPException, status
from datetime import datetime, timezone
from uuid import UUID

from ..models.user import User
from ..models.transaction import Transaction
from ..schemas.wallet_schemas import WalletSendRequest
from ..services.user_service import UserService
from ..utils.fraud_detector import check_fraudulent_activity, is_user_blocked


class WalletService:
    """Service class for wallet operations."""
    
    @staticmethod
    def get_balance(user: User) -> float:
        """
        Get user wallet balance.
        
        Args:
            user: User object
            
        Returns:
            float: Current wallet balance
        """
        return user.wallet_balance
    
    @staticmethod
    def send_money(
        session: Session, 
        sender: User, 
        send_request: WalletSendRequest
    ) -> Transaction:
        """
        Send money from one user to another.
        
        Args:
            session: Database session
            sender: Sender user object
            send_request: Send money request data
            
        Returns:
            Transaction: Created transaction object
            
        Raises:
            HTTPException: If validation fails or transaction is blocked
        """
        # Check if sender is blocked
        if is_user_blocked(session, sender.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account temporarily blocked due to suspicious activity"
            )
        
        # Find receiver by phone number
        receiver = UserService.get_user_by_phone(session, send_request.receiver_phone)
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
        
        # Can't send money to yourself
        if sender.id == receiver.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send money to yourself"
            )
        
        # Check sender balance
        if sender.wallet_balance < send_request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        
        # Check for fraud
        is_fraudulent, fraud_reason = check_fraudulent_activity(
            session, sender.id, send_request.amount
        )
        
        if is_fraudulent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Transaction flagged for review"
            )
        
        # Perform transaction
        try:
            # Deduct from sender
            sender.wallet_balance -= send_request.amount
            session.add(sender)
            
            # Add to receiver
            receiver.wallet_balance += send_request.amount
            session.add(receiver)
            
            # Create transaction record
            transaction = Transaction(
                sender_id=sender.id,
                receiver_id=receiver.id,
                amount=send_request.amount,
                status="completed",
                timestamp=datetime.now(timezone.utc)
            )
            
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            
            return transaction
            
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transaction failed"
            )
    
    @staticmethod
    def get_transactions(
        session: Session, 
        user_id: UUID, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[Transaction]:
        """
        Get user transactions.
        
        Args:
            session: Database session
            user_id: User ID
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List[Transaction]: List of transactions
        """
        statement = (
            select(Transaction)
            .where(
                (Transaction.sender_id == user_id) | 
                (Transaction.receiver_id == user_id)
            )
            .order_by(Transaction.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        
        transactions = session.exec(statement).all()
        return transactions
    
    @staticmethod
    def get_transaction_count(session: Session, user_id: UUID) -> int:
        """
        Get total count of user transactions.
        
        Args:
            session: Database session
            user_id: User ID
            
        Returns:
            int: Total transaction count
        """
        statement = select(Transaction).where(
            (Transaction.sender_id == user_id) | 
            (Transaction.receiver_id == user_id)
        )
        
        transactions = session.exec(statement).all()
        return len(transactions)
    
    @staticmethod
    def add_funds(session: Session, user_id: UUID, amount: float) -> bool:
        """
        Add funds to user wallet (for testing/admin purposes).
        
        Args:
            session: Database session
            user_id: User ID
            amount: Amount to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        if amount <= 0:
            return False
        
        user = UserService.get_user_by_id(session, user_id)
        if not user:
            return False
        
        user.wallet_balance += amount
        session.add(user)
        session.commit()
        
        return True