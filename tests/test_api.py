#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_api.py
-----------
Tests for APIKeyPER core operations.

This module tests the main functionality of APIKeyPER including:
- add_key/get_key/delete_key/list_services round trip
- Uses temporary DB files to ensure test isolation
"""

import logging

import pytest
import tempfile
from pathlib import Path
from apikeyper import APIKey, APIKeyPER, Service


class TestAPIKeyPER:
    """Test class for APIKeyPER core functionality."""

    def test_service_manages_key_objects_in_the_same_store(self, tmp_path):
        api = APIKeyPER(tmp_path / "test.db")
        service = api.service("Home Assistant")
        assert isinstance(service, Service)
        assert service.list_keys() == []

        saved = service.add_key(
            "fake_home_assistant_token", key_name="primary", key_id="fake-provider-id"
        )
        assert isinstance(saved, APIKey)
        assert saved.added.was_defaulted
        api.add_key("other", "fake_other_token", key_name="primary")
        record = service.get_key("primary")
        assert isinstance(record, APIKey)
        assert record == saved
        assert record.key_id == "fake-provider-id"
        assert record.key_id not in repr(record)
        assert record == api.get_key(service.name, "primary")
        assert service.list_keys() == [record]
        assert record.key not in repr(record)

        service.revoke_key("primary")
        assert service.get_key("primary") is None
        assert service.get_key("primary", only_active=False).status == "revoked"
        assert service.list_keys()[0].revoked_on is not None

        service.delete_key()
        assert service.list_keys() == []
        assert api.get_key("other", "primary") is not None

    def test_add_and_get_key(self, tmp_path):
        """Test adding and retrieving a single API key."""
        db_path = tmp_path / "test.db"
        api = APIKeyPER(db_path)
        
        # Add a key
        saved = api.add_key("test_service", "test_key_123")
        
        # Retrieve the key
        result = api.get_key("test_service")
        
        # Verify the result
        assert result is not None
        assert isinstance(saved, APIKey)
        assert saved == result
        assert result.service == "test_service"
        assert len(result) == 6  # (service, key_name, added, key, status, revoked_on)
        assert result.key == "test_key_123"
        assert result.status == "active"

    def test_add_service_persists_an_empty_service(self, tmp_path):
        path = tmp_path / "services.db"
        api = APIKeyPER(path)
        service = api.add_service("Home Assistant")
        assert isinstance(service, Service)
        assert service.name == "Home Assistant"
        assert service.list_keys() == []
        api.add_service(service.name)
        api.db.close()

        api = APIKeyPER(path)
        assert api.list_services() == [service.name]
        service = api.service(service.name)
        key = service.add_key("fake_token", status="revoked")
        assert isinstance(key, APIKey)
        assert key == service.get_key(key.key_name, only_active=False)
        service.delete_key()
        assert api.list_services() == [service.name]

    def test_add_service_rejects_blank_name(self, tmp_path):
        api = APIKeyPER(tmp_path / "services.db")
        with pytest.raises(ValueError, match="blank"):
            api.add_service(" ")

    def test_get_service_exact_first_and_warns_for_fuzzy_matches(self, tmp_path, caplog):
        api = APIKeyPER(tmp_path / "services.db")
        api.add_service("Home Assistant")
        api.add_key("Home Assistant Backup", "fake_backup_token")

        assert api.get_service("Home Assistant").name == "Home Assistant"
        assert api.get_service("Home Assistant Backup").name == "Home Assistant Backup"

        assert caplog.records == []
        matches = api.get_service("home assistant")
        assert [service.name for service in matches] == [
            "Home Assistant", "Home Assistant Backup"
        ]

        matches = api.get_service("Home Asistant")
        assert matches[0].name == "Home Assistant"

        assert api.get_service("zzzzzz") == []
        assert caplog.record_tuples == [
            (
                api.log_device.name,
                logging.WARNING,
                f"No exact service match. Returning {count} fuzzy suggestions.",
            )
            for count in (2, len(matches), 0)
        ]

    def test_get_nonexistent_key(self, tmp_path):
        """Test retrieving a key that doesn't exist."""
        db_path = tmp_path / "test.db"
        api = APIKeyPER(db_path)
        
        # Try to get a key that doesn't exist
        result = api.get_key("nonexistent_service")
        
        # Should return None
        assert result is None

    def test_delete_key(self, tmp_path):
        """Test deleting an API key."""
        db_path = tmp_path / "test.db"
        api = APIKeyPER(db_path)
        
        # Add a key
        api.add_key("test_service", "test_key_123")
        
        # Verify it exists
        result = api.get_key("test_service")
        assert result is not None
        
        # Delete the key
        api.delete_key("test_service")
        
        # Verify it's gone
        result = api.get_key("test_service")
        assert result is None

    def test_list_services_empty(self, tmp_path):
        """Test listing services when database is empty."""
        db_path = tmp_path / "test.db"
        api = APIKeyPER(db_path)
        
        # List services on empty database
        services = api.list_services()
        
        # Should return empty list
        assert services == []

    def test_list_services_with_data(self, tmp_path):
        """Test listing services with data in database."""
        db_path = tmp_path / "test.db"
        api = APIKeyPER(db_path)
        
        # Add keys for multiple services
        api.add_key("service1", "key1")
        api.add_key("service2", "key2")
        api.add_key("service1", "key1_v2")  # Another key for service1
        
        # List services
        services = api.list_services()
        
        # Should return both services
        assert len(services) == 2
        assert "service1" in services
        assert "service2" in services

    def test_round_trip_operations(self, tmp_path):
        """Test a complete round trip of operations."""
        db_path = tmp_path / "test.db"
        api = APIKeyPER(db_path)
        
        # Initially empty
        assert api.list_services() == []
        
        # Add multiple keys
        api.add_key("github", "ghp_123456")
        api.add_key("openai", "sk-123456")
        api.add_key("aws", "AKIAIOSFODNN7EXAMPLE")
        
        # Check services list
        services = api.list_services()
        assert len(services) == 3
        assert "github" in services
        assert "openai" in services
        assert "aws" in services
        
        # Check individual keys
        github_key = api.get_key("github")
        assert github_key.key == "ghp_123456"
        
        openai_key = api.get_key("openai")
        assert openai_key.key == "sk-123456"
        
        aws_key = api.get_key("aws")
        assert aws_key.key == "AKIAIOSFODNN7EXAMPLE"
        
        # Delete one service
        api.delete_key("openai")
        
        # Check services list after deletion
        services = api.list_services()
        assert len(services) == 3
        assert "openai" in services
        assert "github" in services
        assert "aws" in services
        
        # Verify deleted key is gone
        assert api.get_key("openai") is None

        # Verify other keys still exist
        assert api.get_key("github").key == "ghp_123456"
        assert api.get_key("aws").key == "AKIAIOSFODNN7EXAMPLE"

    def test_service_key_id_requirement_persists_and_can_be_changed(self, tmp_path):
        path = tmp_path / "keys.db"
        api = APIKeyPER(path)
        service = api.add_service("Wyze", require_key_id=True)
        assert service.require_key_id
        saved = service.add_key("fake_token", key_name="primary", key_id="fake-id")
        with pytest.raises(ValueError, match="requires a non-blank key_id"):
            api.add_key("Wyze", "fake_replacement", key_name="primary", key_id=" ")
        assert service.get_key("primary") == saved
        api.db.close()

        api = APIKeyPER(path)
        service = api.get_service("Wyze")
        assert service.require_key_id
        with pytest.raises(ValueError, match="requires a non-blank key_id"):
            service.add_key("fake_token")
        service.require_key_id = False
        assert api.add_key("Wyze", "fake_token").key_id is None
        service.require_key_id = True
        assert api.add_service("Wyze").require_key_id

    def test_multiple_keys_per_service(self, tmp_path):
        """Test that get_key returns the most recent active key when multiple exist."""
        db_path = tmp_path / "test.db"
        api = APIKeyPER(db_path)
        
        # Add multiple keys for the same service
        api.add_key("test_service", "old_key")
        api.add_key("test_service", "new_key")
        
        # Should return the most recent key (since we order by added DESC)
        result = api.get_key("test_service")
        assert result is not None
        assert result.key == "new_key"

    def test_revoke_already_revoked_key(self, tmp_path):
        """Test that revoking a key twice reports that it is already revoked."""
        api = APIKeyPER(tmp_path / "test.db")
        api.add_key("test_service", "test_key", key_name="primary")

        api.revoke_key("test_service", "primary")

        with pytest.raises(ValueError, match="already revoked"):
            api.revoke_key("test_service", "primary")

    def test_database_persistence(self, tmp_path):
        """Test that data persists across APIKeyPER instances."""
        db_path = tmp_path / "test.db"
        
        # Create first instance and add data
        api1 = APIKeyPER(db_path)
        api1.add_key("persistent_service", "persistent_key")
        
        # Create second instance with same database
        api2 = APIKeyPER(db_path)
        
        # Data should be accessible from second instance
        result = api2.get_key("persistent_service")
        assert result is not None
        assert result.key == "persistent_key"
        
        # Services list should also be accessible
        services = api2.list_services()
        assert "persistent_service" in services
