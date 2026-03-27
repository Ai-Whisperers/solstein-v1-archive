"""
Field-level evidence ledger and provenance lineage.

STORY-228: Persists per-field candidate evidence, winner rationale,
and run-to-run lineage in a versioned schema.

Schema v2 structure per company:
{
  "schema_version": 2,
  "companies": {
    "<key>": {
      "latest_report": { ... },
      "known_urls": [...],
      "updated_at": "...",
      "runs": [
        {
          "run_id": "...",
          "timestamp": "...",
          "sources_used": [...],
          "field_evidence": {
            "<field>": {
              "winner": { "value": ..., "source": ..., "confidence": ... },
              "candidates": [
                { "value": ..., "source": ..., "confidence": ..., "is_ambiguous": ... }
              ],
              "contradiction_flags": [...]
            }
          }
        }
      ]
    }
  }
}
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .numeric_normalization import (
    ContradictionFlag,
    NormalizedValue,
    contradiction_to_dict,
    normalized_value_to_dict,
)

SCHEMA_VERSION = 2
MAX_RUNS_PER_COMPANY = 20  # retention window


@dataclass(frozen=True)
class WinnerInfo:
    """Bundled winner parameters for field evidence construction."""

    value: Any
    source_url: str
    confidence: float


@dataclass
class EvidenceCandidate:
    """A single source claim for a field value."""

    value: Any
    source_url: str
    confidence: float
    extraction_timestamp: str
    normalization: dict[str, Any] = field(default_factory=dict)
    is_ambiguous: bool = False
    ambiguity_reason: str = ""


@dataclass
class FieldEvidence:
    """Complete evidence record for a single field."""

    field_name: str
    winner: EvidenceCandidate | None = None
    candidates: list[EvidenceCandidate] = field(default_factory=list)
    contradiction_flags: list[ContradictionFlag] = field(default_factory=list)


@dataclass
class RunRecord:
    """A single research run's evidence snapshot."""

    run_id: str
    timestamp: str
    sources_used: list[str] = field(default_factory=list)
    field_evidence: dict[str, FieldEvidence] = field(default_factory=dict)


def generate_run_id() -> str:
    """Generate a unique run identifier."""
    return f"run-{uuid.uuid4().hex[:12]}"


def candidate_to_dict(candidate: EvidenceCandidate) -> dict[str, Any]:
    """Serialize an EvidenceCandidate to dict."""
    return {
        "value": candidate.value,
        "source_url": candidate.source_url,
        "confidence": candidate.confidence,
        "extraction_timestamp": candidate.extraction_timestamp,
        "normalization": candidate.normalization,
        "is_ambiguous": candidate.is_ambiguous,
        "ambiguity_reason": candidate.ambiguity_reason,
    }


def field_evidence_to_dict(evidence: FieldEvidence) -> dict[str, Any]:
    """Serialize a FieldEvidence to dict."""
    return {
        "winner": candidate_to_dict(evidence.winner) if evidence.winner else None,
        "candidates": [candidate_to_dict(c) for c in evidence.candidates],
        "contradiction_flags": [contradiction_to_dict(f) for f in evidence.contradiction_flags],
    }


def run_record_to_dict(run: RunRecord) -> dict[str, Any]:
    """Serialize a RunRecord to dict."""
    return {
        "run_id": run.run_id,
        "timestamp": run.timestamp,
        "sources_used": run.sources_used,
        "field_evidence": {name: field_evidence_to_dict(ev) for name, ev in run.field_evidence.items()},
    }


def dict_to_candidate(data: dict[str, Any]) -> EvidenceCandidate:
    """Deserialize an EvidenceCandidate from dict."""
    return EvidenceCandidate(
        value=data.get("value"),
        source_url=data.get("source_url", ""),
        confidence=float(data.get("confidence", 0.0)),
        extraction_timestamp=data.get("extraction_timestamp", ""),
        normalization=data.get("normalization", {}),
        is_ambiguous=bool(data.get("is_ambiguous", False)),
        ambiguity_reason=data.get("ambiguity_reason", ""),
    )


