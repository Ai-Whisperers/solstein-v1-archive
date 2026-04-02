"""Tests for STORY-251: Enforce Strict Boundary Schemas.

Behavioral tests proving:
1. Connector fact ingress rejects undeclared fields
2. API request models reject unknown fields
3. Domain models define explicit extra-field policy
4. Undeclared fields do not survive model_dump()
"""

import pytest
from pydantic import ValidationError

from solstein.domain.models import Company, FinancialMetric
from solstein.infrastructure.fact_payloads import ConnectorFactPayload

# ─────────────────────────────────────────────
# AC1: Connector fact validation rejects undeclared fields
# ─────────────────────────────────────────────


class TestConnectorFactBoundary:
    """Connector fact payloads must reject undeclared fields."""

    def test_valid_fact_accepted(self) -> None:
        """Standard fact payload passes validation."""
        payload = ConnectorFactPayload(
            company_id="COMP-001",
            fact_type="revenue",
            value=50_000_000,
            confidence=0.9,
        )
        assert payload.company_id == "COMP-001"
        assert payload.fact_type == "revenue"

    def test_undeclared_field_rejected(self) -> None:
        """Extra undeclared fields are rejected at ingress."""
        with pytest.raises(ValidationError, match="extra_forbidden|extra_inputs"):
            ConnectorFactPayload(
                company_id="COMP-001",
                fact_type="revenue",
                value=50_000_000,
                bogus_field="should fail",
            )

    def test_legacy_type_alias_still_works(self) -> None:
        """Legacy 'type' key normalizes to 'fact_type'."""
        payload = ConnectorFactPayload.model_validate(
            {
                "company_id": "COMP-001",
                "type": "revenue",
                "value": 100,
            }
        )
        assert payload.fact_type == "revenue"

    def test_legacy_hash_alias_works(self) -> None:
        """Legacy '_hash' key normalizes to 'value_hash'."""
        payload = ConnectorFactPayload.model_validate(
            {
                "company_id": "COMP-001",
                "fact_type": "revenue",
                "_hash": "abc123",
            }
        )
        assert payload.value_hash == "abc123"

    def test_metadata_none_normalized(self) -> None:
        """metadata=None is normalized to empty dict."""
        payload = ConnectorFactPayload.model_validate(
            {
                "company_id": "COMP-001",
                "fact_type": "revenue",
                "metadata": None,
            }
        )
        assert payload.metadata == {}

    def test_undeclared_field_does_not_survive_model_dump(self) -> None:
        """Validated payloads never contain undeclared keys in dump."""
        payload = ConnectorFactPayload(
            company_id="COMP-001",
            fact_type="revenue",
            value=100,
        )
        dumped = payload.model_dump()
        expected_keys = {
            "company_id",
            "fact_type",
            "value",
            "confidence",
            "extracted_at",
            "metadata",
            "value_hash",
        }
        assert set(dumped.keys()) == expected_keys


# ─────────────────────────────────────────────
# AC2: API request models reject unknown fields
# ─────────────────────────────────────────────


class TestAPIRequestBoundary:
    """Public API request models must reject unknown fields."""

    def test_enrichment_request_rejects_extra(self) -> None:
        """EnrichmentRequest has extra=forbid."""
        from solstein.api.schemas.enrichment import EnrichmentRequest

        with pytest.raises(ValidationError, match="extra_forbidden|extra_inputs"):
            EnrichmentRequest(
                company_id="C001",
                sources=["SEC_EDGAR"],
                unknown_field="rejected",
            )

    def test_batch_enrichment_request_rejects_extra(self) -> None:
        """BatchEnrichmentRequest has extra=forbid."""
        from solstein.api.schemas.enrichment import BatchEnrichmentRequest

        with pytest.raises(ValidationError, match="extra_forbidden|extra_inputs"):
            BatchEnrichmentRequest(
                company_ids=["C001"],
                unknown_field="rejected",
            )

    def test_semantic_search_rejects_extra(self) -> None:
        """SemanticSearchRequest has extra=forbid."""
        from solstein.api.schemas.semantic_search import SemanticSearchRequest

        with pytest.raises(ValidationError, match="extra_forbidden|extra_inputs"):
            SemanticSearchRequest(
                query="test query",
                unknown_field="rejected",
            )

    def test_scoring_request_rejects_extra(self) -> None:
        """AdjudicationRequest has extra=forbid."""
        from solstein.api.routers.scoring import AdjudicationRequest

        with pytest.raises(ValidationError, match="extra_forbidden|extra_inputs"):
            AdjudicationRequest(
                company_id="C001",
                adjudicated_by="admin",
                scores={"growth": 0.8},
                unknown_field="rejected",
            )

    def test_export_request_rejects_extra(self) -> None:
        """ExportRequest has extra=forbid."""
        from solstein.api.routers.exports import ExportRequest

        with pytest.raises(ValidationError, match="extra_forbidden|extra_inputs"):
            ExportRequest(
                company_ids=["C001"],
                format="excel",
                unknown_field="rejected",
            )


# ─────────────────────────────────────────────
# AC3: Domain models define explicit extra-field behavior
# ─────────────────────────────────────────────


class TestDomainModelExtraPolicy:
    """Domain models must define explicit extra-field policy."""

    def test_company_has_explicit_extra_policy(self) -> None:
        """Company model_config explicitly defines extra field handling."""
        config = Company.model_config
        assert "extra" in config, "Company must define explicit extra-field policy"
        assert config["extra"] == "ignore"

    def test_financial_metric_has_explicit_extra_policy(self) -> None:
        """FinancialMetric model_config explicitly defines extra field handling."""
        config = FinancialMetric.model_config
        assert "extra" in config, "FinancialMetric must define explicit extra-field policy"
        assert config["extra"] == "ignore"

    def test_company_extra_fields_do_not_survive_dump(self) -> None:
        """Extra fields passed to Company are dropped, not persisted."""
        company = Company.model_validate(
            {
                "id": "TEST-001",
                "name": "Test Corp",
                "unexpected_extra": "should be dropped",
                "another_extra": 42,
            }
        )
        dumped = company.model_dump()
        assert "unexpected_extra" not in dumped
        assert "another_extra" not in dumped

    def test_financial_metric_extra_fields_do_not_survive_dump(self) -> None:
        """Extra fields passed to FinancialMetric are dropped."""
        fm = FinancialMetric.model_validate(
            {
                "revenue": 50.0,
                "growth_rate": 0.15,
                "allow_empty_primary": True,
                "bogus_metric": 999,
            }
        )
        dumped = fm.model_dump()
        assert "bogus_metric" not in dumped

    def test_connector_payload_model_dump_clean(self) -> None:
        """ConnectorFactPayload model_dump has no extra keys."""
        payload = ConnectorFactPayload(
            company_id="C001",
            fact_type="employee_count",
            value=500,
        )
        dumped = payload.model_dump()
        # All keys must be declared fields
        declared = set(ConnectorFactPayload.model_fields.keys())
        assert set(dumped.keys()).issubset(declared), (
            f"model_dump contains undeclared keys: {set(dumped.keys()) - declared}"
        )
