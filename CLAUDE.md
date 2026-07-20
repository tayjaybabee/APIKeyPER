# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

APIKeyPER ("API Key Personal Encrypted Reliquary") is a Python package for storing and retrieving
API keys in a local SQLite database. The public entry point is `apikeyper.APIKeyPER`
(`apikeyper/__init__.py`), a thin wrapper around the lower-level `APIKeyDB` class
(`apikeyper/database/__init__.py`) that does the actual SQLite work.

## Commands

Dependency management is via Poetry (`pyproject.toml`), though packaging metadata is duplicated in
`setup.py`/`requirements.txt` — keep versions aligned across all three if you touch packaging.

```bash
poetry install
poetry shell
poetry run pytest              # run the full test suite
poetry run pytest tests/test_api.py            # single file
poetry run pytest tests/test_api.py::TestAPIKeyPER::test_add_and_get_key   # single test
poetry run apikeyper add --service github --api-key sk-example-not-real    # exercise the CLI manually
```

CI runs two workflows on push/PR: `.github/workflows/code_quality.yml` (JetBrains Qodana static
analysis) and `.github/workflows/tests.yml` (`poetry install` + `poetry run pytest`).

## Architecture

- `apikeyper/__init__.py` — `APIKeyPER`, the public wrapper class used in README examples.
  Converts `APIKey` dataclass instances to/from plain tuples (`add_key`, `get_key`, `delete_key`,
  `list_services`). `get_key` returns a tuple ordered `(service, key_name, added, key, status,
  revoked_on)` — the raw key material is always at index `3`. `add_key` auto-generates a
  `key_name` (`f"{service}_key_{uuid4().hex[:8]}"`) when none is given, so calls without
  `key_name` never collide with `INSERT OR REPLACE` — you have to pass the same `key_name`
  explicitly to overwrite a row. `revoke_key(service, key_name, revoked_on=None)` wraps
  `APIKeyDB.revoke_key` and is reachable from the CLI via `apikeyper revoke --service ... --key-name
  ...` (`apikeyper/cli/handlers/revoke.py`); unlike `delete`, `revoke` never prompts for
  confirmation since it doesn't remove data.
- `apikeyper/database/__init__.py` — `APIKeyDB`, the SQLite layer. Single table `apikeys` keyed on
  `(service, key_name)`. `add_key` uses `INSERT OR REPLACE`, so re-adding the same
  `(service, key_name)` pair silently overwrites the prior row. `get_key` with `key_name=None`
  returns the most recently *added* active row (`ORDER BY added DESC LIMIT 1`), not necessarily
  the one you expect if a service has several active keys. `delete_key` with `key_name=None`
  deletes **every** key for that service — the CLI's `delete` subcommand always requires
  `--key-name` (see `arguments.py`), so this all-keys path is only reachable by calling
  `APIKeyPER`/`APIKeyDB` directly. Also has JSON/XML export (`export_db_as_json`/
  `export_db_as_xml`, secrets redacted by default) and `revoke_key` (sets `status='revoked'` +
  `revoked_on`, raises `ValueError` if the key doesn't exist or is already revoked).
- `apikeyper/__about__.py` — package metadata; defines `__DEFAULT_DATA_DIR__` via
  `appdirs.user_data_dir`, which both the DB default path and the encryption key default path
  derive from.
- `apikeyper/crypt/encryption_key.py` — `EncryptionKey` and Fernet key retrieval/export via file,
  system keyring, or SFTP (`paramiko`/`keyring` are imported lazily via `importlib.import_module`,
  so they're only required if that storage method is actually used). **This module is not wired
  into `APIKeyDB`** — API keys are currently stored in plaintext in the SQLite `key` column
  despite the encryption infrastructure existing separately. Don't assume stored keys are
  encrypted at rest.
- `apikeyper/utils/decorators.py` — `apikey_required` (function decorator) and
  `apikey_required_class` (class decorator). Both prompt interactively via `input()` for missing
  keys and persist them, and both hardcode the DB path to `Path("default_apikeys.db")` (relative
  to CWD) rather than using the package's default data directory — this is inconsistent with
  `APIKeyPER`'s own default and worth flagging if touched.
- `apikeyper/log_engine/` — `Logger` (singleton-per-name, Rich console + file handlers) and
  `Loggable`, a mixin that gives a class a `self.log_device` derived from a parent logger's
  `get_child()`. Used across the database and CLI modules for structured logging.
- `apikeyper/config/arguments.py` — `Arguments(ArgumentParser)` builds the `add`/`delete`/`get`
  subcommands; the module-level singleton `ARGUMENTS` is built once at import time.
  `ARGUMENTS.parse()` caches the parsed `Namespace` and only reparses `sys.argv` when called with
  `force=True` — calling `.parse()` more than once per process (e.g. in a test that invokes `main()`
  multiple times without `force=True`) returns the *first* parse, not a fresh one.
- `apikeyper/cli/handlers/` — `core.py` defines the `@register(command)` decorator and the
  `COMMAND_HANDLERS` dispatch dict; `add.py`/`get.py`/`delete.py`/`revoke.py` register handlers for
  each subcommand and go through the `APIKeyPER` wrapper (not `APIKeyDB` directly). Importing
  `apikeyper.cli.handlers` (done once, in `main.py`) is what triggers registration — a handler
  module that isn't imported from `handlers/__init__.py` never populates `COMMAND_HANDLERS`.
- `main.py` — the Poetry script entry point (`main:main`). Resolves the parsed subcommand against
  `COMMAND_HANDLERS` and calls it.
- `apikeyper/ui/cli.py` — unused stub (imports `npyscreen`/`datetime`, defines nothing). Not wired
  into `main.py`; treat as dead scaffolding, not a working alternate UI.

## Repository notes

- `default_apikeys.db` and `app.log` in the repo root are local runtime state, not fixtures —
  don't treat their contents as sample/reference data.
- Update `README.md` when public usage, constructor behavior, or example code changes; the test
  suite (`tests/test_readme_examples.py`) checks README examples stay runnable.
- Add or update tests under `tests/` when changing public API behavior, decorator behavior,
  storage behavior, or CLI parsing.

## Security

- Never commit real API keys, encryption keys, exported secrets, or machine-specific database
  contents.
- Use obviously fake tokens (e.g. `sk-example-not-real`) in docs, examples, and tests.
- Keep `redact_secrets=True` behavior intact in the export functions; don't add code paths that
  print or log raw key material.