def dict_to_field_evidence(name: str, data: dict[str, Any]) -> FieldEvidence:
    """Deserialize a FieldEvidence from dict."""
    winner_data = data.get("winner")
    return FieldEvidence(
        field_name=name,
        winner=dict_to_candidate(winner_data) if isinstance(winner_data, dict) else None,
        candidates=[dict_to_candidate(c) for c in data.get("candidates", []) if isinstance(c, dict)],
        contradiction_flags=[],  # flags are informational, not round-tripped
    )


def dict_to_run_record(data: dict[str, Any]) -> RunRecord:
    """Deserialize a RunRecord from dict."""
    evidence_data = data.get("field_evidence", {})
    return RunRecord(
        run_id=data.get("run_id", ""),
        timestamp=data.get("timestamp", ""),
        sources_used=list(data.get("sources_used", [])),
        field_evidence={
            name: dict_to_field_evidence(name, ev) for name, ev in evidence_data.items() if isinstance(ev, dict)
        },
    )


def build_field_evidence(
    field_name: str,
    validated_items: list[dict[str, Any]],
    winner: WinnerInfo,
    normalized: NormalizedValue | None = None,
    contradictions: list[ContradictionFlag] | None = None,
) -> FieldEvidence:
    """Build a FieldEvidence record from synthesis data.

    Args:
        field_name: The field being recorded.
        validated_items: List of {extraction, confidence, ...} dicts from synthesis.
        winner: Winner value, source, and confidence bundled together.
        normalized: Optional NormalizedValue metadata.
        contradictions: Optional contradiction flags for this field.
    """
    now = datetime.now().isoformat()

    candidates: list[EvidenceCandidate] = []
    for item in validated_items:
        extraction = item.get("extraction")
        if extraction is None:
            continue
        source_url = getattr(extraction, "source_url", "")
        data = getattr(extraction, "data", {})
        value = data.get(field_name) if isinstance(data, dict) else None
        if value is None:
            continue

        candidates.append(
            EvidenceCandidate(
                value=value,
                source_url=source_url,
                confidence=float(item.get("confidence", 0.0)),
                extraction_timestamp=now,
                is_ambiguous=False,
            )
        )

    winner_candidate = EvidenceCandidate(
        value=winner.value,
        source_url=winner.source_url,
        confidence=winner.confidence,
        extraction_timestamp=now,
        normalization=normalized_value_to_dict(normalized) if normalized else {},
    )

    return FieldEvidence(
        field_name=field_name,
        winner=winner_candidate,
        candidates=candidates,
        contradiction_flags=contradictions or [],
    )


# ---------------------------------------------------------------------------
# Schema migration v1 -> v2
# ---------------------------------------------------------------------------


def detect_schema_version(memory_data: dict[str, Any]) -> int:
    """Detect the schema version of a memory dict.

    v1: has "companies" but no "schema_version" key.
    v2: has "schema_version": 2.
    """
    version = memory_data.get("schema_version")
    if isinstance(version, int):
        return version
    if "companies" in memory_data:
        return 1
    return 0


def migrate_v1_to_v2(v1_data: dict[str, Any]) -> dict[str, Any]:
    """Migrate v1 memory schema to v2, preserving all existing data.

    v1 company entry: {latest_report, known_urls, updated_at}
    v2 company entry: {latest_report, known_urls, updated_at, runs: [...]}

    The migration creates a synthetic run record from the latest_report.
    """
    v2_data: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "companies": {},
    }

    companies = v1_data.get("companies", {})
    if not isinstance(companies, dict):
        return v2_data

    for key, entry in companies.items():
        if not isinstance(entry, dict):
            continue

        # Preserve existing fields
        v2_entry: dict[str, Any] = {
            "latest_report": entry.get("latest_report"),
            "known_urls": entry.get("known_urls", []),
            "updated_at": entry.get("updated_at", ""),
            "runs": [],
        }

        # Create synthetic run from latest_report
        report = entry.get("latest_report")
        if isinstance(report, dict):
            synthetic_run = _build_synthetic_run(report, entry.get("updated_at", ""))
            if synthetic_run:
                v2_entry["runs"].append(synthetic_run)

        v2_data["companies"][key] = v2_entry

    return v2_data


