from argparse import Namespace

from apikeyper import APIKeyPER

from .core import register


@register("add")
def do_add(ns: Namespace) -> int:
    """Add an API key to the database."""
    try:
        APIKeyPER().add_key(
            ns.service, ns.api_key, key_name=ns.key_name, key_id=getattr(ns, "key_id", None)
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    return 0
