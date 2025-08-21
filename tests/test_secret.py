"""
Test the secret redaction utilities.
"""
import pytest
from apikeyper.utils.secret import redact


class TestSecretRedaction:
    """Test secret redaction functionality."""

    def test_redact_string(self):
        """Test redacting a string."""
        assert redact("secret_password") == "[REDACTED]"

    def test_redact_dict(self):
        """Test redacting a dictionary."""
        secret_dict = {"api_key": "secret123", "user": "admin"}
        assert redact(secret_dict) == "[REDACTED]"

    def test_redact_none(self):
        """Test redacting None."""
        assert redact(None) == "[REDACTED]"

    def test_redact_number(self):
        """Test redacting a number."""
        assert redact(12345) == "[REDACTED]"

    def test_redact_list(self):
        """Test redacting a list."""
        secret_list = ["secret1", "secret2"]
        assert redact(secret_list) == "[REDACTED]"