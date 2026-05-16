---
description: APIKeyPER repository overview
alwaysApply: true
---

# APIKeyPER Repository Overview

## Summary

APIKeyPER is a Python package for storing, retrieving, and managing API keys in
an encrypted local database.

## Structure

- `apikeyper/`: main package
  - `database/`: storage layer
  - `crypt/`: encryption helpers
  - `config/`: CLI argument definitions
  - `cli/`: command handlers
  - `ui/`: user-facing interface helpers
  - `utils/`: shared helpers and decorators
- `tests/`: automated regression coverage
- `.github/`: CI and contribution templates

## Runtime and Tooling

- Language: Python
- Python target: 3.10+
- Dependency management: Poetry
- Packaging metadata: `pyproject.toml` and `setup.py`

## Validation

```bash
poetry install
poetry run pytest
```

## Security

- Never include real API keys or encryption secrets in repository content.
- Treat local files such as `default_apikeys.db` and `app.log` as local state,
  not sample data.
