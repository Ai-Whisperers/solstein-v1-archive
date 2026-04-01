"""Application-wide constants with zero application-layer imports.

STORY-117: Pure constants used across all layers. No imports from
domain, infrastructure, analytics, or any other application package.
"""

# Default timeout for external HTTP calls (seconds)
DEFAULT_HTTP_TIMEOUT_S: int = 30

# Default page size for paginated queries
DEFAULT_PAGE_SIZE: int = 50

# Maximum retries for network operations
DEFAULT_MAX_RETRIES: int = 3

# Rate limit default (requests per minute)
DEFAULT_RATE_LIMIT_RPM: int = 60

# Cache TTL defaults (seconds)
CACHE_TTL_SHORT: int = 300  # 5 minutes
CACHE_TTL_MEDIUM: int = 3600  # 1 hour
CACHE_TTL_LONG: int = 86400  # 24 hours

# Score bounds
SCORE_MIN: float = 0.0
SCORE_MAX: float = 10.0

# Confidence thresholds
CONFIDENCE_HIGH: float = 0.8
CONFIDENCE_MEDIUM: float = 0.5
CONFIDENCE_LOW: float = 0.3
