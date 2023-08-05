"""
Project: APIKeyPER
Author: Inspyre Softworks - https://inspyre.techCreated: 5/21/2023 @ 10:18 PM
File:
  Name: __init__.py
  Filepath: apikeyper/ui
"""
from apikeyper import APIKeyPER
from apikeyper.utils import PackageChecker
from apikeyper.log_engine import LOG_DEVICE as ROOT_LOGGER

from rich.console import Console


CONSOLE = Console()


LOG_DEVICE = ROOT_LOGGER.get_child("ui")

LOGGER = LOG_DEVICE.logger

DEFAULT_PASSWORD_PROMPT = "Enter password: "

LOGGER.debug(f"Default password prompt: {DEFAULT_PASSWORD_PROMPT}")


class CLI:
    """
    This class provides a command line interface for managing API keys stored in a SQLite database.

    Attributes:
        apikeyper (APIKeyPER): An instance of the APIKeyPER class for managing API keys.
    """

    def __init__(self, db_file_path):
        """
        Initializes the CLI with an APIKeyPER instance connected to the specified SQLite database file.

        Args:
            db_file_path (str): The path to the SQLite database file.
        """
        self.apikeyper = APIKeyPER(db_file_path)


class UserInputHandler:
    """
    This class handles user input, either through a graphical user interface (GUI) or command line interface (CLI).

    Attributes:
        use_gui (bool): Whether to use a GUI for input.
        __gui (PySimpleGUI, optional): The PySimpleGUI instance for GUI input. None if use_gui is False.
    """

    def __init__(self, use_gui=False):
        """
        Initializes the UserInputHandler with the specified input mode.

        Args:
            use_gui (bool, optional): Whether to use a GUI for input. Defaults to False.
        """
        self.use_gui = use_gui
        self.__gui = None

        if self.use_gui:
            try:
                import PySimpleGUI as gui
            except (NameError, ImportError) as e:
                print(e)

    @staticmethod
    def __prep_custom_prompt_string(prompt_string):
        """
        Prepares a custom prompt string by stripping space and ensuring it ends with a colon.

        Args:
            prompt_string (str): The prompt string to prepare.

        Returns:
            str: The prepared prompt string.
        """
        ps = prompt_string.strip()
        if not ps.endswith(":"):
            ps = f"{ps}:"
        return f"{ps}"

    def prompt(self, msg: str):
        """
        Prompt the end-user for input.

        Arguments:
            msg (str): The message the user sees when prompted.

        Returns:
            str: The input provided by the user in answer.
        """
        msg = self.__prep_custom_prompt_string(msg)

    def get_password(self, skip_formatting=False, prompt=None, **kwargs):
        """
        Gets a password from the user, either through a GUI or CLI.

        Args:
            skip_formatting (bool, optional): Whether to skip formatting the prompt string. Defaults to False.
            prompt (str, optional): The prompt to display to the user. Defaults to None.

        Returns:
            str: The password entered by the user.
        """

        if prompt and not skip_formatting:
            prompt = self.__prep_custom_prompt_string(prompt)

        return (
            self.__get_password_gui(prompt)
            if self.use_gui
            else self.__get_password_cli(prompt)
        )

    @staticmethod
    def __get_password_cli(prompt=None):
        """
        Gets a password from the user via a command line interface.

        Args:
            prompt (str, optional): The prompt to display to the user. Defaults to None.

        Returns:
            str: The password entered by the user.
        """
        prompt = prompt or DEFAULT_PASSWORD_PROMPT
        return input(prompt)

    @staticmethod
    def __get_password_gui(prompt=None):
        """
        Gets a password from the user via a graphical user interface.

        Args:
            prompt (str, optional): The prompt to display to the user. Defaults to None.

        Returns:
            str: The password entered by the user.
        """
        prompt = prompt or DEFAULT_PASSWORD_PROMPT
        print("GUI mode activated, but not yet implemented.")

        print(prompt)
        return ""


"""
The MIT License (MIT)
Copyright © 2023 Inspyre Softworks - https://inspyre.tech
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""
