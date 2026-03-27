"""Data encryption and protection utilities.

EPIC-027 Story 4: Encryption at rest and in transit.

Usage:
    from solstein.security.encryption import EncryptedField, DataClassification

    # Encrypt sensitive fields
    encrypted_email = EncryptedField(cipher).encrypt("user@example.com")
"""

from enum import Enum

from cryptography.fernet import Fernet


class DataClassification(str, Enum):
    """Data classification levels."""

    PUBLIC = "public"  # No restriction
    INTERNAL = "internal"  # Employees only
    CONFIDENTIAL = "confidential"  # Need-to-know
    RESTRICTED = "restricted"  # Highest protection


class EncryptedField:
    """Automatically encrypt/decrypt sensitive fields."""

    def __init__(self, key: bytes | None = None):
        """Initialize with encryption key.

        Args:
            key: Fernet key (generated if None).
        """
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)

    def encrypt(self, value: str) -> bytes:
        """Encrypt string value.

        Args:
            value: String to encrypt.

        Returns:
            Encrypted bytes.
        """
        if not value:
            return b""
        return self.cipher.encrypt(value.encode())

    def decrypt(self, value: bytes) -> str:
        """Decrypt bytes to string.

        Args:
            value: Encrypted bytes.

        Returns:
            Decrypted string.
        """
        if not value:
            return ""
        return self.cipher.decrypt(value).decode()


class DataProtector:
    """Protect data based on classification level."""

    def __init__(self, encryption_key: bytes | None = None):
        """Initialize data protector.

        Args:
            encryption_key: Encryption key for sensitive data.
        """
        self.encrypted_field = EncryptedField(encryption_key)

    def protect_field(self, value: str, classification: DataClassification) -> str | bytes:
        """Protect field based on classification.

        Args:
            value: Field value.
            classification: Data classification.

        Returns:
            Protected value.
        """
        if classification in (DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED):
            return self.encrypted_field.encrypt(value)
        return value

    def unprotect_field(self, value: str | bytes, classification: DataClassification) -> str:
        """Unprotect field based on classification.

        Args:
            value: Protected value.
            classification: Data classification.

        Returns:
            Original value.
        """
        if classification in (DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED):
            if isinstance(value, bytes):
                return self.encrypted_field.decrypt(value)
        return str(value)


def generate_encryption_key() -> bytes:
    """Generate new encryption key.

    Returns:
        Fernet key.
    """
    return Fernet.generate_key()


# TLS Configuration helpers
TLS_CONFIG = {
    "min_version": "TLSv1.3",
    "cipher_suites": [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256",
    ],
    "hsts_max_age": 31536000,  # 1 year
    "hsts_include_subdomains": True,
}


def get_security_headers() -> dict[str, str]:
    """Get recommended security headers.

    Returns:
        Dictionary of security headers.
    """
    return {
        "Strict-Transport-Security": f"max-age={TLS_CONFIG['hsts_max_age']}; includeSubDomains",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'",
    }
