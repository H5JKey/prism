from bcrypt import checkpw, gensalt, hashpw


def hash_password(password: str) -> str:
    salt = gensalt()
    password_bytes = password.encode()
    hashed_password_bytes = hashpw(
        password=password_bytes,
        salt=salt,
    )
    hashed_password = hashed_password_bytes.decode()
    return hashed_password


def validate_password(
    password: str,
    encrypted_password: str,
) -> bool:
    password_bytes = password.encode()
    hashed_password_bytes = encrypted_password.encode()
    return checkpw(
        password=password_bytes,
        hashed_password=hashed_password_bytes,
    )
