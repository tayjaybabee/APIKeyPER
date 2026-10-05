from argparse import Namespace

from apikeyper import APIKeyPER

from .core import register


@register("list")
def do_list(ns: Namespace) -> int:
    """List all services, or the keys stored for one service.

    Key values are never printed; only key names and their status.
    """
    api = APIKeyPER()

    if ns.service:
        rows = api.list_keys_for_service(ns.service)
        if not rows:
            print(f"No keys found for service '{ns.service}'.")
            return 1

        for _service, key_name, _added, _key, status, revoked_on in rows:
            line = f"{key_name} [{status}]"
            if revoked_on:
                line += f" (revoked {revoked_on})"
            print(line)
    else:
        for service in api.list_services():
            print(service)

    return 0
