"""Constants for agent resilience, circuit breakers, and retry policies."""

# Circuit Breaker Configuration
GITHUB_AGENT_FAILURE_THRESHOLD = 5  # Failures before circuit opens
GITHUB_AGENT_RECOVERY_TIMEOUT_S = 60.0  # Seconds before attempting recovery

COMPANIES_HOUSE_AGENT_FAILURE_THRESHOLD = 4  # Failures before circuit opens
COMPANIES_HOUSE_AGENT_RECOVERY_TIMEOUT_S = 90.0  # Seconds before attempting recovery

WEB_SEARCH_AGENT_FAILURE_THRESHOLD = 3  # Failures before circuit opens
WEB_SEARCH_AGENT_RECOVERY_TIMEOUT_S = 45.0  # Seconds before attempting recovery

# Retry Configuration
RETRY_MAX_ATTEMPTS = 5  # Maximum number of retry attempts
RETRY_MAX_DELAY_S = 60.0  # Maximum delay between retries in seconds
RETRY_TIMEOUT_S = 30.0  # Timeout for individual retry attempts

# Request Timeouts
GITHUB_AGENT_REQUEST_TIMEOUT_S = 15  # GitHub API request timeout
WEBSITE_AGENT_REQUEST_TIMEOUT_S = 20  # Website scraping timeout
WEB_SEARCH_AGENT_REQUEST_TIMEOUT_S = 10  # Web search request timeout

# Data Limits
GITHUB_AGENT_TOP_REPOS_LIMIT = 5  # Number of top repositories to analyze
WEB_SEARCH_AGENT_ARTICLES_LIMIT = 5  # Number of articles to process
WEBSITE_AGENT_EXCERPT_MAX_LENGTH = 5000  # Maximum characters for website excerpt

# Confidence Scores
GITHUB_AGENT_CONFIDENCE = 0.95  # High confidence for GitHub data
WEBSITE_AGENT_CONFIDENCE = 0.70  # Moderate confidence for website data
WEB_SEARCH_AGENT_CONFIDENCE = 0.75  # Moderate confidence for web search
SEED_MARKDOWN_AGENT_CONFIDENCE = 0.90  # High confidence for seed data

# Pagination
COMPANIES_HOUSE_ITEMS_PER_PAGE = 10  # Items per page for Companies House API
WEB_SEARCH_AGENT_RESULTS_PER_PAGE = 10  # Results per page for web search

# Data Source Confidence Weights (for coordinator agent)
DATA_SOURCE_CONFIDENCE_WEIGHTS = {
    "COMPANY_FILINGS": 0.99,  # SEC/Companies House filings
    "GITHUB": 0.95,  # GitHub technical data
    "NEWS": 0.75,  # News articles
    "CRUNCHBASE": 0.85,  # Crunchbase funding data
    "LINKEDIN": 0.82,  # LinkedIn company data
    "WEBSITE": 0.84,  # Company website data
    "YAHOO_FINANCE": 0.88,  # Yahoo Finance market data
    "PATENTS": 0.80,  # Patent data
    "WEB_SEARCH": 0.68,  # General web search
}
