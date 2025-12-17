"""
Password utilities for secure hashing and verification.
Uses bcrypt directly for secure password hashing.
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password (str): Plain text password to verify
        hashed_password (str): Stored hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        # Convert to bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Verify password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """
    Check if a password meets strength requirements.
    
    Requirements:
    - At least 8 characters long
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains digit
    - Contains special character
    
    Args:
        password (str): Password to check
        
    Returns:
        tuple[bool, list[str]]: (is_strong, list_of_missing_requirements)
    """
    requirements = []
    
    if len(password) < 8:
        requirements.append("At least 8 characters long")
    
    if not any(c.isupper() for c in password):
        requirements.append("At least one uppercase letter")
    
    if not any(c.islower() for c in password):
        requirements.append("At least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        requirements.append("At least one digit")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        requirements.append("At least one special character")
    
    return len(requirements) == 0, requirements