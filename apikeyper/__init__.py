from apikeyper.database import APIKeyDB
try:
    from apikeyper.__about__ import __DEFAULT_DATA_DIR__ as DEFAULT_DATA_DIR
except ImportError:
    # Fallback if dependencies not available
    from pathlib import Path
    DEFAULT_DATA_DIR = Path.home() / ".apikeyper"

from apikeyper.config import Config
from apikeyper.crypto.backends import EncryptionBackend, KeyringBackend, InMemoryBackend, make_key_id
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

    def __init__(self, db_file_path=None, config=None):
        """
        Initializes the APIKeyPER with secure backend storage.

        Args:
            db_file_path (str, optional): The path to the SQLite database file.
            config (Config, optional): Configuration object. If None, creates from environment.
        """
        # Create config if not provided
        if config is None:
            config = Config.from_env()
        
        # Override db_file_path if provided
        if db_file_path is not None:
            config = config.with_backend(config.backend)
            config = Config(
                profile=config.profile,
                namespace=config.namespace,
                db_file_path=Path(db_file_path),
                include_secrets=config.include_secrets,
                backend=config.backend
            )
        
        # Use config db_file_path or fallback to default
        final_db_path = config.db_file_path
        if final_db_path is None:
            final_db_path = Path(DEFAULT_DATA_DIR).joinpath("api_keys.db")

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
        
        # Store the final config
        self.config = config.with_backend(backend)
        self.db = APIKeyDB(final_db_path)

    def add_key(self, service, api_key):
        """
        Add a key to the secure backend and store metadata in database.

        Parameters:
            service (str):
                The service the API key is associated with.

            api_key (str):
                The API key associated with the given service.

        Returns:
            None
        """
        from datetime import datetime
        
        # Generate a unique key ID for the encryption backend
        key_id = make_key_id(
            namespace=self.config.namespace,
            service=service,
            key_name="default",
            profile=self.config.profile
        )
        
        # Store the actual secret in the encryption backend
        self.config.backend.store_secret(key_id, api_key)
        
        # Store only metadata in the database
        added = datetime.now().isoformat()
        key_name = "default"
        status = "active"
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

    def delete_key(self, service):
        """
        Deletes an API key for a specific service from both backend and database.

        Args:
            service (str): The service to delete the key for.

        Returns:
            None
        """
        # Get metadata first to find the key_id
        result = self.db.get_key(service)
        if result:
            key_id = result[3]  # key field is at index 3
            # Delete from encryption backend
            self.config.backend.delete_secret(key_id)
        
        # Delete metadata from database
        self.db.delete_key(service)

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
