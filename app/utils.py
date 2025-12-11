"""Utility functions for the application"""


def get_current_timestamp():
    """Get current timestamp in ISO format"""
    import datetime
    return datetime.datetime.utcnow().isoformat() + "Z"