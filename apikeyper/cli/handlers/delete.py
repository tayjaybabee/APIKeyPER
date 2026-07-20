from .core import register
from apikeyper import APIKeyPER


@register('delete')
def do_delete(ns):
    """Delete an API key from the database."""
    if not ns.yes:
        confirm = input(f"Delete API key '{ns.key_name}' for service '{ns.service}'? [y/N] ")
        if confirm.strip().lower() not in ('y', 'yes'):
            print('Aborted.')
            return 1

    api = APIKeyPER()
    api.delete_key(ns.service, key_name=ns.key_name)
    print(f"Deleted API key '{ns.key_name}' for service '{ns.service}'.")
    return 0
