from __future__ import annotations

from typing import Optional
from datetime import datetime
from apikeyper.database import APIKeyDB, DEFAULT_DB_FILEPATH
from apikeyper.__about__ import __DEFAULT_DATA_DIR__ as DEFAULT_DATA_DIR
from pathlib import Path
import os


"""
This module defines a class, APIKeyPER, as a wrapper for APIKeyDB to manage API keys. 
"""


class APIKeyPER:
    """
    This class provides a higher-level interface for managing API keys stored in a SQLite database.

    Attributes:
        db (APIKeyDB): An instance of the APIKeyDB class for managing API keys.
    """

    def __init__(self, db_file_path: Optional[str] = None) -> None:
        """
        Initializes the APIKeyPER with a APIKeyDB instance connected to the specified SQLite database file.

        Parameters:
            db_file_path: The path to the SQLite database file. If None, uses the unified default path.
        """
        if db_file_path is None:
            db_file_path = DEFAULT_DB_FILEPATH

        if not Path(db_file_path).parent.exists():
            os.makedirs(Path(db_file_path).parent)

        self.db = APIKeyDB(db_file_path)

    def add_key(self, service: str, api_key: str, key_name: str = 'default', status: str = 'active', added: Optional[str] = None) -> None:
        """
        Add a key to database associated with a service.

        Parameters:
            service: The service the API key is associated with.
            api_key: The API key associated with the given service.
            key_name: The name of the API key. Defaults to 'default'.
            status: The status of the API key. Defaults to 'active'.
            added: The date the key was added (ISO8601 format). If None, current UTC time is used.
        """
        if added is None:
            added = datetime.utcnow().isoformat()
        self.db.add_key(service, key_name, api_key, added, status)

    def get_key(self, service: str) -> Optional[str]:
        """
        Retrieves an API key for a specific service from the database.

        Parameters:
            service: The service to retrieve the key for.

        Returns:
            The retrieved API key, or None if not found.
        """
        return self.db.get_key(service)

    def delete_key(self, service: str, key_name: Optional[str] = None) -> None:
        """
        Deletes an API key for a specific service from the database.

        Parameters:
            service: The service to delete the key for.
            key_name: The specific key name to delete. If None, deletes all keys for the service.
        """
        self.db.delete_key(service, key_name)

    def list_services(self) -> list[str]:
        """
        Lists all unique services in the database.

        Returns:
            A list of all unique services.
        """
        return self.db.list_services()
