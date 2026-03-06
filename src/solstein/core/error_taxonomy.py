"""Exception taxonomy and error handling standards.

F1: Define global exception taxonomy
F2: Refactor top 20 hotspot modules with typed errors

This module provides:
1. Typed exception classes for specific error scenarios
2. Error classification utilities
3. Standards for exception handling
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Any


class ErrorCategory(Enum):
    """Classification of error types for handling policies."""

    # Client errors (4xx) - caller's fault
    VALIDATION = auto()  # Invalid input format/values
    AUTHENTICATION = auto()  # Missing/invalid credentials
    AUTHORIZATION = auto()  # Insufficient permissions
    NOT_FOUND = auto()  # Resource doesn't exist
    CONFLICT = auto()  # Resource conflict/state violation
    RATE_LIMIT = auto()  # Too many requests

    # Server errors (5xx) - service's fault
    INFRASTRUCTURE = auto()  # Internal service failure
    EXTERNAL_SERVICE = auto()  # Third-party service failure
    TIMEOUT = auto()  # Operation timed out
    UNAVAILABLE = auto()  # Service temporarily unavailable

    # Business logic errors
    BUSINESS_RULE = auto()  # Violates business rules
    DATA_QUALITY = auto()  # Data quality issues


class ErrorSeverity(Enum):
    """Severity levels for errors."""

    DEBUG = auto()  # Informational, no action needed
    INFO = auto()  # Notable but not problematic
    WARNING = auto()  # Should be investigated
    ERROR = auto()  # Requires attention
    CRITICAL = auto()  # Immediate response required


class RetryPolicy(Enum):
    """Retry policies for different error types."""

    NEVER = auto()  # Don't retry (client error)
    IMMEDIATE = auto()  # Retry immediately (transient)
    BACKOFF = auto()  # Retry with exponential backoff
    CIRCUIT_BREAK = auto()  # Stop and check circuit breaker


# Error classification mapping
ERROR_CLASSIFICATION: dict[str, dict[str, Any]] = {
    # Validation errors
    "VALIDATION_ERROR": {
        "category": ErrorCategory.VALIDATION,
        "severity": ErrorSeverity.WARNING,
        "retry": RetryPolicy.NEVER,
        "http_status": 400,
    },
    "SCHEMA_VIOLATION": {
        "category": ErrorCategory.VALIDATION,
        "severity": ErrorSeverity.WARNING,
        "retry": RetryPolicy.NEVER,
        "http_status": 400,
    },
    # Authentication/Authorization
    "AUTHENTICATION_FAILED": {
        "category": ErrorCategory.AUTHENTICATION,
        "severity": ErrorSeverity.WARNING,
        "retry": RetryPolicy.NEVER,
        "http_status": 401,
    },
    "PERMISSION_DENIED": {
        "category": ErrorCategory.AUTHORIZATION,
        "severity": ErrorSeverity.WARNING,
        "retry": RetryPolicy.NEVER,
        "http_status": 403,
    },
    # Not found
    "NOT_FOUND": {
        "category": ErrorCategory.NOT_FOUND,
        "severity": ErrorSeverity.INFO,
        "retry": RetryPolicy.NEVER,
        "http_status": 404,
    },
    # Conflict
    "CONFLICT": {
        "category": ErrorCategory.CONFLICT,
        "severity": ErrorSeverity.WARNING,
        "retry": RetryPolicy.NEVER,
        "http_status": 409,
    },
    "STATE_ERROR": {
        "category": ErrorCategory.CONFLICT,
        "severity": ErrorSeverity.WARNING,
        "retry": RetryPolicy.NEVER,
        "http_status": 409,
    },
    # Rate limiting
    "RATE_LIMIT_EXCEEDED": {
        "category": ErrorCategory.RATE_LIMIT,
        "severity": ErrorSeverity.WARNING,
        "retry": RetryPolicy.BACKOFF,
        "http_status": 429,
    },
    # Infrastructure
    "DATABASE_ERROR": {
        "category": ErrorCategory.INFRASTRUCTURE,
        "severity": ErrorSeverity.ERROR,
        "retry": RetryPolicy.BACKOFF,
        "http_status": 500,
    },
    "CONFIGURATION_ERROR": {
        "category": ErrorCategory.INFRASTRUCTURE,
        "severity": ErrorSeverity.CRITICAL,
        "retry": RetryPolicy.NEVER,
        "http_status": 500,
    },
    # External services
    "EXTERNAL_SERVICE_ERROR": {
        "category": ErrorCategory.EXTERNAL_SERVICE,
        "severity": ErrorSeverity.ERROR,
        "retry": RetryPolicy.BACKOFF,
        "http_status": 502,
    },
    "LLM_ERROR": {
        "category": ErrorCategory.EXTERNAL_SERVICE,
        "severity": ErrorSeverity.ERROR,
        "retry": RetryPolicy.BACKOFF,
        "http_status": 502,
    },
    # Timeouts
    "TIMEOUT_ERROR": {
        "category": ErrorCategory.TIMEOUT,
        "severity": ErrorSeverity.ERROR,
        "retry": RetryPolicy.BACKOFF,
        "http_status": 504,
    },
    # Business rules
    "BUSINESS_RULE_VIOLATION": {
        "category": ErrorCategory.BUSINESS_RULE,
        "severity": ErrorSeverity.WARNING,
        "retry": RetryPolicy.NEVER,
        "http_status": 400,
    },
    # Data quality
    "DATA_QUALITY_ERROR": {
        "category": ErrorCategory.DATA_QUALITY,
        "severity": ErrorSeverity.WARNING,
        "retry": RetryPolicy.NEVER,
        "http_status": 400,
    },
}


def classify_error(error_code: str) -> dict[str, Any]:
    """Get classification for an error code.

    Args:
        error_code: The error code to classify

    Returns:
        Classification dictionary with category, severity, retry policy, and HTTP status
    """
    return ERROR_CLASSIFICATION.get(
        error_code,
        {
            "category": ErrorCategory.INFRASTRUCTURE,
            "severity": ErrorSeverity.ERROR,
            "retry": RetryPolicy.BACKOFF,
            "http_status": 500,
        },
    )


def is_retryable(error_code: str) -> bool:
    """Check if an error is retryable.

    Args:
        error_code: The error code to check

    Returns:
        True if the error is retryable
    """
    classification = classify_error(error_code)
    return classification["retry"] != RetryPolicy.NEVER


def get_http_status(error_code: str) -> int:
    """Get HTTP status code for an error.

    Args:
        error_code: The error code

    Returns:
        HTTP status code
    """
    classification = classify_error(error_code)
    return classification["http_status"]


# F2: Exception handling standards documentation
EXCEPTION_HANDLING_STANDARDS = """
# Exception Handling Standards (F2)

