import pytest
from core.security.password_utils import hash_password, validate_password


@pytest.fixture(scope="function")
def password() -> str:
    return "test_password"


def test_encrypt_and_decrypt_password(password: str) -> None:
    encoded_password = hash_password(password)
    assert validate_password(password, encoded_password)


def test_password_encryption_is_reproducible(password: str) -> None:
    encoded_password1 = hash_password(password)
    encoded_password2 = hash_password(password)
    assert encoded_password1 != encoded_password2


def test_verify_wrong_password(password: str) -> None:
    wrong_password = "wrong_prefix_" + password
    encoded_wrong_password = hash_password(wrong_password)
    assert not validate_password(password, encoded_wrong_password)
