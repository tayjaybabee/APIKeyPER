from .core import register
from apikeyper import APIKeyPER


@register('get')
def do_get(ns):
    """Retrieve an API key from the database."""
    api = APIKeyPER()
    result = api.get_key(ns.service, key_name=ns.key_name)
    if result is None:
        print(f"No active API key found for service '{ns.service}'.")
        return 1

    print(result[3])
    return 0
