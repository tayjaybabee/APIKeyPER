from argparse import Namespace

from apikeyper import APIKeyPER

from .core import register


@register("revoke")
def do_revoke(ns: Namespace) -> int:
    """Revoke an API key, marking it inactive without deleting it."""
    if not ns.yes:
        answer = input(
            f"Revoke API key '{ns.key_name}' for service '{ns.service}'? [y/N]: "
        ).strip().lower()
        if answer not in {"y", "yes"}:
            return 1

    try:
        APIKeyPER().revoke_key(ns.service, ns.key_name)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    return 0
