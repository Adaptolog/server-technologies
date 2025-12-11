"""Utility functions for the application"""
import datetime
from typing import Optional, Dict, Any


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.datetime.utcnow().isoformat() + "Z"


def validate_user_data(data: Dict[str, Any]) -> Optional[str]:
    """Validate user data"""
    if not data or 'name' not in data:
        return "Name is required"
    
    name = data.get('name', '').strip()
    if not name:
        return "Name cannot be empty"
    
    if len(name) > 100:
        return "Name is too long (max 100 characters)"
    
    return None


def validate_category_data(data: Dict[str, Any]) -> Optional[str]:
    """Validate category data"""
    if not data or 'name' not in data:
        return "Name is required"
    
    name = data.get('name', '').strip()
    if not name:
        return "Name cannot be empty"
    
    if len(name) > 50:
        return "Name is too long (max 50 characters)"
    
    return None


def validate_record_data(data: Dict[str, Any]) -> Optional[str]:
    """Validate expense record data"""
    required_fields = ['user_id', 'category_id', 'amount']
    if not data or not all(field in data for field in required_fields):
        return "user_id, category_id, and amount are required"
    
    user_id = data.get('user_id', '').strip()
    category_id = data.get('category_id', '').strip()
    amount_str = data.get('amount', '')
    
    if not user_id:
        return "user_id cannot be empty"
    
    if not category_id:
        return "category_id cannot be empty"
    
    try:
        amount = float(amount_str)
        if amount <= 0:
            return "Amount must be positive"
        if amount > 1000000:  # Reasonable limit
            return "Amount is too large"
    except (ValueError, TypeError):
        return "Amount must be a valid number"
    
    return None