"""
NID (National ID) validation utilities for Bangladesh.
Supports 10, 13, and 17-digit NID formats with year validation.
"""

import re
from datetime import datetime


def is_valid_nid(nid: str) -> bool:
    """
    Validate Bangladesh National ID format.
    
    Rules:
    - Must be all digits
    - Length: 10, 13, or 17 characters
    - For 13/17-digit NIDs: first 4 digits must be a valid year (1900-2025)
    
    Args:
        nid (str): National ID string to validate
        
    Returns:
        bool: True if NID format is valid, False otherwise
    """
    if not nid or not isinstance(nid, str):
        return False
    
    # Remove any whitespace
    nid = nid.strip()
    
    # Check if all characters are digits
    if not nid.isdigit():
        return False
    
    # Check valid lengths
    if len(nid) not in [10, 13, 17]:
        return False
    
    # For 13 and 17-digit NIDs, validate the year part
    if len(nid) in [13, 17]:
        year_part = nid[:4]
        try:
            year = int(year_part)
            current_year = datetime.now().year
            
            # Year should be between 1900 and current year + 5
            if not (1900 <= year <= current_year + 5):
                return False
        except ValueError:
            return False
    
    return True


def verify_nid_with_api(nid: str) -> bool:
    """
    Verify NID with government API (placeholder implementation).
    
    This is a placeholder for future integration with Bangladesh
    government's NID verification API. Currently returns False
    to indicate that API verification is not available.
    
    Args:
        nid (str): National ID to verify
        
    Returns:
        bool: Always False (API not available)
    """
    # TODO: Implement actual API integration with Bangladesh Election Commission
    # For now, return False to indicate API verification is not available
    return False


def format_nid(nid: str) -> str:
    """
    Format NID for display purposes.
    
    Args:
        nid (str): Raw NID string
        
    Returns:
        str: Formatted NID string
    """
    if not nid:
        return ""
    
    nid = nid.strip()
    
    # Format based on length
    if len(nid) == 10:
        # Format: XXXX-XXXXX-X
        return f"{nid[:4]}-{nid[4:9]}-{nid[9:]}"
    elif len(nid) == 13:
        # Format: XXXX-XXXX-XXXXX
        return f"{nid[:4]}-{nid[4:8]}-{nid[8:]}"
    elif len(nid) == 17:
        # Format: XXXX-XXXX-XXXX-XXXXX
        return f"{nid[:4]}-{nid[4:8]}-{nid[8:12]}-{nid[12:]}"
    
    return nid