def _build_synthetic_run(report: dict[str, Any], timestamp: str) -> dict[str, Any] | None:
    """Build a synthetic run record from a v1 latest_report."""
    if not report:
        return None

    field_evidence: dict[str, Any] = {}
    basic = report.get("basic_info", {}) if isinstance(report.get("basic_info"), dict) else {}
    financials = report.get("financials", {}) if isinstance(report.get("financials"), dict) else {}
    funding = report.get("funding", {}) if isinstance(report.get("funding"), dict) else {}

    # Record evidence for each field that has a value
    all_fields = {**basic, **financials, **funding}
    for field_name, value in all_fields.items():
        if value in (None, "", [], {}):
            continue
        field_evidence[field_name] = {
            "winner": {
                "value": value,
                "source_url": "migrated_from_v1",
                "confidence": 0.5,
                "extraction_timestamp": timestamp or datetime.now().isoformat(),
                "normalization": {},
                "is_ambiguous": False,
                "ambiguity_reason": "",
            },
            "candidates": [],
            "contradiction_flags": [],
        }

    sources = report.get("data_sources", [])
    source_urls = []
    if isinstance(sources, list):
        for s in sources:
            if isinstance(s, dict) and isinstance(s.get("url"), str):
                source_urls.append(s["url"])

    return {
        "run_id": f"migrated-{uuid.uuid4().hex[:8]}",
        "timestamp": timestamp or datetime.now().isoformat(),
        "sources_used": source_urls,
        "field_evidence": field_evidence,
    }


def append_run(
    company_entry: dict[str, Any],
    run: RunRecord,
) -> None:
    """Append a run record to a company entry, enforcing retention window."""
    runs = company_entry.setdefault("runs", [])
    runs.append(run_record_to_dict(run))
    # Trim to retention window
    if len(runs) > MAX_RUNS_PER_COMPANY:
        company_entry["runs"] = runs[-MAX_RUNS_PER_COMPANY:]


def get_latest_run(company_entry: dict[str, Any]) -> RunRecord | None:
    """Get the most recent run record for a company."""
    runs = company_entry.get("runs", [])
    if not runs or not isinstance(runs, list):
        return None
    last = runs[-1]
    if isinstance(last, dict):
        return dict_to_run_record(last)
    return None


def get_field_lineage(
    company_entry: dict[str, Any],
    field_name: str,
) -> list[dict[str, Any]]:
    """Get the winner history for a field across all runs."""
    lineage: list[dict[str, Any]] = []
    runs = company_entry.get("runs", [])
    if not isinstance(runs, list):
        return lineage

    for run_data in runs:
        if not isinstance(run_data, dict):
            continue
        evidence = run_data.get("field_evidence", {})
        if not isinstance(evidence, dict):
            continue
        field_ev = evidence.get(field_name)
        if not isinstance(field_ev, dict):
            continue
        winner = field_ev.get("winner")
        if isinstance(winner, dict):
            lineage.append(
                {
                    "run_id": run_data.get("run_id", ""),
                    "timestamp": run_data.get("timestamp", ""),
                    "value": winner.get("value"),
                    "source_url": winner.get("source_url", ""),
                    "confidence": winner.get("confidence", 0.0),
                }
            )

    return lineage


__all__ = [
    "SCHEMA_VERSION",
    "MAX_RUNS_PER_COMPANY",
    "WinnerInfo",
    "EvidenceCandidate",
    "FieldEvidence",
    "RunRecord",
    "generate_run_id",
    "build_field_evidence",
    "candidate_to_dict",
    "field_evidence_to_dict",
    "run_record_to_dict",
    "dict_to_candidate",
    "dict_to_field_evidence",
    "dict_to_run_record",
    "detect_schema_version",
    "migrate_v1_to_v2",
    "append_run",
    "get_latest_run",
    "get_field_lineage",
]
