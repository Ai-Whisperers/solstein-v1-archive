"""Constants for data connectors - API timeouts, retry policies, and confidence scores."""

# SEC EDGAR Connector
SEC_EDGAR_DEFAULT_CONFIDENCE = 0.95  # SEC filings are authoritative
SEC_EDGAR_DEFAULT_MAX_ATTEMPTS = 4  # Maximum retry attempts for SEC API calls
SEC_EDGAR_DEFAULT_BASE_SLEEP_S = 0.5  # Initial backoff delay in seconds
SEC_EDGAR_DEFAULT_MAX_SLEEP_S = 8.0  # Maximum backoff delay in seconds
SEC_EDGAR_DEFAULT_RATE_LIMIT_SLEEP_S = 15.0  # Sleep duration when rate limited (429)

# GitHub Connector
GITHUB_DEFAULT_PER_PAGE = 30  # Default pagination size for GitHub API
GITHUB_REQUEST_TIMEOUT_S = 15  # HTTP request timeout in seconds
GITHUB_DEFAULT_CONFIDENCE = 0.85  # GitHub data is authoritative for technical signals

# Companies House Connector
COMPANIES_HOUSE_DEFAULT_CONFIDENCE = 0.93  # UK Companies House is authoritative
COMPANIES_HOUSE_REQUEST_TIMEOUT_S = 15.0  # HTTP request timeout in seconds

# News Signal Detector
NEWS_SIGNAL_DAILY_QUERY_LIMIT = 100  # Maximum queries per day
NEWS_SIGNAL_REQUEST_TIMEOUT_S = 10  # HTTP request timeout in seconds

# HTTP Status Codes (for clarity in error handling)
HTTP_STATUS_OK = 200
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_RATE_LIMITED = 429
HTTP_STATUS_SERVER_ERROR_MIN = 500
