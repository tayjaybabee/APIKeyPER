from apikeyper.database import APIKeyDB
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

    def __init__(self, db_file_path=None):
        """
        Initializes the APIKeyPER with a APIKeyDB instance connected to the specified SQLite database file.

        Args:
            db_file_path (str): The path to the SQLite database file.
        """
        if db_file_path is None:
            db_file_path = Path(DEFAULT_DATA_DIR).joinpath("api_keys.db")

        if not db_file_path.parent.exists():
            os.makedirs(db_file_path.parent)

        self.db = APIKeyDB(db_file_path)

    def add_key(self, service, api_key):
        """
        Add a key to database associated with a service.

        Parameters:
            service (str):
                The service the API key is associated with.

            api_key (str):
                The API key associated with the given service.

        Returns:
            None
        """
        from datetime import datetime
        added = datetime.now().isoformat()
        # Use the service name as the key_name by default
        key_name = "default"
        status = "active"
        self.db.add_key(service, key_name, api_key, added, status)

    def get_key(self, service):
        """
        Retrieves an API key for a specific service from the database.

        Args:
            service (str): The service to retrieve the key for.

        Returns:
            str: The retrieved API key.
        """
        return self.db.get_key(service)

    def delete_key(self, service):
        """
        Deletes an API key for a specific service from the database.

        Args:
            service (str): The service to delete the key for.

        Returns:
            None
        """
        self.db.delete_key(service)

    def list_services(self):
        """
        Lists all unique services in the database.

        Returns:
            list: A list of all unique services.
        """
        return self.db.list_services()
