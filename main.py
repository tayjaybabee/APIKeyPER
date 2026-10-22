from apikeyper.cli import handlers  # noqa: F401
from apikeyper.cli.handlers.core import COMMAND_HANDLERS
from apikeyper.config.arguments import ARGUMENTS


def main() -> int:
    args = ARGUMENTS.parse(force=True)
    handler = COMMAND_HANDLERS.get(args.command)
    if handler is None:
        ARGUMENTS.error(f"Unsupported command: {args.command}")

    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
