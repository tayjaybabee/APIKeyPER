from argparse import Namespace

import apikeyper
from apikeyper import APIKeyPER
from apikeyper.cli.handlers.add import do_add
from apikeyper.cli.handlers.core import COMMAND_HANDLERS
from apikeyper.config.arguments import Arguments


class TestCLI:
    def test_arguments_build_delete_parser(self):
        parser = Arguments()

        parsed = parser.parse_args(
            ["delete", "--service", "github", "--key-name", "primary", "-y"]
        )

        assert parsed.command == "delete"
        assert parsed.service == "github"
        assert parsed.key_name == "primary"
        assert parsed.yes is True

    def test_handlers_are_registered(self):
        assert {"add", "delete", "get"}.issubset(COMMAND_HANDLERS)

    def test_add_handler_persists_key(self, tmp_path, monkeypatch):
        db_path = tmp_path / "cli.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", db_path)

        result = do_add(
            Namespace(service="github", api_key="ghp_cli_token", key_name="primary")
        )

        record = APIKeyPER(db_path).get_key("github", "primary")

        assert result == 0
        assert record is not None
        assert record.key == "ghp_cli_token"
