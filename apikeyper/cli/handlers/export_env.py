from argparse import Namespace
import os
import re
import shlex
import sys

from apikeyper import APIKeyPER
from apikeyper.env_names import is_env_name

from .core import register


@register("export-env")
def do_export_env(ns: Namespace) -> int:
    """Export active keys to a shell or to the Windows user environment."""
    if ns.name is not None and not is_env_name(ns.name):
        print("Invalid environment variable name. Set a valid name with --name.", file=sys.stderr)
        return 1
    if ns.all and ns.name is not None:
        print("--name requires a single-key export.", file=sys.stderr)
        return 1
    if ns.user and os.name != "nt":
        print("--user is available on Windows. Use --shell for a shell assignment.", file=sys.stderr)
        return 1

    api = APIKeyPER()
    try:
        service = api.service(ns.service)
        if ns.all:
            records = [record for record in service.list_keys() if record.status == "active"]
        else:
            record = service.get_key(ns.key_name)
            records = [record] if record is not None else []
    finally:
        api.db.close()
    if not records:
        print("No matching active key found.", file=sys.stderr)
        return 1
    try:
        assignments = [
            (ns.name or record.get_env_name(prefix=ns.prefix), record.key)
            for record in records
        ]
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if len({name.casefold() for name, _ in assignments}) != len(assignments):
        print("Key names resolve to the same environment variable. Export them separately with --name.", file=sys.stderr)
        return 1
    if any("\0" in value for _, value in assignments):
        print("Environment variables cannot contain null characters.", file=sys.stderr)
        return 1

    shell = ns.shell or ("powershell" if os.name == "nt" else "sh")
    for name, value in assignments:
        if ns.user:
            try:
                _set_windows_user_variable(name, value)
            except OSError:
                print(f"Could not write Windows user environment variable {name}.", file=sys.stderr)
                return 1
            print(f"Saved {name} to the Windows user environment.")
        elif shell == "powershell":
            quoted = re.sub(r"['\u2018\u2019\u201a\u201b]", lambda match: match[0] * 2, value)
            print(f"$env:{name} = '{quoted}'")
        else:
            print(f"export {name}={shlex.quote(value)}")
    return 0


def _set_windows_user_variable(name: str, value: str) -> None:
    import winreg

    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
