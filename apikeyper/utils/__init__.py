# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__init__.py
-----------
Author: Taylor-Jayde
Date: 8/3/2023

This module provides the `PackageChecker` class to verify the installation status
of a list of Python packages within the current environment.

The main functionality of the `PackageChecker` class is to take a list of package names
as input and return a dictionary indicating which packages are installed and which are not.

Usage example::

    checker = PackageChecker(["numpy", "tensorflow"])
    status = checker.check_installed_packages()
    print(status)  # Output might be: {"numpy": True, "tensorflow": False}

Dependencies:
    This module requires the `pkg_resources` module to determine the installation status of packages.

Note:
    Ensure the list of packages provided to the `PackageChecker` class are correctly named
    as they appear in the Python Package Index (PyPI) or your local installation.
"""


import pkg_resources


class PackageChecker:
    """
    A class to check the installation status of a list of Python packages.

    Attributes:
        packages_list (list): A list of package names to check.
    """

    def __init__(self, packages_list: list):
        """
        Args:
            packages_list (list): A list of package names to check.
        """
        self.packages_list = packages_list

    def check_installed_packages(self) -> dict:
        """
        Check which packages from the list are installed.

        Returns:
            dict: A dictionary with package names as keys and their installation status (True/False) as values.
        """
        installed_packages = pkg_resources.working_set
        installed_packages_list = sorted(
            ["%s==%s" % (i.key, i.version) for i in installed_packages]
        )

        return {
            pkg: any([pkg in item for item in installed_packages_list])
            for pkg in self.packages_list
        }
