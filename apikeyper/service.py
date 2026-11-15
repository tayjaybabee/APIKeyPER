from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from apikeyper.database import APIKey
from apikeyper.date import DateInput
from apikeyper.env_names import key_env_name, normalize_env_prefix
from apikeyper.log_engine import Loggable, ROOT_LOGGER

if TYPE_CHECKING:
    from apikeyper import APIKeyPER


class Service(Loggable):
    """Manage keys for one named service in an APIKeyPER store."""

    def __init__(self, name: str, store: APIKeyPER) -> None:
        super().__init__(parent_log_device=ROOT_LOGGER)
        self.name = name
        self._store = store

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"

    @property
    def env_prefix(self) -> str:
        """The saved environment prefix, or the normalized service name."""
        return self._store.db.get_env_prefix(self.name) or normalize_env_prefix(self.name)

    @env_prefix.setter
    def env_prefix(self, prefix: str | None) -> None:
        if prefix is not None:
            key_env_name(prefix)
            prefix = normalize_env_prefix(prefix)
        self._store.db.set_env_prefix(self.name, prefix)

    @property
    def require_key_id(self) -> bool:
        """Whether writes to this service require a provider Key ID."""
        return self._store.db.requires_key_id(self.name)

    @require_key_id.setter
    def require_key_id(self, required: bool) -> None:
        if not isinstance(required, bool):
            raise TypeError("require_key_id must be a bool")
        self._store.add_service(self.name, require_key_id=required)

    def add_key(
        self,
        api_key: str,
        key_name: str | None = None,
        status: str = "active",
        added: DateInput = None,
        *,
        key_id: str | None = None,
    ) -> APIKey:
        """Store a key for this service and return its APIKey record."""
        key_name = key_name or f"{self.name}_key_{uuid4().hex[:8]}"
        return self._store.db.add_key(
            self.name, key_name, api_key, added, status, key_id=key_id
        )

    def get_key(
        self, key_name: str | None = None, only_active: bool = True
    ) -> APIKey | None:
        """Get a named key or the latest matching key."""
        return self._store.get_key(self.name, key_name, only_active)

    def list_keys(self) -> list[APIKey]:
        """Return all keys for this service, including revoked keys."""
        return self._store.db.list_key_records(self.name)

    def revoke_key(self, key_name: str) -> None:
        """Mark a named key inactive."""
        self._store.revoke_key(self.name, key_name)

    def delete_key(self, key_name: str | None = None) -> None:
        """Delete a named key, or all keys for this service when omitted."""
        self._store.delete_key(self.name, key_name)
