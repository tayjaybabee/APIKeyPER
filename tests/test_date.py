import sqlite3

import pytest

from apikeyper import APIKeyPER, Date


@pytest.mark.parametrize(
    "text",
    ["9/20/2023", "20/09/2023", "September 20, 2023", "Wed, 20 Sep 2023 00:00:00 GMT"],
)
def test_common_dates_compare_by_utc_instant(text):
    date = Date(text)
    assert date == Date("2023-09-19T20:00:00-04:00")
    assert date < Date("2023-09-20 12:30 PM")
    assert not date.was_defaulted
    with pytest.raises(AttributeError):
        date.was_defaulted = True


def test_legacy_dates_and_default_flags_survive_reopen(tmp_path):
    path = tmp_path / "legacy.db"
    connection = sqlite3.connect(path)
    with connection:
        connection.execute(
            "CREATE TABLE apikeys (service text, key_name text, added text, key text, "
            "status text, revoked_on text, PRIMARY KEY (service, key_name))"
        )
        connection.execute(
            "INSERT INTO apikeys VALUES (?, ?, ?, ?, ?, ?)",
            ("example", "old", "9/20/2023", "fake_legacy_key", "active", None),
        )
    connection.close()

    api = APIKeyPER(path)
    service = api.service("example")
    service.add_key("fake_new_key", key_name="new")
    assert service.get_key().key_name == "new"
    service.revoke_key("new")
    api.db.close()

    service = APIKeyPER(path).service("example")
    legacy = service.get_key()
    assert legacy.added == Date("2023-09-20")
    assert not legacy.added.was_defaulted
    assert legacy.revoked_on is None
    assert legacy.key_id is None
    revoked = service.get_key("new", only_active=False)
    assert revoked.added.was_defaulted and revoked.revoked_on.was_defaulted
    assert legacy.added < revoked.added <= revoked.revoked_on
    assert len(service.list_keys()) == 2
