from apikeyper.crypt import CryptDB, encryption_key


def test_cryptdb_creates_and_reuses_default_key(tmp_path, monkeypatch):
    key_path = tmp_path / "data" / "key.pem"
    monkeypatch.setattr(encryption_key, "DEFAULT_KEY_FILEPATH", str(key_path))
    database_path = tmp_path / "encrypted.db"

    database = CryptDB(database_path)
    assert key_path.is_file()
    database.data["example"] = "fake-value"
    database.save()

    reopened = CryptDB(database_path)
    assert reopened.data == {"example": "fake-value"}


def test_cryptdb_uses_explicit_key_file(tmp_path, monkeypatch):
    default_path = tmp_path / "data" / "key.pem"
    monkeypatch.setattr(encryption_key, "DEFAULT_KEY_FILEPATH", str(default_path))
    supplied_key = encryption_key.EncryptionKey("file", tmp_path / "custom.pem")

    database = CryptDB(tmp_path / "encrypted.db", encryption_key=supplied_key)

    assert database.encryption_key is supplied_key
    assert not default_path.exists()
