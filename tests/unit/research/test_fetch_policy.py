"""
Tests for STORY-226: Domain-aware fetch policy matrix and retry strategy.

Tests cover:
- Domain classification by URL
- Policy selection per domain class
- Retry cap behavior
- Fetch sequence generation
- Backoff computation
- Fetch attempt recording
"""

import time

from solstein.research.fetch_policy import (
    DEFAULT_POLICIES,
    DomainClass,
    FetchAttempt,
    FetchOutcome,
    FetchPolicy,
    FetchResult,
    FetchStrategy,
    build_fetch_sequence,
    classify_domain,
    compute_backoff,
    elapsed_ms,
    get_policy,
    record_attempt,
)

# ---------------------------------------------------------------------------
# Domain classification tests
# ---------------------------------------------------------------------------

class TestClassifyDomainKnown:
    """Test domain classification for known domain classes."""

    def test_linkedin_is_blocked_prone(self) -> None:
        assert classify_domain("https://www.linkedin.com/company/acme") == DomainClass.BLOCKED_PRONE

    def test_glassdoor_is_blocked_prone(self) -> None:
        assert classify_domain("https://glassdoor.com/reviews") == DomainClass.BLOCKED_PRONE

    def test_twitter_is_blocked_prone(self) -> None:
        assert classify_domain("https://twitter.com/acme") == DomainClass.BLOCKED_PRONE

    def test_x_com_is_blocked_prone(self) -> None:
        assert classify_domain("https://x.com/acme") == DomainClass.BLOCKED_PRONE

    def test_bloomberg_is_js_heavy(self) -> None:
        assert classify_domain("https://www.bloomberg.com/news/article") == DomainClass.JS_HEAVY

    def test_wsj_is_js_heavy(self) -> None:
        assert classify_domain("https://wsj.com/articles/test") == DomainClass.JS_HEAVY

    def test_pitchbook_is_js_heavy(self) -> None:
        assert classify_domain("https://pitchbook.com/profiles/acme") == DomainClass.JS_HEAVY

    def test_sec_gov_is_trusted(self) -> None:
        assert classify_domain("https://sec.gov/cgi-bin/browse-edgar") == DomainClass.TRUSTED

    def test_wikipedia_is_trusted(self) -> None:
        assert classify_domain("https://en.wikipedia.org/wiki/Acme") == DomainClass.TRUSTED

    def test_crunchbase_is_trusted(self) -> None:
        assert classify_domain("https://crunchbase.com/organization/acme") == DomainClass.TRUSTED

    def test_pdf_extension_is_document_heavy(self) -> None:
        assert classify_domain("https://example.com/report.pdf") == DomainClass.DOCUMENT_HEAVY

    def test_xlsx_extension_is_document_heavy(self) -> None:
        assert classify_domain("https://example.com/data.xlsx") == DomainClass.DOCUMENT_HEAVY


class TestClassifyDomainEdgeCases:
    """Test domain classification edge cases and priority rules."""

    def test_unknown_domain_is_default(self) -> None:
        assert classify_domain("https://some-random-site.com/page") == DomainClass.DEFAULT

    def test_empty_url_is_default(self) -> None:
        assert classify_domain("") == DomainClass.DEFAULT

    def test_malformed_url_is_default(self) -> None:
        assert classify_domain("not a url at all") == DomainClass.DEFAULT

    def test_subdomain_linkedin_is_blocked_prone(self) -> None:
        assert classify_domain("https://de.linkedin.com/company/acme") == DomainClass.BLOCKED_PRONE

    def test_document_extension_takes_priority_over_domain(self) -> None:
        # A PDF on a trusted domain should be classified as document_heavy
        assert classify_domain("https://sec.gov/filing.pdf") == DomainClass.DOCUMENT_HEAVY


# ---------------------------------------------------------------------------
# Policy selection tests
# ---------------------------------------------------------------------------

