"""Constants for data enrichment, validation, and processing."""

# Request Timeouts
REQUEST_TIMEOUT_DEFAULT_S = 10  # Default HTTP request timeout
REQUEST_TIMEOUT_LONG_S = 15  # Longer timeout for complex requests
REQUEST_TIMEOUT_WEBSITE_S = 20  # Website scraping timeout
REQUEST_TIMEOUT_PATENT_S = 30  # Patent API timeout

# Retry Configuration
ENRICHMENT_MAX_RETRIES = 3  # Maximum retry attempts for enrichment
ENRICHMENT_TIMEOUT_SECONDS = 30  # Timeout for enrichment operations
ENRICHMENT_BATCH_SIZE = 10  # Batch size for enrichment processing

# News Data
NEWS_DEFAULT_DAYS_BACK = 30  # Default lookback period for news
NEWS_LINKEDIN_DAYS_BACK = 90  # Lookback period for LinkedIn news
NEWS_FUNDING_DAYS_BACK = 180  # Lookback period for funding news
NEWS_MAX_ARTICLES = 20  # Maximum articles to process
NEWS_SNIPPET_MAX_LENGTH = 500  # Maximum snippet length

# Patent Data
PATENT_MAX_RESULTS = 20  # Maximum patent results per query
PATENT_ABSTRACT_MAX_LENGTH = 200  # Maximum abstract length

# Web Search
WEB_SEARCH_MAX_RESULTS = 20  # Maximum web search results
WEB_SEARCH_SNIPPET_MAX_LENGTH = 500  # Maximum snippet length
WEB_SEARCH_RESULTS_PER_PAGE = 10  # Results per page

# Data Extraction
LINKEDIN_RECENT_HIRES_LIMIT = 10  # Maximum recent hires to extract
WEBSITE_PRODUCTS_LIMIT = 10  # Maximum products to extract
WEBSITE_TECH_STACK_LIMIT = 10  # Maximum tech stack items to extract
WEBSITE_CUSTOMERS_LIMIT = 10  # Maximum customers to extract
COMPETITOR_DISCOVERY_TAGS_LIMIT = 3  # Maximum tags for competitor discovery
COMPETITOR_DISCOVERY_MAX_RESULTS = 50  # Maximum competitor discovery results

# Data Validation
REVENUE_DIVERGENCE_THRESHOLD = 10  # Revenue divergence threshold (10x)
REVENUE_DIVERGENCE_MIN = 0.1  # Minimum divergence ratio
EMPLOYEE_COUNT_MAX = 500000  # Maximum reasonable employee count
COMPANY_AGE_THRESHOLD_YEARS = 20  # Company age threshold for growth validation
GROWTH_RATE_THRESHOLD = 1.0  # Growth rate threshold for validation

# Data Interpolation
REVENUE_MAX_GAP_YEARS = 3  # Don't interpolate gaps > 3 years
GROWTH_SECTOR_AVERAGE_FALLBACK = 10.0  # Default sector growth rate (%)
EMPLOYEE_REVENUE_RATIO = 0.0003  # Employees per EUR of revenue

# Data Completeness
COMPLETENESS_COMPLETE_MIN = 80  # Minimum for complete (80%)
COMPLETENESS_PARTIAL_MIN = 50  # Minimum for partial (50%)
COMPLETENESS_MINIMAL_MIN = 20  # Minimum for minimal (20%)

# Enrichment Errors
ERROR_MESSAGE_MAX_LENGTH = 200  # Maximum error message length
ENRICHMENT_ERRORS_MAX = 50  # Maximum errors to store per company

# Data Quality
ENEVE_TOTAL_METRICS = 8  # Total metrics tracked by Eneve enrichment

# Confidence Scores
CONFIDENCE_CRUNCHBASE_WITH_KEY = 0.7  # Crunchbase confidence with API key
CONFIDENCE_CRUNCHBASE_WITHOUT_KEY = 0.3  # Crunchbase confidence without API key
CONFIDENCE_NEWS_WITH_KEY = 0.6  # News confidence with API key
CONFIDENCE_NEWS_WITHOUT_KEY = 0.4  # News confidence without API key
CONFIDENCE_FUNDING_UNIFIED = 0.65  # Unified funding confidence
CONFIDENCE_LINKEDIN_UNIFIED = 0.60  # Unified LinkedIn confidence
CONFIDENCE_NEWS_UNIFIED = 0.70  # Unified news confidence
CONFIDENCE_PATENTS_UNIFIED = 0.80  # Unified patents confidence
CONFIDENCE_WEB_SEARCH_UNIFIED = 0.70  # Unified web search confidence
CONFIDENCE_WEBSITE_UNIFIED = 0.70  # Unified website confidence
CONFIDENCE_YAHOO_FINANCE = 0.88  # Yahoo Finance confidence
CONFIDENCE_GLOBAL_MARKET = 0.87  # Global market data confidence

# Company Research Scoring
AI_SCORE_EXCEPTIONAL = 10  # Exceptional AI score
AI_SCORE_ADVANCED = 8  # Advanced AI score
AI_SCORE_MODERATE = 7  # Moderate AI score
AI_SCORE_EMERGING = 5  # Emerging AI score
AI_SCORE_THRESHOLD_EXCEPTIONAL = 5  # Threshold for exceptional AI count
AI_SCORE_THRESHOLD_ADVANCED = 3  # Threshold for advanced AI count

REVENUE_GROWTH_SCORE_EXCEPTIONAL = 8  # Exceptional revenue growth score
REVENUE_GROWTH_SCORE_GOOD = 6  # Good revenue growth score
REVENUE_GROWTH_SCORE_FAIR = 4  # Fair revenue growth score

PROFITABILITY_SCORE_EXCEPTIONAL = 8  # Exceptional profitability score
PROFITABILITY_SCORE_GOOD = 6  # Good profitability score
PROFITABILITY_SCORE_FAIR = 3  # Fair profitability score

MARKET_POSITION_SCORE_EXCEPTIONAL = 8  # Exceptional market position score
MARKET_POSITION_SCORE_GOOD = 6  # Good market position score
MARKET_POSITION_SCORE_FAIR = 4  # Fair market position score

INNOVATION_SCORE_EXCEPTIONAL = 9  # Exceptional innovation score
INNOVATION_SCORE_ADVANCED = 8  # Advanced innovation score
INNOVATION_SCORE_GOOD = 5  # Good innovation score

COMPOSITE_SCORE_EXCEPTIONAL = 8  # Exceptional composite score
COMPOSITE_SCORE_GOOD = 6  # Good composite score
COMPOSITE_SCORE_FAIR = 4  # Fair composite score

# Ticker Validation
TICKER_MAX_LENGTH = 4  # Maximum ticker length

# Cache Configuration
CACHE_DEFAULT_TTL_S = 3600  # Default cache TTL (1 hour)
CACHE_LONG_TTL_S = 86400  # Long cache TTL (24 hours)

# Security
RATE_LIMIT_REQUESTS_PER_MINUTE = 60  # Default rate limit
RATE_LIMIT_CACHE_MAX_ENTRIES = 10000  # Maximum cache entries for rate limiting

# Celery Configuration
CELERY_REDIS_PORT = 6379  # Redis port for Celery
CELERY_TASK_TIME_LIMIT_S = 30  # Hard time limit for tasks
CELERY_TASK_SOFT_TIME_LIMIT_S = 25  # Soft time limit for graceful shutdown

# Scheduled Tasks
SCHEDULED_TASK_HOUR = 9  # Hour for scheduled tasks (9 AM)
SCHEDULED_TASK_MINUTE = 0  # Minute for scheduled tasks
