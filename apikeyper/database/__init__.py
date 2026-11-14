from __future__ import annotations

import sqlite3
import json
import xml.etree.ElementTree as ElementTree
from typing import Optional
from dataclasses import dataclass, field
from apikeyper.__about__ import __DEFAULT_DATA_DIR__
from apikeyper.date import Date, DateInput
from apikeyper.log_engine import Loggable, ROOT_LOGGER

__all__ = ["APIKey", "APIKeyDB", "DEFAULT_DB_FILEPATH", "Loggable"]


LOGGER = ROOT_LOGGER.get_child("database")

DEFAULT_DB_FILEPATH = __DEFAULT_DATA_DIR__.joinpath('apikeyper.db')
_KEY_COLUMNS = "service, key_name, added, key, status, revoked_on"
_KEY_DATE_FLAGS = "added_defaulted, revoked_defaulted"

"""
This module defines a class, APIKeyDB, for managing API keys stored in a SQLite database.
"""


# The dataclass decorator generates the constructor.
# noinspection PyClassHasNoInit
@dataclass
class APIKey(Loggable):
    """A stored API key and its metadata."""

    service: str
    key_name: str
    added: Date
    key: str = field(repr=False)
    status: str
    revoked_on: Optional[Date]
    key_id: Optional[str] = field(default=None, repr=False)

    def __post_init__(self):
        super().__init__(parent_log_device=LOGGER)
        if not isinstance(self.added, Date):
            self.added = Date(self.added)
        if isinstance(self.revoked_on, str) and not self.revoked_on.strip():
            self.revoked_on = None
        if self.revoked_on is not None and not isinstance(self.revoked_on, Date):
            self.revoked_on = Date(self.revoked_on)

    def _values(self) -> tuple[str, str, Date, str, str, Optional[Date]]:
        return (
            self.service,
            self.key_name,
            self.added,
            self.key,
            self.status,
            self.revoked_on,
        )

    def __iter__(self):
        return iter(self._values())

    def __getitem__(self, index: int):
        return self._values()[index]

    def __len__(self) -> int:
        return len(self._values())


