"""
Configuration module for APIKeyPER.

This module provides a centralized configuration system using a dataclass
that can read from environment variables and provide defaults.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from apikeyper.crypto.backends import EncryptionBackend

try:
    from apikeyper.__about__ import __DEFAULT_DATA_DIR__
except ImportError:
    # Fallback if dependencies not available
    from pathlib import Path
    __DEFAULT_DATA_DIR__ = Path.home() / ".apikeyper"


@dataclass(frozen=True)
class Config:
    """
    Configuration object for APIKeyPER.
    
    Args:
        profile: Optional profile name for multi-profile support
        namespace: Namespace for keyring storage (default: 'apikeyper')
        db_file_path: Path to the SQLite database file
        include_secrets: Whether to include secrets in exports (default: False)
        backend: Encryption backend instance (default: None, will use KeyringBackend)
    """
    profile: Optional[str] = None
    namespace: str = "apikeyper"
    db_file_path: Optional[Path] = None
    include_secrets: bool = False
    backend: Optional["EncryptionBackend"] = None

    @classmethod
    def from_env(cls) -> "Config":
        """
        Create a Config instance from environment variables.
        
        Environment variables:
        - APIKEYPER_PROFILE: Profile name
        - APIKEYPER_NAMESPACE: Namespace for keyring (default: 'apikeyper')
        - APIKEYPER_DB_PATH: Database file path
        - APIKEYPER_INCLUDE_SECRETS: Include secrets in exports ('true'/'false')
        
        Returns:
            Config instance with values from environment or defaults
        """
        profile = os.getenv("APIKEYPER_PROFILE")
        namespace = os.getenv("APIKEYPER_NAMESPACE", "apikeyper")
        
        db_path_str = os.getenv("APIKEYPER_DB_PATH")
        if db_path_str:
            db_file_path = Path(db_path_str)
        else:
            db_file_path = __DEFAULT_DATA_DIR__ / "apikeyper.db"
        
        include_secrets_str = os.getenv("APIKEYPER_INCLUDE_SECRETS", "false").lower()
        include_secrets = include_secrets_str in ("true", "1", "yes", "on")
        
        return cls(
            profile=profile,
            namespace=namespace,
            db_file_path=db_file_path,
            include_secrets=include_secrets,
            backend=None  # Will be set by APIKeyPER
        )

    def with_backend(self, backend: "EncryptionBackend") -> "Config":
        """
        Create a new Config instance with the specified backend.
        
        Args:
            backend: The encryption backend to use
            
        Returns:
            New Config instance with the backend set
        """
        from dataclasses import replace
        return replace(self, backend=backend)