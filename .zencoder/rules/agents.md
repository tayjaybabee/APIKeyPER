---
description: APIKeyPER agent guidance
alwaysApply: true
---

# APIKeyPER Agent Guidance

## Overview

APIKeyPER is a Python package for managing API keys in an encrypted local data
store. The project exposes a simple high-level wrapper class and also includes
CLI, UI, encryption, and decorator helpers.

## Main Components

### Public API

- `apikeyper.APIKeyPER` in `apikeyper/__init__.py` is the main entry point.
- README examples should remain consistent with this API surface.

### Storage and Encryption

- `apikeyper/database/` handles storage and retrieval.
- `apikeyper/crypt/` handles encryption key concerns.

### User-Facing Flows

- `apikeyper/config/arguments.py` builds CLI arguments.
- `apikeyper/cli/` and `apikeyper/ui/` contain command and interface code.

### Tests

- `tests/test_api.py` covers core API behavior.
- `tests/test_decorators.py` covers decorator behavior.
- `tests/test_exports.py` and `tests/test_readme_examples.py` help catch public
  API drift.

## Best Practices

1. Keep changes small and repository-specific.
2. Add or update tests when changing public behavior.
3. Update `README.md` when public examples or usage change.
4. Do not expose real secrets in code, docs, or logs.
