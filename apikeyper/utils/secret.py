"""
Secret redaction utilities for APIKeyPER.

This module provides utilities for redacting sensitive information
in logs, exports, and other outputs.
"""


def redact(_: object) -> str:
    """
    Redact any object by returning a placeholder string.
    
    This function is used to replace sensitive values (like API keys)
    with a redacted placeholder to prevent accidental exposure in
    logs, exports, or other outputs.
    
    Args:
        _: Any object (the value is ignored for security)
        
    Returns:
        A redacted placeholder string
    """
    return "[REDACTED]"