class TestGetPolicy:
    """Test policy retrieval and override mechanism."""

    def test_default_policy_exists_for_all_classes(self) -> None:
        for dc in DomainClass:
            policy = get_policy(dc)
            assert isinstance(policy, FetchPolicy)
            assert policy.domain_class == dc

    def test_blocked_prone_uses_reader_first(self) -> None:
        policy = get_policy(DomainClass.BLOCKED_PRONE)
        assert policy.strategy == FetchStrategy.READER_THEN_DIRECT

    def test_trusted_has_short_timeout(self) -> None:
        policy = get_policy(DomainClass.TRUSTED)
        assert policy.timeout_seconds <= 20.0

    def test_document_heavy_uses_direct_only(self) -> None:
        policy = get_policy(DomainClass.DOCUMENT_HEAVY)
        assert policy.strategy == FetchStrategy.DIRECT_ONLY

    def test_override_timeout(self) -> None:
        policy = get_policy(DomainClass.DEFAULT, overrides={"timeout_seconds": 99.0})
        assert policy.timeout_seconds == 99.0
        # Other fields unchanged
        assert policy.max_retries == DEFAULT_POLICIES[DomainClass.DEFAULT].max_retries

    def test_override_strategy(self) -> None:
        policy = get_policy(
            DomainClass.DEFAULT,
            overrides={"strategy": "reader"},
        )
        assert policy.strategy == FetchStrategy.READER

    def test_no_override_returns_default(self) -> None:
        policy = get_policy(DomainClass.DEFAULT)
        assert policy is DEFAULT_POLICIES[DomainClass.DEFAULT]


# ---------------------------------------------------------------------------
# Fetch sequence tests
# ---------------------------------------------------------------------------

class TestBuildFetchSequence:
    """Test fetch strategy sequence generation."""

    def test_direct_then_reader(self) -> None:
        policy = FetchPolicy(
            domain_class=DomainClass.DEFAULT,
            strategy=FetchStrategy.DIRECT_THEN_READER,
            max_retries=1,
            timeout_seconds=30.0,
        )
        seq = build_fetch_sequence(policy)
        assert seq == [FetchStrategy.DIRECT, FetchStrategy.READER]

    def test_reader_then_direct(self) -> None:
        policy = FetchPolicy(
            domain_class=DomainClass.BLOCKED_PRONE,
            strategy=FetchStrategy.READER_THEN_DIRECT,
            max_retries=1,
            timeout_seconds=30.0,
        )
        seq = build_fetch_sequence(policy)
        assert seq == [FetchStrategy.READER, FetchStrategy.DIRECT]

    def test_direct_only(self) -> None:
        policy = FetchPolicy(
            domain_class=DomainClass.DOCUMENT_HEAVY,
            strategy=FetchStrategy.DIRECT_ONLY,
            max_retries=1,
            timeout_seconds=30.0,
        )
        seq = build_fetch_sequence(policy)
        assert seq == [FetchStrategy.DIRECT]


# ---------------------------------------------------------------------------
# Retry and backoff tests
# ---------------------------------------------------------------------------

class TestRetryBehavior:
    """Test retry caps and backoff computation."""

    def test_backoff_increases_exponentially(self) -> None:
        delays = [compute_backoff(i, 1.0) for i in range(5)]
        assert delays[0] == 1.0  # 1 * 2^0
        assert delays[1] == 2.0  # 1 * 2^1
        assert delays[2] == 4.0  # 1 * 2^2

    def test_backoff_capped_at_30_seconds(self) -> None:
        delay = compute_backoff(10, 1.0)
        assert delay == 30.0

    def test_custom_backoff_base(self) -> None:
        delay = compute_backoff(0, 2.0)
        assert delay == 2.0

    def test_max_retries_bounded_for_all_policies(self) -> None:
        for dc in DomainClass:
            policy = get_policy(dc)
            # No policy should allow more than 3 retries
            assert policy.max_retries <= 3, (
                f"Policy for {dc.value} has max_retries={policy.max_retries}, "
                f"which exceeds the hard cap of 3"
            )

    def test_no_infinite_retry_path(self) -> None:
        """Verify that every policy has a bounded total attempt count."""
        for dc in DomainClass:
            policy = get_policy(dc)
            sequence = build_fetch_sequence(policy)
            # Total attempts = len(sequence) * (max_retries + 1)
            max_attempts = len(sequence) * (policy.max_retries + 1)
            assert max_attempts <= 10, (
                f"Policy for {dc.value} can produce up to {max_attempts} attempts"
            )


