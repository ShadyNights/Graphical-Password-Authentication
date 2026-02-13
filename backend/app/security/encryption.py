import json
import secrets
from typing import List
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.security.hsm_client import keys

# Initialize AES-GCM with key from HSM provider
_aes_key = keys.get_aes_key()
_aesgcm = AESGCM(_aes_key)


def encrypt_recognition_data(image_ids: List[str]) -> bytes:
    """
    Encrypt the recognition image IDs using AES-256-GCM.
    Returns: nonce (12 bytes) + ciphertext.
    """
    plaintext = json.dumps(sorted(image_ids)).encode()
    nonce = secrets.token_bytes(12)
    ciphertext = _aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext


def decrypt_recognition_data(encrypted: bytes) -> List[str]:
    """Decrypt AES-256-GCM encrypted recognition image IDs."""
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]
    plaintext = _aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode())
