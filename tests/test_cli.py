from argparse import Namespace

import apikeyper
from apikeyper import APIKeyPER
from apikeyper.cli.handlers.add import do_add
from apikeyper.cli.handlers.core import COMMAND_HANDLERS
from apikeyper.cli.handlers.list import do_list
from apikeyper.cli.handlers.revoke import do_revoke
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

    def test_arguments_build_revoke_parser(self):
        parser = Arguments()

        parsed = parser.parse_args(
            ["revoke", "--service", "github", "--key-name", "primary", "-y"]
        )

        assert parsed.command == "revoke"
        assert parsed.service == "github"
        assert parsed.key_name == "primary"
        assert parsed.yes is True

    def test_arguments_build_list_parser(self):
        parser = Arguments()

        parsed = parser.parse_args(["list"])

        assert parsed.command == "list"
        assert parsed.service is None

        parsed = parser.parse_args(["list", "--service", "github"])

        assert parsed.command == "list"
        assert parsed.service == "github"

    def test_handlers_are_registered(self):
        assert {"add", "delete", "get", "revoke", "list"}.issubset(COMMAND_HANDLERS)

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

    def test_revoke_handler_revokes_key(self, tmp_path, monkeypatch):
        db_path = tmp_path / "cli.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", db_path)

        do_add(
            Namespace(service="github", api_key="ghp_cli_token", key_name="primary")
        )

        result = do_revoke(
            Namespace(service="github", key_name="primary", yes=True)
        )

        assert result == 0
        record = APIKeyPER(db_path).get_key("github", "primary", only_active=False)
        assert record is not None
        assert record.status == "revoked"
        assert record.revoked_on is not None
        # Revoked keys are hidden from active lookups.
        assert APIKeyPER(db_path).get_key("github", "primary") is None

    def test_revoke_handler_missing_key_returns_1(self, tmp_path, monkeypatch, capsys):
        db_path = tmp_path / "cli.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", db_path)

        result = do_revoke(
            Namespace(service="github", key_name="nope", yes=True)
        )

        assert result == 1
        assert "Error" in capsys.readouterr().out

    def test_list_handler_lists_services(self, tmp_path, monkeypatch, capsys):
        db_path = tmp_path / "cli.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", db_path)

        do_add(Namespace(service="github", api_key="ghp_1", key_name="primary"))
        do_add(Namespace(service="openai", api_key="sk-1", key_name="primary"))

        result = do_list(Namespace(service=None))

        assert result == 0
        out = capsys.readouterr().out
        assert "github" in out
        assert "openai" in out

    def test_list_handler_lists_keys_for_service_without_secrets(
        self, tmp_path, monkeypatch, capsys
    ):
        db_path = tmp_path / "cli.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", db_path)

        do_add(Namespace(service="github", api_key="ghp_super_secret", key_name="primary"))
        do_revoke(Namespace(service="github", key_name="primary", yes=True))

        result = do_list(Namespace(service="github"))

        assert result == 0
        out = capsys.readouterr().out
        assert "primary" in out
        assert "revoked" in out
        # Key material must never be printed.
        assert "ghp_super_secret" not in out

    def test_list_handler_unknown_service_returns_1(
        self, tmp_path, monkeypatch, capsys
    ):
        db_path = tmp_path / "cli.db"
        monkeypatch.setattr(apikeyper, "DEFAULT_DB_FILEPATH", db_path)

        result = do_list(Namespace(service="nope"))

        assert result == 1
        assert "No keys found" in capsys.readouterr().out
