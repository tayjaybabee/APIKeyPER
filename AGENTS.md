# APIKeyPER Agent Guide

## Overview

APIKeyPER is a Python package for storing and retrieving API keys in an
encrypted local database. The main public entry point is `apikeyper.APIKeyPER`,
which wraps the lower-level database layer and exposes add/get/delete/list
operations for service keys.

## Repository Structure

- `apikeyper/__init__.py`: public `APIKeyPER` wrapper used by README examples.
- `apikeyper/__about__.py`: package metadata and default data directory.
- `apikeyper/database/`: database access and default database path handling.
- `apikeyper/crypt/`: encryption key management.
- `apikeyper/utils/decorators.py`: decorators that require or inject API keys.
- `apikeyper/config/arguments.py`: CLI argument construction.
- `apikeyper/cli/` and `apikeyper/ui/`: CLI and interactive user-facing flows.
- `main.py`: script entry point referenced by Poetry.
- `tests/`: regression coverage for API behavior, decorators, exports, and README
  examples.

## Development Notes

- Python version target: `^3.10` (see `pyproject.toml`).
- Dependency management uses Poetry.
- Packaging metadata currently lives in both `pyproject.toml` and `setup.py`;
  keep the version aligned if it changes.
- The repo contains generated and local-state files such as `app.log`,
  `default_apikeys.db`, and `__pycache__/`. Do not treat them as authoritative
  source material when making code changes.

## Security Rules

- Never commit real API keys, encryption keys, exported secrets, or machine-
  specific database contents.
- Never add logs, examples, fixtures, or tests that contain live credentials.
- Avoid printing or logging sensitive key material. Redact or mask secret values
  in debug output and user-facing errors.
- When writing docs, examples, or issue templates, use obviously fake tokens.

## Contribution Expectations

- Prefer small, targeted changes that preserve existing public behavior unless a
  behavior change is intentional and documented.
- Add or update tests when changing public API behavior, decorator behavior,
  storage behavior, or CLI parsing.
- Update `README.md` when changing public usage, constructor behavior, or
  example code.
- If CLI flows change, keep `main.py`, `apikeyper/config/arguments.py`, and any
  handler modules aligned.

## Validation

Typical local validation:

```bash
poetry install
poetry run pytest
```

If you touch packaging or exports, also sanity-check the examples in
`README.md` and the tests that cover them.
