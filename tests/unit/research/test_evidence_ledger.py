"""
Tests for STORY-228: Field-level evidence ledger and provenance lineage.

Tests cover:
- Schema version detection
- v1 -> v2 migration
- Run record serialization round-trip
- Field evidence construction
- Run append with retention window
- Field lineage across runs
- Edge cases (empty data, missing fields)
"""

from solstein.research.evidence_ledger import (
    MAX_RUNS_PER_COMPANY,
    SCHEMA_VERSION,
    EvidenceCandidate,
    FieldEvidence,
    RunRecord,
    WinnerInfo,
    append_run,
    build_field_evidence,
    candidate_to_dict,
    detect_schema_version,
    dict_to_candidate,
    dict_to_field_evidence,
    dict_to_run_record,
    field_evidence_to_dict,
    generate_run_id,
    get_field_lineage,
    get_latest_run,
    migrate_v1_to_v2,
    run_record_to_dict,
)
from solstein.research.numeric_normalization import (
    ContradictionFlag,
    NormalizedValue,
    NumericUnit,
    Currency,
)


# ---------------------------------------------------------------------------
# Schema version detection
# ---------------------------------------------------------------------------


class TestDetectSchemaVersion:
    """Test schema version detection."""

    def test_v2_detected(self) -> None:
        assert detect_schema_version({"schema_version": 2, "companies": {}}) == 2

    def test_v1_detected(self) -> None:
        assert detect_schema_version({"companies": {"acme": {}}}) == 1

    def test_unknown_returns_zero(self) -> None:
        assert detect_schema_version({}) == 0

    def test_empty_companies_is_v1(self) -> None:
        assert detect_schema_version({"companies": {}}) == 1


# ---------------------------------------------------------------------------
# v1 -> v2 migration
# ---------------------------------------------------------------------------


class TestMigrateV1ToV2:
    """Test schema migration from v1 to v2."""

    def test_migration_sets_schema_version(self) -> None:
        v1 = {"companies": {}}
        v2 = migrate_v1_to_v2(v1)
        assert v2["schema_version"] == SCHEMA_VERSION

    def test_migration_preserves_company_data(self) -> None:
        v1 = {
            "companies": {
                "acme": {
                    "latest_report": {
                        "company_name": "Acme Corp",
                        "basic_info": {"website": "https://acme.com"},
                        "financials": {"revenue": 100},
                        "funding": {},
                        "data_sources": [{"url": "https://example.com"}],
                    },
                    "known_urls": ["https://example.com"],
                    "updated_at": "2026-01-01T00:00:00",
                },
            },
        }
        v2 = migrate_v1_to_v2(v1)
        acme = v2["companies"]["acme"]
        assert acme["latest_report"]["company_name"] == "Acme Corp"
        assert acme["known_urls"] == ["https://example.com"]

    def test_migration_creates_synthetic_run(self) -> None:
        v1 = {
            "companies": {
                "acme": {
                    "latest_report": {
                        "basic_info": {"website": "https://acme.com", "employees": 500},
                        "financials": {"revenue": 100},
                        "funding": {},
                        "data_sources": [{"url": "https://src.com"}],
                    },
                    "known_urls": [],
                    "updated_at": "2026-01-01",
                },
            },
        }
        v2 = migrate_v1_to_v2(v1)
        runs = v2["companies"]["acme"]["runs"]
        assert len(runs) == 1
        run = runs[0]
        assert run["run_id"].startswith("migrated-")
        assert "website" in run["field_evidence"]
        assert run["field_evidence"]["website"]["winner"]["value"] == "https://acme.com"

    def test_migration_empty_companies(self) -> None:
        v2 = migrate_v1_to_v2({"companies": {}})
        assert v2["schema_version"] == SCHEMA_VERSION
        assert v2["companies"] == {}

    def test_migration_no_report_creates_no_run(self) -> None:
        v1 = {"companies": {"empty": {"latest_report": None, "known_urls": []}}}
        v2 = migrate_v1_to_v2(v1)
        assert v2["companies"]["empty"]["runs"] == []

    def test_migration_skips_null_fields(self) -> None:
        v1 = {
            "companies": {
                "acme": {
                    "latest_report": {
                        "basic_info": {"website": "https://acme.com", "description": None},
                        "financials": {},
                        "funding": {},
                        "data_sources": [],
                    },
                    "known_urls": [],
                    "updated_at": "2026-01-01",
                },
            },
        }
        v2 = migrate_v1_to_v2(v1)
        evidence = v2["companies"]["acme"]["runs"][0]["field_evidence"]
        assert "website" in evidence
        assert "description" not in evidence


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------


