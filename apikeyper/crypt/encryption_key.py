#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: encryption_key
Author: tayja
Date: 8/3/2023
Description: 
"""
import importlib
import os

from cryptography.fernet import Fernet
from apikeyper.__about__ import __DEFAULT_DATA_DIR__ as DEFAULT_DATA_DIR


DEFAULT_KEY_FILEPATH = os.path.join(DEFAULT_DATA_DIR, 'key.pem')


def get_key_from_file(key_file):
    """
    Retrieve the encryption key from a file. If the file doesn't exist, generate a new key and save it to the file.

    Args:
        key_file (str): Path to the file storing the encryption key.

    Returns:
        bytes: The encryption key.
    """

    if os.path.exists(key_file):
        with open(key_file, "rb") as key_f:
            return key_f.read()
    else:
        # Generate key and save it to file
        key = Fernet.generate_key()
        with open(key_file, "wb") as key_f:
            key_f.write(key)
        return key


def get_key_from_keyring():
    """
    Retrieve the encryption key from the system's keyring. If it's not found, generate a new key and save it.

    Returns:
        bytes: The encryption key.
    """

    keyring = importlib.import_module("keyring")

    if key := keyring.get_password("cryptdb", "encryption_key"):
        return key.encode("utf-8")
    # Generate key and save it to keyring
    key = Fernet.generate_key()
    keyring.set_password("cryptdb", "encryption_key", key.decode("utf-8"))
    return key


def get_key_from_sftp(sftp_details):
    """
    Retrieve the encryption key from an SFTP server.

    Args:
        sftp_details (dict): A dictionary containing the connection details for the SFTP server.

    Returns:
        bytes: The encryption key.
    """

    paramiko = importlib.import_module("paramiko")

    transport = paramiko.Transport((sftp_details["host"], sftp_details["port"]))
    transport.connect(
        username=sftp_details["username"], password=sftp_details["password"]
    )
    sftp = transport.open_sftp()

    with sftp.file(sftp_details["remote_key_path"], "r") as remote_file:
        key = remote_file.read().encode("utf-8")

    sftp.close()
    transport.close()

    return key


class EncryptionKey:
    """
    A class that represents an encryption key. This class supports multiple storage methods.
    """

    def __init__(self, storage_method, key_file=None, sftp_details=None):
        """
        Initialize a new EncryptionKey instance.

        Args:
            storage_method (str): The method used for key storage.
            key_file (str, optional): The path to the file that stores the encryption key.
            sftp_details (dict, optional): A dictionary containing the connection details for the SFTP server.
        """

        self.storage_method = storage_method
        self.key_file = key_file
        self.sftp_details = sftp_details

        # Load the encryption key from the specified storage method
        self.key = self._load_key()

    def _load_key(self):
        """
        Load the encryption key from the specified storage method.

        Returns:
            bytes: The encryption key.
        """

        if self.storage_method == "file":
            return get_key_from_file(self.key_file)
        elif self.storage_method == "keyring":
            return get_key_from_keyring()
        elif self.storage_method == "sftp":
            return get_key_from_sftp(self.sftp_details)
        else:
            raise ValueError(f"Unknown key_storage method: {self.storage_method}")

    def export_to_file(self, key_file):
        """
        Export the encryption key to a file.

        Args:
            key_file (str): The path to the file that will store the exported key.
        """

        with open(key_file, "wb") as file:
            file.write(self.key)

    def export_to_keyring(self):
        """
        Export the encryption key to the system's keyring.
        """

        keyring = importlib.import_module("keyring")
        keyring.set_password("cryptdb", "encryption_key", self.key.decode("utf-8"))

    def export_to_sftp(self, sftp_details):
        """
        Export the encryption key to an SFTP server.

        Args:
            sftp_details (dict): A dictionary containing the connection details for the SFTP server.
        """

        paramiko = importlib.import_module("paramiko")

        transport = paramiko.Transport((sftp_details["host"], sftp_details["port"]))
        transport.connect(
            username=sftp_details["username"], password=sftp_details["password"]
        )
        sftp = transport.open_sftp()

        with sftp.file(sftp_details["remote_key_path"], "w") as remote_file:
            remote_file.write(self.key.decode("utf-8"))

        sftp.close()
        transport.close()