## Golden Rules

1. **Never use bare except:**
   ```python
   # BAD
   except:
       pass

   # GOOD
   except SpecificError:
       handle_error()
   ```

2. **Never use except Exception for control flow:**
   ```python
   # BAD
   try:
       result = operation()
   except Exception:
       result = default

   # GOOD
   try:
       result = operation()
   except SpecificError as e:
       logger.warning("Operation failed, using default", error=str(e))
       result = default
   ```

3. **Always log exceptions with context:**
   ```python
   # BAD
   except Exception as e:
       logger.error("Error occurred")

   # GOOD
   except DatabaseError as e:
       logger.error(
           "Database query failed",
           error=str(e),
           query=query,
           company_id=company_id
       )
   ```

4. **Use specific exception types:**
   ```python
   # BAD
   raise Exception("Invalid input")

   # GOOD
   raise ValidationError(
       "Invalid revenue value",
       details={"field": "revenue", "value": -100}
   )
   ```

## Error Categories

### Validation Errors (4xx)
- **VALIDATION_ERROR**: Input format/type violations
- **SCHEMA_VIOLATION**: JSON schema validation failures
- **NOT_FOUND**: Resource doesn't exist
- **CONFLICT**: Resource conflicts/state violations
- **RATE_LIMIT_EXCEEDED**: Too many requests

### Infrastructure Errors (5xx)
- **DATABASE_ERROR**: Database operation failures
- **EXTERNAL_SERVICE_ERROR**: Third-party API failures
- **LLM_ERROR**: LLM provider failures
- **TIMEOUT_ERROR**: Operation timeouts
- **CONFIGURATION_ERROR**: Invalid/missing configuration

### Business Logic Errors
- **BUSINESS_RULE_VIOLATION**: Violates business rules
- **DATA_QUALITY_ERROR**: Data quality issues

## Retry Policies

| Error Category | Retry Policy | Backoff |
|----------------|--------------|---------|
| Validation | Never | N/A |
| Authentication | Never | N/A |
| Not Found | Never | N/A |
| Database | Backoff | Exponential |
| External Service | Backoff | Exponential |
| Timeout | Backoff | Linear |
| Rate Limit | Backoff | Based on Retry-After |

## Hotspot Files Requiring Refactoring

The following files have been identified as having broad exception handling:

1. src/solstein/agents/github_agent.py (line 342)
2. src/solstein/exporters/llm.py (line 74)
3. src/solstein/api/websocket/manager.py (line 69)
4. src/solstein/api/middleware/tenant.py (line 74)
5. src/solstein/api/middleware/tracing.py (line 171)
6. src/solstein/api/middleware/logging.py (line 77)
7. src/solstein/data/patent_client.py (line 163)
8. src/solstein/data/eneve_enrichment_integration.py (lines 112, 130)
9. src/solstein/llm/enhanced_client.py (line 311)
10. src/solstein/data/connectors/lookup_service.py (line 28)
11. src/solstein/infrastructure/test_cleanup.py (lines 33, 51, 80, 109)
12. src/solstein/infrastructure/research_dual_write.py (line 134)
13. src/solstein/data/connectors/sec_edgar_connector.py (line 330)
14. src/solstein/analytics/workflows.py (line 6)
15. src/solstein/infrastructure/connectors/github_refresh.py (line 198)
16. src/solstein/infrastructure/connectors/news_signal_refresh.py (line 105)
17. src/solstein/research/sources.py (line 73)
18. src/solstein/infrastructure/connectors/sec_edgar_refresh.py (line 118)
19. src/solstein/analytics/scorers/financial_health.py (line 167)
20. src/solstein/infrastructure/connectors/companies_house_refresh.py (line 116)
21. src/solstein/analytics/scorers/growth_momentum.py (line 194)

Each should be refactored to:
1. Catch specific exceptions instead of Exception
2. Use appropriate SolsteinError subclasses
3. Log with proper context
4. Follow retry policies based on error classification
"""


def get_exception_standards() -> str:
    """Get the exception handling standards documentation."""
    return EXCEPTION_HANDLING_STANDARDS
