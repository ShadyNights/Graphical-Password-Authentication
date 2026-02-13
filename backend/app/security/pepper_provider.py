# Facade for retrieving pepper from HSM/KeyProvider
from app.security.hsm_client import keys

def get_argon2_pepper() -> bytes:
    """
    Retrieve specific pepper for Argon2id hashing.
    """
    return keys.get_pepper()
