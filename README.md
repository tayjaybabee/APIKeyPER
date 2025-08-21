# APIKeyPER

APIKeyPER is a Python-based project developed by Inspyre Softworks. It provides a simple and efficient way to manage API
keys associated with various services. The project is designed to store, retrieve, and manage API keys in a **secure** and
organized manner using encryption backends.

## Features

### 1. Secure API Key Management

- **Encrypted Storage**: API keys are stored using secure backends (system keyring by default)
- **Metadata-Only Database**: Only metadata is stored in SQLite; actual secrets are encrypted separately  
- **Add API Keys**: Add API keys associated with a specific service
- **Retrieve API Keys**: Retrieve API keys associated with a specific service
- **Delete API Keys**: Delete API keys associated with a specific service
- **List Services**: List all the services for which API keys are stored

### 2. Security and Encryption

- **System Keyring Integration**: Uses your system's secure keyring (Windows Credential Manager, macOS Keychain, etc.)
- **Pluggable Backends**: Support for different encryption backends including in-memory for testing
- **Secret Redaction**: Automatic redaction of secrets in logs and exports
- **No Plaintext Storage**: Secrets are never stored in plaintext in the database

### 3. Configuration System

APIKeyPER uses a centralized configuration system that supports environment variables:

```python
from apikeyper.config import Config
from apikeyper import APIKeyPER

# Use default configuration (reads from environment)
api_manager = APIKeyPER()

# Or create custom configuration
config = Config(
    namespace="myapp",
    profile="production", 
    include_secrets=False  # Redact secrets in exports
)
api_manager = APIKeyPER(config=config)
```

#### Environment Variables

- `APIKEYPER_PROFILE`: Profile name for multi-profile support
- `APIKEYPER_NAMESPACE`: Namespace for keyring storage (default: 'apikeyper')
- `APIKEYPER_DB_PATH`: Custom database file path
- `APIKEYPER_INCLUDE_SECRETS`: Include secrets in exports ('true'/'false', default: 'false')

### 4. Decorators for API Key Requirements

APIKeyPER provides decorators to ensure that the required API keys are available for specific services. These decorators now support the new configuration system.

#### Function-level Decorator: `apikey_required`

```python
from apikeyper.utils.decorators import apikey_required

@apikey_required(["github", "openai"])
def my_function(api_keys):
    # api_keys dict contains the required keys
    github_token = api_keys["github"]
    openai_key = api_keys["openai"]
    # Your code here
```

#### Class-level Decorator: `apikey_required_class`

```python
from apikeyper.utils.decorators import apikey_required_class

@apikey_required_class(["github", "openai"])
class MyAPIClient:
    def __init__(self):
        # Keys are automatically available as class attributes
        pass
    
    def make_request(self):
        # Access keys via class attributes
        github_token = self.GITHUB_API_KEY
        openai_key = self.OPENAI_API_KEY
        # Your code here
```

#### Using Custom Configuration with Decorators

```python
from apikeyper.config import Config
from apikeyper.utils.decorators import apikey_required

# Create custom config
config = Config(namespace="myapp", profile="dev")

@apikey_required(["github"], config=config)
def deploy_code(api_keys):
    # Uses the custom configuration
    pass
```

## Security Considerations

- **System Keyring**: By default, APIKeyPER uses your system's secure keyring to store API keys
- **No Plaintext Storage**: API keys are never stored in plaintext in the database
- **Redacted Exports**: Exports redact secrets by default to prevent accidental exposure
- **Configurable Security**: Use environment variables or Config objects to control security settings

## Installation

```bash
pip install cryptography keyring appdirs rich prompt-toolkit
```

## Basic Usage

```python
from apikeyper import APIKeyPER

# Initialize with default configuration
api_manager = APIKeyPER()

# Add an API key
api_manager.add_key("github", "ghp_your_token_here")

# Retrieve an API key
github_token = api_manager.get_key("github")

# List all services
services = api_manager.list_services()

# Export database (secrets redacted by default)
api_manager.export_db_as_json("backup.json")
```

## Testing

APIKeyPER includes a test suite using pytest:

```bash
pytest tests/ -v
```

The tests use an in-memory backend to avoid touching your real keyring during testing.
