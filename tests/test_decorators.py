#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_decorators.py
------------------
Tests for APIKeyPER decorators.

This module tests the decorator functionality including:
- apikey_required function injection behavior
- apikey_required_class attribute setting behavior
- Function parameter inspection and injection logic
"""

from argparse import Namespace
from unittest.mock import patch

import apikeyper
from apikeyper import APIKeyPER
from apikeyper.cli.handlers.add import do_add
from apikeyper.utils.decorators import apikey_required, apikey_required_class


class TestAPIKeyRequiredDecorator:
    """Test class for apikey_required function decorator."""

    def test_injects_single_key_into_named_parameter(self, tmp_path, monkeypatch):
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", tmp_path / "keys.db")
        APIKeyPER().add_key("Home Assistant", "fake_home_assistant_key")

        @apikey_required("Home Assistant")
        def get_key(label, api_key):
            return label, api_key

        assert get_key("home") == ("home", "fake_home_assistant_key")
        assert get_key("home", "fake_override") == ("home", "fake_override")
        assert get_key("home", api_key="fake_override") == ("home", "fake_override")

    def test_injects_single_key_into_keyword_only_parameter(self, tmp_path, monkeypatch):
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", tmp_path / "keys.db")
        APIKeyPER().add_key("Home Assistant", "fake_home_assistant_key")

        @apikey_required(["Home Assistant"])
        def get_key(*, api_key):
            return api_key

        assert get_key() == "fake_home_assistant_key"

    def test_decorator_injects_api_keys_with_kwargs(self, tmp_path, monkeypatch):
        """Test that apikey_required injects api_keys when function accepts **kwargs."""

        # Set up a test database with sample keys
        test_db = tmp_path / "test_func.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)
        api.add_key("github", "ghp_test123")
        api.add_key("openai", "sk_test456")

        @apikey_required(["github", "openai"])
        def test_function(**kwargs):
            return kwargs.get("api_keys", {})

        result = test_function()

        # Should receive both API keys
        assert "github" in result
        assert "openai" in result
        assert result["github"] == "ghp_test123"
        assert result["openai"] == "sk_test456"

    def test_decorator_injects_api_keys_with_explicit_param(self, tmp_path, monkeypatch):
        """Test that apikey_required injects api_keys when function has api_keys parameter."""

        test_db = tmp_path / "test_func2.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)
        api.add_key("github", "ghp_test123")

        @apikey_required(["github"])
        def test_function_with_param(api_keys=None, other_param="default"):
            return api_keys

        result = test_function_with_param()

        # Should receive API keys
        assert "github" in result
        assert result["github"] == "ghp_test123"

    def test_decorator_preserves_function_args(self, tmp_path, monkeypatch):
        """Test that decorator preserves original function arguments."""

        test_db = tmp_path / "test_func3.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)
        api.add_key("github", "ghp_test123")

        @apikey_required(["github"])
        def test_function(arg1, arg2, **kwargs):
            return {
                "arg1": arg1,
                "arg2": arg2,
                "api_keys": kwargs.get("api_keys", {})
            }

        result = test_function("value1", "value2")

        # Should preserve original arguments and add api_keys
        assert result["arg1"] == "value1"
        assert result["arg2"] == "value2"
        assert "github" in result["api_keys"]

    def test_decorator_single_service_string(self, tmp_path, monkeypatch):
        """Test that decorator accepts single service as string (not list)."""

        test_db = tmp_path / "test_func4.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)
        api.add_key("github", "ghp_test123")

        @apikey_required("github")  # Single string, not list
        def test_function(**kwargs):
            return kwargs.get("api_keys", {})

        result = test_function()

        # Should work with single service
        assert "github" in result
        assert result["github"] == "ghp_test123"

    def test_decorator_with_missing_key(self, tmp_path, monkeypatch):
        """Test decorator behavior when API key is missing."""
        # Create empty DB
        test_db = tmp_path / "empty.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)  # Just create the DB, don't add keys

        # Mock input() to simulate user providing a key
        with patch('builtins.input', return_value='user_provided_key'):
            with patch('builtins.print'):  # Suppress print output
                @apikey_required(["missing_service"])
                def test_function(**kwargs):
                    return kwargs.get("api_keys", {})

                result = test_function()

                # Should use the user-provided key
                assert "missing_service" in result
                assert result["missing_service"] == "user_provided_key"

    def test_decorator_preserves_return_value(self, tmp_path, monkeypatch):
        """Test that decorator preserves the original function's return value."""

        test_db = tmp_path / "test_func5.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)
        api.add_key("github", "ghp_test123")

        @apikey_required(["github"])
        def test_function(**kwargs):
            return "original_return_value"

        result = test_function()

        # Should return the original function's return value
        assert result == "original_return_value"


