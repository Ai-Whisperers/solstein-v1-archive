"""Per-tenant rate limiting - EPIC-016.

Provides configurable rate limiting per API tenant.
"""

import time
from dataclasses import dataclass

from fastapi import HTTPException, Request
from loguru import logger


@dataclass
class RateLimitConfig:
    """Rate limit configuration for a tenant."""

    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 20


class RateLimiter:
    """Token bucket rate limiter per tenant.

    Usage:
        limiter = RateLimiter()

        @app.middleware("http")
        async def rate_limit_middleware(request: Request, call_next):
            await limiter.check_rate_limit(request)
            return await call_next(request)
    """

    def __init__(self):
        # tenant_id -> {minute_bucket, hour_bucket, day_bucket, tokens, last_update}
        self._buckets: dict[str, dict] = {}
        self._configs: dict[str, RateLimitConfig] = {}
        self._default_config = RateLimitConfig()

    def set_tenant_config(self, tenant_id: str, config: RateLimitConfig) -> None:
        """Set rate limit config for a tenant."""
        self._configs[tenant_id] = config
        logger.info(f"Set rate limit config for tenant {tenant_id}")

    def _get_config(self, tenant_id: str) -> RateLimitConfig:
        """Get config for tenant or default."""
        return self._configs.get(tenant_id, self._default_config)

    def _get_tenant_id(self, request: Request) -> str:
        """Extract tenant ID from request."""
        # Try API key header first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"apikey_{api_key[:8]}"

        # Try authorization token
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth[7:]
            return f"token_{token[:8]}"

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip_{client_ip}"

    def _update_bucket(self, tenant_id: str, config: RateLimitConfig) -> tuple[bool, dict]:
        """Update token bucket for tenant. Returns (allowed, rate_info)."""
        now = time.time()

        if tenant_id not in self._buckets:
            self._buckets[tenant_id] = {
                "tokens": config.burst_size,
                "last_update": now,
                "minute_count": 0,
                "minute_start": now,
                "hour_count": 0,
                "hour_start": now,
                "day_count": 0,
                "day_start": now,
            }

        bucket = self._buckets[tenant_id]

        # Reset counters if time windows have passed
        if now - bucket["minute_start"] >= 60:
            bucket["minute_count"] = 0
            bucket["minute_start"] = now

        if now - bucket["hour_start"] >= 3600:
            bucket["hour_count"] = 0
            bucket["hour_start"] = now

        if now - bucket["day_start"] >= 86400:
            bucket["day_count"] = 0
            bucket["day_start"] = now

        # Check hard limits
        if bucket["minute_count"] >= config.requests_per_minute:
            return False, {"limit": "per_minute", "retry_after": 60}

        if bucket["hour_count"] >= config.requests_per_hour:
            return False, {"limit": "per_hour", "retry_after": 3600}

        if bucket["day_count"] >= config.requests_per_day:
            return False, {"limit": "per_day", "retry_after": 86400}

        # Token bucket algorithm
        elapsed = now - bucket["last_update"]
        tokens_to_add = elapsed * (config.requests_per_minute / 60)
        bucket["tokens"] = min(config.burst_size, bucket["tokens"] + tokens_to_add)
        bucket["last_update"] = now

        if bucket["tokens"] < 1:
            return False, {"limit": "burst", "retry_after": int(60 / config.requests_per_minute)}

        # Consume token
        bucket["tokens"] -= 1
        bucket["minute_count"] += 1
        bucket["hour_count"] += 1
        bucket["day_count"] += 1

        rate_info = {
            "limit": config.requests_per_minute,
            "remaining": int(bucket["tokens"]),
            "reset": int(bucket["minute_start"] + 60),
        }

        return True, rate_info

    async def check_rate_limit(self, request: Request) -> None:
        """Check if request is within rate limit.

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        tenant_id = self._get_tenant_id(request)
        config = self._get_config(tenant_id)

        allowed, rate_info = self._update_bucket(tenant_id, config)

        # Add rate limit headers to request state for later
        request.state.rate_limit = rate_info

        if not allowed:
            logger.warning(f"Rate limit exceeded for tenant {tenant_id}: {rate_info['limit']}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {rate_info['limit']}",
                headers={"Retry-After": str(rate_info.get("retry_after", 60))},
            )

    def get_rate_limit_headers(self, request: Request) -> dict[str, str]:
        """Get rate limit headers for response."""
        rate_info = getattr(request.state, "rate_limit", {})

        headers = {}
        if "limit" in rate_info:
            headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        if "remaining" in rate_info:
            headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        if "reset" in rate_info:
            headers["X-RateLimit-Reset"] = str(rate_info["reset"])

        return headers


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(request: Request) -> None:
    """Convenience function to check rate limit."""
    await rate_limiter.check_rate_limit(request)


def get_rate_limit_headers(request: Request) -> dict[str, str]:
    """Convenience function to get rate limit headers."""
    return rate_limiter.get_rate_limit_headers(request)
