from argparse import Namespace

from apikeyper import APIKeyPER

from .core import register


@register("add")
def do_add(ns: Namespace) -> int:
    """Add an API key to the database."""
    APIKeyPER().add_key(ns.service, ns.api_key, key_name=ns.key_name)
    return 0
