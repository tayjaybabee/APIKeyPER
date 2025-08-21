#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_exports.py
---------------
Tests for APIKeyPER export functionality.

This module tests that exports redact secrets by default to prevent secret leakage.
"""

import pytest
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from apikeyper import APIKeyPER


class TestExportRedaction:
    """Test class for export secret redaction functionality."""

    def test_json_export_redacts_secrets(self, tmp_path):
        """Test that JSON export redacts API key values by default."""
        db_path = tmp_path / "test_export.db"
        api = APIKeyPER(db_path)
        
        # Add test keys
        api.add_key("github", "ghp_secret123456")
        api.add_key("openai", "sk-secretkey789")
        
        # Export to JSON
        export_path = tmp_path / "export.json"
        api.db.export_db_as_json(export_path)
        
        # Read exported data
        with open(export_path, "r") as f:
            data = json.load(f)
        
        # Check that secrets are redacted
        github_keys = data["github"]
        assert len(github_keys) == 1
        assert github_keys[0]["key"] == "***REDACTED***"
        
        openai_keys = data["openai"]
        assert len(openai_keys) == 1
        assert openai_keys[0]["key"] == "***REDACTED***"
        
        # Other fields should not be redacted
        assert github_keys[0]["key_name"] is not None
        assert github_keys[0]["status"] == "active"

    def test_xml_export_redacts_secrets(self, tmp_path):
        """Test that XML export redacts API key values by default."""
        db_path = tmp_path / "test_export_xml.db"
        api = APIKeyPER(db_path)
        
        # Add test keys
        api.add_key("aws", "AKIAIOSFODNN7EXAMPLE")
        api.add_key("stripe", "sk_test_secret123")
        
        # Export to XML
        export_path = tmp_path / "export.xml"
        api.db.export_db_as_xml(export_path)
        
        # Parse exported XML
        tree = ET.parse(export_path)
        root = tree.getroot()
        
        # Check that secrets are redacted
        services = {service.get("name"): service for service in root.findall("service")}
        
        # Check AWS service
        aws_key = services["aws"].find("key/key_value")
        assert aws_key.text == "***REDACTED***"
        
        # Check Stripe service  
        stripe_key = services["stripe"].find("key/key_value")
        assert stripe_key.text == "***REDACTED***"
        
        # Other fields should not be redacted
        aws_status = services["aws"].find("key/status")
        assert aws_status.text == "active"

    def test_export_redaction_preserves_structure(self, tmp_path):
        """Test that redaction preserves the structure and other data."""
        db_path = tmp_path / "test_structure.db"
        api = APIKeyPER(db_path)
        
        # Add a key
        api.add_key("test_service", "test_secret_key")
        
        # Export to JSON
        export_path = tmp_path / "structure_test.json"
        api.db.export_db_as_json(export_path)
        
        # Read and verify structure
        with open(export_path, "r") as f:
            data = json.load(f)
        
        assert "test_service" in data
        key_data = data["test_service"][0]
        
        # Required fields should be present
        required_fields = ["key_name", "added", "key", "status", "revoked_on"]
        for field in required_fields:
            assert field in key_data
        
        # Key should be redacted but other fields preserved
        assert key_data["key"] == "***REDACTED***"
        assert key_data["status"] == "active"
        assert key_data["key_name"] is not None
        assert key_data["added"] is not None

    def test_export_with_redaction_disabled(self, tmp_path):
        """Test that exports can show full keys when redaction is disabled."""
        db_path = tmp_path / "test_no_redact.db"
        api = APIKeyPER(db_path)
        
        # Add test key
        api.add_key("test_service", "full_secret_key_123")
        
        # Export JSON without redaction
        json_path = tmp_path / "no_redact.json"
        api.db.export_db_as_json(json_path, redact_secrets=False)
        
        with open(json_path, "r") as f:
            data = json.load(f)
        
        # Should show full key
        assert data["test_service"][0]["key"] == "full_secret_key_123"
        
        # Export XML without redaction
        xml_path = tmp_path / "no_redact.xml"
        api.db.export_db_as_xml(xml_path, redact_secrets=False)
        
        tree = ET.parse(xml_path)
        root = tree.getroot()
        key_value = root.find("service/key/key_value")
        
        # Should show full key
        assert key_value.text == "full_secret_key_123"