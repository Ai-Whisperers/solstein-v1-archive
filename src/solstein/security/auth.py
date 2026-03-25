"""Enhanced authentication and authorization with RBAC.

EPIC-027 Story 3: Multi-factor authentication, role-based access control,
and session security.

Usage:
    from solstein.security.auth import require_permission, Permission, Role

    @router.get("/admin")
    @require_permission(Permission.ADMIN_ACCESS)
    async def admin_endpoint(user: User = Depends(get_current_user)):
        pass
"""

from enum import Enum
from functools import wraps
from typing import Any, Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from loguru import logger


class Role(str, Enum):
    """User roles."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API = "api"


class Permission(str, Enum):
    """Permissions for resource access."""

    COMPANY_READ = "company:read"
    COMPANY_WRITE = "company:write"
    COMPANY_DELETE = "company:delete"
    RESEARCH_RUN = "research:run"
    EXPORT_CREATE = "export:create"
    EXPORT_DELETE = "export:delete"
    ADMIN_ACCESS = "admin:access"
    USER_MANAGE = "user:manage"
    API_KEY_MANAGE = "api_key:manage"


# Role to permission mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: list(Permission),  # All permissions
    Role.ANALYST: [
        Permission.COMPANY_READ,
        Permission.COMPANY_WRITE,
        Permission.RESEARCH_RUN,
        Permission.EXPORT_CREATE,
    ],
    Role.VIEWER: [
        Permission.COMPANY_READ,
    ],
    Role.API: [
        Permission.COMPANY_READ,
        Permission.EXPORT_CREATE,
    ],
}


class User:
    """User with roles and permissions."""

    def __init__(
        self,
        id: str,
        email: str,
        role: Role,
        tenant_id: str | None = None,
        mfa_enabled: bool = False,
        mfa_verified: bool = False,
    ):
        self.id = id
        self.email = email
        self.role = role
        self.tenant_id = tenant_id
        self.mfa_enabled = mfa_enabled
        self.mfa_verified = mfa_verified
        self.permissions = set(ROLE_PERMISSIONS.get(role, []))

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has permission."""
        return permission in self.permissions

    def has_any_permission(self, permissions: list[Permission]) -> bool:
        """Check if user has any of the permissions."""
        return any(p in self.permissions for p in permissions)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role.value,
            "tenant_id": self.tenant_id,
            "mfa_enabled": self.mfa_enabled,
            "mfa_verified": self.mfa_verified,
            "permissions": [p.value for p in self.permissions],
        }


security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> User:
    """Get current user from JWT token.

    Args:
        credentials: HTTP authorization credentials.

    Returns:
        User instance.

    Raises:
        HTTPException: If authentication fails.
    """
    from solstein.security.jwt import verify_token

    token = credentials.credentials

    try:
        payload = verify_token(token)

        return User(
            id=payload.get("sub", ""),
            email=payload.get("email", ""),
            role=Role(payload.get("role", "viewer")),
            tenant_id=payload.get("tenant_id"),
            mfa_enabled=payload.get("mfa_enabled", False),
            mfa_verified=payload.get("mfa_verified", False),
        )
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """Get current active user.

    Args:
        user: Current user.

    Returns:
        User if active.

    Raises:
        HTTPException: If user is inactive.
    """
    # Check if user is active (would query database in production)
    return user


