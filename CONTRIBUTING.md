# Contributing to APIKeyPER

Thank you for your interest in contributing. This document follows the same
repo-carried guidance style used in `IS-Matrix-Forge`, adapted for APIKeyPER's
package layout and security needs.

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork locally.
3. Create a branch for your work.

```bash
git clone https://github.com/<your-username>/APIKeyPER.git
cd APIKeyPER
git checkout -b your-feature-or-fix
```

## Development Setup

This project uses Poetry for dependency management.

```bash
poetry install
poetry shell
```

Python `3.10` is the current target version declared in `pyproject.toml`.

## Repository Layout

- `apikeyper/__init__.py`: public package interface.
- `apikeyper/database/`: persistent storage and retrieval.
- `apikeyper/crypt/`: encryption key handling.
- `apikeyper/utils/decorators.py`: decorators that enforce API key
  availability.
- `apikeyper/config/arguments.py`: CLI parser construction.
- `apikeyper/cli/` and `apikeyper/ui/`: user-facing command and interface code.
- `tests/`: regression coverage and README example verification.

## Running Tests

```bash
poetry run pytest
```

Tests live in `tests/`. If you change public API behavior, decorator behavior,
CLI parsing, or README examples, add or update tests in the same change.

## Security Expectations

Because this project handles secrets, security hygiene is part of every
contribution:

- Never commit real API keys, encryption keys, or exported secrets.
- Never check in local databases, secret dumps, or machine-specific logs as
  fixtures.
- Redact sensitive values in examples, screenshots, issue reports, and debug
  output.
- Prefer fake placeholder tokens in docs and tests.

## Submitting Changes

1. Keep changes scoped and explain why they are needed.
2. Ensure tests pass after your changes.
3. Update documentation when public behavior changes.
4. Open a Pull Request against the default branch and fill out the PR template.

## Packaging Notes

Version metadata currently appears in both `pyproject.toml` and `setup.py`.
When changing the version, keep both files aligned.
