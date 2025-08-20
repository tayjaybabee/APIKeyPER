import sqlite3
import json
import xml.etree.ElementTree as ET
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

    def __init__(self, db_file_path=None):
        """
        Initializes the APIKeyDB with a connection to the specified SQLite database file.

        Args:
            db_file_path (str): The path to the SQLite database file.
        """
        if db_file_path is None:
            db_file_path = DEFAULT_DB_FILEPATH

        print(db_file_path)

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

    def add_key(self, service, key_name, key, added, status, revoked_on=None):
        """
        Adds a new API key to the database.

        Args:
            service (str): The service for the API key.
            key_name (str): The name of the API key.
            key (str): The API key.
            added (str): The date the key was added.
            status (str): The status of the API key.
            revoked_on (str, optional): The date the key was revoked. Defaults to None.
        """
        self.cursor.execute(
            "INSERT INTO apikeys VALUES (?,?,?,?,?,?)",
            (service, key_name, added, key, status, revoked_on),
        )
        self.conn.commit()

    def list_keys_for_service(self, service):
        """
        Lists all API keys for a specific service.

        Args:
            service (str): The service to list keys for.

        Returns:
            list: A list of tuples representing the API keys for the service.
        """
        self.cursor.execute("SELECT * FROM apikeys WHERE service=?", (service,))
        return self.cursor.fetchall()

    def list_services(self):
        """
        Lists all unique services in the database.

        Returns:
            list: A list of all unique services.
        """
        self.cursor.execute("SELECT DISTINCT service FROM apikeys")
        return [service[0] for service in self.cursor.fetchall()]

    def get_key(self, service):
        """
        Retrieves the first active API key for a specific service from the database.

        Args:
            service (str): The service to retrieve the key for.

        Returns:
            tuple or None: A tuple representing the API key row (service, key_name, added, key, status, revoked_on)
                          or None if no key is found.
        """
        self.cursor.execute(
            "SELECT * FROM apikeys WHERE service=? AND status='active' ORDER BY added DESC LIMIT 1", 
            (service,)
        )
        return self.cursor.fetchone()

    def delete_key(self, service):
        """
        Deletes all API keys for a specific service from the database.

        Args:
            service (str): The service to delete keys for.

        Returns:
            None
        """
        self.cursor.execute("DELETE FROM apikeys WHERE service=?", (service,))
        self.conn.commit()

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
            keys = self.list_keys_for_service(service)
            data[service] = [
                {
                    "key_name": key[1],
                    "added": key[2],
                    "key": "***REDACTED***" if redact_secrets else key[3],
                    "status": key[4],
                    "revoked_on": key[5],
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
        root = ET.Element("services")

        all_services = self.list_services()
        for service in all_services:
            service_element = ET.SubElement(root, "service", name=service)
            keys = self.list_keys_for_service(service)
            for key in keys:
                key_element = ET.SubElement(service_element, "key")
                ET.SubElement(key_element, "key_name").text = key[1]
                ET.SubElement(key_element, "added").text = key[2]
                ET.SubElement(key_element, "key_value").text = "***REDACTED***" if redact_secrets else key[3]
                ET.SubElement(key_element, "status").text = key[4]
                ET.SubElement(key_element, "revoked_on").text = key[5]

        tree = ET.ElementTree(root)
        tree.write(export_path)
