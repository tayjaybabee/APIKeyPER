"""
Project: APIKeyPER
Author: Inspyre Softworks - https://inspyre.techCreated: 5/19/2023 @ 3:24 PM
File:
  Name: arguments.py
  Filepath: apikeyper/config
"""
from argparse import ArgumentParser


class Arguments(ArgumentParser):
    """
    A custom ArgumentParser for managing API keys associated with different services.

    Subclasses ArgumentParser to provide methods for parsing command line arguments
    related to managing API keys.

    Properties:
        parsed:
            Stores the parsed arguments, private to this class.
    """

    def __build_add_cmd__(self):
        """
        Builds the add command parser. Internal use only.
        """
        if not self.__p_subparsers:
            raise RuntimeError('Subparsers not built.')

        if self.__add_sp:
            raise RuntimeError('"add" command already built.')

        self.__add_sp = self.__p_subparsers.add_parser(
            'add',
            help='Add an API key for a service.'
        )

        self.__add_sp.add_argument(
            '--service',
            type=str,
            help='Name of the service.',
            required=True
        )

        self.__add_sp.add_argument(
            '--api-key',
            required=True,
            type=str,
            help='API key for the service.'
        )

        self.__add_sp.add_argument(
            '--key-name',
            type=str,
            help='Name of the API key (unique, within the service).',
        )

    def __build_del_cmd__(self):
        """
        Builds the delete command parser. Internal use only.
        """
        if not self.__p_subparsers:
            raise RuntimeError('Subparsers not built.')

        if self.__del_sp:
            raise RuntimeError('"delete" command already built.')

        self.__del_sp = self.__p_subparsers.add_parser(
            'delete',
            help='Delete an API key for a service.'
        )

        self.__del_sp.add_argument(
            '--service',
            type=str,
            help='Name of the service.',
            required=True
        )

        self.__del_sp.add_argument(
            '--key-name',
            type=str,
            help='Name of the API key (unique, within the service).',
            required=True
        )

        self.__del_sp.add_argument(
            '-y', '--yes',
            action='store_true',
            help='If set, will not prompt for confirmation.',
        )

    def __build_get_cmd__(self):
        """
        Builds the get command parser. Internal use only.
        """
        if not self.__p_subparsers:
            raise RuntimeError('Subparsers not built.')

        if self.__get_sp:
            raise RuntimeError('"get" command already built.')

        self.__get_sp = self.__p_subparsers.add_parser(
            'get',
            help='Get an API key for a service.'
        )

        self.__get_sp.add_argument(
            '--service',
            type=str,
            help='Name of the service.',
            required=True
        )

        self.__get_sp.add_argument(
            '--key-name',
            type=str,
            help='Name of the API key (unique, within the service).',
        )

    def __build_subparsers__(self):
        self.__p_subparsers = self.add_subparsers(
            dest='command',
            help='Subcommand to run.',
            required=True,
            parser_class=ArgumentParser,
        )

        self.__build_add_cmd__()
        self.__build_del_cmd__()
        self.__build_get_cmd__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, description='APIKeyPER - API Key Personal Encrypted Reliquary', **kwargs)
        self.__parsed = None
        self.__p_subparsers = None
        self.__add_sp = None
        self.__del_sp = None
        self.__get_sp = None
        self.__build_subparsers__()

    def parse(self, force=False):
        if (self.__parsed and force) or not self.__parsed:
            self.__parsed = self.parse_args()
        return self.parsed

    @property
    def parsed(self):
        return self.__parsed


ARGUMENTS = Arguments()


"""
The MIT License (MIT)
Copyright © 2023 Inspyre Softworks - https://inspyre.tech
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""
