"""API Key Management Service (EPIC-019 STORY-065).

Provides CRUD operations for tenant-scoped API keys including
creation, listing, rotation, revocation, and usage logging.

Key design decisions:
- Full plaintext key is returned only once at creation time
- Only SHA-256 hash is stored in the database
- Key prefix (first 8 chars) is stored for identification
- Scope enforcement is handled at the middleware layer
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


# Key generation constants
KEY_PREFIX_LIVE = "sk_live_"
KEY_PREFIX_TEST = "sk_test_"
KEY_DISPLAY_PREFIX_LENGTH = 8


def generate_api_key(*, test_mode: bool = False) -> str:
    """Generate a cryptographically secure API key.

    Returns:
        Full plaintext API key (e.g. sk_live_AbCdEf...)
    """
    prefix = KEY_PREFIX_TEST if test_mode else KEY_PREFIX_LIVE
    token = secrets.token_urlsafe(32)
    return f"{prefix}{token}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage.

    Returns:
        SHA-256 hex digest of the key.
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_key_prefix(api_key: str) -> str:
    """Extract a safe display prefix from an API key.

    Returns the first KEY_DISPLAY_PREFIX_LENGTH characters for identification.
    """
    return api_key[:KEY_DISPLAY_PREFIX_LENGTH]


def create_api_key(
    db: Session,
    *,
    tenant_id: str,
    name: str,
    scope: str = "read_only",
    expires_at: datetime | None = None,
    test_mode: bool = False,
) -> dict[str, object]:
    """Create a new API key for a tenant.

    Returns a dict containing the full plaintext key (shown once) and
    the stored record metadata. The caller must display the key to the
    user immediately — it cannot be retrieved later.

    Args:
        db: SQLAlchemy session.
        tenant_id: UUID of the owning tenant.
        name: Human-readable label.
        scope: One of read_only, read_write, admin.
        expires_at: Optional expiry datetime.
        test_mode: If True, generates sk_test_ prefix.

    Returns:
        Dict with 'key' (plaintext, one-time) and 'record' (metadata).
    """
    from solstein.infrastructure.models.infrastructure import ApiKeyRecord

    plaintext_key = generate_api_key(test_mode=test_mode)
    key_hash = hash_api_key(plaintext_key)
    key_prefix = get_key_prefix(plaintext_key)

    record = ApiKeyRecord(
        id=uuid.uuid4(),
        tenant_id=uuid.UUID(tenant_id),
        name=name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        scope=scope,
        is_active=True,
        expires_at=expires_at,
    )

    db.add(record)
    db.flush()

    logger.info(
        f"[ApiKeyService] Created API key '{name}' for tenant {tenant_id} "
        f"(scope={scope}, prefix={key_prefix}...)"
    )

    return {
        "key": plaintext_key,  # One-time display only
        "record": record.to_dict(),
    }


def list_api_keys(db: Session, *, tenant_id: str) -> list[dict[str, object]]:
    """List all API keys for a tenant (never exposes hashes).

    Args:
        db: SQLAlchemy session.
        tenant_id: UUID of the owning tenant.

    Returns:
        List of key metadata dicts.
    """
    from solstein.infrastructure.models.infrastructure import ApiKeyRecord

    records = (
        db.query(ApiKeyRecord)
        .filter(ApiKeyRecord.tenant_id == uuid.UUID(tenant_id))
        .order_by(ApiKeyRecord.created_at.desc())
        .all()
    )

    return [r.to_dict() for r in records]


def revoke_api_key(db: Session, *, key_id: str, tenant_id: str) -> dict[str, object] | None:
    """Revoke an API key (sets is_active=False, records revoked_at).

    Args:
        db: SQLAlchemy session.
        key_id: UUID of the key to revoke.
        tenant_id: UUID of the owning tenant (for isolation).

    Returns:
        Updated key metadata, or None if not found.
    """
    from solstein.infrastructure.models.infrastructure import ApiKeyRecord

    record = (
        db.query(ApiKeyRecord)
        .filter(
            ApiKeyRecord.id == uuid.UUID(key_id),
            ApiKeyRecord.tenant_id == uuid.UUID(tenant_id),
        )
        .first()
    )

    if not record:
        logger.warning(f"[ApiKeyService] Key {key_id} not found for tenant {tenant_id}")
        return None

    record.is_active = False
    record.revoked_at = datetime.now(timezone.utc)
    db.flush()

    logger.info(f"[ApiKeyService] Revoked API key '{record.name}' ({key_id})")

    return record.to_dict()


def rotate_api_key(
    db: Session,
    *,
    key_id: str,
    tenant_id: str,
    test_mode: bool = False,
) -> dict[str, object] | None:
    """Rotate an API key — revoke the old one and create a new one with same settings.

    Args:
        db: SQLAlchemy session.
        key_id: UUID of the key to rotate.
        tenant_id: UUID of the owning tenant.
        test_mode: If True, generates sk_test_ prefix.

    Returns:
        Dict with 'key' (new plaintext) and 'record' (new metadata), or None if not found.
    """
    from solstein.infrastructure.models.infrastructure import ApiKeyRecord

    old_record = (
        db.query(ApiKeyRecord)
        .filter(
            ApiKeyRecord.id == uuid.UUID(key_id),
            ApiKeyRecord.tenant_id == uuid.UUID(tenant_id),
        )
        .first()
    )

    if not old_record:
        logger.warning(f"[ApiKeyService] Key {key_id} not found for rotation")
        return None

    # Revoke old key
    old_record.is_active = False
    old_record.revoked_at = datetime.now(timezone.utc)

    # Create new key with same settings
    result = create_api_key(
        db,
        tenant_id=tenant_id,
        name=old_record.name,
        scope=old_record.scope,
        expires_at=old_record.expires_at,
        test_mode=test_mode,
    )

    logger.info(
        f"[ApiKeyService] Rotated API key '{old_record.name}' "
        f"(old={key_id}, new={result['record']['id']})"
    )

    return result


def validate_api_key(db: Session, *, api_key: str) -> dict[str, object] | None:
    """Validate an API key and return its metadata if valid.

    Checks that the key exists, is active, and not expired.
    Updates last_used_at on successful validation.

    Args:
        db: SQLAlchemy session.
        api_key: Full plaintext API key.

    Returns:
        Key metadata dict if valid, None otherwise.
    """
    from solstein.infrastructure.models.infrastructure import ApiKeyRecord

    key_hash = hash_api_key(api_key)

    record = (
        db.query(ApiKeyRecord)
        .filter(ApiKeyRecord.key_hash == key_hash)
        .first()
    )

    if not record:
        return None

    if not record.is_active:
        logger.debug(f"[ApiKeyService] Rejected inactive key (prefix={record.key_prefix})")
        return None

    if record.expires_at and datetime.now(timezone.utc) > record.expires_at:
        logger.debug(f"[ApiKeyService] Rejected expired key (prefix={record.key_prefix})")
        return None

    # Update last used timestamp
    record.last_used_at = datetime.now(timezone.utc)
    db.flush()

    return record.to_dict()


def log_api_key_usage(
    db: Session,
    *,
    api_key_id: str,
    tenant_id: str,
    endpoint: str,
    method: str,
    status_code: int,
) -> None:
    """Log API key usage for audit purposes (REQ-5).

    Args:
        db: SQLAlchemy session.
        api_key_id: UUID of the API key used.
        tenant_id: UUID of the tenant.
        endpoint: The API endpoint accessed.
        method: HTTP method (GET, POST, etc.).
        status_code: HTTP response status code.
    """
    from solstein.infrastructure.models.infrastructure import ApiKeyUsageRecord

    log_entry = ApiKeyUsageRecord(
        id=uuid.uuid4(),
        api_key_id=uuid.UUID(api_key_id),
        tenant_id=uuid.UUID(tenant_id),
        endpoint=endpoint,
        method=method,
        status_code=status_code,
    )

    db.add(log_entry)
    # Don't flush here — let the caller's transaction handle it


def scope_allows(key_scope: str, required_scope: str) -> bool:
    """Check if an API key's scope allows a required permission level.

    Scope hierarchy: admin > read_write > read_only.

    Args:
        key_scope: The scope of the API key.
        required_scope: The minimum scope required for the operation.

    Returns:
        True if the key's scope is sufficient.
    """
    hierarchy = {"read_only": 0, "read_write": 1, "admin": 2}
    key_level = hierarchy.get(key_scope, -1)
    required_level = hierarchy.get(required_scope, 99)
    return key_level >= required_level
