"""
Encryption backend implementations for APIKeyPER.

This module provides different backends for storing and retrieving secrets,
including system keyring and in-memory storage for testing.
"""
from typing import Protocol, Optional, Dict
import hashlib


def make_key_id(namespace: str, service: str, key_name: str, profile: Optional[str] = None) -> str:
    """
    Generate a unique key identifier for secret storage.
    
    Args:
        namespace: The namespace (e.g., 'apikeyper')
        service: The service name
        key_name: The key name within the service
        profile: Optional profile name
        
    Returns:
        Unique key identifier string
    """
    parts = [namespace, service, key_name]
    if profile:
        parts.append(profile)
    
    # Create a stable, unique identifier
    key_str = ":".join(parts)
    # Use a hash to ensure consistent length and avoid special characters
    return f"{namespace}:{hashlib.sha256(key_str.encode()).hexdigest()[:16]}"


class EncryptionBackend(Protocol):
    """
    Protocol defining the interface for encryption backends.
    
    All backends must implement these methods to store, retrieve, and delete secrets.
    """
    
    def store_secret(self, key_id: str, value: str) -> None:
        """
        Store a secret value with the given key ID.
        
        Args:
            key_id: Unique identifier for the secret
            value: The secret value to store
            
        Raises:
            Exception: If storage fails
        """
        ...
    
    def retrieve_secret(self, key_id: str) -> Optional[str]:
        """
        Retrieve a secret value by key ID.
        
        Args:
            key_id: Unique identifier for the secret
            
        Returns:
            The secret value if found, None otherwise
        """
        ...
    
    def delete_secret(self, key_id: str) -> None:
        """
        Delete a secret by key ID.
        
        Args:
            key_id: Unique identifier for the secret
            
        Raises:
            Exception: If deletion fails
        """
        ...


class KeyringBackend:
    """
    Backend that uses the system keyring for secure secret storage.
    
    This backend uses the 'keyring' library to store secrets in the system's
    secure keyring (e.g., Windows Credential Manager, macOS Keychain, etc.).
    """
    
    def __init__(self):
        """Initialize the keyring backend."""
        try:
            import keyring
            self._keyring = keyring
        except ImportError:
            raise ImportError(
                "The 'keyring' library is required for KeyringBackend. "
                "Install it with: pip install keyring"
            )
    
    def store_secret(self, key_id: str, value: str) -> None:
        """Store a secret in the system keyring."""
        self._keyring.set_password("apikeyper", key_id, value)
    
    def retrieve_secret(self, key_id: str) -> Optional[str]:
        """Retrieve a secret from the system keyring."""
        return self._keyring.get_password("apikeyper", key_id)
    
    def delete_secret(self, key_id: str) -> None:
        """Delete a secret from the system keyring."""
        try:
            self._keyring.delete_password("apikeyper", key_id)
        except Exception:
            # Some keyring backends don't support deletion
            # or the key doesn't exist - this is acceptable
            pass


class InMemoryBackend:
    """
    Backend that stores secrets in memory.
    
    This backend is primarily intended for testing and development.
    Secrets are lost when the process exits.
    """
    
    def __init__(self):
        """Initialize the in-memory backend."""
        self._storage: Dict[str, str] = {}
    
    def store_secret(self, key_id: str, value: str) -> None:
        """Store a secret in memory."""
        self._storage[key_id] = value
    
    def retrieve_secret(self, key_id: str) -> Optional[str]:
        """Retrieve a secret from memory."""
        return self._storage.get(key_id)
    
    def delete_secret(self, key_id: str) -> None:
        """Delete a secret from memory."""
        self._storage.pop(key_id, None)
    
    def clear_all(self) -> None:
        """Clear all stored secrets (useful for testing)."""
        self._storage.clear()