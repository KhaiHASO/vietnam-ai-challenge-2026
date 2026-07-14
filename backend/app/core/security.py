from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_secret(secret: str) -> str:
    """Hash a secret (like password or refresh token) using Argon2."""
    return ph.hash(secret)

def verify_secret(plain_secret: str, hashed_secret: str) -> bool:
    """Verify a plain secret against a hash."""
    try:
        return ph.verify(hashed_secret, plain_secret)
    except VerifyMismatchError:
        return False
