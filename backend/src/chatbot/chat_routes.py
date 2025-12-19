from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from .chat_service import (
    chat_with_tia,
    get_session_info,
    clear_session,
    get_session_count
)


router = APIRouter()



class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=1000, description="User's message to Tia")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity. If not provided, a new session will be created.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "How do I send money to someone?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Tia's response")
    session_id: str = Field(..., description="Session ID for this conversation")
    timestamp: str = Field(..., description="Response timestamp in ISO format")
    message_count: int = Field(..., description="Total messages in this session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "To send money in TrustWallet, follow these steps:\n1. Go to the 'Send Money' section\n2. Enter the recipient's phone number\n3. Enter the amount in BDT\n4. Review the transaction details\n5. Confirm to complete the transfer 💸",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-12-18T10:30:45.123456",
                "message_count": 2
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    ok: bool = Field(..., description="Health status")
    service: str = Field(default="Tia Chatbot", description="Service name")
    sessions_active: int = Field(..., description="Number of active chat sessions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ok": True,
                "service": "Tia Chatbot",
                "sessions_active": 15
            }
        }


class SessionInfoResponse(BaseModel):
    """Response model for session info endpoint."""
    session_id: str
    message_count: int
    exists: bool
    max_messages: int


@router.get("/health", response_model=HealthResponse, tags=["chat"])
async def health_check():
    """
    Health check endpoint for the chatbot service.
    
    Returns:
        HealthResponse with service status and active sessions count
    """
    return HealthResponse(
        ok=True,
        service="Tia Chatbot",
        sessions_active=get_session_count()
    )


@router.post("/chat", response_model=ChatResponse, tags=["chat"], status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    """
    Chat with Tia, TrustWallet's helpful in-app assistant.
    
    Tia helps users with:
    - Understanding app features (registration, NID verification, transactions)
    - Wallet operations (balance, send money, add funds)
    - Security tips and fraud detection information
    - Troubleshooting and finding features
    
    **Important:** Tia cannot access user accounts, balances, or transactions.
    
    Args:
        request: ChatRequest with user message and optional session_id
        
    Returns:
        ChatResponse with AI assistant's response and session info
        
    Raises:
        HTTPException: If the chatbot service fails
    """
    try:
        # Generate or use provided session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get chatbot response
        result = await chat_with_tia(
            session_id=session_id,
            user_message=request.message
        )
        
        return ChatResponse(**result)
        
    except ValueError as e:
        # Configuration error (e.g., missing API key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot configuration error: {str(e)}"
        )
    except Exception as e:
        # General error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=SessionInfoResponse, tags=["chat"])
async def get_session(session_id: str):
    """
    Get information about a specific chat session.
    
    Args:
        session_id: The session identifier
        
    Returns:
        Session information including message count and status
    """
    try:
        session_data = get_session_info(session_id)
        return SessionInfoResponse(**session_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session info: {str(e)}"
        )


@router.delete("/session/{session_id}", tags=["chat"])
async def delete_session(session_id: str):
    """
    Clear/delete a chat session and its history.
    
    Args:
        session_id: The session identifier to clear
        
    Returns:
        Success message
    """
    try:
        cleared = clear_session(session_id)
        if cleared:
            return {
                "success": True,
                "message": f"Session {session_id} has been cleared",
                "session_id": session_id
            }
        else:
            return {
                "success": False,
                "message": f"Session {session_id} not found",
                "session_id": session_id
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear session: {str(e)}"
        )


@router.get("/sessions/count", tags=["chat"])
async def get_active_sessions_count():
    """
    Get the total number of active chat sessions.
    
    Returns:
        Dictionary with active sessions count
    """
    return {
        "active_sessions": get_session_count(),
        "service": "Tia Chatbot"
    }
