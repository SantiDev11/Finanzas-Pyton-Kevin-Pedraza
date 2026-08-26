import pytest
from app.core.security import hash_password, verify_password


def test_hash_password_generates_valid_bcrypt_hash():
    password = "MiSuperPassword123*"
    hashed = hash_password(password)

    assert hashed is not None
    assert hashed != password
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert len(hashed) >= 60


def test_verify_password_matches_correct_password():
    password = "SecretPassword!2026"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
    assert verify_password("IncorrectPassword", hashed) is False
    assert verify_password("", hashed) is False


def test_hash_password_empty_raises_value_error():
    with pytest.raises(ValueError):
        hash_password("")