class TestSerializationRoundTrip:
    """Test serialization and deserialization of evidence records."""

    def test_candidate_round_trip(self) -> None:
        original = EvidenceCandidate(
            value=200.0,
            source_url="https://example.com",
            confidence=0.85,
            extraction_timestamp="2026-01-01T00:00:00",
            normalization={"unit": "millions"},
            is_ambiguous=False,
        )
        serialized = candidate_to_dict(original)
        restored = dict_to_candidate(serialized)
        assert restored.value == original.value
        assert restored.source_url == original.source_url
        assert restored.confidence == original.confidence

    def test_field_evidence_round_trip(self) -> None:
        winner = EvidenceCandidate(
            value=100.0, source_url="https://a.com",
            confidence=0.9, extraction_timestamp="2026-01-01",
        )
        candidate = EvidenceCandidate(
            value=95.0, source_url="https://b.com",
            confidence=0.7, extraction_timestamp="2026-01-01",
        )
        evidence = FieldEvidence(
            field_name="revenue",
            winner=winner,
            candidates=[winner, candidate],
        )
        serialized = field_evidence_to_dict(evidence)
        restored = dict_to_field_evidence("revenue", serialized)
        assert restored.winner is not None
        assert restored.winner.value == 100.0
        assert len(restored.candidates) == 2

    def test_run_record_round_trip(self) -> None:
        run = RunRecord(
            run_id="run-abc123",
            timestamp="2026-01-01T00:00:00",
            sources_used=["https://a.com", "https://b.com"],
            field_evidence={
                "revenue": FieldEvidence(
                    field_name="revenue",
                    winner=EvidenceCandidate(
                        value=200.0, source_url="https://a.com",
                        confidence=0.9, extraction_timestamp="2026-01-01",
                    ),
                ),
            },
        )
        serialized = run_record_to_dict(run)
        restored = dict_to_run_record(serialized)
        assert restored.run_id == "run-abc123"
        assert len(restored.sources_used) == 2
        assert "revenue" in restored.field_evidence
        assert restored.field_evidence["revenue"].winner.value == 200.0

    def test_null_winner_round_trip(self) -> None:
        evidence = FieldEvidence(field_name="valuation", winner=None)
        serialized = field_evidence_to_dict(evidence)
        assert serialized["winner"] is None
        restored = dict_to_field_evidence("valuation", serialized)
        assert restored.winner is None


# ---------------------------------------------------------------------------
# Run ID generation
# ---------------------------------------------------------------------------


class TestGenerateRunId:
    """Test run ID generation."""

    def test_starts_with_run_prefix(self) -> None:
        run_id = generate_run_id()
        assert run_id.startswith("run-")

    def test_unique_ids(self) -> None:
        ids = {generate_run_id() for _ in range(100)}
        assert len(ids) == 100


# ---------------------------------------------------------------------------
# Build field evidence
# ---------------------------------------------------------------------------


class TestBuildFieldEvidence:
    """Test field evidence construction from synthesis data."""

    def test_basic_evidence_build(self) -> None:
        evidence = build_field_evidence(
            field_name="revenue",
            validated_items=[],
            winner=WinnerInfo(value=200.0, source_url="https://sec.gov", confidence=0.9),
        )
        assert evidence.field_name == "revenue"
        assert evidence.winner is not None
        assert evidence.winner.value == 200.0
        assert evidence.winner.source_url == "https://sec.gov"

    def test_evidence_with_normalization(self) -> None:
        nv = NormalizedValue(
            raw_input="$200M", value=200.0,
            unit=NumericUnit.MILLIONS, currency=Currency.USD,
            confidence=0.9, is_ambiguous=False,
        )
        evidence = build_field_evidence(
            field_name="revenue",
            validated_items=[],
            winner=WinnerInfo(value=200.0, source_url="https://sec.gov", confidence=0.9),
            normalized=nv,
        )
        assert evidence.winner.normalization["unit"] == "millions"
        assert evidence.winner.normalization["currency"] == "USD"

    def test_evidence_with_contradictions(self) -> None:
        flags = [
            ContradictionFlag("revenue", "a", 100, "b", 500, 5.0, "major"),
        ]
        evidence = build_field_evidence(
            field_name="revenue",
            validated_items=[],
            winner=WinnerInfo(value=100.0, source_url="a", confidence=0.8),
            contradictions=flags,
        )
        assert len(evidence.contradiction_flags) == 1
        assert evidence.contradiction_flags[0].severity == "major"


# ---------------------------------------------------------------------------
# Run append and retention
# ---------------------------------------------------------------------------


