"""Constants for API endpoints, rate limiting, and HTTP configuration."""

# HTTP Status Codes
HTTP_STATUS_OK = 200
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_RATE_LIMITED = 429
HTTP_STATUS_INTERNAL_ERROR = 500
HTTP_STATUS_ERROR_MIN = 400  # Threshold for error status codes

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE = 60  # Default rate limit
RATE_LIMIT_BURST_SIZE = 10  # Burst allowance
RATE_LIMIT_WINDOW_SECONDS = 60  # Rate limit window duration

# CORS Configuration
CORS_CACHE_MAX_AGE_S = 600  # Cache preflight requests for 10 minutes

# Security Headers
SECURITY_HSTS_MAX_AGE_S = 31536000  # HSTS max-age: 1 year in seconds

# Token Validation
TOKEN_MIN_LENGTH = 10  # Minimum token length for validation

# Pagination
PAGINATION_DEFAULT_LIMIT = 100  # Default page size
PAGINATION_MAX_LIMIT = 1000  # Maximum page size
PAGINATION_DEFAULT_PAGE_SIZE = 20  # Default items per page

# Enrichment API
ENRICHMENT_BATCH_SIZE = 10  # Default batch size for enrichment
ENRICHMENT_CACHE_TTL_HOURS = 24  # Cache TTL for enrichment results

# Async Jobs
ASYNC_JOBS_BATCH_SIZE = 10  # Batch size for async job processing

# Logging
LOGGING_REQUEST_ID_LENGTH = 8  # Length of request ID prefix
LOGGING_TOKEN_REDACT_LENGTH = 8  # Length of token to show before redaction

# Metrics
METRICS_MAX_RESPONSE_TIMES = 1000  # Maximum response times to track
