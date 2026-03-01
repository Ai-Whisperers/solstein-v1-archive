"""Constants for infrastructure, database, and caching configuration."""

# Database Configuration
DATABASE_POOL_SIZE = 20  # Connection pool size
DATABASE_MAX_OVERFLOW = 10  # Maximum overflow connections

# Cache Configuration
CACHE_DEFAULT_TTL_S = 3600  # Default cache TTL (1 hour)
CACHE_LONG_TTL_S = 86400  # Long cache TTL (24 hours)
CACHE_SHORT_TTL_S = 300   # Short cache TTL (5 minutes) for volatile data
CACHE_VERY_LONG_TTL_S = 604800  # Very long cache TTL (7 days) for static data
CACHE_REDIS_DEFAULT_URL = "redis://localhost:6379/0"  # Default Redis URL

# Refresh Configuration
REFRESH_DEFAULT_CONFIDENCE = 0.5  # Default confidence for refresh operations
REFRESH_LOOKBACK_DAYS = 30  # Default lookback period for refresh (30 days)
REFRESH_NEXT_INTERVAL_HOURS = 24  # Hours until next refresh

# Retry Policy
RETRY_MAX_ATTEMPTS = 5  # Maximum retry attempts
RETRY_BASE_DELAY_S = 0.25  # Base delay for exponential backoff
RETRY_MAX_DELAY_S = 30.0  # Maximum delay between retries
RETRY_JITTER_RATIO = 0.2  # Jitter ratio for randomization

# Conflict Resolution Confidence Scores
CONFLICT_RESOLUTION_COMPANIES_HOUSE = 0.95  # Companies House authority
CONFLICT_RESOLUTION_SEC_EDGAR = 0.95  # SEC Edgar authority
CONFLICT_RESOLUTION_YAHOO_FINANCE = 0.88  # Yahoo Finance authority
CONFLICT_RESOLUTION_GLOBAL_MARKET = 0.87  # Global market data
CONFLICT_RESOLUTION_GITHUB = 0.85  # GitHub data
CONFLICT_RESOLUTION_WEBSITE = 0.84  # Website data
CONFLICT_RESOLUTION_LINKEDIN = 0.75  # LinkedIn data
CONFLICT_RESOLUTION_NEWS = 0.72  # News data
CONFLICT_RESOLUTION_PATENTS = 0.80  # Patent data
CONFLICT_RESOLUTION_WEB_SEARCH = 0.68  # Web search data
CONFLICT_RESOLUTION_FUNDING = 0.73  # Funding data

# Confidence Adjustment
CONFIDENCE_ADJUSTMENT_BASE = 0.5  # Base confidence
CONFIDENCE_ADJUSTMENT_SMOOTHING = 0.1  # Smoothing factor
CONFIDENCE_ADJUSTMENT_MIN = 0.3  # Minimum confidence
CONFIDENCE_ADJUSTMENT_MAX = 0.99  # Maximum confidence

# Performance Baseline
PERFORMANCE_BASELINE_COMPANY_FETCH_MS = 10.0  # Expected company fetch time
PERFORMANCE_BASELINE_COMPANY_FETCH_ROWS = 65  # Expected rows for company fetch
PERFORMANCE_BASELINE_MARKET_ANALYSIS_MS = 50.0  # Expected market analysis time
PERFORMANCE_BASELINE_MARKET_ANALYSIS_ROWS = 10  # Expected rows for market analysis
PERFORMANCE_BASELINE_SCORING_MS = 200.0  # Expected scoring time
PERFORMANCE_BASELINE_SCORING_ROWS = 5  # Expected rows for scoring

# Outbox Processing
OUTBOX_BATCH_SIZE = 25  # Batch size for outbox processing

# Database Models
DATABASE_FACT_TTL_SECONDS = 86400  # Fact TTL (24 hours)
DATABASE_FACT_ACCURACY_TOLERANCE_PCT = 10.0  # Accuracy tolerance percentage

# Enrichment Repositories
ENRICHMENT_REPO_BATCH_SIZE = 50  # Batch size for enrichment repository
ENRICHMENT_REPO_TTL_SECONDS = 86400  # TTL for enrichment data (24 hours)

# Continuous Monitoring
CONTINUOUS_MONITOR_CHECK_INTERVAL_HOURS = 24  # Check interval for monitoring
CONTINUOUS_MONITOR_REFRESH_INTERVAL_DAYS = 30  # Refresh interval for monitoring
CONTINUOUS_MONITOR_LARGE_DATASET_THRESHOLD = 10  # Threshold for large datasets

# Validation
DOMAIN_VALIDATION_SCORE_MIN = 0  # Minimum score
DOMAIN_VALIDATION_SCORE_MAX = 10  # Maximum score
DOMAIN_VALIDATION_TAGS_MIN = 1  # Minimum tags
DOMAIN_VALIDATION_TAGS_MAX = 5  # Maximum tags
DOMAIN_VALIDATION_COMPANY_NUMBER_LENGTH = 8  # UK company number length
DOMAIN_VALIDATION_REVENUE_MIN = -100  # Minimum revenue
DOMAIN_VALIDATION_REVENUE_MAX = 1000  # Maximum revenue (in billions)
DOMAIN_VALIDATION_GROWTH_RATE_MIN = -50  # Minimum growth rate
DOMAIN_VALIDATION_GROWTH_RATE_MAX = 200  # Maximum growth rate
