"""
Test the encryption backends functionality.
"""
import pytest
import tempfile
import os
from pathlib import Path

from apikeyper.crypto.backends import InMemoryBackend, make_key_id
from apikeyper.config import Config
from apikeyper import APIKeyPER


class TestEncryptionBackends:
    """Test encryption backend implementations."""

    def test_in_memory_backend(self):
        """Test InMemoryBackend basic functionality."""
        backend = InMemoryBackend()
        
        # Test store and retrieve
        backend.store_secret("test_key", "test_secret")
        assert backend.retrieve_secret("test_key") == "test_secret"
        
        # Test non-existent key
        assert backend.retrieve_secret("nonexistent") is None
        
        # Test delete
        backend.delete_secret("test_key")
        assert backend.retrieve_secret("test_key") is None
        
        # Test clear_all
        backend.store_secret("key1", "secret1")
        backend.store_secret("key2", "secret2")
        backend.clear_all()
        assert backend.retrieve_secret("key1") is None
        assert backend.retrieve_secret("key2") is None

    def test_make_key_id(self):
        """Test key ID generation."""
        # Basic key ID
        key_id = make_key_id("apikeyper", "github", "default")
        assert key_id.startswith("apikeyper:")
        assert len(key_id) > len("apikeyper:")
        
        # With profile
        key_id_with_profile = make_key_id("apikeyper", "github", "default", "prod")
        assert key_id_with_profile != key_id
        assert key_id_with_profile.startswith("apikeyper:")
        
        # Same inputs should produce same key
        key_id2 = make_key_id("apikeyper", "github", "default")
        assert key_id == key_id2


class TestAPIKeyPERIntegration:
    """Test APIKeyPER with in-memory backend."""

    def setup_method(self):
        """Set up test with temporary database and in-memory backend."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        
        # Create config with in-memory backend
        self.backend = InMemoryBackend()
        self.config = Config(
            profile=None,
            namespace="test",
            db_file_path=self.db_path,
            include_secrets=False,
            backend=self.backend
        )
        
        self.api_manager = APIKeyPER(config=self.config)

    def teardown_method(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_and_get_key(self):
        """Test adding and retrieving keys."""
        # Add a key
        self.api_manager.add_key("github", "gh_test_token_123")
        
        # Retrieve the key
        retrieved_key = self.api_manager.get_key("github")
        assert retrieved_key == "gh_test_token_123"

    def test_nonexistent_key(self):
        """Test retrieving non-existent key."""
        result = self.api_manager.get_key("nonexistent")
        assert result is None

    def test_delete_key(self):
        """Test deleting keys."""
        # Add a key
        self.api_manager.add_key("github", "gh_test_token_123")
        
        # Verify it exists
        assert self.api_manager.get_key("github") == "gh_test_token_123"
        
        # Delete it
        self.api_manager.delete_key("github")
        
        # Verify it's gone
        assert self.api_manager.get_key("github") is None

    def test_list_services(self):
        """Test listing services."""
        # Initially empty
        assert self.api_manager.list_services() == []
        
        # Add some keys
        self.api_manager.add_key("github", "token1")
        self.api_manager.add_key("gitlab", "token2")
        
        # Check services list
        services = self.api_manager.list_services()
        assert set(services) == {"github", "gitlab"}

    def test_export_redaction(self):
        """Test that exports redact secrets by default."""
        import json
        
        # Add a key
        self.api_manager.add_key("github", "secret_token")
        
        # Export to JSON (should be redacted by default)
        json_path = Path(self.temp_dir) / "export.json"
        self.api_manager.export_db_as_json(str(json_path))
        
        # Check that the export is redacted
        with open(json_path) as f:
            data = json.load(f)
        
        assert "github" in data
        assert data["github"][0]["key"] == "[REDACTED]"

    def test_export_with_secrets(self):
        """Test export with secrets included when configured."""
        import json
        
        # Create config with include_secrets=True
        config_with_secrets = Config(
            profile=None,
            namespace="test",
            db_file_path=self.db_path,
            include_secrets=True,
            backend=self.backend
        )
        api_manager = APIKeyPER(config=config_with_secrets)
        
        # Add a key
        api_manager.add_key("github", "secret_token")
        
        # Export to JSON (should include secrets)
        json_path = Path(self.temp_dir) / "export_with_secrets.json"
        api_manager.export_db_as_json(str(json_path))
        
        # Check that the export includes the key_id (not the actual secret since we store key_id in DB)
        with open(json_path) as f:
            data = json.load(f)
        
        assert "github" in data
        # The database stores the key_id, not the actual secret
        key_value = data["github"][0]["key"]
        assert key_value != "[REDACTED]"
        assert key_value.startswith("test:")  # namespace prefix


class TestConfig:
    """Test configuration functionality."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = Config()
        assert config.namespace == "apikeyper"
        assert config.include_secrets is False
        assert config.profile is None
        assert config.backend is None

    def test_config_from_env(self):
        """Test configuration from environment variables."""
        # Set environment variables
        os.environ["APIKEYPER_PROFILE"] = "test_profile"
        os.environ["APIKEYPER_NAMESPACE"] = "test_namespace"
        os.environ["APIKEYPER_INCLUDE_SECRETS"] = "true"
        
        try:
            config = Config.from_env()
            assert config.profile == "test_profile"
            assert config.namespace == "test_namespace"
            assert config.include_secrets is True
        finally:
            # Clean up environment
            for key in ["APIKEYPER_PROFILE", "APIKEYPER_NAMESPACE", "APIKEYPER_INCLUDE_SECRETS"]:
                os.environ.pop(key, None)

    def test_config_with_backend(self):
        """Test config with backend modification."""
        backend = InMemoryBackend()
        config = Config()
        new_config = config.with_backend(backend)
        
        assert new_config.backend is backend
        assert new_config.namespace == config.namespace  # Other fields preserved
        assert config.backend is None  # Original unchanged