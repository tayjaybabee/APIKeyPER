from argparse import Namespace

from apikeyper import APIKeyPER

from .core import register


@register("delete")
def do_delete(ns: Namespace) -> int:
    """Delete an API key from the database."""
    if not ns.yes:
        answer = input(
            f"Delete API key '{ns.key_name}' for service '{ns.service}'? [y/N]: "
        ).strip().lower()
        if answer not in {"y", "yes"}:
            return 1

    APIKeyPER().delete_key(ns.service, ns.key_name)
    return 0