# ---------------------------------------------------------------------------
# Fetch attempt recording tests
# ---------------------------------------------------------------------------

class TestRecordAttempt:
    """Test structured fetch attempt recording."""

    def test_creates_attempt_with_all_fields(self) -> None:
        attempt = record_attempt(
            url="https://example.com",
            strategy=FetchStrategy.DIRECT,
            attempt_number=1,
            outcome=FetchOutcome.SUCCESS,
            status_code=200,
            duration_ms=150.5,
            content_length=5000,
        )
        assert attempt.url == "https://example.com"
        assert attempt.strategy_used == FetchStrategy.DIRECT
        assert attempt.attempt_number == 1
        assert attempt.outcome == FetchOutcome.SUCCESS
        assert attempt.status_code == 200
        assert attempt.duration_ms == 150.5
        assert attempt.content_length == 5000
        assert attempt.error_message is None

    def test_error_attempt(self) -> None:
        attempt = record_attempt(
            url="https://example.com",
            strategy=FetchStrategy.READER,
            attempt_number=2,
            outcome=FetchOutcome.TIMEOUT,
            error_message="Connection timed out",
        )
        assert attempt.outcome == FetchOutcome.TIMEOUT
        assert attempt.error_message == "Connection timed out"


# ---------------------------------------------------------------------------
# FetchResult metadata tests
# ---------------------------------------------------------------------------

class TestFetchResultMetadata:
    """Test FetchResult.to_metadata() produces structured output."""

    def test_successful_result_metadata(self) -> None:
        result = FetchResult(
            url="https://example.com",
            domain_class=DomainClass.DEFAULT,
            policy=get_policy(DomainClass.DEFAULT),
            success=True,
            content="Hello world",
            content_type="text/html",
            attempts=[
                FetchAttempt(
                    url="https://example.com",
                    strategy_used=FetchStrategy.DIRECT,
                    attempt_number=1,
                    outcome=FetchOutcome.SUCCESS,
                    status_code=200,
                    duration_ms=100.0,
                    content_length=11,
                ),
            ],
            terminal_outcome=FetchOutcome.SUCCESS,
            total_duration_ms=100.0,
        )
        meta = result.to_metadata()
        assert meta["success"] is True
        assert meta["domain_class"] == "default"
        assert meta["terminal_outcome"] == "success"
        assert meta["attempt_count"] == 1
        assert meta["content_length"] == 11

    def test_failed_result_metadata(self) -> None:
        result = FetchResult(
            url="https://linkedin.com/company/x",
            domain_class=DomainClass.BLOCKED_PRONE,
            policy=get_policy(DomainClass.BLOCKED_PRONE),
            success=False,
            attempts=[
                FetchAttempt(
                    url="https://linkedin.com/company/x",
                    strategy_used=FetchStrategy.READER,
                    attempt_number=1,
                    outcome=FetchOutcome.BLOCKED,
                    duration_ms=500.0,
                ),
            ],
            terminal_outcome=FetchOutcome.BLOCKED,
            total_duration_ms=500.0,
        )
        meta = result.to_metadata()
        assert meta["success"] is False
        assert meta["domain_class"] == "blocked_prone"
        assert meta["content_length"] == 0


# ---------------------------------------------------------------------------
# Utility tests
# ---------------------------------------------------------------------------

class TestElapsedMs:
    """Test elapsed time helper."""

    def test_returns_positive_float(self) -> None:
        start = time.monotonic()
        time.sleep(0.01)
        ms = elapsed_ms(start)
        assert ms > 0.0
        assert isinstance(ms, float)


# ---------------------------------------------------------------------------
# Reader URL generation
# ---------------------------------------------------------------------------

class TestReaderUrl:
    """Test reader URL template in policy."""

    def test_default_reader_url(self) -> None:
        policy = get_policy(DomainClass.DEFAULT)
        assert policy.reader_url("https://example.com") == "https://r.jina.ai/https://example.com"

    def test_strips_whitespace(self) -> None:
        policy = get_policy(DomainClass.DEFAULT)
        assert policy.reader_url("  https://example.com  ") == "https://r.jina.ai/https://example.com"
