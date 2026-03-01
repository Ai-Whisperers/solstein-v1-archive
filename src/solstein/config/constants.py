"""Constants for application configuration and settings."""

# Database Configuration
DATABASE_POOL_SIZE = 20  # Connection pool size
DATABASE_MAX_OVERFLOW = 10  # Maximum overflow connections
DATABASE_DEFAULT_PORT = 5432  # Default PostgreSQL port

# Cache Configuration
CACHE_DEFAULT_TTL_S = 3600  # Default cache TTL (1 hour)
CACHE_MIN_TTL_S = 60  # Minimum cache TTL
CACHE_MAX_TTL_S = 86400  # Maximum cache TTL (24 hours)

# API Configuration
API_DEFAULT_PORT = 8000  # Default API port
API_MAX_PORT = 65535  # Maximum port number

# Security Configuration
SECURITY_HSTS_MAX_AGE_S = 31536000  # HSTS max-age: 1 year

# Celery Configuration
CELERY_REDIS_DEFAULT_PORT = 6379  # Default Redis port
CELERY_TASK_TIME_LIMIT_S = 30  # Hard time limit for tasks
CELERY_TASK_SOFT_TIME_LIMIT_S = 25  # Soft time limit for graceful shutdown
CELERY_SCHEDULED_TASK_HOUR = 9  # Hour for scheduled tasks
CELERY_SCHEDULED_TASK_MINUTE = 0  # Minute for scheduled tasks

# Logging Configuration
LOGGING_REQUEST_ID_LENGTH = 8  # Length of request ID prefix
LOGGING_TOKEN_REDACT_LENGTH = 8  # Length of token to show before redaction
