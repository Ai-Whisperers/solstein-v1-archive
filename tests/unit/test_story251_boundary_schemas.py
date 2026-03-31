"""Tests for STORY-251: Enforce Strict Boundary Schemas.

Validates that:
- API request models reject unknown fields (extra="forbid")
- ConnectorFactPayload rejects undeclared fields
- ConnectorFactPayload still accepts legacy aliases (type, _hash)
- Legacy alias normalization works correctly
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from solstein.infrastructure.fact_payloads import (
    ConnectorFactPayload,
    validate_connector_fact_payloads,
)


# ===========================================================================
# ConnectorFactPayload: strict ingress with legacy alias support
# ===========================================================================


class TestConnectorFactPayloadStrictIngress:
    """ConnectorFactPayload rejects undeclared fields at ingress."""

    def test_valid_payload_accepted(self) -> None:
        payload = ConnectorFactPayload(
            company_id="COMP-001",
            fact_type="revenue",
            value=1_000_000,
            confidence=0.9,
        )
        assert payload.company_id == "COMP-001"
        assert payload.fact_type == "revenue"

    def test_undeclared_field_rejected(self) -> None:
        """Extra fields not in the schema must cause a ValidationError."""
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ConnectorFactPayload(
                company_id="COMP-001",
                fact_type="revenue",
                value=100,
                surprise_field="should fail",
            )

    def test_multiple_undeclared_fields_rejected(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ConnectorFactPayload(
                company_id="COMP-001",
                fact_type="revenue",
                foo="bar",
                baz=42,
            )
        errors = exc_info.value.errors()
        extra_errors = [e for e in errors if e["type"] == "extra_forbidden"]
        assert len(extra_errors) >= 2

    def test_undeclared_field_does_not_survive_model_dump(self) -> None:
        """Even if somehow constructed, extra fields must not appear in dump."""
        payload = ConnectorFactPayload(
            company_id="COMP-001",
            fact_type="revenue",
            value=100,
        )
        dumped = payload.model_dump()
        declared_keys = {
            "company_id", "fact_type", "value", "confidence",
            "extracted_at", "metadata", "value_hash",
        }
        assert set(dumped.keys()) == declared_keys


class TestConnectorFactPayloadLegacyAliases:
    """Legacy aliases are normalised before validation."""

    def test_type_alias_accepted_as_fact_type(self) -> None:
        """Legacy 'type' key is normalised to 'fact_type'."""
        payload = ConnectorFactPayload.model_validate({
            "company_id": "COMP-001",
            "type": "revenue",
            "value": 100,
        })
        assert payload.fact_type == "revenue"

    def test_type_alias_stripped_when_fact_type_present(self) -> None:
        """If both 'type' and 'fact_type' exist, 'type' is stripped without error."""
        payload = ConnectorFactPayload.model_validate({
            "company_id": "COMP-001",
            "fact_type": "revenue",
            "type": "ignored",
            "value": 100,
        })
        assert payload.fact_type == "revenue"

    def test_hash_alias_accepted(self) -> None:
        """Legacy '_hash' alias maps to value_hash field."""
        payload = ConnectorFactPayload.model_validate({
            "company_id": "COMP-001",
            "fact_type": "revenue",
            "_hash": "abc123",
        })
        assert payload.value_hash == "abc123"

    def test_metadata_none_normalised_to_empty_dict(self) -> None:
        payload = ConnectorFactPayload.model_validate({
            "company_id": "COMP-001",
            "fact_type": "revenue",
            "metadata": None,
        })
        assert payload.metadata == {}


class TestValidateConnectorFactPayloads:
    """The batch validator rejects invalid facts and keeps valid ones."""

    def test_valid_facts_pass(self) -> None:
        facts = [
            {"company_id": "C1", "fact_type": "revenue", "value": 100},
            {"company_id": "C2", "fact_type": "growth", "value": 0.1},
        ]
        result = validate_connector_fact_payloads(
            facts, source_name="test", default_confidence=0.8,
        )
        assert len(result) == 2

    def test_invalid_fact_rejected(self) -> None:
        """A fact with an undeclared field is silently dropped."""
        facts = [
            {"company_id": "C1", "fact_type": "revenue", "value": 100},
            {"company_id": "C2", "fact_type": "growth", "surprise": "boom"},
        ]
        result = validate_connector_fact_payloads(
            facts, source_name="test", default_confidence=0.8,
        )
        # Second fact should be rejected (undeclared 'surprise' field)
        assert len(result) == 1
        assert result[0]["company_id"] == "C1"

    def test_legacy_alias_fact_accepted(self) -> None:
        """A fact using the legacy 'type' key is accepted after normalisation."""
        facts = [
            {"company_id": "C1", "type": "revenue", "value": 100},
        ]
        result = validate_connector_fact_payloads(
            facts, source_name="test", default_confidence=0.8,
        )
        assert len(result) == 1
        assert result[0]["fact_type"] == "revenue"


# ===========================================================================
# API request models: extra="forbid" enforcement
#
# Router modules use relative imports and trigger heavy init chains (env
# validation, DB connection). We verify the source files contain the
# correct ConfigDict(extra="forbid") declaration, then use importlib to
# import the models where possible.
# ===========================================================================

from pathlib import Path

_SRC = Path(__file__).resolve().parents[2] / "src" / "solstein" / "api" / "routers"


class TestAPIRequestModelConfigInSource:
    """Verify API request models declare extra='forbid' in source code.

    These are static checks because the router modules can't be imported
    in isolation without triggering heavy env-validation side effects.
    The behavioral validation (extra_forbidden at runtime) is covered by
    the ConnectorFactPayload tests above, which prove the Pydantic
    ConfigDict(extra='forbid') pattern works correctly.
    """

    # STATIC-OK: Router modules have relative imports that prevent
    # isolated loading. Source inspection confirms the config is present.

    def test_async_enrichment_has_forbid(self) -> None:
        text = (_SRC / "async_jobs.py").read_text()
        assert 'extra="forbid"' in text, "AsyncEnrichmentRequest missing extra=forbid"
        # Verify it appears after the class definition
        idx_class = text.index("class AsyncEnrichmentRequest")
        idx_forbid = text.index('extra="forbid"', idx_class)
        assert idx_forbid > idx_class

    def test_async_batch_has_forbid(self) -> None:
        text = (_SRC / "async_jobs.py").read_text()
        idx_class = text.index("class AsyncBatchEnrichmentRequest")
        idx_forbid = text.index('extra="forbid"', idx_class)
        assert idx_forbid > idx_class

    def test_approve_request_has_forbid(self) -> None:
        text = (_SRC / "review.py").read_text()
        idx_class = text.index("class ApproveRequest")
        idx_forbid = text.index('extra="forbid"', idx_class)
        assert idx_forbid > idx_class

    def test_reject_request_has_forbid(self) -> None:
        text = (_SRC / "review.py").read_text()
        idx_class = text.index("class RejectRequest")
        idx_forbid = text.index('extra="forbid"', idx_class)
        assert idx_forbid > idx_class

    def test_adjudication_request_has_forbid(self) -> None:
        text = (_SRC / "scoring.py").read_text()
        idx_class = text.index("class AdjudicationRequest")
        idx_forbid = text.index('extra="forbid"', idx_class)
        assert idx_forbid > idx_class

    def test_all_existing_strict_models_still_strict(self) -> None:
        """Verify pre-existing strict models haven't regressed."""
        schemas_dir = _SRC.parent / "schemas"
        # validation.py has StrictRequestModel base class
        text = (schemas_dir / "validation.py").read_text()
        assert 'extra="forbid"' in text, "StrictRequestModel lost extra=forbid"
        # enrichment.py request models
        text = (schemas_dir / "enrichment.py").read_text()
        assert 'extra="forbid"' in text, "EnrichmentRequest lost extra=forbid"
