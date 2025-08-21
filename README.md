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

#### Basic API Usage Example:

```python
from apikeyper import APIKeyPER
from pathlib import Path

# Initialize APIKeyPER with a database file
api = APIKeyPER(Path("my_api_keys.db"))

# Add API keys for different services
api.add_key("github", "ghp_your_github_token_here")
api.add_key("openai", "sk-your_openai_key_here")
api.add_key("aws", "AKIAIOSFODNN7EXAMPLE")

# Retrieve an API key
github_key = api.get_key("github")
if github_key:
    print(f"GitHub API Key: {github_key}")

# List all services with stored keys
services = api.list_services()
print(f"Services with API keys: {services}")

# Delete a key
api.delete_key("aws")
```

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

#### Example Usage of `apikey_required`:

```python
from apikeyper.utils.decorators import apikey_required

@apikey_required(["github", "openai"])
def my_function(**kwargs):
    # The decorator injects an 'api_keys' parameter containing the requested keys
    api_keys = kwargs.get("api_keys", {})
    github_key = api_keys["github"]
    openai_key = api_keys["openai"]
    
    print(f"GitHub API Key: {github_key}")
    print(f"OpenAI API Key: {openai_key}")
    
    # Your function logic here
    return "Function executed successfully"

# When the function is called, the decorator ensures the required API keys are available
result = my_function()
```

### Class-level Decorator: `apikey_required_class`

```python
from apikeyper.utils.decorators import apikey_required_class

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
        print(f"Using keys: {service1_key}, {service2_key}")
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
