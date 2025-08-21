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

import pytest
import tempfile
from pathlib import Path
from apikeyper import APIKeyPER


class TestAPIKeyPER:
    """Test class for APIKeyPER core functionality."""

    def test_add_and_get_key(self, tmp_path):
        """Test adding and retrieving a single API key."""
        db_path = tmp_path / "test.db"
        api = APIKeyPER(db_path)
        
        # Add a key
        api.add_key("test_service", "test_key_123")
        
        # Retrieve the key
        result = api.get_key("test_service")
        
        # Verify the result
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 6  # (service, key_name, added, key, status, revoked_on)
        assert result[0] == "test_service"  # service
        assert result[3] == "test_key_123"  # key
        assert result[4] == "active"        # status

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
        assert github_key[3] == "ghp_123456"
        
        openai_key = api.get_key("openai")
        assert openai_key[3] == "sk-123456"
        
        aws_key = api.get_key("aws")
        assert aws_key[3] == "AKIAIOSFODNN7EXAMPLE"
        
        # Delete one service
        api.delete_key("openai")
        
        # Check services list after deletion
        services = api.list_services()
        assert len(services) == 2
        assert "openai" not in services
        assert "github" in services
        assert "aws" in services
        
        # Verify deleted key is gone
        assert api.get_key("openai") is None
        
        # Verify other keys still exist
        assert api.get_key("github")[3] == "ghp_123456"
        assert api.get_key("aws")[3] == "AKIAIOSFODNN7EXAMPLE"

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
        assert result[3] == "new_key"

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
        assert result[3] == "persistent_key"
        
        # Services list should also be accessible
        services = api2.list_services()
        assert "persistent_service" in services