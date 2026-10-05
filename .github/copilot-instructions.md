# APIKeyPER Copilot Instructions

## Project Overview

APIKeyPER is a Python package for securely storing and retrieving API keys. The
main public interface is `apikeyper.APIKeyPER`, which wraps the database layer
and is the interface used in the README examples.

## Key Files

- `apikeyper/__init__.py`: public API surface.
- `apikeyper/__about__.py`: package metadata and default data directory.
- `apikeyper/database/`: storage layer.
- `apikeyper/crypt/`: encryption key logic.
- `apikeyper/utils/decorators.py`: decorators that require or inject API keys.
- `apikeyper/config/arguments.py`: CLI argument parsing.
- `tests/`: API, decorator, export, and README example coverage.

## Contribution Guidance

- Prefer small edits that fit the current package structure.
- Keep behavior changes explicit and update tests when public behavior changes.
- Keep `pyproject.toml` and `setup.py` version metadata aligned if versioning is
  touched.
- Update `README.md` if public usage or examples change.

## Security Guidance

- Never introduce real secrets into code, docs, tests, logs, or fixtures.
- Avoid suggestions that print, log, or expose stored API keys unless the code
  already does so intentionally and safely.
- Use obvious placeholders such as `sk-example-not-real` in examples.

## Validation

Recommended validation command:

```bash
poetry run pytest
```
