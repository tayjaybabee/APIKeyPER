from __future__ import annotations

from typing import Optional
from datetime import datetime
from apikeyper.database import APIKeyDB
try:
    from apikeyper.database import DEFAULT_DB_FILEPATH
except ImportError:
    # Fallback for backward compatibility
    DEFAULT_DB_FILEPATH = None

try:
    from apikeyper.__about__ import __DEFAULT_DATA_DIR__ as DEFAULT_DATA_DIR
except ImportError:
    # Fallback if dependencies not available
    from pathlib import Path
    DEFAULT_DATA_DIR = Path.home() / ".apikeyper"

from pathlib import Path
import os


"""
This module defines a class, APIKeyPER, as a wrapper for APIKeyDB to manage API keys. 
"""


class APIKeyPER:
    """
    This class provides a higher-level interface for managing API keys with secure storage.

    The API keys are stored using an encryption backend (system keyring by default),
    while only metadata is stored in the SQLite database.

    Attributes:
        db (APIKeyDB): An instance of the APIKeyDB class for managing metadata.
        config (Config): Configuration object with settings and backend.
    """

    def __init__(self, db_file_path: Optional[str] = None, config=None) -> None:
        """
        Initializes the APIKeyPER with secure backend storage.

        Args:
            db_file_path (str, optional): The path to the SQLite database file.
            config (Config, optional): Configuration object. If None, creates from environment.
        """
        # Import here to avoid circular imports
        from apikeyper.config import Config
        from apikeyper.crypto.backends import KeyringBackend, InMemoryBackend, make_key_id
        
        # Create config if not provided
        if config is None:
            config = Config.from_env()
        
        # Determine the database file path
        if db_file_path is not None:
            # Use the explicitly provided path
            final_db_path = Path(db_file_path)
        elif config.db_file_path is not None:
            # Use the config's path
            final_db_path = config.db_file_path
        elif DEFAULT_DB_FILEPATH is not None:
            # Use the legacy default path for backward compatibility
            final_db_path = Path(DEFAULT_DB_FILEPATH)
        else:
            # Fallback to the new default path
            final_db_path = Path(DEFAULT_DATA_DIR).joinpath("api_keys.db")

        # Update config with the final db path
        if db_file_path is not None:
            config = Config(
                profile=config.profile,
                namespace=config.namespace,
                db_file_path=final_db_path,
                include_secrets=config.include_secrets,
                backend=config.backend
            )
        else:
            config = config.with_db_path(final_db_path)

        # Create directory if it doesn't exist
        if not final_db_path.parent.exists():
            os.makedirs(final_db_path.parent)

        # Initialize the backend if not provided
        backend = config.backend
        if backend is None:
            try:
                backend = KeyringBackend()
            except ImportError:
                # Fallback to in-memory backend if keyring is not available
                backend = InMemoryBackend()
        
        # Store the final config and make_key_id available
        self.config = config.with_backend(backend)
        self.db = APIKeyDB(final_db_path)
        self._make_key_id = make_key_id

    def add_key(self, service, api_key, key_name="default", status="active", added=None):
        """
        Add a key to the secure backend and store metadata in database.

        Parameters:
            service (str):
                The service the API key is associated with.

            api_key (str):
                The API key associated with the given service.
                
            key_name (str, optional):
                The name of the API key. Defaults to 'default'.
                
            status (str, optional):
                The status of the API key. Defaults to 'active'.
                
            added (str, optional):
                The date the key was added (ISO8601 format). If None, current time is used.

        Returns:
            None
        """
        from datetime import datetime
        import uuid
        
        # Generate timestamp if not provided
        if added is None:
            added = datetime.now().isoformat()
        
        # Generate unique key name if using default
        if key_name == "default":
            key_name = f"{service}_key_{uuid.uuid4().hex[:8]}"
        
        # Generate a unique key ID for the encryption backend
        key_id = self._make_key_id(
            namespace=self.config.namespace,
            service=service,
            key_name=key_name,
            profile=self.config.profile
        )
        
        # Store the actual secret in the encryption backend
        self.config.backend.store_secret(key_id, api_key)
        
        # Store only metadata in the database
        # Store the key_id as a reference instead of the actual key
        self.db.add_key(service, key_name, key_id, added, status)

    def get_key(self, service):
        """
        Retrieves an API key for a specific service from the secure backend.

        Args:
            service (str): The service to retrieve the key for.

        Returns:
            str or None: The retrieved API key, or None if not found.
        """
        # Get metadata from database
        result = self.db.get_key(service)
        if not result:
            return None
        
        # Extract the key_id from the metadata (stored in the 'key' field)
        key_id = result[3]  # key field is at index 3
        
        # Retrieve the actual secret from the encryption backend
        return self.config.backend.retrieve_secret(key_id)

    def delete_key(self, service, key_name=None):
        """
        Deletes an API key for a specific service from both backend and database.

        Args:
            service (str): The service to delete the key for.
            key_name (str, optional): The specific key name to delete. If None, deletes all keys for the service.

        Returns:
            None
        """
        if key_name is None:
            # Get all keys for the service and delete them from backend
            all_keys = self.db.get_all_keys_for_service(service)
            for key_record in all_keys:
                key_id = key_record[3]  # key field is at index 3
                # Delete from encryption backend
                self.config.backend.delete_secret(key_id)
        else:
            # Get specific key metadata to find the key_id
            result = self.db.get_key_by_name(service, key_name)
            if result:
                key_id = result[3]  # key field is at index 3
                # Delete from encryption backend
                self.config.backend.delete_secret(key_id)
        
        # Delete metadata from database
        self.db.delete_key(service, key_name)

    def list_services(self):
        """
        Lists all unique services in the database.

        Returns:
            list: A list of all unique services.
        """
        return self.db.list_services()

    def export_db_as_json(self, export_path):
        """
        Exports the contents of the database to a JSON file.
        
        Secrets are redacted by default unless config.include_secrets is True.

        Args:
            export_path (str): The path to the output JSON file.
        """
        self.db.export_db_as_json(export_path, include_secrets=self.config.include_secrets)

    def export_db_as_xml(self, export_path):
        """
        Exports the contents of the database to an XML file.
        
        Secrets are redacted by default unless config.include_secrets is True.

        Args:
            export_path (str): The path to the output XML file.
        """
        self.db.export_db_as_xml(export_path, include_secrets=self.config.include_secrets)
