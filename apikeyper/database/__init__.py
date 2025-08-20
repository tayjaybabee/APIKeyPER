from __future__ import annotations

import sqlite3
import json
import xml.etree.ElementTree as ET
from typing import Optional
from apikeyper.__about__ import __DEFAULT_DATA_DIR__
from apikeyper.log_engine import Loggable, LOG_DEVICE as ROOT_LOGGER


logger = ROOT_LOGGER.get_child()
log = logger.logger

DEFAULT_DB_FILEPATH = __DEFAULT_DATA_DIR__.joinpath('apikeyper.db')
log.debug(f'Default DB filepath is {DEFAULT_DB_FILEPATH}')

"""
This module defines a class, APIKeyDB, for managing API keys stored in a SQLite database.
"""


class APIKeyDB:
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
        if db_file_path is None:
            db_file_path = DEFAULT_DB_FILEPATH

        self.db_file_path = db_file_path
        self.conn = sqlite3.connect(db_file_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS apikeys (
                                    service text,
                                    key_name text,
                                    added text,
                                    key text,
                                    status text,
                                    revoked_on text,
                                    PRIMARY KEY (service, key_name))"""
        )

    def add_key(self, service: str, key_name: str, key: str, added: str, status: str, revoked_on: Optional[str] = None) -> None:
        """
        Adds a new API key to the database using INSERT OR REPLACE to update existing entries.

        Parameters:
            service: The service for the API key.
            key_name: The name of the API key.
            key: The API key.
            added: The date the key was added (ISO8601 format).
            status: The status of the API key.
            revoked_on: The date the key was revoked. Defaults to None.
        """
        self.cursor.execute(
            "INSERT OR REPLACE INTO apikeys (service, key_name, added, key, status, revoked_on) VALUES (?,?,?,?,?,?)",
            (service, key_name, added, key, status, revoked_on),
        )
        self.conn.commit()

    def get_key(self, service: str, key_name: Optional[str] = None, only_active: bool = True) -> Optional[str]:
        """
        Retrieves an API key for a specific service from the database.

        Parameters:
            service: The service to retrieve the key for.
            key_name: The specific key name to retrieve. If None, gets the most recent key.
            only_active: Whether to only return active keys. Defaults to True.

        Returns:
            The API key string if found, None otherwise.
        """
        if key_name is not None:
            # Get specific key by name
            query = "SELECT key FROM apikeys WHERE service=? AND key_name=?"
            params = [service, key_name]
            if only_active:
                query += " AND status='active'"
        else:
            # Get most recent key for service
            query = "SELECT key FROM apikeys WHERE service=?"
            params = [service]
            if only_active:
                query += " AND status='active'"
            query += " ORDER BY added DESC LIMIT 1"
        
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()
        return result[0] if result else None

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
        self.cursor.execute("SELECT * FROM apikeys WHERE service=?", (service,))
        return self.cursor.fetchall()

    def list_services(self) -> list[str]:
        """
        Lists all unique services in the database.

        Returns:
            A list of all unique services.
        """
        self.cursor.execute("SELECT DISTINCT service FROM apikeys")
        return [service[0] for service in self.cursor.fetchall()]

    def close(self) -> None:
        """
        Closes the connection to the SQLite database.
        """
        self.conn.close()

    def export_db_as_json(self, export_path: str) -> None:
        """
        Exports the contents of the database to a JSON file.

        Parameters:
            export_path: The path to the output JSON file.
        """

        all_services = self.list_services()
        data = {}
        for service in all_services:
            keys = self.list_keys_for_service(service)
            data[service] = [
                {
                    "key_name": key[1],
                    "added": key[2],
                    "key": key[3],
                    "status": key[4],
                    "revoked_on": key[5],
                }
                for key in keys
            ]

        with open(export_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def export_db_as_xml(self, export_path: str) -> None:
        """
        Exports the contents of the database to an XML file.

        Parameters:
            export_path: The path to the output XML file.
        """
        root = ET.Element("services")

        all_services = self.list_services()
        for service in all_services:
            service_element = ET.SubElement(root, "service", name=service)
            keys = self.list_keys_for_service(service)
            for key in keys:
                key_element = ET.SubElement(service_element, "key")
                ET.SubElement(key_element, "key_name").text = key[1]
                ET.SubElement(key_element, "added").text = key[2]
                ET.SubElement(key_element, "key_value").text = key[3]
                ET.SubElement(key_element, "status").text = key[4]
                ET.SubElement(key_element, "revoked_on").text = key[5]

        tree = ET.ElementTree(root)
        tree.write(export_path)
