"""
Tests for STORY-229: Freshness windows and evidence-aware export trust tiers.

Tests cover:
- Field volatility classification
- Freshness window computation
- Field staleness checking
- Trust tier computation (gold, silver, bronze, review-required)
- Export metadata generation
- Edge cases (empty data, missing fields)
"""

from datetime import datetime, timezone, timedelta

from solstein.research.freshness_trust import (
    KEY_FIELDS,
    STATIC_FRESHNESS_HOURS,
    VOLATILE_FRESHNESS_HOURS,
    FreshnessResult,
    TrustAssessment,
    TrustTier,
    assess_and_export,
    build_export_metadata,
    check_field_freshness,
    classify_field_volatility,
    compute_trust_tier,
    get_freshness_window,
)


# ---------------------------------------------------------------------------
# Field volatility classification
# ---------------------------------------------------------------------------


class TestClassifyFieldVolatility:
    """Test field volatility classification."""

    def test_volatile_field(self) -> None:
        assert classify_field_volatility("revenue") == "volatile"
        assert classify_field_volatility("employee_count") == "volatile"

    def test_static_field(self) -> None:
        assert classify_field_volatility("company_name") == "static"
        assert classify_field_volatility("founded_year") == "static"

    def test_unknown_field(self) -> None:
        assert classify_field_volatility("custom_metric") == "unknown"
        assert classify_field_volatility("") == "unknown"


class TestGetFreshnessWindow:
    """Test freshness window retrieval."""

    def test_volatile_window(self) -> None:
        assert get_freshness_window("revenue") == VOLATILE_FRESHNESS_HOURS

    def test_static_window(self) -> None:
        assert get_freshness_window("company_name") == STATIC_FRESHNESS_HOURS

    def test_unknown_uses_volatile(self) -> None:
        assert get_freshness_window("unknown_field") == VOLATILE_FRESHNESS_HOURS

    def test_static_longer_than_volatile(self) -> None:
        assert STATIC_FRESHNESS_HOURS > VOLATILE_FRESHNESS_HOURS


# ---------------------------------------------------------------------------
# Freshness checking
# ---------------------------------------------------------------------------


