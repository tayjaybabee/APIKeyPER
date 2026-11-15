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
- **List Keys**: List key names and statuses for a service without displaying key values.
- **Revoke Keys**: Mark a key inactive without deleting its record.

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
    actual_key = github_key_data.key
    print(f"GitHub API Key: {actual_key}")

# List all services with stored keys
services = api.list_services()
print(f"Services with API keys: {services}")

# List a service's key records (key values are not displayed)
keys = api.list_keys_for_service("github")
print([(key[1], key[4]) for key in keys])

# Revoke a key without deleting its record
api.revoke_key("github", "primary")

# Delete a key
api.delete_key("aws")
```

Use `api.add_service(name)` to register a service and get a `Service` object.
Registered services appear in `list_services()` even when they have no keys.
Use `api.service(name)` to get a handle for a name without registering it.
`api.get_service(name)` returns a single `Service` for an exact,
case-sensitive match. For other queries it logs a warning through InspyLogger and returns
a list of suggestions based on case-insensitive partial matches and similar
spellings. The list is empty if there are no suggestions.
`add_key()`, `get_key()`, and `list_keys()` provide `APIKey` records with metadata such as
`key_name` and `status`. Access the credential explicitly through `.key`.

```python
home = api.add_service("Home Assistant")
record = home.add_key("fake_home_assistant_token", key_name="primary")
token = record.key
```

The `added` and `revoked_on` fields use comparable `Date` objects. For
example, `Date("9/20/2023") == Date("2023-09-20T00:00:00Z")` after importing
`Date` from `apikeyper`. Common formats include ISO 8601, slash-separated
dates, English month names, and RFC-style timestamps. Ambiguous slash dates
use month-first order. Dates without a timezone use UTC.

`was_defaulted` is read-only and records whether APIKeyPER supplied the
current time. Existing stored timestamps carry no default history and are
treated as supplied. A missing revocation date remains `None`. Invalid
nonblank date strings raise `ValueError`.

For providers such as Wyze, store the token and provider-assigned Key ID
together. `key_name` is the local label. Read the token through `record.key`
and the optional ID through `record.key_id`. Default exports redact both.

```python
wyze = api.add_service("Wyze", require_key_id=True)
record = wyze.add_key(
    "fake_wyze_token",
    key_name="primary",
    key_id="example-provider-key-id",
)
```

Change the requirement by assigning `wyze.require_key_id = False` or
`wyze.require_key_id = True`. The setting is saved immediately and applies
to subsequent writes, including replacements. Existing keys stay readable.
`api.add_key(service, ...)` registers the service before adding the key.
Registered services stay listed after their last key is deleted.

### CLI Usage

Use `--key-id` on `apikeyper add` when the provider supplies a Key ID.

`export-env` exports the latest active token for a service. Use `--key-name`
to pick a specific active key. The default variable for `Home Assistant` is
`HOME_ASSISTANT_API_KEY`. Use `--prefix MY_APP` for `MY_APP_API_KEY`, or
`--name HASS_TOKEN` to set the full name.

Set `service.env_prefix = "MY_HOME"` in Python to save a prefix for future
exports. Assign `None` to restore the service name as the prefix. A loaded
`APIKey` exposes its resolved default as `record.env_name`. Reload the
record after changing the prefix or the set of active keys.

When the service has multiple active keys, the default includes the key
name, for example `MY_HOME_PRIMARY_API_KEY`. Use `export-env --all` with
`--service` to export all active keys. `--prefix` and `--name` are
overrides for the current command.

Load the variable into your current PowerShell session and its child processes.

```powershell
$assignment = apikeyper export-env --service "Home Assistant" --shell powershell
if ($LASTEXITCODE -eq 0) { Invoke-Expression ($assignment -join [Environment]::NewLine) }
```

For Bash or another POSIX shell, use the shell's `eval`.

```sh
assignment=$(apikeyper export-env --service "Home Assistant" --shell sh) &&
    eval "$assignment"
```

On Windows, use `--user` to save the variable to your account's environment
without printing the token. Sign out and back in to load it across applications.
This replaces any existing user variable with the same name.

```powershell
apikeyper export-env --service "Home Assistant" --name HASS_TOKEN --user
```

Shell assignments contain the token in plaintext. Windows user variables also
store the exported value in plaintext. The regular CLI store currently uses
SQLite text fields. Fernet encryption is available separately through `CryptDB`.

List all services, or list the key names and statuses for one service:

```console
apikeyper list
apikeyper list --service github
```

Revoke a key by service and key name. The command asks for confirmation unless
`--yes` (or `-y`) is provided:

```console
apikeyper revoke --service github --key-name primary
apikeyper revoke --service github --key-name primary --yes
```

### 2. Encryption and Security

- **Encryption Key Management**: Manage encryption keys through file, system keyring, or SFTP server.
  `CryptDB` creates or reuses `key.pem` in the per-user APIKeyPER data directory
  when constructed without an explicit encryption key.
- **Encryption Key Export**: Export the encryption key to a file, system keyring, or SFTP server.


## 3. Decorators for API Key Requirements

APIKeyPER provides decorators to ensure that the required API keys are available for specific services. These can be
applied at both the function and class levels.
Both decorators use the same per-user database as the `apikeyper` CLI.

### Function-level Decorator: `apikey_required`

For a single service, declare an `api_key` parameter to receive the stored key
directly. It can be a regular or keyword-only parameter. An explicitly passed
`api_key` value takes precedence over injection.

```python
from apikeyper.utils.decorators import apikey_required

@apikey_required("Home Assistant")
def my_func(api_key):
    return api_key

key = my_func()
```

For multiple services, use the `api_keys` mapping.

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