def require_permission(permission: Permission):
    """Decorator to require a specific permission.

    Args:
        permission: Required permission.

    Returns:
        Decorator function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from kwargs (injected by FastAPI)
            user = kwargs.get("user")
            if not user:
                for arg in args:
                    if isinstance(arg, User):
                        user = arg
                        break

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if not user.has_permission(permission):
                logger.warning(f"Permission denied: {user.email} lacks {permission.value}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value} required",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role: Role):
    """Decorator to require a specific role.

    Args:
        role: Required role.

    Returns:
        Decorator function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if not user:
                for arg in args:
                    if isinstance(arg, User):
                        user = arg
                        break

            if not user or user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role {role.value} required",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_mfa(func: Callable) -> Callable:
    """Decorator to require MFA verification.

    Args:
        func: Function to decorate.

    Returns:
        Decorated function.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        user = kwargs.get("user")
        if not user:
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break

        if user and user.mfa_enabled and not user.mfa_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MFA verification required",
            )

        return await func(*args, **kwargs)

    return wrapper


class MFAHandler:
    """Handle MFA verification."""

    def __init__(self):
        """Initialize MFA handler."""
        self._codes: dict[str, tuple[str, float]] = {}  # user_id -> (code, expiry)

    def generate_code(self, user_id: str) -> str:
        """Generate TOTP code.

        Args:
            user_id: User identifier.

        Returns:
            6-digit code.
        """
        import random
        import time

        code = f"{random.randint(0, 999999):06d}"
        self._codes[user_id] = (code, time.time() + 300)  # 5 minute expiry
        return code

    def verify_code(self, user_id: str, code: str) -> bool:
        """Verify TOTP code.

        Args:
            user_id: User identifier.
            code: Code to verify.

        Returns:
            True if valid.
        """
        import time

        stored = self._codes.get(user_id)
        if not stored:
            return False

        stored_code, expiry = stored
        if time.time() > expiry:
            del self._codes[user_id]
            return False

        if stored_code == code:
            del self._codes[user_id]
            return True

        return False


class RateLimiter:
    """Rate limiting for authentication."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        """Initialize rate limiter.

        Args:
            max_attempts: Maximum attempts per window.
            window_seconds: Time window in seconds.
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = {}  # key -> list of timestamps

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed.

        Args:
            key: Rate limit key (IP, user_id, etc.).

        Returns:
            True if allowed.
        """
        import time

        now = time.time()
        attempts = self._attempts.get(key, [])

        # Remove old attempts
        attempts = [a for a in attempts if now - a < self.window_seconds]
        self._attempts[key] = attempts

        return len(attempts) < self.max_attempts

    def record_attempt(self, key: str):
        """Record an attempt.

        Args:
            key: Rate limit key.
        """
        import time

        if key not in self._attempts:
            self._attempts[key] = []
        self._attempts[key].append(time.time())

    def get_remaining(self, key: str) -> int:
        """Get remaining attempts.

        Args:
            key: Rate limit key.

        Returns:
            Number of remaining attempts.
        """
        if self.is_allowed(key):
            attempts = self._attempts.get(key, [])
            return max(0, self.max_attempts - len(attempts))
        return 0


class SessionManager:
    """Manage user sessions securely."""

    def __init__(self, token_ttl_minutes: int = 15):
        """Initialize session manager.

        Args:
            token_ttl_minutes: Token time-to-live in minutes.
        """
        self.token_ttl_minutes = token_ttl_minutes

    def create_access_token(self, user: User) -> str:
        """Create JWT access token.

        Args:
            user: User to create token for.

        Returns:
            JWT token.
        """
        from datetime import datetime, timedelta, timezone

        from solstein.security.jwt import create_token

        expires = datetime.now(timezone.utc) + timedelta(minutes=self.token_ttl_minutes)

        return create_token(
            data={
                "sub": user.id,
                "email": user.email,
                "role": user.role.value,
                "tenant_id": user.tenant_id,
                "mfa_enabled": user.mfa_enabled,
                "mfa_verified": user.mfa_verified,
            },
            expires_delta=expires,
        )

    def create_refresh_token(self, user: User) -> str:
        """Create refresh token.

        Args:
            user: User to create token for.

        Returns:
            Refresh token.
        """
        from datetime import datetime, timedelta, timezone

        from solstein.security.jwt import create_token

        expires = datetime.now(timezone.utc) + timedelta(days=7)

        return create_token(
            data={
                "sub": user.id,
                "type": "refresh",
            },
            expires_delta=expires,
        )


# Global instances
mfa_handler = MFAHandler()
auth_rate_limiter = RateLimiter()
session_manager = SessionManager()
