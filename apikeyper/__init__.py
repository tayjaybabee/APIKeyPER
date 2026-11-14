from __future__ import annotations

from typing import Optional
from difflib import get_close_matches
from apikeyper.date import Date, DateInput
from apikeyper.database import APIKey, APIKeyDB, DEFAULT_DB_FILEPATH
from apikeyper.log_engine import Loggable, ROOT_LOGGER
from apikeyper.service import Service
from apikeyper.__about__ import __DEFAULT_DATA_DIR__ as DEFAULT_DATA_DIR
from pathlib import Path
import os


"""
This module defines a class, APIKeyPER, as a wrapper for APIKeyDB to manage API keys. 
"""


class APIKeyPER(Loggable):
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
        super().__init__(parent_log_device=ROOT_LOGGER)
        if db_file_path is None:
            db_file_path = DEFAULT_DB_FILEPATH

        if not Path(db_file_path).parent.exists():
            os.makedirs(Path(db_file_path).parent)

        self.db = APIKeyDB(db_file_path)

    def service(self, name: str) -> Service:
        """Bind a service name to this store, including before its first key is added."""
        return Service(name, self)

    def add_service(self, name: str, *, require_key_id: bool | None = None) -> Service:
        """Register a service and optionally set its Key ID requirement."""
        if not isinstance(name, str):
            raise TypeError("Service name must be a string")
        if not name.strip():
            raise ValueError("Service name cannot be blank")
        self.db.add_service(name, require_key_id=require_key_id)
        return self.service(name)

    def get_service(self, name: str) -> Service | list[Service]:
        """Return an exact match, or warn and return ranked fuzzy suggestions."""
        names = self.list_services()
        if name in names:
            return self.service(name)

        query = name.strip().casefold()
        by_folded_name: dict[str, list[str]] = {}
        for stored_name in names:
            by_folded_name.setdefault(stored_name.casefold(), []).append(stored_name)

        matches = []
        if query:
            matches = [candidate for candidate in by_folded_name if query in candidate]
            matches.sort(key=lambda candidate: (candidate != query, candidate))
            remaining = by_folded_name.keys() - set(matches)
            matches.extend(get_close_matches(query, remaining, n=5, cutoff=0.6))

        suggestions = [
            self.service(stored_name)
            for match in matches
            for stored_name in by_folded_name[match]
        ]
        self.log_device.warning(
            "No exact service match. Returning %d fuzzy suggestions.", len(suggestions)
        )
        return suggestions

    def add_key(
        self,
        service: str,
        api_key: str,
        key_name: Optional[str] = None,
        status: str = "active",
        added: DateInput = None,
        *,
        key_id: Optional[str] = None,
    ) -> APIKey:
        """
        Store a key for a service and return its APIKey record.

        Parameters:
            service: The service the API key is associated with.
            api_key: The API key associated with the given service.
            key_name: Optional name of the API key.
            status: The status of the API key. Defaults to 'active'.
            added: A Date, datetime, date, or timestamp string. Defaults to current UTC time.
            key_id: Optional identifier supplied by the credential provider.
        """
        return self.add_service(service).add_key(
            api_key, key_name=key_name, status=status, added=added, key_id=key_id
        )

    def get_key(
        self,
        service: str,
        key_name: Optional[str] = None,
        only_active: bool = True,
    ) -> Optional[APIKey]:
        """
        Retrieves an API key for a specific service from the database.

        Parameters:
            service: The service to retrieve the key for.
            key_name: The specific key name to retrieve. If None, gets the most recent key.
            only_active: Whether to only return active keys. Defaults to True.

        Returns:
            An APIKey dataclass instance representing the API key data, or None if not found.
        """
        return self.db.get_key(service, key_name, only_active)

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

    def list_keys_for_service(self, service: str) -> list[tuple]:
        """
        Lists all API key records for a specific service.

        Parameters:
            service: The service to list keys for.

        Returns:
            A list of tuples representing the API keys for the service.
        """
        return self.db.list_keys_for_service(service)

    def revoke_key(self, service: str, key_name: str) -> None:
        """
        Revokes an API key for a specific service, marking it inactive
        without deleting it.

        Parameters:
            service: The service the key belongs to.
            key_name: The specific key name to revoke.
        """
        self.db.revoke_key(service, key_name)
