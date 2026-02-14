import os
import logging
from abc import ABC, abstractmethod
from hashlib import sha3_256

logger = logging.getLogger("gpa.keys")


class KeyProvider(ABC):
    """Abstract key provider interface — swap to HSM in production."""

    @abstractmethod
    def get_pepper(self) -> bytes:
        """Retrieve the Argon2 PEPPER secret."""
        pass

    @abstractmethod
    def get_aes_key(self) -> bytes:
        """Retrieve the AES-256-GCM master key (32 bytes)."""
        pass

    @abstractmethod
    def get_jwt_secret(self) -> str:
        """Retrieve the JWT signing secret."""
        pass

    @abstractmethod
    def get_hmac_key(self) -> bytes:
        """Retrieve the HMAC-SHA256 challenge signing key."""
        pass


class EnvironmentKeyProvider(KeyProvider):
    """Development key provider — reads from environment variables."""

    def __init__(self):
        self._pepper = os.getenv("GPA_PEPPER", "dev-pepper-value-store-in-hsm")
        self._secret_key = os.getenv("GPA_SECRET_KEY", "dev-secret-key-change-in-production-immediately")
        self._master_key = os.getenv("GPA_MASTER_KEY", "dev-master-key-change-in-production")
        

    def get_pepper(self) -> bytes:
        return self._pepper.encode()

    def get_aes_key(self) -> bytes:
        return sha3_256(self._master_key.encode()).digest()

    def get_jwt_secret(self) -> str:
        return self._secret_key

    def get_hmac_key(self) -> bytes:
        return sha3_256(f"hmac:{self._secret_key}".encode()).digest()


class HSMKeyProvider(KeyProvider):
    """Production HSM key provider stub."""

    def __init__(self, hsm_endpoint: str = "", slot_id: int = 0):
        self._endpoint = hsm_endpoint
        self._slot_id = slot_id
        logger.info(f"HSM provider initialized: {hsm_endpoint}")

    def get_pepper(self) -> bytes:
        raise NotImplementedError("Configure HSM PKCS#11 client for production")

    def get_aes_key(self) -> bytes:
        raise NotImplementedError("Configure HSM PKCS#11 client for production")

    def get_jwt_secret(self) -> str:
        raise NotImplementedError("Configure HSM PKCS#11 client for production")

    def get_hmac_key(self) -> bytes:
        raise NotImplementedError("Configure HSM PKCS#11 client for production")


def create_key_provider() -> KeyProvider:
    """Create the appropriate key provider based on environment."""
    env = os.getenv("GPA_ENV", "dev")
    if env == "production":
        hsm_endpoint = os.getenv("HSM_ENDPOINT", "")
        if hsm_endpoint:
            return HSMKeyProvider(hsm_endpoint=hsm_endpoint)
        
        logger.warning("PRODUCTION WARNING: No HSM_ENDPOINT configured. Using EnvironmentKeyProvider (Software Keys).")
        return EnvironmentKeyProvider()
    return EnvironmentKeyProvider()



keys = create_key_provider()
