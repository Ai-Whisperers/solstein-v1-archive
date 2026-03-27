"""
Domain-aware fetch policy matrix and retry strategy.

STORY-226: Implements policy-driven fetch behavior by domain reliability class
and content type. Every fetch attempt records strategy and outcome metadata.

Policy classes:
- default: Standard direct fetch with reader fallback
- blocked_prone: Skip direct, go straight to reader API
- js_heavy: Reader-first, with longer timeout
- document_heavy: Direct fetch only, skip reader (PDFs, spreadsheets)
- trusted: Direct fetch with short timeout, no fallback needed
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from urllib.parse import urlparse

import httpx
from loguru import logger


class DomainClass(str, Enum):
    """Domain reliability classification for fetch strategy selection."""

    DEFAULT = "default"
    BLOCKED_PRONE = "blocked_prone"
    JS_HEAVY = "js_heavy"
    DOCUMENT_HEAVY = "document_heavy"
    TRUSTED = "trusted"


class FetchStrategy(str, Enum):
    """Available fetch strategies."""

    DIRECT = "direct"
    READER = "reader"
    DIRECT_THEN_READER = "direct_then_reader"
    READER_THEN_DIRECT = "reader_then_direct"
    DIRECT_ONLY = "direct_only"


class FetchOutcome(str, Enum):
    """Terminal outcome of a fetch attempt."""

    SUCCESS = "success"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"
    HTTP_ERROR = "http_error"
    NETWORK_ERROR = "network_error"
    EMPTY_CONTENT = "empty_content"
    UNUSABLE_CONTENT = "unusable_content"


@dataclass(frozen=True)
class FetchPolicy:
    """Fetch configuration for a domain class."""

    domain_class: DomainClass
    strategy: FetchStrategy
    max_retries: int
    timeout_seconds: float
    backoff_base: float = 1.0
    reader_url_template: str = "https://r.jina.ai/{url}"

    def reader_url(self, url: str) -> str:
        return self.reader_url_template.format(url=url.strip())


@dataclass
class FetchAttempt:
    """Record of a single fetch attempt."""

    url: str
    strategy_used: FetchStrategy
    attempt_number: int
    outcome: FetchOutcome
    status_code: int | None = None
    duration_ms: float = 0.0
    error_message: str | None = None
    content_length: int = 0


@dataclass
class FetchResult:
    """Complete fetch result with all attempt metadata."""

    url: str
    domain_class: DomainClass
    policy: FetchPolicy
    success: bool
    content: str = ""
    content_type: str = ""
    attempts: list[FetchAttempt] = field(default_factory=list)
    terminal_outcome: FetchOutcome = FetchOutcome.NETWORK_ERROR
    total_duration_ms: float = 0.0

    def to_metadata(self) -> dict[str, Any]:
        """Return structured metadata for downstream consumption."""
        return {
            "url": self.url,
            "domain_class": self.domain_class.value,
            "strategy": self.policy.strategy.value,
            "success": self.success,
            "terminal_outcome": self.terminal_outcome.value,
            "attempt_count": len(self.attempts),
            "total_duration_ms": round(self.total_duration_ms, 1),
            "content_length": len(self.content) if self.success else 0,
            "attempts": [
                {
                    "strategy": a.strategy_used.value,
                    "attempt": a.attempt_number,
                    "outcome": a.outcome.value,
                    "status_code": a.status_code,
                    "duration_ms": round(a.duration_ms, 1),
                    "error": a.error_message,
                }
                for a in self.attempts
            ],
        }


# ---------------------------------------------------------------------------
# Default policy matrix (externally configurable via FETCH_POLICY_OVERRIDES)
# ---------------------------------------------------------------------------

DEFAULT_POLICIES: dict[DomainClass, FetchPolicy] = {
    DomainClass.DEFAULT: FetchPolicy(
        domain_class=DomainClass.DEFAULT,
        strategy=FetchStrategy.DIRECT_THEN_READER,
        max_retries=2,
        timeout_seconds=30.0,
    ),
    DomainClass.BLOCKED_PRONE: FetchPolicy(
        domain_class=DomainClass.BLOCKED_PRONE,
        strategy=FetchStrategy.READER_THEN_DIRECT,
        max_retries=2,
        timeout_seconds=45.0,
        backoff_base=2.0,
    ),
    DomainClass.JS_HEAVY: FetchPolicy(
        domain_class=DomainClass.JS_HEAVY,
        strategy=FetchStrategy.READER_THEN_DIRECT,
        max_retries=1,
        timeout_seconds=45.0,
    ),
    DomainClass.DOCUMENT_HEAVY: FetchPolicy(
        domain_class=DomainClass.DOCUMENT_HEAVY,
        strategy=FetchStrategy.DIRECT_ONLY,
        max_retries=1,
        timeout_seconds=60.0,
    ),
    DomainClass.TRUSTED: FetchPolicy(
        domain_class=DomainClass.TRUSTED,
        strategy=FetchStrategy.DIRECT_THEN_READER,
        max_retries=1,
        timeout_seconds=15.0,
    ),
}


# ---------------------------------------------------------------------------
# Domain classification registry
# ---------------------------------------------------------------------------

# Domains known to block bots aggressively
_BLOCKED_PRONE_DOMAINS: frozenset[str] = frozenset(
    {
        "linkedin.com",
        "glassdoor.com",
        "indeed.com",
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "x.com",
    }
)

# Domains that rely heavily on JavaScript rendering
_JS_HEAVY_DOMAINS: frozenset[str] = frozenset(
    {
        "bloomberg.com",
        "wsj.com",
        "ft.com",
        "reuters.com",
        "techcrunch.com",
        "pitchbook.com",
        "app.dealroom.co",
    }
)

# Trusted data sources with stable, bot-friendly pages
_TRUSTED_DOMAINS: frozenset[str] = frozenset(
    {
        "sec.gov",
        "companieshouse.gov.uk",
        "opencorporates.com",
        "wikipedia.org",
        "wikidata.org",
        "github.com",
        "crunchbase.com",
    }
)

# Document-heavy domains (PDFs, spreadsheets, etc.)
_DOCUMENT_HEAVY_DOMAINS: frozenset[str] = frozenset(
    {
        "sec.gov",  # Also trusted, but EDGAR filings are document-heavy
    }
)

# Document-heavy file extensions
_DOCUMENT_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".pdf",
        ".xlsx",
        ".xls",
        ".csv",
        ".doc",
        ".docx",
    }
)


def classify_domain(url: str) -> DomainClass:
    """Classify a URL into a domain reliability class.

    Classification priority:
    1. Document-heavy (by extension)
    2. Blocked-prone (by domain)
    3. JS-heavy (by domain)
    4. Trusted (by domain)
    5. Default
    """
    try:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower().strip()
        path = (parsed.path or "").lower()
    except Exception as exc:
        logger.debug(f"URL parse failed during classification: {exc}", url=url)
        return DomainClass.DEFAULT

    # Check file extension first
    for ext in _DOCUMENT_EXTENSIONS:
        if path.endswith(ext):
            return DomainClass.DOCUMENT_HEAVY

    # Strip www. for matching
    if host.startswith("www."):
        host = host[4:]

    # Check domain registries (most restrictive first)
    for domain in _BLOCKED_PRONE_DOMAINS:
        if host == domain or host.endswith(f".{domain}"):
            return DomainClass.BLOCKED_PRONE

    for domain in _JS_HEAVY_DOMAINS:
        if host == domain or host.endswith(f".{domain}"):
            return DomainClass.JS_HEAVY

    for domain in _TRUSTED_DOMAINS:
        if host == domain or host.endswith(f".{domain}"):
            return DomainClass.TRUSTED

    return DomainClass.DEFAULT


def get_policy(
    domain_class: DomainClass,
    overrides: dict[str, Any] | None = None,
) -> FetchPolicy:
    """Get the fetch policy for a domain class, with optional overrides.

    Args:
        domain_class: The classification of the target domain.
        overrides: Optional dict of field overrides (e.g., {"timeout_seconds": 60}).

    Returns:
        FetchPolicy for the given domain class.
    """
    base = DEFAULT_POLICIES[domain_class]
    if not overrides:
        return base

    # Apply overrides by reconstructing the dataclass
    return FetchPolicy(
        domain_class=base.domain_class,
        strategy=FetchStrategy(overrides["strategy"]) if "strategy" in overrides else base.strategy,
        max_retries=int(overrides["max_retries"]) if "max_retries" in overrides else base.max_retries,
        timeout_seconds=float(overrides["timeout_seconds"]) if "timeout_seconds" in overrides else base.timeout_seconds,
        backoff_base=float(overrides["backoff_base"]) if "backoff_base" in overrides else base.backoff_base,
        reader_url_template=str(overrides["reader_url_template"])
        if "reader_url_template" in overrides
        else base.reader_url_template,
    )


def compute_backoff(attempt: int, backoff_base: float) -> float:
    """Compute bounded backoff delay in seconds.

    Uses exponential backoff with a hard cap of 30 seconds.
    """
    delay = backoff_base * (2**attempt)
    return min(delay, 30.0)


def build_fetch_sequence(policy: FetchPolicy) -> list[FetchStrategy]:
    """Build the ordered list of fetch strategies to try.

    Returns a list of strategies; the caller should try each in order,
    retrying according to policy.max_retries for transient failures.
    """
    if policy.strategy == FetchStrategy.DIRECT_THEN_READER:
        return [FetchStrategy.DIRECT, FetchStrategy.READER]
    elif policy.strategy == FetchStrategy.READER_THEN_DIRECT:
        return [FetchStrategy.READER, FetchStrategy.DIRECT]
    elif policy.strategy == FetchStrategy.DIRECT_ONLY or policy.strategy == FetchStrategy.DIRECT:
        return [FetchStrategy.DIRECT]
    elif policy.strategy == FetchStrategy.READER:
        return [FetchStrategy.READER]
    else:
        return [FetchStrategy.DIRECT, FetchStrategy.READER]


def record_attempt(
    url: str,
    strategy: FetchStrategy,
    attempt_number: int,
    outcome: FetchOutcome,
    **kwargs: Any,
) -> FetchAttempt:
    """Create a structured fetch attempt record.

    Keyword args forwarded: status_code, duration_ms, error_message, content_length.
    """
    return FetchAttempt(
        url=url,
        strategy_used=strategy,
        attempt_number=attempt_number,
        outcome=outcome,
        **kwargs,
    )


def elapsed_ms(start: float) -> float:
    """Compute elapsed milliseconds since start (from time.monotonic())."""
    return (time.monotonic() - start) * 1000.0


# ---------------------------------------------------------------------------
# Async fetch executor — accepts an httpx.AsyncClient + usability checker
# ---------------------------------------------------------------------------

from typing import Protocol


class UsabilityChecker(Protocol):
    """Protocol for content usability checking."""

    def is_usable(self, text: str, content_type: str) -> bool: ...  # noqa: E704
    def looks_blocked(self, text: str) -> bool: ...  # noqa: E704


async def execute_policy_fetch(
    url: str,
    http_client: Any,
    usability: UsabilityChecker,
) -> FetchResult:
    """Execute a policy-driven fetch for a URL.

    This is the main entry point for domain-aware fetching. It:
    1. Classifies the URL into a domain reliability class
    2. Selects the appropriate fetch policy
    3. Executes the fetch sequence with retries and backoff
    4. Records every attempt for provenance

    Args:
        url: The target URL to fetch.
        http_client: An httpx.AsyncClient instance.
        usability: Object with is_usable() and looks_blocked() methods.

    Returns:
        FetchResult with content (if successful) and full attempt metadata.
    """
    import asyncio

    domain_class = classify_domain(url)
    policy = get_policy(domain_class)
    sequence = build_fetch_sequence(policy)
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SolsteinResearchBot/1.0)"}
    attempts: list[FetchAttempt] = []
    overall_start = time.monotonic()

    for step_strategy in sequence:
        for retry in range(policy.max_retries + 1):
            attempt_start = time.monotonic()
            target_url = policy.reader_url(url) if step_strategy == FetchStrategy.READER else url
            try:
                response = await http_client.get(
                    target_url,
                    headers=headers,
                    timeout=policy.timeout_seconds,
                )
                response.raise_for_status()
                text = response.text
                content_type = (response.headers.get("content-type") or "").lower()
                duration = elapsed_ms(attempt_start)

                # Check content quality
                is_good = (
                    (text and len(text) >= 50)
                    if step_strategy == FetchStrategy.READER
                    else usability.is_usable(text, content_type)
                )

                if is_good:
                    attempts.append(
                        record_attempt(
                            url,
                            step_strategy,
                            retry + 1,
                            FetchOutcome.SUCCESS,
                            status_code=response.status_code,
                            duration_ms=duration,
                            content_length=len(text),
                        )
                    )
                    return FetchResult(
                        url=url,
                        domain_class=domain_class,
                        policy=policy,
                        success=True,
                        content=text,
                        content_type=content_type,
                        attempts=attempts,
                        terminal_outcome=FetchOutcome.SUCCESS,
                        total_duration_ms=elapsed_ms(overall_start),
                    )

                # Content retrieved but not usable
                outcome = FetchOutcome.BLOCKED if usability.looks_blocked(text) else FetchOutcome.UNUSABLE_CONTENT
                attempts.append(
                    record_attempt(
                        url,
                        step_strategy,
                        retry + 1,
                        outcome,
                        status_code=response.status_code,
                        duration_ms=duration,
                        error_message=f"Content not usable ({outcome.value})",
                        content_length=len(text),
                    )
                )
                break  # Don't retry for blocked/unusable — move to next strategy

            except Exception as exc:
                outcome, status_code = _classify_fetch_error(exc)
                attempts.append(
                    record_attempt(
                        url,
                        step_strategy,
                        retry + 1,
                        outcome,
                        status_code=status_code,
                        duration_ms=elapsed_ms(attempt_start),
                        error_message=str(exc),
                    )
                )
                # Don't retry 4xx errors
                if outcome == FetchOutcome.HTTP_ERROR and status_code and 400 <= status_code < 500:
                    break
                if retry < policy.max_retries:
                    await asyncio.sleep(compute_backoff(retry, policy.backoff_base))

    # All strategies exhausted
    terminal = attempts[-1].outcome if attempts else FetchOutcome.NETWORK_ERROR
    return FetchResult(
        url=url,
        domain_class=domain_class,
        policy=policy,
        success=False,
        attempts=attempts,
        terminal_outcome=terminal,
        total_duration_ms=elapsed_ms(overall_start),
    )


def _classify_fetch_error(exc: Exception) -> tuple[FetchOutcome, int | None]:
    """Classify an exception into a FetchOutcome and optional status code."""
    if isinstance(exc, httpx.TimeoutException):
        return FetchOutcome.TIMEOUT, None
    if isinstance(exc, httpx.HTTPStatusError):
        return FetchOutcome.HTTP_ERROR, exc.response.status_code
    return FetchOutcome.NETWORK_ERROR, None
