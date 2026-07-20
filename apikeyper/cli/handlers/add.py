from .core import register
from apikeyper import APIKeyPER


@register('add')
def do_add(ns):
    """Add an API key to the database."""
    api = APIKeyPER()
    api.add_key(ns.service, ns.api_key, key_name=ns.key_name)
    print(f"Added API key for service '{ns.service}'.")
    return 0