class APIKeyDB(Loggable):
    """
    This class provides methods to interact with a SQLite database of API keys. It also supports
    exporting the database contents to JSON and XML formats.

    Attributes:
        db_file_path (str): The path to the SQLite database file.
        conn (sqlite3.Connection): The connection to the SQLite database.
        cursor (sqlite3.Cursor): The cursor for executing SQL statements.
    """

    def __init__(self, db_file_path: Optional[str] = None) -> None:
        """
        Initializes the APIKeyDB with a connection to the specified SQLite database file.

        Parameters:
            db_file_path: The path to the SQLite database file. If None, uses the default path.
        """
        super().__init__(parent_log_device=LOGGER)
        if db_file_path is None:
            db_file_path = DEFAULT_DB_FILEPATH

        self.db_file_path = db_file_path
        self.conn = sqlite3.connect(db_file_path)
        self.cursor = self.conn.cursor()
        with self.conn:
            self.cursor.execute("BEGIN IMMEDIATE")
            self._initialize_schema()

    def _initialize_schema(self) -> None:
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS services (name TEXT PRIMARY KEY NOT NULL, "
            "require_key_id INTEGER NOT NULL DEFAULT 0)"
        )
        service_columns = {row[1] for row in self.cursor.execute("PRAGMA table_info(services)")}
        if "require_key_id" not in service_columns:
            self.cursor.execute(
                "ALTER TABLE services ADD COLUMN require_key_id INTEGER NOT NULL DEFAULT 0"
            )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS apikeys (
                                    service text,
                                    key_name text,
                                    added text,
                                    key text,
                                    status text,
                                    revoked_on text,
                                    key_id text,
                                    added_defaulted integer NOT NULL DEFAULT 0,
                                    revoked_defaulted integer NOT NULL DEFAULT 0,
                                    PRIMARY KEY (service, key_name))"""
        )
        columns = {row[1] for row in self.cursor.execute("PRAGMA table_info(apikeys)")}
        if "key_id" not in columns:
            self.cursor.execute("ALTER TABLE apikeys ADD COLUMN key_id text")
        for column in ("added_defaulted", "revoked_defaulted"):
            if column not in columns:
                self.cursor.execute(
                    f"ALTER TABLE apikeys ADD COLUMN {column} integer NOT NULL DEFAULT 0"
                )

    def add_key(
        self,
        service: str,
        key_name: str,
        key: str,
        added: DateInput,
        status: str,
        revoked_on: DateInput = None,
        *,
        key_id: Optional[str] = None,
    ) -> APIKey:
        """
        Adds a new API key to the database using INSERT OR REPLACE to update existing entries.

        Parameters:
            service:
                The service for the API key.

            key_name:
                The name of the API key.

            key:
                The API key.

            added:
                The date the key was added (ISO8601 format).

            status:
                The status of the API key.

            revoked_on:
                The date the key was revoked. Defaults to None.

            key_id:
                The optional identifier supplied by the credential provider.

        Returns:
            The saved APIKey record.
        """
        added_date = Date(added)
        revoked_date = None
        if revoked_on is not None and not (isinstance(revoked_on, str) and not revoked_on.strip()):
            revoked_date = Date(revoked_on)
        with self.conn:
            self.cursor.execute("BEGIN IMMEDIATE")
            if self.requires_key_id(service) and (key_id is None or not key_id.strip()):
                raise ValueError("This service requires a non-blank key_id")
            self.cursor.execute(
                f"INSERT OR REPLACE INTO apikeys ({_KEY_COLUMNS}, {_KEY_DATE_FLAGS}, key_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    service, key_name, added_date.isoformat(), key, status,
                    revoked_date.isoformat() if revoked_date else None,
                    added_date.was_defaulted,
                    revoked_date.was_defaulted if revoked_date else False,
                    key_id,
                ),
            )
        return APIKey(service, key_name, added_date, key, status, revoked_date, key_id)

    def delete_service(self, service: str) -> None:
        """
        Deletes all API keys for a specific service from the database.

        Parameters:
            service:
                The service to delete keys for.

        """
        self.delete_key(service)

    def get_key(
        self,
        service: str,
        key_name: Optional[str] = None,
        only_active: bool = True,
    ) -> Optional[APIKey]:
        """
        Retrieves an API key for a specific service from the database.

        Parameters:
            service:
                The service to retrieve the key for.

            key_name:
                The specific key name to retrieve. If None, gets the most recent key.

            only_active:
                Whether to only return active keys. Defaults to True.

        Returns:
            An APIKey instance if found, None otherwise.
        """
        query = f"SELECT {_KEY_COLUMNS}, {_KEY_DATE_FLAGS}, key_id FROM apikeys WHERE service=?"
        params = [service]

        if key_name is not None:
            query += " AND key_name=?"
            params.append(key_name)

        if only_active:
            query += " AND status='active'"

        records = (
            self._key_record(row) for row in self.cursor.execute(query, params)
        )
        return max(records, key=lambda record: record.added, default=None)

    @staticmethod
    def _key_record(row: tuple) -> APIKey:
        service, name, added, key, status, revoked, added_defaulted, revoked_defaulted, key_id = row
        return APIKey(
            service, name, Date(added, was_defaulted=bool(added_defaulted)), key, status,
            Date(revoked, was_defaulted=bool(revoked_defaulted))
            if revoked and revoked.strip() else None,
            key_id,
        )

    def list_key_records(self, service: str) -> list[APIKey]:
        rows = self.cursor.execute(
            f"SELECT {_KEY_COLUMNS}, {_KEY_DATE_FLAGS}, key_id FROM apikeys WHERE service=?",
            (service,),
        )
        return [self._key_record(row) for row in rows]

    def delete_key(self, service: str, key_name: Optional[str] = None) -> None:
        """
        Deletes an API key for a specific service from the database.

        Parameters:
            service: The service to delete the key for.
            key_name: The specific key name to delete. If None, deletes all keys for the service.
        """
        if key_name is not None:
            self.cursor.execute("DELETE FROM apikeys WHERE service=? AND key_name=?", (service, key_name))
        else:
            self.cursor.execute("DELETE FROM apikeys WHERE service=?", (service,))
        self.conn.commit()

    def list_keys_for_service(self, service: str) -> list[tuple]:
        """
        Lists all API keys for a specific service.

        Parameters:
            service: The service to list keys for.

        Returns:
            A list of tuples representing the API keys for the service.
        """
        return self._list_key_rows(service, include_key_id=False)

    def _list_key_rows(self, service: str, *, include_key_id: bool = True) -> list[tuple]:
        columns = f"{_KEY_COLUMNS}, key_id" if include_key_id else _KEY_COLUMNS
        self.cursor.execute(f"SELECT {columns} FROM apikeys WHERE service=?", (service,))
        return self.cursor.fetchall()

    def list_services(self) -> list[str]:
        """
        Lists all unique services in the database.

        Returns:
            A list of all unique services.
        """
        self.cursor.execute("SELECT name FROM services UNION SELECT service FROM apikeys")
        return [service[0] for service in self.cursor.fetchall()]

    def requires_key_id(self, name: str) -> bool:
        row = self.cursor.execute(
            "SELECT require_key_id FROM services WHERE name=?", (name,)
        ).fetchone()
        return bool(row and row[0])

    def add_service(self, name: str, *, require_key_id: bool | None = None) -> None:
        """Register a service and update its policy when explicitly supplied."""
        if require_key_id is not None and not isinstance(require_key_id, bool):
            raise TypeError("require_key_id must be a bool")
        with self.conn:
            if require_key_id is None:
                self.cursor.execute(
                    "INSERT INTO services (name) VALUES (?) ON CONFLICT(name) DO NOTHING",
                    (name,),
                )
            else:
                self.cursor.execute(
                    "INSERT INTO services (name, require_key_id) VALUES (?, ?) "
                    "ON CONFLICT(name) DO UPDATE SET require_key_id=excluded.require_key_id",
                    (name, require_key_id),
                )

    def close(self):
        """
        Closes the connection to the SQLite database.
        """
        self.conn.close()
        
    def export_db_as_json(self, export_path, redact_secrets=True):
        """
        Exports the contents of the database to a JSON file.

        Args:
            export_path (str): The path to the output JSON file.
            redact_secrets (bool): Whether to redact API key values. Defaults to True for security.

        """

        all_services = self.list_services()
        data = {}
        for service in all_services:
            keys = self._list_key_rows(service)
            data[service] = [
                {
                    "key_name": key[1],
                    "added": key[2],
                    "key": "***REDACTED***" if redact_secrets else key[3],
                    "status": key[4],
                    "revoked_on": key[5],
                    **({"key_id": "***REDACTED***" if redact_secrets else key[6]}
                       if key[6] is not None else {}),
                }
                for key in keys
            ]

        with open(export_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def export_db_as_xml(self, export_path, redact_secrets=True):
        """
        Exports the contents of the database to an XML file.

        Args:
            export_path (str): The path to the output XML file.
            redact_secrets (bool): Whether to redact API key values. Defaults to True for security.

        """
        root = ElementTree.Element("services")

        all_services = self.list_services()
        for service in all_services:
            service_element = ElementTree.SubElement(root, "service", name=service)
            keys = self._list_key_rows(service)
            for key in keys:
                key_element = ElementTree.SubElement(service_element, "key")
                ElementTree.SubElement(key_element, "key_name").text = key[1]
                ElementTree.SubElement(key_element, "added").text = key[2]
                ElementTree.SubElement(key_element, "key_value").text = "***REDACTED***" if redact_secrets else key[3]
                ElementTree.SubElement(key_element, "status").text = key[4]
                ElementTree.SubElement(key_element, "revoked_on").text = key[5]
                if key[6] is not None:
                    ElementTree.SubElement(key_element, "key_id").text = (
                        "***REDACTED***" if redact_secrets else key[6]
                    )

        tree = ElementTree.ElementTree(root)
        tree.write(export_path)

    def revoke_key(
            self,
            service: str,
            key_name: str,
            revoked_on: DateInput = None
    ) -> None:
        matching_key = self.get_key(service, key_name, only_active=False)
        if not matching_key:
            raise ValueError(f"Key {key_name} not found for service {service}")
        elif matching_key.status == 'revoked':
            raise ValueError(
                f"Key {key_name} for service {service} is already revoked. Revoked on: {matching_key.revoked_on}"
            )

        revoked_date = Date(revoked_on)
        self.cursor.execute(
            "UPDATE apikeys SET status='revoked', revoked_on=?, revoked_defaulted=? "
            "WHERE service=? AND key_name=?",
            (revoked_date.isoformat(), revoked_date.was_defaulted, service, key_name),
        )

        self.conn.commit()
