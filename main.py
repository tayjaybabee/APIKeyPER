from apikeyper.config.arguments import ARGUMENTS
from apikeyper.cli.handlers import COMMAND_HANDLERS


def main() -> int:
    args = ARGUMENTS.parse()
    handler = COMMAND_HANDLERS[args.command]
    return handler(args) or 0


if __name__ == '__main__':
    raise SystemExit(main())
