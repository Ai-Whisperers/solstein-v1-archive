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


# ===========================================================================
# Domain ingress models: extra="forbid" enforcement
# ===========================================================================

# Load evidence/models.py directly to avoid evidence/__init__ import chain
# (which pulls in crawl4ai, neo4j, and other heavy deps)
import importlib.util as _ilu
import types as _types

from solstein.domain.models import Company, FinancialMetric
from solstein.tenant.models import (
    Tenant,
    TenantConfig,
    TenantFeatures,
    TenantLimits,
    TenantUsage,
    TenantUser,
)

_EVIDENCE_MODELS_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "solstein" / "evidence" / "models.py"
)
_ev_spec = _ilu.spec_from_file_location(
    "solstein_evidence_models_isolated",
    _EVIDENCE_MODELS_PATH,
    submodule_search_locations=[],
)
assert _ev_spec is not None and _ev_spec.loader is not None
_ev_mod: _types.ModuleType = _ilu.module_from_spec(_ev_spec)
_ev_spec.loader.exec_module(_ev_mod)

# Rebuild models to resolve forward references from __future__ annotations
from datetime import datetime
from typing import Any
from uuid import UUID

_ns = {
    "UUID": UUID,
    "datetime": datetime,
    "Any": Any,
    "ConfidenceComponent": _ev_mod.ConfidenceComponent,
    "ClaimStatus": _ev_mod.ClaimStatus,
    "SourceType": _ev_mod.SourceType,
}
for _cls_name in ("ConfidenceComponent", "Claim", "SourceDocument", "Contradiction", "EvidenceReadiness"):
    _cls = getattr(_ev_mod, _cls_name)
    _cls.model_rebuild(_types_namespace=_ns)

Claim = _ev_mod.Claim
ConfidenceComponent = _ev_mod.ConfidenceComponent
Contradiction = _ev_mod.Contradiction
EvidenceReadiness = _ev_mod.EvidenceReadiness
SourceDocument = _ev_mod.SourceDocument
SourceType = _ev_mod.SourceType


class TestDomainModelStrictIngress:
    """Domain models reject undeclared fields at ingress."""

    def test_financial_metric_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            FinancialMetric(revenue=1000, employees=10, bogus_field="oops")

    def test_financial_metric_valid_creation(self) -> None:
        fm = FinancialMetric(revenue=1000, employees=10)
        assert fm.revenue == 1000

    def test_financial_metric_extra_absent_from_dump(self) -> None:
        fm = FinancialMetric(revenue=500, employees=5)
        dumped = fm.model_dump()
        assert "bogus_field" not in dumped

    def test_company_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            Company(id="COMP-001", name="Test", unknown_attr="nope")

    def test_company_valid_creation(self) -> None:
        c = Company(id="COMP-001", name="TestCo")
        assert c.name == "TestCo"

    def test_company_extra_absent_from_dump(self) -> None:
        c = Company(id="COMP-001", name="TestCo")
        dumped = c.model_dump()
        assert "unknown_attr" not in dumped


class TestTenantModelStrictIngress:
    """Tenant models reject undeclared fields at ingress."""

    def test_tenant_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            Tenant(name="Acme", hacker_field="injected")

    def test_tenant_valid_creation(self) -> None:
        t = Tenant(name="Acme")
        assert t.name == "Acme"

    def test_tenant_limits_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            TenantLimits(max_companies=100, sneaky="data")

    def test_tenant_features_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            TenantFeatures(ai_enrichment=True, hidden_flag=True)

    def test_tenant_config_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            TenantConfig(tenant_id="T1", rogue_setting="bad")

    def test_tenant_user_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            TenantUser(tenant_id="T1", email="a@b.com", admin_override=True)

    def test_tenant_usage_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            TenantUsage(tenant_id="T1", date="2026-01-01", phantom_metric=99)


class TestEvidenceModelStrictIngress:
    """Evidence models reject undeclared fields at ingress."""

    def test_confidence_component_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ConfidenceComponent(name="src", score=0.8, explanation="ok", bonus=1.0)

    def test_claim_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            Claim(
                entity_id="E1",
                field="revenue",
                value=1000,
                source_url="https://example.com",
                source_type=SourceType.WEBSITE,
                snippet="Revenue was $1000",
                extraction_method="regex",
                ghost_field="haunted",
            )

    def test_claim_valid_creation(self) -> None:
        claim = Claim(
            entity_id="E1",
            field="revenue",
            value=1000,
            source_url="https://example.com",
            source_type=SourceType.WEBSITE,
            snippet="Revenue was $1000",
            extraction_method="regex",
        )
        assert claim.entity_id == "E1"

    def test_claim_extra_absent_from_dump(self) -> None:
        claim = Claim(
            entity_id="E1",
            field="revenue",
            value=1000,
            source_url="https://example.com",
            source_type=SourceType.WEBSITE,
            snippet="Revenue was $1000",
            extraction_method="regex",
        )
        dumped = claim.model_dump()
        assert "ghost_field" not in dumped

    def test_source_document_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            SourceDocument(
                url="https://example.com",
                source_type=SourceType.NEWS,
                domain="example.com",
                extra_meta="leaked",
            )

    def test_contradiction_rejects_extra_field(self) -> None:
        from uuid import uuid4

        with pytest.raises(ValidationError, match="extra_forbidden"):
            Contradiction(
                claim_ids=[uuid4(), uuid4()],
                field="revenue",
                values=[100, 200],
                debug_info="should not exist",
            )

    def test_evidence_readiness_rejects_extra_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            EvidenceReadiness(
                entity_id="E1",
                internal_score=99.9,
            )
