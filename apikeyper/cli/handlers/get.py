from argparse import Namespace

from apikeyper import APIKeyPER

from .core import register


@register("get")
def do_get(ns: Namespace) -> int:
    """Get an API key from the database."""
    record = APIKeyPER().get_key(ns.service, ns.key_name)
    if record is None:
        return 1

    print(record.key)
    return 0
