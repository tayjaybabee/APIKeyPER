"""


Author: 
    Inspyre Softworks

Project:
    APIKeyPER

File: 
    apikeyper/cli/handlers/__init__.py
 

Description:
    Registers the built-in command handlers with COMMAND_HANDLERS on import.

"""
from apikeyper.cli.handlers.core import COMMAND_HANDLERS
from apikeyper.cli.handlers import add, delete, get, revoke  # noqa: F401