class TestAPIKeyRequiredClassDecorator:
    """Test class for apikey_required_class decorator."""

    def test_class_decorator_sets_attributes(self, tmp_path, monkeypatch):
        """Test that apikey_required_class sets class attributes."""

        test_db = tmp_path / "test_class.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)
        api.add_key("github", "ghp_class123")
        api.add_key("openai", "sk_class456")

        @apikey_required_class(["github", "openai"])
        class TestClass:
            def __init__(self):
                pass

        # Create instance to trigger decorator
        instance = TestClass()

        # Check that class attributes are set
        assert hasattr(TestClass, "GITHUB_API_KEY")
        assert hasattr(TestClass, "OPENAI_API_KEY")
        assert TestClass.GITHUB_API_KEY == "ghp_class123"
        assert TestClass.OPENAI_API_KEY == "sk_class456"

    def test_class_decorator_preserves_init(self, tmp_path, monkeypatch):
        """Test that class decorator preserves original __init__ behavior."""

        test_db = tmp_path / "test_class2.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)
        api.add_key("github", "ghp_class123")

        @apikey_required_class(["github"])
        class TestClass:
            def __init__(self, value):
                self.value = value

        # Create instance with arguments
        instance = TestClass("test_value")

        # Should preserve original init behavior
        assert instance.value == "test_value"
        # And add the API key attribute
        assert hasattr(TestClass, "GITHUB_API_KEY")

    def test_class_decorator_single_service(self, tmp_path, monkeypatch):
        """Test that class decorator accepts single service as string."""

        test_db = tmp_path / "test_class3.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)
        api.add_key("github", "ghp_class123")

        @apikey_required_class("github")  # Single string, not list
        class TestClass:
            pass

        instance = TestClass()

        # Should work with single service
        assert hasattr(TestClass, "GITHUB_API_KEY")
        assert TestClass.GITHUB_API_KEY == "ghp_class123"

    def test_class_decorator_attribute_naming(self, tmp_path, monkeypatch):
        """Test that class decorator creates correctly named attributes."""

        test_db = tmp_path / "test_class4.db" 
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)
        api.add_key("github-api", "key1")
        api.add_key("openai_service", "key2")
        api.add_key("aws-s3", "key3")

        @apikey_required_class(["github-api", "openai_service", "aws-s3"])
        class TestClass:
            pass

        instance = TestClass()

        # Check attribute naming (should be uppercase with underscores)
        assert hasattr(TestClass, "GITHUB-API_API_KEY")
        assert hasattr(TestClass, "OPENAI_SERVICE_API_KEY")
        assert hasattr(TestClass, "AWS-S3_API_KEY")

    def test_class_decorator_with_missing_key(self, tmp_path, monkeypatch):
        """Test class decorator behavior when API key is missing."""
        # Create empty DB
        test_db = tmp_path / "empty_class.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)  # Just create the DB, don't add keys

        # Mock input() to simulate user providing a key
        with patch('builtins.input', return_value='user_class_key'):
            with patch('builtins.print'):  # Suppress print output
                @apikey_required_class(["missing_service"])
                class TestClass:
                    pass

                instance = TestClass()

                # Should use the user-provided key
                assert hasattr(TestClass, "MISSING_SERVICE_API_KEY")
                assert TestClass.MISSING_SERVICE_API_KEY == "user_class_key"

    def test_class_decorator_multiple_instances(self, tmp_path, monkeypatch):
        """Test that class decorator behavior is consistent across multiple instances."""

        test_db = tmp_path / "test_class5.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        api = APIKeyPER(test_db)
        api.add_key("github", "ghp_class123")

        @apikey_required_class(["github"])
        class TestClass:
            def __init__(self, name):
                self.name = name

        # Create multiple instances
        instance1 = TestClass("first")
        instance2 = TestClass("second")

        # Both should have access to the same class attribute
        assert TestClass.GITHUB_API_KEY == "ghp_class123"
        assert instance1.name == "first"
        assert instance2.name == "second"

        # The class attribute should be the same for both instances
        assert hasattr(TestClass, "GITHUB_API_KEY")


class TestDecoratorIntegration:
    """Integration tests for decorator functionality."""

    def test_decorators_read_key_added_by_cli(self, tmp_path, monkeypatch):
        """Both decorators can read a key added to the default database by the CLI."""
        test_db = tmp_path / "integration.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", test_db)
        assert do_add(Namespace(service="Muse", api_key="fake_muse_key", key_name=None)) == 0

        @apikey_required("Muse")
        def test_function(**kwargs):
            return kwargs.get("api_keys", {})

        @apikey_required_class("Muse")
        class TestClass:
            pass

        assert test_function() == {"Muse": "fake_muse_key"}
        assert TestClass().MUSE_API_KEY == "fake_muse_key"
