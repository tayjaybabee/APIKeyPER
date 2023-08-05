# APIKeyPER

APIKeyPER is a Python-based project developed by Inspyre Softworks. It provides a simple and efficient way to manage API
keys associated with various services. The project is designed to store, retrieve, and manage API keys in a secure and
organized manner.

## Features

### 1. API Key Management

- **Add API Keys**: Add API keys associated with a specific service.
- **Retrieve API Keys**: Retrieve API keys associated with a specific service.
- **Delete API Keys**: Delete API keys associated with a specific service.
- **List Services**: List all the services for which API keys are stored.

### 2. Encryption and Security

- **Encryption Key Management**: Manage encryption keys through file, system keyring, or SFTP server.
- **Encryption Key Export**: Export the encryption key to a file, system keyring, or SFTP server.

### 3. Decorators for API Key Requirements

- **Function-level Decorator**: Ensure API keys are available for specific services.
- **Class-level Decorator**: Ensure API keys are available for specific services when an instance is created.

## How to Use

### Example Usage of APIKeyPER Class:

```python
from apikeyper import APIKeyPER

# Initialize APIKeyPER with a database file path
api_key_per = APIKeyPER('path_to_your_database_file')

# Add an API key
api_key_per.add_key('service_name', 'api_key')

# Get an API key
api_key = api_key_per.get_key('service_name')
print(api_key)
```

### Example Usage of Decorators:

```python
from apikeyper.utils.decorators import apikey_required, apikey_required_class

@apikey_required(["service1", "service2"])
def my_function():
    pass

@apikey_required_class(["service1", "service2"])
class MyClass:
    pass
```