class TestCheckFieldFreshness:
    """Test field freshness checking."""

    def test_fresh_volatile_field(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = (now - timedelta(hours=1)).isoformat()
        result = check_field_freshness("revenue", ts, now=now)
        assert not result.is_stale
        assert result.age_hours < 2.0

    def test_stale_volatile_field(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = (now - timedelta(days=10)).isoformat()
        result = check_field_freshness("revenue", ts, now=now)
        assert result.is_stale

    def test_fresh_static_field(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = (now - timedelta(days=30)).isoformat()
        result = check_field_freshness("company_name", ts, now=now)
        assert not result.is_stale

    def test_stale_static_field(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = (now - timedelta(days=100)).isoformat()
        result = check_field_freshness("company_name", ts, now=now)
        assert result.is_stale

    def test_bad_timestamp_is_stale(self) -> None:
        result = check_field_freshness("revenue", "not-a-date")
        assert result.is_stale
        assert result.age_hours == float("inf")

    def test_empty_timestamp_is_stale(self) -> None:
        result = check_field_freshness("revenue", "")
        assert result.is_stale

    def test_result_has_correct_fields(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        result = check_field_freshness("revenue", ts, now=now)
        assert isinstance(result, FreshnessResult)
        assert result.field_name == "revenue"
        assert result.max_age_hours == VOLATILE_FRESHNESS_HOURS


# ---------------------------------------------------------------------------
# Trust tier computation
# ---------------------------------------------------------------------------


def _make_run(
    sources: list[str],
    fields: dict[str, float],
    timestamp: str = "2026-03-27T00:00:00+00:00",
    contradictions: dict[str, list[dict]] | None = None,
) -> dict:
    """Helper to build a run dict for testing."""
    evidence: dict = {}
    for fname, value in fields.items():
        flags = []
        if contradictions and fname in contradictions:
            flags = contradictions[fname]
        evidence[fname] = {
            "winner": {
                "value": value,
                "source_url": sources[0] if sources else "",
                "confidence": 0.9,
                "extraction_timestamp": timestamp,
            },
            "candidates": [],
            "contradiction_flags": flags,
        }
    return {
        "run_id": "run-test",
        "timestamp": timestamp,
        "sources_used": sources,
        "field_evidence": evidence,
    }


class TestComputeTrustTierGold:
    """Test gold tier requirements."""

    def test_gold_with_full_evidence(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        run = _make_run(
            sources=["https://a.com", "https://b.com", "https://c.com"],
            fields={
                "company_name": "Acme",
                "website": "https://acme.com",
                "industry": "Tech",
                "revenue": 100.0,
                "employee_count": 500,
            },
            timestamp=ts,
        )
        entry = {"runs": [run]}
        result = compute_trust_tier(entry, now=now)
        assert result.tier == TrustTier.GOLD
        assert result.source_count == 3
        assert result.key_field_coverage == 1.0
        assert len(result.stale_fields) == 0

    def test_gold_requires_3_sources(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        run = _make_run(
            sources=["https://a.com", "https://b.com"],
            fields={f: 1 for f in KEY_FIELDS},
            timestamp=ts,
        )
        entry = {"runs": [run]}
        result = compute_trust_tier(entry, now=now)
        assert result.tier != TrustTier.GOLD


class TestComputeTrustTierSilver:
    """Test silver tier requirements."""

    def test_silver_with_two_sources(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        run = _make_run(
            sources=["https://a.com", "https://b.com"],
            fields={
                "company_name": "Acme",
                "website": "https://acme.com",
                "industry": "Tech",
                "revenue": 100.0,
            },
            timestamp=ts,
        )
        entry = {"runs": [run]}
        result = compute_trust_tier(entry, now=now)
        assert result.tier == TrustTier.SILVER

    def test_silver_with_major_contradictions(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        run = _make_run(
            sources=["https://a.com", "https://b.com", "https://c.com"],
            fields={f: 1 for f in KEY_FIELDS},
            timestamp=ts,
            contradictions={
                "revenue": [{"severity": "major", "ratio": 4.0}],
            },
        )
        entry = {"runs": [run]}
        result = compute_trust_tier(entry, now=now)
        # Major contradictions with good coverage -> silver, not gold
        assert result.tier == TrustTier.SILVER


class TestComputeTrustTierBronze:
    """Test bronze tier requirements."""

    def test_bronze_single_source(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        run = _make_run(
            sources=["https://a.com"],
            fields={
                "company_name": "Acme",
                "website": "https://acme.com",
                "industry": "Tech",
                "revenue": 100.0,
            },
            timestamp=ts,
        )
        entry = {"runs": [run]}
        result = compute_trust_tier(entry, now=now)
        assert result.tier == TrustTier.BRONZE
        assert "single source only" in result.reasons

    def test_bronze_low_coverage(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        run = _make_run(
            sources=["https://a.com", "https://b.com"],
            fields={"company_name": "Acme", "website": "https://acme.com"},
            timestamp=ts,
        )
        entry = {"runs": [run]}
        result = compute_trust_tier(entry, now=now)
        assert result.tier == TrustTier.BRONZE


class TestComputeTrustTierReviewRequired:
    """Test review-required tier requirements."""

    def test_no_runs(self) -> None:
        result = compute_trust_tier({"runs": []})
        assert result.tier == TrustTier.REVIEW_REQUIRED
        assert "no evidence runs found" in result.reasons

    def test_empty_entry(self) -> None:
        result = compute_trust_tier({})
        assert result.tier == TrustTier.REVIEW_REQUIRED

    def test_critical_contradiction(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        run = _make_run(
            sources=["https://a.com", "https://b.com", "https://c.com"],
            fields={f: 1 for f in KEY_FIELDS},
            timestamp=ts,
            contradictions={
                "revenue": [{"severity": "critical", "ratio": 15.0}],
            },
        )
        entry = {"runs": [run]}
        result = compute_trust_tier(entry, now=now)
        assert result.tier == TrustTier.REVIEW_REQUIRED
        assert any("critical" in r for r in result.reasons)

    def test_majority_stale_fields(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        old_ts = (now - timedelta(days=30)).isoformat()
        run = _make_run(
            sources=["https://a.com", "https://b.com"],
            fields={
                "revenue": 100.0,
                "employee_count": 500,
                "funding_total": 50.0,
                "company_name": "Acme",
            },
            timestamp=old_ts,
        )
        entry = {"runs": [run]}
        result = compute_trust_tier(entry, now=now)
        # 3 of 4 fields are volatile and 30 days old (stale for 7-day window)
        assert result.tier == TrustTier.REVIEW_REQUIRED

    def test_no_sources(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        run = _make_run(
            sources=[],
            fields={"company_name": "Acme"},
            timestamp=ts,
        )
        entry = {"runs": [run]}
        result = compute_trust_tier(entry, now=now)
        assert result.tier == TrustTier.REVIEW_REQUIRED


# ---------------------------------------------------------------------------
# Export metadata
# ---------------------------------------------------------------------------


class TestBuildExportMetadata:
    """Test export metadata generation."""

    def test_metadata_structure(self) -> None:
        assessment = TrustAssessment(
            tier=TrustTier.GOLD,
            reasons=["well-evidenced"],
            stale_fields=[],
            source_count=3,
            contradiction_count=0,
            key_field_coverage=1.0,
        )
        meta = build_export_metadata(assessment)
        assert meta["trust_tier"] == "gold"
        assert meta["trust_reasons"] == ["well-evidenced"]
        assert meta["stale_fields"] == []
        assert meta["source_count"] == 3
        assert meta["contradiction_count"] == 0
        assert meta["key_field_coverage"] == 1.0

    def test_review_required_metadata(self) -> None:
        assessment = TrustAssessment(
            tier=TrustTier.REVIEW_REQUIRED,
            reasons=["1 critical contradiction(s)"],
            stale_fields=["revenue"],
            source_count=2,
            contradiction_count=1,
            key_field_coverage=0.4,
        )
        meta = build_export_metadata(assessment)
        assert meta["trust_tier"] == "review-required"
        assert "revenue" in meta["stale_fields"]


class TestAssessAndExport:
    """Test convenience function."""

    def test_returns_metadata_dict(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        run = _make_run(
            sources=["https://a.com"],
            fields={"company_name": "Acme"},
            timestamp=ts,
        )
        entry = {"runs": [run]}
        meta = assess_and_export(entry, now=now)
        assert isinstance(meta, dict)
        assert "trust_tier" in meta
        assert "trust_reasons" in meta

    def test_empty_entry_returns_review_required(self) -> None:
        meta = assess_and_export({})
        assert meta["trust_tier"] == "review-required"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Test edge cases and defensive behavior."""

    def test_non_dict_runs(self) -> None:
        result = compute_trust_tier({"runs": "not a list"})
        assert result.tier == TrustTier.REVIEW_REQUIRED

    def test_malformed_run_entries(self) -> None:
        entry = {"runs": [None, "bad", 42]}
        result = compute_trust_tier(entry)
        assert result.tier == TrustTier.REVIEW_REQUIRED

    def test_missing_field_evidence(self) -> None:
        entry = {
            "runs": [{
                "run_id": "run-1",
                "timestamp": "2026-03-27",
                "sources_used": ["https://a.com"],
            }],
        }
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        result = compute_trust_tier(entry, now=now)
        # Has a source but no field evidence -> bronze
        assert result.tier == TrustTier.BRONZE

    def test_multiple_runs_accumulate_sources(self) -> None:
        now = datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc)
        ts = now.isoformat()
        run1 = _make_run(
            sources=["https://a.com"],
            fields={f: 1 for f in KEY_FIELDS},
            timestamp=ts,
        )
        run2 = _make_run(
            sources=["https://b.com"],
            fields={f: 2 for f in KEY_FIELDS},
            timestamp=ts,
        )
        run3 = _make_run(
            sources=["https://c.com"],
            fields={f: 3 for f in KEY_FIELDS},
            timestamp=ts,
        )
        entry = {"runs": [run1, run2, run3]}
        result = compute_trust_tier(entry, now=now)
        assert result.source_count == 3
        assert result.tier == TrustTier.GOLD
