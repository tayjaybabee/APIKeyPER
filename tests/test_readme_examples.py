#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_readme_examples.py
-----------------------
Tests to ensure README examples work as documented.
"""

import pytest
from pathlib import Path
from unittest.mock import patch
from apikeyper import APIKeyPER
from apikeyper.utils.decorators import apikey_required, apikey_required_class


class TestREADMEExamples:
    """Test class to verify README examples work correctly."""

    def test_basic_api_usage_example(self, tmp_path):
        """Test the basic API usage example from README."""
        # Initialize APIKeyPER with a database file
        api = APIKeyPER(tmp_path / "my_api_keys.db")

        # Add API keys for different services
        api.add_key("github", "ghp_your_github_token_here")
        api.add_key("openai", "sk-your_openai_key_here")
        api.add_key("aws", "AKIAIOSFODNN7EXAMPLE")

        # Retrieve an API key
        github_key_data = api.get_key("github")
        assert github_key_data is not None
        actual_key = github_key_data[3]  # The key is at index 3 in the tuple
        assert actual_key == "ghp_your_github_token_here"

        # List all services with stored keys
        services = api.list_services()
        assert len(services) == 3
        assert "github" in services
        assert "openai" in services  
        assert "aws" in services

        # Delete a key
        api.delete_key("aws")
        
        # Verify deletion
        services_after_delete = api.list_services()
        assert "aws" not in services_after_delete
        assert len(services_after_delete) == 2

    def test_function_decorator_example(self, tmp_path):
        """Test the function decorator example from README."""
        # Set up test database
        test_db = tmp_path / "func_example.db"
        api = APIKeyPER(test_db)
        api.add_key("github", "ghp_example_token")
        api.add_key("openai", "sk-example_key")
        
        # Copy to default location for decorators
        import shutil
        shutil.copy(test_db, "default_apikeys.db")
        
        try:
            @apikey_required(["github", "openai"])
            def my_function(**kwargs):
                # The decorator injects an 'api_keys' parameter containing the requested keys
                api_keys = kwargs.get("api_keys", {})
                github_key = api_keys["github"]
                openai_key = api_keys["openai"]
                
                return {
                    "github_key": github_key,
                    "openai_key": openai_key,
                    "status": "Function executed successfully"
                }

            # When the function is called, the decorator ensures the required API keys are available
            result = my_function()
            
            assert result["github_key"] == "ghp_example_token"
            assert result["openai_key"] == "sk-example_key"
            assert result["status"] == "Function executed successfully"
        finally:
            Path("default_apikeys.db").unlink(missing_ok=True)

    def test_class_decorator_example(self, tmp_path):
        """Test the class decorator example from README."""
        # Set up test database
        test_db = tmp_path / "class_example.db"
        api = APIKeyPER(test_db)
        api.add_key("service1", "key1_value")
        api.add_key("service2", "key2_value")
        
        # Copy to default location for decorators
        import shutil
        shutil.copy(test_db, "default_apikeys.db")
        
        try:
            @apikey_required_class(["service1", "service2"])
            class MyClass:
                def __init__(self):
                    # The decorator automatically sets class attributes:
                    # MyClass.SERVICE1_API_KEY and MyClass.SERVICE2_API_KEY
                    pass

                def use_keys(self):
                    # Access the API keys via class attributes
                    service1_key = self.__class__.SERVICE1_API_KEY
                    service2_key = self.__class__.SERVICE2_API_KEY
                    return f"Using keys: {service1_key}, {service2_key}"

            # When an instance of MyClass is created, the decorator ensures that the keys are available
            my_instance = MyClass()

            # The keys should now be available as class attributes
            assert hasattr(MyClass, "SERVICE1_API_KEY")
            assert hasattr(MyClass, "SERVICE2_API_KEY")
            assert MyClass.SERVICE1_API_KEY == "key1_value"
            assert MyClass.SERVICE2_API_KEY == "key2_value"
            
            # Test the use_keys method
            result = my_instance.use_keys()
            assert result == "Using keys: key1_value, key2_value"
        finally:
            Path("default_apikeys.db").unlink(missing_ok=True)