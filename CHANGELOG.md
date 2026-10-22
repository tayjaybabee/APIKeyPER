# Changelog

## [0.2.0]

Consolidates Dependabot PRs #12 (`urllib3`) and #13 (`cryptography`).

### Added
- This changelog.

### Changed
- Upgraded `cryptography` from `40.0.2` to `50.0.2` (constraint `^50.0.0`).
- Upgraded `urllib3` from `2.6.3` to `2.8.0` (`requirements.txt` synced with `poetry.lock`).
- Transitive `cffi` (`2.1.1`) and `pycparser` (`3.0`) updated as required by `cryptography`.
- Project version bumped to `0.2.0`.

### Fixed
- Picks up upstream security and bug fixes from `urllib3` and `cryptography`.

### Removed
- Nothing.

### Breaking Changes
- None in APIKeyPER's public API. `cryptography` is a major-version upgrade; the test suite passes unchanged.
