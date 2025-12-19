
from typing import Dict, List, Optional
import google.generativeai as genai
from datetime import datetime
import os



class Message:
    def __init__(self, role: str, content: str):
        self.role = role  
        self.content = content



SESSIONS: Dict[str, List[Message]] = {}


MAX_SESSION_MESSAGES = 20


# System prompt for Tia
SYSTEM_PROMPT = """You are Tia, TrustWallet's friendly digital assistant available 24/7.

**Your Role:**
Help users understand and use the TrustWallet mobile app effectively.

**What TrustWallet offers:**
1. **User Registration & Login**
   - Email-based registration with strong password requirements
   - Bangladesh NID (National ID) verification (10, 13, or 17 digits)
   - Face recognition for enhanced security
   - JWT token-based secure authentication

2. **Wallet Operations**
   - Check wallet balance in BDT (Bangladeshi Taka)
   - Send money to other TrustWallet users (by phone number)
   - Add funds to wallet
   - Real-time balance updates

3. **Transaction Features**
   - View complete transaction history
   - Track sent and received money
   - Transaction status tracking
   - Transaction preview before confirmation

4. **Fraud Detection & Security**
   - Real-time fraud monitoring using AI/ML models
   - High-value transaction alerts (>100,000 BDT)
   - Velocity checks for suspicious activity
   - Risk assessment before transactions
   - Step-up authentication for risky transactions
   - Admin fraud alert dashboard

5. **Security Features**
   - Secure JWT authentication
   - NID format validation
   - Face verification
   - Securely Reset your Password

**How to help users:**
- Be concise, step-by-step, and friendly
- Use emojis occasionally to be playful 😊
- Explain features in simple Bangladeshi context
- Guide users to in-app features when applicable
- Provide troubleshooting tips for common issues

**IMPORTANT Limitations:**
❌ You CANNOT access or view:
   - User account details, balances, or transactions
   - Personal information (NID, phone numbers, emails)
   - Transaction history or records
   
If a user asks about their specific data, politely say:
"I cannot access your personal account information. Please check your account details directly in the app, or contact our support team for account-specific assistance."

**Security Policy - REFUSE these requests:**
🚫 NEVER provide, ask for, or help with:
   - OTP (One-Time Password) codes
   - PIN numbers
   - Passwords or password resets
   - Full NID numbers
   - Credit/debit card details
   - Bank account information

Instead, direct users to:
"For security reasons, please contact our official support team at support@trustwallet.genmorphixcoders.com"

**Out of Scope:**
If users ask about topics unrelated to TrustWallet (weather, news, general knowledge, etc.), politely respond:
"I'm specifically designed to help with TrustWallet features and usage. For that topic, I'd recommend checking other resources. Is there anything about TrustWallet I can help you with?"

**Language:**
Communicate in English by default. Keep responses clear and professional.

Remember: You're a helpful guide who provides customer care service, Guide users to the right in-app features! 💚"""


def get_gemini_model() -> genai.GenerativeModel:
    """
    Initialize and return the Google Gemini model.
    
    Returns:
        genai.GenerativeModel: Configured Gemini model instance
        
    Raises:
        ValueError: If GEMINI_API_KEY is not set in environment
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
  
    genai.configure(api_key=api_key)
    
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    

    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 500,
    }
    
   
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=SYSTEM_PROMPT
    )
    
    return model


def get_session_history(session_id: str) -> List[Message]:
    """
    Retrieve message history for a session.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        List of Message objects for the session
    """
    if session_id not in SESSIONS:
        SESSIONS[session_id] = []
    
    return SESSIONS[session_id]


def add_message_to_session(session_id: str, message: Message) -> None:
    """
    Add a message to session history, maintaining max message limit.
    
    Args:
        session_id: Unique session identifier
        message: Message to add (user or model message)
    """
    if session_id not in SESSIONS:
        SESSIONS[session_id] = []
    
    SESSIONS[session_id].append(message)
    

    if len(SESSIONS[session_id]) > MAX_SESSION_MESSAGES:
        SESSIONS[session_id] = SESSIONS[session_id][-MAX_SESSION_MESSAGES:]


def clear_session(session_id: str) -> bool:
    """
    Clear all messages from a session.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        True if session existed and was cleared, False otherwise
    """
    if session_id in SESSIONS:
        del SESSIONS[session_id]
        return True
    return False


def get_session_count() -> int:
    """
    Get the total number of active sessions.
    
    Returns:
        Number of active sessions
    """
    return len(SESSIONS)


async def chat_with_tia(session_id: str, user_message: str) -> Dict[str, any]:
    """
    Process a user message and generate a response from Tia.
    
    Args:
        session_id: Unique session identifier for conversation continuity
        user_message: The user's input message
        
    Returns:
        Dictionary containing:
            - response: AI assistant's response
            - session_id: The session identifier
            - timestamp: Response timestamp
            - message_count: Number of messages in current session
            
    Raises:
        Exception: If Gemini API call fails
    """
    try:
  
        model = get_gemini_model()
        
  
        history = get_session_history(session_id)
        
        
        gemini_history = []
        for msg in history:
            gemini_history.append({
                "role": msg.role,
                "parts": [msg.content]
            })
        
      
        chat = model.start_chat(history=gemini_history)
        
    
        response = chat.send_message(user_message)
        response_text = response.text
        
       
        add_message_to_session(session_id, Message("user", user_message))
        add_message_to_session(session_id, Message("model", response_text))
        
        return {
            "response": response_text,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message_count": len(get_session_history(session_id))
        }
        
    except Exception as e:
      
        print(f"Error in chat_with_tia: {str(e)}")
        raise Exception(f"Failed to generate chatbot response: {str(e)}")


def get_session_info(session_id: str) -> Dict[str, any]:
    """
    Get information about a specific session.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Dictionary with session information
    """
    history = get_session_history(session_id)
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "exists": session_id in SESSIONS,
        "max_messages": MAX_SESSION_MESSAGES
    }
