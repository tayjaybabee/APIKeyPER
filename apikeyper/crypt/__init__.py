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
import importlib
from cryptography.fernet import Fernet


from apikeyper.log_engine import LOG_DEVICE as ROOT_LOGGER

LOGGER = ROOT_LOGGER.get_child()
LOG = LOGGER.logger
LOG.debug(f'Starting {LOG.name}')


from apikeyper.crypt.encryption_key import (
    EncryptionKey,
)  # Assuming EncryptionKey is stored in this module


class CryptDB:
    """
    A class that represents an encrypted database. This database supports encryption using Fernet symmetric encryption.
    """

    def __init__(self, file_path=None, encryption_key=None):
        """
        Initialize a new CryptDB instance.

        Args:
            file_path (str, optional): The path to the file that stores the encrypted database.
                Defaults to None, which will use a default path based on appdirs.
            encryption_key (EncryptionKey, optional): The encryption key used for encrypting and decrypting the database.
                Defaults to None, which will generate a new key.
        """

        if file_path is None:
            # Set a default path using appdirs or any other preferred method
            # For this example, we'll simply set it to 'default_path.db'
            file_path = "default_path.db"

        self.file_path = file_path

        # If no encryption key is provided, generate one and store it in a file by default
        if encryption_key is None:
            encryption_key = EncryptionKey("file")

        self.encryption_key = encryption_key

        self.cipher_suite = Fernet(self.encryption_key.key)

        # If the encrypted DB file exists, load and decrypt it
        if os.path.exists(self.file_path):
            with open(self.file_path, "rb") as file:
                encrypted_data = file.read()
            decrypted_data = self.decrypt(encrypted_data)
            self.data = json.loads(decrypted_data)
        else:
            self.data = {}

    def save(self):
        """
        Save the current database state to the encrypted file.
        """

        with open(self.file_path, "wb") as file:
            encrypted_data = self.encrypt(json.dumps(self.data))
            file.write(encrypted_data)

    def load(self):
        """
        Load the database state from the encrypted file.

        Returns:
            dict: The decrypted and deserialized database data.
        """

        with open(self.file_path, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = self.decrypt(encrypted_data)
        return json.loads(decrypted_data)

    def delete(self):
        """
        Delete the encrypted database file.
        """

        os.remove(self.file_path)

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
