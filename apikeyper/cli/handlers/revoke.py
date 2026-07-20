from .core import register
from apikeyper import APIKeyPER


@register('revoke')
def do_revoke(ns):
    """Revoke an API key for a service without deleting it."""
    api = APIKeyPER()
    try:
        api.revoke_key(ns.service, ns.key_name)
    except ValueError as e:
        print(str(e))
        return 1

    print(f"Revoked API key '{ns.key_name}' for service '{ns.service}'.")
    return 0
