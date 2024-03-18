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
from functools import wraps


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


def validate_type(*allowed_types, preferred_type):
    """
    A decorator for validating the type of a value passed to a class property setter, with
    an option to convert to a preferred type if specified.

    Args:
        preferred_type (type, optional): The preferred type to which values should be converted
                                          if possible. If None, no conversion is attempted.
        *allowed_types: Variable length list of allowed types for the property value.

    Returns:
        A decorator function for the property setter.

    Raises:
        TypeError: If the incoming value does not match one of the allowed types or cannot be
                   converted to the preferred type.

    Example:
        >>> class MyClass:
        ...     @property
        ...     def my_property(self):
        ...         return self._my_property
        ...
        ...     @my_property.setter
        ...     @validate_type(int, float, preferred_type=int)
        ...     def my_property(self, value):
        ...         self._my_property = value
        ...
        >>> obj = MyClass()
        >>> obj.my_property = 10.5  # This is converted to int and set
        >>> obj.my_property = "hello"  # This raises TypeError
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, value):
            if not isinstance(value, allowed_types):
                allowed = ', '.join([t.__name__ for t in allowed_types])
                raise TypeError(f"Value must be of type {allowed}, got type {type(value).__name__}")

            if preferred_type and not isinstance(value, preferred_type):
                try:
                    value = preferred_type(value)
                except Exception as e:
                    raise TypeError(f"Could not convert value to preferred type {preferred_type.__name__}: {e}")

            return func(self, value)
        return wrapper
    return decorator

