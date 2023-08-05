#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
decorators.py
-------------
Author: tayja
Date: 8/3/2023

This module provides decorators for ensuring API keys are available for specific services.
It offers both function-level and class-level decorators:

1. `apikey_required(service_names)`:
    A decorator for functions. When a function decorated with this is called, it checks
    if the required API keys are available. If a key is not found in the database,
    it prompts the user for input and saves the provided key.

    Args:
        service_names (Union[str, List[str]]):
            A list of service names for which API keys are needed.
            If a single string is provided, it's converted to a list.

2. `apikey_required_class(service_names)`:
    A decorator for classes. When an instance of a class decorated with this is created,
    it checks if the required API keys are available for the given services.
    If a key is not found in the database, it prompts the user for input and saves the provided key.
    It then sets the API key as a class attribute.

    Args:
        service_names (Union[str, List[str]]):
            A list of service names for which API keys are needed.
            If a single string is provided, it's converted to a list.

Usage example::

    @apikey_required(["service1", "service2"])
    def my_function():
        pass

    @apikey_required_class(["service1", "service2"])
    class MyClass:
        pass

Note:
    This module uses the APIKeyPER database manager for retrieving and storing API keys.Ensure that the APIKeyPER
    manager is initialized and connected to the correct database before use.

"""


def apikey_required(service_names):
    """
    A decorator to ensure API keys are available for given services.
    If a key is not available in the database, it prompts the user for input.
    """
    if not isinstance(service_names, list):
        service_names = [service_names]

    def decorator(func):
        def wrapper(*args, **kwargs):
            api_manager = APIKeyPER("default_apikeys.db")

            api_keys = {}
            for service_name in service_names:
                api_key = api_manager.get_key(service_name)
                if not api_key:
                    print(
                        f"No API key found for {service_name}. Please provide the API key:"
                    )
                    user_api_key = input()  # Get user input for the API key
                    api_manager.add_key(service_name, user_api_key)
                    api_keys[service_name] = user_api_key
                else:
                    api_keys[service_name] = api_key[0]

            kwargs["api_keys"] = api_keys
            return func(*args, **kwargs)

        return wrapper

    return decorator


def apikey_required_class(service_names):
    """
    A class decorator to ensure API keys are available for given services.
    If a key is not available in the database, it prompts the user for input.
    """
    if not isinstance(service_names, list):
        service_names = [service_names]

    def decorator(cls):
        original_init = cls.__init__

        def new_init(self, *args, **kwargs):
            api_manager = APIKeyPER("default_apikeys.db")

            for service_name in service_names:
                api_key = api_manager.get_key(service_name)
                if not api_key:
                    print(
                        f"No API key found for {service_name}. Please provide the API key:"
                    )
                    user_api_key = input()  # Get user input for the API key
                    api_manager.add_key(service_name, user_api_key)
                    setattr(cls, service_name.upper() + "_API_KEY", user_api_key)
                else:
                    setattr(cls, service_name.upper() + "_API_KEY", api_key[0])

            original_init(self, *args, **kwargs)

        cls.__init__ = new_init
        return cls

    return decorator
