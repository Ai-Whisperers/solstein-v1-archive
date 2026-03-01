"""Constants for data adapters and enrichment sources."""

# Discovery Adapters
DISCOVERY_MAX_RESULTS = 50  # Maximum results for discovery adapters
DISCOVERY_CONFIDENCE_DEFAULT = 0.5  # Default confidence for discovery
DISCOVERY_TAGS_LIMIT = 3  # Maximum tags to extract

# Enrichment Adapter Confidence Scores
ENRICHMENT_CONFIDENCE_FUNDING_WITH_KEY = 0.7  # Funding confidence with API key
ENRICHMENT_CONFIDENCE_FUNDING_WITHOUT_KEY = 0.3  # Funding confidence without API key
ENRICHMENT_CONFIDENCE_FUNDING_UNIFIED = 0.65  # Unified funding confidence
ENRICHMENT_RELEVANCE_FUNDING = 0.8  # Funding relevance score

ENRICHMENT_CONFIDENCE_LINKEDIN = 0.3  # LinkedIn confidence
ENRICHMENT_RELEVANCE_LINKEDIN = 0.5  # LinkedIn relevance score
ENRICHMENT_CONFIDENCE_LINKEDIN_UNIFIED = 0.60  # Unified LinkedIn confidence

ENRICHMENT_CONFIDENCE_NEWS = 0.6  # News confidence with API key
ENRICHMENT_CONFIDENCE_NEWS_WITHOUT_KEY = 0.4  # News confidence without API key
ENRICHMENT_CONFIDENCE_NEWS_UNIFIED = 0.70  # Unified news confidence
ENRICHMENT_RELEVANCE_NEWS = 0.7  # News relevance score
ENRICHMENT_NEWS_DEFAULT_DAYS_BACK = 30  # Default lookback for news

ENRICHMENT_CONFIDENCE_PATENTS = 0.7  # Patents confidence
ENRICHMENT_CONFIDENCE_PATENTS_UNIFIED = 0.80  # Unified patents confidence
ENRICHMENT_RELEVANCE_PATENTS = 0.6  # Patents relevance score

ENRICHMENT_CONFIDENCE_WEB_SEARCH = 0.5  # Web search confidence
ENRICHMENT_CONFIDENCE_WEB_SEARCH_UNIFIED = 0.70  # Unified web search confidence
ENRICHMENT_RELEVANCE_WEB_SEARCH = 0.7  # Web search relevance score
ENRICHMENT_WEB_SEARCH_MAX_RESULTS = 20  # Maximum web search results

ENRICHMENT_CONFIDENCE_WEBSITE = 0.5  # Website confidence
ENRICHMENT_CONFIDENCE_WEBSITE_UNIFIED = 0.70  # Unified website confidence
ENRICHMENT_RELEVANCE_WEBSITE = 0.7  # Website relevance score
ENRICHMENT_WEBSITE_REQUEST_TIMEOUT_S = 10  # Website request timeout

ENRICHMENT_CONFIDENCE_GLOBAL_MARKET = 0.8  # Global market confidence
ENRICHMENT_RELEVANCE_GLOBAL_MARKET = 0.9  # Global market relevance score

ENRICHMENT_CONFIDENCE_YAHOO_FINANCE = 0.8  # Yahoo Finance confidence
ENRICHMENT_RELEVANCE_YAHOO_FINANCE = 0.9  # Yahoo Finance relevance score

# Data Extraction Limits
ENRICHMENT_LINKEDIN_RECENT_HIRES_LIMIT = 10  # Maximum recent hires
ENRICHMENT_WEBSITE_PRODUCTS_LIMIT = 10  # Maximum products
ENRICHMENT_WEBSITE_TECH_STACK_LIMIT = 10  # Maximum tech stack items
ENRICHMENT_WEB_SEARCH_SNIPPET_LIMIT = 200  # Maximum snippet length

# Pagination
ENRICHMENT_ADAPTER_MAX_RESULTS = 50  # Maximum results for adapters
ENRICHMENT_ADAPTER_PAGINATION_SIZE = 50  # Pagination size for adapters

# Instrumented Adapter
INSTRUMENTED_ADAPTER_MAX_RESULTS = 50  # Maximum results for instrumented adapter

# Protocol Defaults
PROTOCOL_MAX_RESULTS = 50  # Default max results for protocols
