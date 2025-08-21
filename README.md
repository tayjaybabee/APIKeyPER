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
github_key_data = api.get_key("github")
if github_key_data:
    actual_key = github_key_data[3]  # The key is at index 3 in the tuple
    print(f"GitHub API Key: {actual_key}")

# List all services with stored keys
services = api.list_services()
print(f"Services with API keys: {services}")

# Delete a key
api.delete_key("aws")
```

### 2. Encryption and Security

- **Encryption Key Management**: Manage encryption keys through file, system keyring, or SFTP server.
- **Encryption Key Export**: Export the encryption key to a file, system keyring, or SFTP server.


## 3. Decorators for API Key Requirements

APIKeyPER provides decorators to ensure that the required API keys are available for specific services. These can be
applied at both the function and class levels.

### Function-level Decorator: `apikey_required`

Ensure API keys are available for specific services at the function level.

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

The `apikey_required_class` decorator ensures that the required API keys are available when an instance of the decorated
class is created. If a key is not found in the database, it prompts the user for input and saves the provided key. It
then sets the API key as a class attribute.

#### Example Usage of `apikey_required_class`:

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
