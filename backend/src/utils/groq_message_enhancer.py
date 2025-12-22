"""
Groq API integration for enhancing fraud risk messages with user-friendly explanations.
"""

import os
import json
from typing import Optional
import httpx
from ..config import settings


async def enhance_risk_message(
    risk_level: str,
    severity: str,
    original_reason: str,
    amount: float,
    risk_score: float,
) -> str:
    """
    Use Groq API to generate a user-friendly risk message.
    
    Args:
        risk_level: "low", "medium", or "high"
        severity: Specific severity level (critical, high, medium-high, etc.)
        original_reason: Technical reason from fraud detector
        amount: Transaction amount
        risk_score: Risk score (0-1)
        
    Returns:
        Enhanced user-friendly message, or original reason if API fails
    """
    if not settings.GROQ_API_KEY:
        return original_reason
    
    try:
        face_verify_note = " Note: Risk scores above 50% require face verification to proceed." if risk_score > 0.5 else ""
        prompt = f"""You are a helpful financial assistant for TrustWallet. A transaction has been flagged with the following details:

                Risk Level: {risk_level}
                Severity: {severity}
                Amount: ৳{amount:,.2f} BDT
                Risk Score: {risk_score:.1%}
                Technical Reason: {original_reason}
                Generate a brief, friendly message (2-3 sentences max) explaining why this transaction was flagged and what the user should know. Be reassuring if severity is low, cautious if medium, and firm if high/critical. Use simple language suitable for Bangladesh users.{face_verify_note} Do not use markdown formatting."""

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.GROQ_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful financial security assistant. Provide clear, concise explanations about transaction risks in 2-3 sentences maximum."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150,
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                enhanced_message = data["choices"][0]["message"]["content"].strip()
                return enhanced_message
            else:
                # Fallback to original reason on API error
                return original_reason
                
    except Exception as e:
        # Fail gracefully - return original reason if Groq API fails
        print(f"Groq API error: {e}")
        return original_reason


def enhance_risk_message_sync(
    risk_level: str,
    severity: str,
    original_reason: str,
    amount: float,
    risk_score: float,
) -> str:
    """
    Synchronous version using httpx sync client.
    
    Args:
        risk_level: "low", "medium", or "high"
        severity: Specific severity level (critical, high, medium-high, etc.)
        original_reason: Technical reason from fraud detector
        amount: Transaction amount
        risk_score: Risk score (0-1)
        
    Returns:
        Enhanced user-friendly message, or original reason if API fails
    """
    if not settings.GROQ_API_KEY:
        return original_reason
    
    try:
        face_verify_note = " Note: Risk scores above 50% require face verification to proceed." if risk_score > 0.5 else ""
        prompt = f"""You are a helpful financial assistant for TrustWallet. A transaction has been flagged with the following details:

Risk Level: {risk_level}
Severity: {severity}
Amount: ৳{amount:,.2f} BDT
Risk Score: {risk_score:.1%}
Technical Reason: {original_reason}

Generate a brief, friendly message (2-3 sentences max) explaining why this transaction was flagged and what the user should know. Be reassuring if severity is low, cautious if medium, and firm if high/critical. Use simple language suitable for Bangladesh users.{face_verify_note} Do not use markdown formatting."""

        with httpx.Client(timeout=5.0) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.GROQ_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful financial security assistant. Provide clear, concise explanations about transaction risks in 2-3 sentences maximum."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150,
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                enhanced_message = data["choices"][0]["message"]["content"].strip()
                return enhanced_message
            else:
                return original_reason
                
    except Exception as e:
        print(f"Groq API error: {e}")
        return original_reason
