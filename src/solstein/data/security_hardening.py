"""
Phase 9: Security Hardening & Operations
Phase 13.5: Redis-Backed Rate Limiter

Implements security patterns for:
- Audit logging of all enrichment operations
- Input validation and sanitization
- Rate limiting middleware (Redis-backed with memory fallback)
- Security headers configuration
- API key rotation and secrets management
"""

import logging
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class AuditLogEntry:
    """Audit log entry for enrichment operations."""

    timestamp: datetime
    operation: str  # 'enrich', 'validate', 'enrich_batch', etc.
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    source: Optional[str] = None  # 'SEC_EDGAR', 'Companies House', 'News Signals'
    status: str = "SUCCESS"  # 'SUCCESS', 'FAILURE', 'SKIPPED'
    reason: Optional[str] = None
    user_id: Optional[str] = None
    duration_ms: float = 0.0
    data_sensitivity: str = "PUBLIC"  # 'PUBLIC', 'CONFIDENTIAL', 'RESTRICTED'


class AuditLogger:
    """Centralized audit logging for enrichment operations (Phase 9 - Security item 10)."""

    def __init__(self, max_entries: int = 10000):
        """
        Initialize audit logger.

        Args:
            max_entries: Maximum number of entries to keep in memory
        """
        self.max_entries = max_entries
        self.entries: deque = deque(maxlen=max_entries)

    def log_enrichment_start(
        self,
        company_name: str,
        company_id: str,
        source: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Log start of enrichment operation."""
        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc),
            operation="enrich_start",
            company_id=company_id,
            company_name=company_name,
            source=source,
            status="IN_PROGRESS",
            user_id=user_id,
        )
        self.entries.append(entry)
        logger.info(
            f"🔐 AUDIT: Enrichment started for {company_name} from {source}",
            extra={"audit": entry},
        )

    def log_enrichment_success(
        self,
        company_name: str,
        company_id: str,
        source: str,
        duration_ms: float,
        fields_enriched: List[str],
        user_id: Optional[str] = None,
    ) -> None:
        """Log successful enrichment completion."""
        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc),
            operation="enrich_success",
            company_id=company_id,
            company_name=company_name,
            source=source,
            status="SUCCESS",
            duration_ms=duration_ms,
            reason=f"Fields enriched: {', '.join(fields_enriched)}",
            user_id=user_id,
        )
        self.entries.append(entry)
        logger.info(
            f"🔐 AUDIT: Enrichment successful for {company_name} ({len(fields_enriched)} fields, {duration_ms:.2f}ms)",
            extra={"audit": entry},
        )

    def log_enrichment_failure(
        self,
        company_name: str,
        company_id: str,
        source: str,
        error: str,
        duration_ms: float = 0.0,
        user_id: Optional[str] = None,
    ) -> None:
        """Log enrichment failure."""
        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc),
            operation="enrich_failure",
            company_id=company_id,
            company_name=company_name,
            source=source,
            status="FAILURE",
            reason=error[:200],  # Truncate error
            duration_ms=duration_ms,
            user_id=user_id,
        )
        self.entries.append(entry)
        logger.warning(
            f"🔐 AUDIT: Enrichment failed for {company_name}: {error}",
            extra={"audit": entry},
        )

    def log_validation_failure(
        self,
        company_name: str,
        company_id: str,
        validation_rule: str,
        reason: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Log validation failure."""
        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc),
            operation="validation_failure",
            company_id=company_id,
            company_name=company_name,
            status="FAILURE",
            reason=f"{validation_rule}: {reason}",
            user_id=user_id,
            data_sensitivity="CONFIDENTIAL",
        )
        self.entries.append(entry)
        logger.warning(
            f"🔐 AUDIT: Validation failed for {company_name}: {validation_rule}",
            extra={"audit": entry},
        )

    def get_audit_trail(self, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit trail for specific company or all operations."""
        if company_id:
            entries = [e for e in self.entries if e.company_id == company_id]
        else:
            entries = list(self.entries)

        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "operation": e.operation,
                "company_id": e.company_id,
                "company_name": e.company_name,
                "source": e.source,
                "status": e.status,
                "reason": e.reason,
                "duration_ms": e.duration_ms,
            }
            for e in entries
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get audit logging statistics."""
        entries_list = list(self.entries)
        if not entries_list:
            return {
                "total_entries": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
            }

        success_count = sum(1 for e in entries_list if e.status == "SUCCESS")
        failure_count = sum(1 for e in entries_list if e.status == "FAILURE")

        return {
            "total_entries": len(entries_list),
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": (success_count / len(entries_list) * 100 if entries_list else 0),
            "oldest_entry": entries_list[0].timestamp.isoformat() if entries_list else None,
            "newest_entry": (entries_list[-1].timestamp.isoformat() if entries_list else None),
        }


# ============================================================================
# PHASE 13.5: REDIS-BACKED RATE LIMITER WITH MEMORY FALLBACK
# ============================================================================


class RedisRateLimiter:
    """Redis-backed rate limiter for API protection (Phase 13.5).
    
    IMPORTANT: Redis is OPTIONAL. If redis_client=None, automatically falls back to
    in-memory rate limiting. This means:
    
    - With Redis: Distributed rate limiting across multiple servers (shared state)
    - Without Redis (redis_client=None): Per-server rate limiting (no shared state)
    
    Current production uses memory fallback (redis_client=None), so rate limits are
    per-server, not distributed across servers.
    """

    def __init__(self, requests_per_minute: int = 60, redis_client=None):
        """Initialize Redis-backed rate limiter.
        
        Args:
            requests_per_minute: Max requests per minute per client (default: 60)
            redis_client: Redis client instance (optional, uses memory fallback if None)
                         To enable distributed rate limiting, pass a redis.Redis() instance
        """
        self.requests_per_minute = requests_per_minute
        self.redis_client = redis_client
        # Memory fallback for when Redis is unavailable or not configured
        self.memory_fallback = SimpleRateLimiter(requests_per_minute)
        # Expose memory fallback's client_requests for test compatibility
        self.client_requests = self.memory_fallback.client_requests
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make request."""
        if self.redis_client:
            try:
                # Try Redis first
                key = f"rate_limit:{client_id}"
                current = self.redis_client.incr(key)

                # Set expiration on first request
                if current == 1:
                    self.redis_client.expire(key, 60)

                if current > self.requests_per_minute:
                    logger.warning(
                        f"🔐 Rate limit exceeded for client {client_id}: {current} requests in last minute (Redis)"
                    )
                    return False

                return True
            except Exception as e:
                logger.warning(f"Redis rate limiter failed, falling back to memory: {e}")
                # Fall back to memory if Redis fails
                return self.memory_fallback.is_allowed(client_id)
        else:
            # Use memory fallback if Redis not configured
            return self.memory_fallback.is_allowed(client_id)

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client this minute."""
        if self.redis_client:
            try:
                key = f"rate_limit:{client_id}"
                current = self.redis_client.get(key)
                current = int(current) if current else 0
                return max(0, self.requests_per_minute - current)
            except Exception as e:
                logger.warning(f"Redis get_remaining failed, falling back to memory: {e}")
                return self.memory_fallback.get_remaining(client_id)
        else:
            return self.memory_fallback.get_remaining(client_id)


class SimpleRateLimiter:
    """Simple in-memory rate limiter for API protection (Phase 9 - Operations item 8)."""

    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Max requests per minute per client
        """
        self.requests_per_minute = requests_per_minute
        self.client_requests: Dict[str, deque] = defaultdict(deque)

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make request."""
        now = datetime.now(timezone.utc)
        minute_ago = now - timedelta(minutes=1)

        # Clean old requests
        while self.client_requests[client_id] and self.client_requests[client_id][0] < minute_ago:
            self.client_requests[client_id].popleft()

        # Check limit
        if len(self.client_requests[client_id]) >= self.requests_per_minute:
            logger.warning(
                f"🔐 Rate limit exceeded for client {client_id}: {len(self.client_requests[client_id])} requests in last minute"
            )
            return False

        # Add request
        self.client_requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client this minute."""
        now = datetime.now(timezone.utc)
        minute_ago = now - timedelta(minutes=1)

        # Clean old requests
        while self.client_requests[client_id] and self.client_requests[client_id][0] < minute_ago:
            self.client_requests[client_id].popleft()

        return max(0, self.requests_per_minute - len(self.client_requests[client_id]))


class InputValidator:
    """Enhanced input validation for API endpoints (Phase 9 - Security item 1)."""

    @staticmethod
    def validate_company_id(company_id: str) -> tuple[bool, Optional[str]]:
        """Validate company ID format."""
        if not company_id or not isinstance(company_id, str):
            return False, "Company ID must be non-empty string"

        if len(company_id) > 100:
            return False, "Company ID too long (max 100 chars)"

        # Check for SQL injection patterns
        dangerous_chars = ["';", "--", "/*", "*/", "xp_", "sp_"]
        if any(pattern in company_id.lower() for pattern in dangerous_chars):
            return False, "Company ID contains suspicious patterns"

        # Check for special characters - only allow alphanumeric, hyphens, underscores
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", company_id):
            return False, "Company ID contains invalid characters (only alphanumeric, hyphens, underscores allowed)"

        return True, None

    @staticmethod
    def validate_ticker(ticker: str) -> tuple[bool, Optional[str]]:
        """Validate stock ticker format."""
        if not ticker or not isinstance(ticker, str):
            return False, "Ticker must be non-empty string"

        if len(ticker) > 10:
            return False, "Ticker too long (max 10 chars)"

        # Must be alphanumeric and dash only
        if not all(c.isalnum() or c == "-" for c in ticker):
            return False, "Ticker contains invalid characters"

        return True, None

    @staticmethod
    def validate_company_number(company_number: str) -> tuple[bool, Optional[str]]:
        """Validate UK company number format."""
        if not company_number or not isinstance(company_number, str):
            return False, "Company number must be non-empty string"

        # UK company numbers are 8 digits
        if len(company_number) != 8 or not company_number.isdigit():
            return False, "Invalid UK company number (must be 8 digits)"

        return True, None

    @staticmethod
    def sanitize_error_message(error_msg: str) -> str:
        """Sanitize error message for logging (remove sensitive data)."""
        if not error_msg:
            return ""

        # Remove API keys
        error_msg = error_msg.replace("api_key=", "api_key=[REDACTED]")
        # Remove tokens
        error_msg = error_msg.replace("Authorization:", "Authorization: [REDACTED]")
        # Remove secrets
        error_msg = error_msg.replace("secret=", "secret=[REDACTED]")

        return error_msg


class SecurityHeadersConfig:
    """Security headers configuration for API responses (Phase 9 - Security item 9)."""

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers."""
        return {
            "X-Content-Type-Options": "nosniff",  # Prevent MIME sniffing
            "X-Frame-Options": "DENY",  # Prevent clickjacking
            "X-XSS-Protection": "1; mode=block",  # XSS protection
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",  # HSTS
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }


# Global instances
audit_logger = AuditLogger()
# Phase 13.5: Use Redis-backed rate limiter if available, else memory fallback
rate_limiter = RedisRateLimiter(requests_per_minute=100, redis_client=None)  # redis_client set by config
input_validator = InputValidator()
security_headers = SecurityHeadersConfig()

logger.info("✅ Security hardening module loaded (Phase 13.5: Redis-backed rate limiter with memory fallback)")
