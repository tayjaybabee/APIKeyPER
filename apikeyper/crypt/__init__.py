"""
Project: APIKeyPER
Author: Inspyre Softworks - https://inspyre.tech
Created: 5/21/2023 @ 10:24 PM
File:
  Name: __init__.py
  Filepath: apikeyper/crypt
"""
import json
import os
import shutil
from cryptography.fernet import Fernet
from apikeyper.log_engine import LOG_DEVICE as ROOT_LOGGER
from pathlib import Path
from apikeyper.database import DEFAULT_DB_FILEPATH

# Initialize logger
LOGGER = ROOT_LOGGER.get_child()
LOG = LOGGER.logger


class CryptDB:
    """
    Manages an encrypted database using Fernet symmetric encryption.
    """

    DEFAULT_FILEPATH = DEFAULT_DB_FILEPATH

    def __init__(self, file_path=None, encryption_key=None):
        """
        Initialize a new CryptDB instance.

        Args:
            file_path (Path, optional): Path to the file storing the encrypted database.
            encryption_key (EncryptionKey, optional): Encryption key for the database.
        """
        try:
            self.file_path = file_path or self.DEFAULT_FILEPATH

            if not self.file_path.parent.exists():
                self.file_path.parent.mkdir(parents=True, exist_ok=True)

            if encryption_key is None:
                encryption_key = Fernet.generate_key()
            self.encryption_key = encryption_key

            self.cipher_suite = Fernet(self.encryption_key)

            if self.file_path.exists():
                with self.file_path.open("rb") as file:
                    encrypted_data = file.read()
                decrypted_data = self.decrypt(encrypted_data)
                self.data = json.loads(decrypted_data)
            else:
                self.data = {}
                self.save()  # Initialize the file with an empty database
        except Exception as e:
            LOG.error(f"Error initializing CryptDB: {e}")
            raise

    def save(self):
        """
        Save the current database state to the encrypted file.

        Raises:
            IOError: If there is an error saving the file.
        """
        try:
            with open(self.file_path, "wb") as file:
                encrypted_data = self.encrypt(json.dumps(self.data))
                file.write(encrypted_data)
        except IOError as e:
            LOG.error(f"Error saving the database: {e}")
            raise

    def load(self):
        """
        Load the database state from the encrypted file.

        Returns:
            dict: The decrypted and deserialized database data.

        Raises:
            IOError: If there is an error loading the file.
        """
        try:
            with open(self.file_path, "rb") as file:
                encrypted_data = file.read()
            decrypted_data = self.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except IOError as e:
            LOG.error(f"Error loading the database: {e}")
            raise

    def delete(self):
        """
        Delete the encrypted database file.

        Raises:
            OSError: If there is an error deleting the file.
        """
        try:
            os.remove(self.file_path)
        except OSError as e:
            LOG.error(f"Error deleting the database file: {e}")
            raise

    def move(self, new_path):
        """
        Move the encrypted database file to a new location.

        Args:
            new_path (str): The path to the new location.
        """

        shutil.move(self.file_path, new_path)
        self.file_path = new_path

    def export(self, export_path):
        """
        Export the decrypted database data to a JSON or XML file.

        Args:
            export_path (str): The path to the file where the decrypted data will be exported.
        """

        with open(export_path, "w") as file:
            json.dump(self.data, file, indent=4)

    def encrypt(self, message):
        """
        Encrypt a message using the Fernet symmetric encryption.

        Args:
            message (str): The message to be encrypted.

        Returns:
            bytes: The encrypted message.
        """

        return self.cipher_suite.encrypt(message.encode("utf-8"))

    def decrypt(self, encrypted_message):
        """
        Decrypt an encrypted message using the Fernet symmetric encryption.

        Args:
            encrypted_message (bytes): The encrypted message to be decrypted.

        Returns:
            str: The decrypted message.
        """

        return self.cipher_suite.decrypt(encrypted_message).decode("utf-8")


# Usage:
# db = CryptDB("encrypted_path.db")
# data = db.load()
# db.data["new_key"] = "new_value"
# db.save()
# db.export("exported_data.json")


"""
The MIT License (MIT)
Copyright © 2023 Inspyre Softworks - https://inspyre.tech
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""
