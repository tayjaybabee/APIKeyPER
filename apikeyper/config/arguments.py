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
    def __init__(self, *args, **kwargs):
        super().__init__(description='APIKeyPER - API Key Personal Encrypted Reliquary')
        self.__parsed = None
        subparsers = self.add_subparsers(dest='command')

        add_parser = subparsers.add_parser('add')
        add_parser.add_argument(
            'service',
            type=str,
            help='Name of the service.'
        )

        add_parser.add_argument(
            'api_key',
            type=str,
            help='API key for the service.'
        )






    def parse(self, force=False):
        if (self.__parsed and force) or not self.__parsed:
            self.__parsed = self.parse_args()
        return self.parsed

    @property
    def parsed(self):
        return self.__parsed




"""
The MIT License (MIT)
Copyright © 2023 Inspyre Softworks - https://inspyre.tech
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""
