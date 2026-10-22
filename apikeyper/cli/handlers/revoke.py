from argparse import Namespace

from apikeyper import APIKeyPER

from .core import register


@register("revoke")
def do_revoke(ns: Namespace) -> int:
    """Revoke an API key for a service without deleting it."""
    try:
        APIKeyPER().revoke_key(ns.service, ns.key_name)
    except ValueError:
        return 1

    return 0
