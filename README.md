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


## 3. Decorators for API Key Requirements

APIKeyPER provides decorators to ensure that the required API keys are available for specific services. These can be
applied at both the function and class levels.

### Function-level Decorator: `apikey_required`

Ensure API keys are available for specific services at the function level.

### Class-level Decorator: `apikey_required_class`

The `apikey_required_class` decorator ensures that the required API keys are available when an instance of the decorated
class is created. If a key is not found in the database, it prompts the user for input and saves the provided key. It
then sets the API key as a class attribute.

#### Example Usage of `apikey_required_class`:

```python
from apikeyper.utils.decorators import apikey_required_class

@apikey_required_class(["service1", "service2"])
class MyClass:
    def __init__(self, service1, service2):
        self.service1_key = service1
        self.service2_key = service2

    def use_keys(self):
        print(f"Using keys: {self.service1_key}, {self.service2_key}")

# When an instance of MyClass is created, the decorator ensures that the keys for "service1" and "service2" are available.
# If not found, it prompts the user for input and saves the keys.
my_instance = MyClass()

# The keys are now available as class attributes and can be used within the class methods.
my_instance.use_keys()
```

In this example, the `apikey_required_class` decorator is applied to the `MyClass` class, requiring keys for "service1"
and "service2". When an instance of `MyClass` is created, the decorator ensures that the keys are available, either
retrieving them from the database or prompting the user for input. The keys are then set as class attributes and can be
used within the class methods.
