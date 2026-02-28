"""Domain constants and validation rules - Phase 2, Item 2.4"""

# Allowed search fields by model
ALLOWED_SEARCH_FIELDS = {
    "company": {"id", "name", "industry", "headquarters", "tier", "classification", "status"},
    "market": {"id", "name", "region", "industry"},
}

# Validation rules
COMPANY_NAME_MIN_LENGTH = 2
COMPANY_NAME_MAX_LENGTH = 255

# Valid industry values
INDUSTRY_VALID_VALUES = {
    "Technology",
    "Healthcare",
    "Finance",
    "Energy",
    "Consumer",
    "Industrial",
    "Materials",
    "Real Estate",
    "Retail",
    "Telecommunications",
    "Automotive",
    "Pharmaceuticals",
    "Aerospace",
    "Chemicals",
}

# Score ranges
SCORE_MIN = 0.0
SCORE_MAX = 1.0

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Cache TTL defaults
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 3600  # 1 hour
CACHE_TTL_LONG = 86400  # 24 hours