class TestAppendRun:
    """Test run append with retention window enforcement."""

    def test_append_first_run(self) -> None:
        entry: dict = {"runs": []}
        run = RunRecord(run_id="run-001", timestamp="2026-01-01")
        append_run(entry, run)
        assert len(entry["runs"]) == 1
        assert entry["runs"][0]["run_id"] == "run-001"

    def test_append_creates_runs_key(self) -> None:
        entry: dict = {}
        run = RunRecord(run_id="run-001", timestamp="2026-01-01")
        append_run(entry, run)
        assert "runs" in entry
        assert len(entry["runs"]) == 1

    def test_retention_window_enforced(self) -> None:
        entry: dict = {
            "runs": [
                {"run_id": f"run-{i:03d}", "timestamp": f"2026-01-{i+1:02d}",
                 "sources_used": [], "field_evidence": {}}
                for i in range(MAX_RUNS_PER_COMPANY)
            ]
        }
        new_run = RunRecord(run_id="run-new", timestamp="2026-02-01")
        append_run(entry, new_run)
        assert len(entry["runs"]) == MAX_RUNS_PER_COMPANY
        assert entry["runs"][-1]["run_id"] == "run-new"
        assert entry["runs"][0]["run_id"] == "run-001"


# ---------------------------------------------------------------------------
# Get latest run
# ---------------------------------------------------------------------------


class TestGetLatestRun:
    """Test retrieving the most recent run record."""

    def test_returns_last_run(self) -> None:
        entry = {
            "runs": [
                {"run_id": "run-001", "timestamp": "2026-01-01",
                 "sources_used": [], "field_evidence": {}},
                {"run_id": "run-002", "timestamp": "2026-01-02",
                 "sources_used": [], "field_evidence": {}},
            ]
        }
        run = get_latest_run(entry)
        assert run is not None
        assert run.run_id == "run-002"

    def test_returns_none_for_empty(self) -> None:
        assert get_latest_run({"runs": []}) is None
        assert get_latest_run({}) is None


# ---------------------------------------------------------------------------
# Field lineage
# ---------------------------------------------------------------------------


class TestGetFieldLineage:
    """Test field value lineage across runs."""

    def test_lineage_across_runs(self) -> None:
        entry = {
            "runs": [
                {
                    "run_id": "run-001", "timestamp": "2026-01-01",
                    "sources_used": [], "field_evidence": {
                        "revenue": {
                            "winner": {"value": 100, "source_url": "a", "confidence": 0.8},
                            "candidates": [], "contradiction_flags": [],
                        },
                    },
                },
                {
                    "run_id": "run-002", "timestamp": "2026-01-15",
                    "sources_used": [], "field_evidence": {
                        "revenue": {
                            "winner": {"value": 120, "source_url": "b", "confidence": 0.9},
                            "candidates": [], "contradiction_flags": [],
                        },
                    },
                },
            ],
        }
        lineage = get_field_lineage(entry, "revenue")
        assert len(lineage) == 2
        assert lineage[0]["value"] == 100
        assert lineage[1]["value"] == 120
        assert lineage[1]["run_id"] == "run-002"

    def test_lineage_missing_field(self) -> None:
        entry = {
            "runs": [
                {"run_id": "run-001", "timestamp": "2026-01-01",
                 "sources_used": [], "field_evidence": {}},
            ],
        }
        lineage = get_field_lineage(entry, "revenue")
        assert len(lineage) == 0

    def test_lineage_empty_runs(self) -> None:
        assert get_field_lineage({"runs": []}, "revenue") == []
        assert get_field_lineage({}, "revenue") == []

    def test_lineage_partial_runs(self) -> None:
        """Some runs have the field, some don't."""
        entry = {
            "runs": [
                {
                    "run_id": "run-001", "timestamp": "2026-01-01",
                    "sources_used": [], "field_evidence": {
                        "revenue": {
                            "winner": {"value": 100, "source_url": "a", "confidence": 0.8},
                            "candidates": [], "contradiction_flags": [],
                        },
                    },
                },
                {
                    "run_id": "run-002", "timestamp": "2026-01-15",
                    "sources_used": [], "field_evidence": {},
                },
                {
                    "run_id": "run-003", "timestamp": "2026-02-01",
                    "sources_used": [], "field_evidence": {
                        "revenue": {
                            "winner": {"value": 150, "source_url": "c", "confidence": 0.95},
                            "candidates": [], "contradiction_flags": [],
                        },
                    },
                },
            ],
        }
        lineage = get_field_lineage(entry, "revenue")
        assert len(lineage) == 2
        assert lineage[0]["value"] == 100
        assert lineage[1]["value"] == 150
