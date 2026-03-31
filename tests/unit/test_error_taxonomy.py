"""Tests for error taxonomy module.

F1: Tests for global exception taxonomy.
"""


from solstein.core.error_taxonomy import (
    ERROR_CLASSIFICATION,
    ErrorCategory,
    ErrorSeverity,
    RetryPolicy,
    classify_error,
    get_exception_standards,
    get_http_status,
    is_retryable,
)


class TestErrorCategories:
    """Tests for error category enum."""

    def test_validation_category(self) -> None:
        assert ErrorCategory.VALIDATION

    def test_all_categories_exist(self) -> None:
        categories = [
            ErrorCategory.VALIDATION,
            ErrorCategory.AUTHENTICATION,
            ErrorCategory.AUTHORIZATION,
            ErrorCategory.NOT_FOUND,
            ErrorCategory.CONFLICT,
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.INFRASTRUCTURE,
            ErrorCategory.EXTERNAL_SERVICE,
            ErrorCategory.TIMEOUT,
            ErrorCategory.UNAVAILABLE,
            ErrorCategory.BUSINESS_RULE,
            ErrorCategory.DATA_QUALITY,
        ]
        assert len(categories) == 12


class TestErrorSeverity:
    """Tests for error severity enum."""

    def test_all_severities_exist(self) -> None:
        severities = [
            ErrorSeverity.DEBUG,
            ErrorSeverity.INFO,
            ErrorSeverity.WARNING,
            ErrorSeverity.ERROR,
            ErrorSeverity.CRITICAL,
        ]
        assert len(severities) == 5


class TestRetryPolicy:
    """Tests for retry policy enum."""

    def test_all_policies_exist(self) -> None:
        policies = [
            RetryPolicy.NEVER,
            RetryPolicy.IMMEDIATE,
            RetryPolicy.BACKOFF,
            RetryPolicy.CIRCUIT_BREAK,
        ]
        assert len(policies) == 4


class TestClassifyError:
    """Tests for classify_error function."""

    def test_validation_error_classification(self) -> None:
        result = classify_error("VALIDATION_ERROR")
        assert result["category"] == ErrorCategory.VALIDATION
        assert result["severity"] == ErrorSeverity.WARNING
        assert result["retry"] == RetryPolicy.NEVER
        assert result["http_status"] == 400

    def test_database_error_classification(self) -> None:
        result = classify_error("DATABASE_ERROR")
        assert result["category"] == ErrorCategory.INFRASTRUCTURE
        assert result["severity"] == ErrorSeverity.ERROR
        assert result["retry"] == RetryPolicy.BACKOFF
        assert result["http_status"] == 500

    def test_external_service_error_classification(self) -> None:
        result = classify_error("EXTERNAL_SERVICE_ERROR")
        assert result["category"] == ErrorCategory.EXTERNAL_SERVICE
        assert result["retry"] == RetryPolicy.BACKOFF
        assert result["http_status"] == 502

    def test_rate_limit_classification(self) -> None:
        result = classify_error("RATE_LIMIT_EXCEEDED")
        assert result["category"] == ErrorCategory.RATE_LIMIT
        assert result["retry"] == RetryPolicy.BACKOFF
        assert result["http_status"] == 429

    def test_unknown_error_defaults(self) -> None:
        result = classify_error("UNKNOWN_ERROR")
        assert result["category"] == ErrorCategory.INFRASTRUCTURE
        assert result["severity"] == ErrorSeverity.ERROR
        assert result["retry"] == RetryPolicy.BACKOFF
        assert result["http_status"] == 500


class TestIsRetryable:
    """Tests for is_retryable function."""

    def test_validation_not_retryable(self) -> None:
        assert is_retryable("VALIDATION_ERROR") is False

    def test_auth_not_retryable(self) -> None:
        assert is_retryable("AUTHENTICATION_FAILED") is False

    def test_database_is_retryable(self) -> None:
        assert is_retryable("DATABASE_ERROR") is True

    def test_external_service_is_retryable(self) -> None:
        assert is_retryable("EXTERNAL_SERVICE_ERROR") is True

    def test_timeout_is_retryable(self) -> None:
        assert is_retryable("TIMEOUT_ERROR") is True


class TestGetHttpStatus:
    """Tests for get_http_status function."""

    def test_validation_400(self) -> None:
        assert get_http_status("VALIDATION_ERROR") == 400

    def test_not_found_404(self) -> None:
        assert get_http_status("NOT_FOUND") == 404

    def test_conflict_409(self) -> None:
        assert get_http_status("CONFLICT") == 409

    def test_rate_limit_429(self) -> None:
        assert get_http_status("RATE_LIMIT_EXCEEDED") == 429

    def test_database_500(self) -> None:
        assert get_http_status("DATABASE_ERROR") == 500

    def test_external_service_502(self) -> None:
        assert get_http_status("EXTERNAL_SERVICE_ERROR") == 502

    def test_unknown_defaults_500(self) -> None:
        assert get_http_status("UNKNOWN") == 500


class TestErrorClassificationMapping:
    """Tests for ERROR_CLASSIFICATION mapping."""

    def test_all_entries_have_required_fields(self) -> None:
        for code, classification in ERROR_CLASSIFICATION.items():
            assert "category" in classification
            assert "severity" in classification
            assert "retry" in classification
            assert "http_status" in classification

    def test_http_status_codes_are_valid(self) -> None:
        for code, classification in ERROR_CLASSIFICATION.items():
            status = classification["http_status"]
            assert 400 <= status < 600, f"{code} has invalid status {status}"


class TestExceptionStandards:
    """Tests for exception standards documentation."""

    def test_standards_documentation_exists(self) -> None:
        standards = get_exception_standards()
        assert len(standards) > 0

    def test_standards_contains_golden_rules(self) -> None:
        standards = get_exception_standards()
        assert "Golden Rules" in standards

    def test_standards_contains_hotspot_files(self) -> None:
        standards = get_exception_standards()
        assert "Hotspot Files" in standards
