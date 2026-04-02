"""STORY-180: Field Mapping Parity Test Between Raw JSON and Company Objects.

Verifies that all JSON fields from competitor_data.json are correctly mapped
to Company domain attributes. This test catches silent data loss when new
fields are added to the JSON schema without updating the converter.

How to update this test when adding new JSON fields:
1. If the field should be mapped: add it to EXPECTED_FIELD_MAPPINGS.
2. If the field is intentionally not mapped: add it to INTENTIONALLY_UNMAPPED
   with a documented reason.
3. Run the test to confirm green.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from solstein.data.converters.company import convert_to_domain_company

FIXTURE_PATH = Path("tests/fixtures/synthetic/competitor_data.json")

# Intentionally-unmapped JSON fields (with documented reasons)
INTENTIONALLY_UNMAPPED: dict[str, str] = {
    # Metadata / source-provenance fields — stored in metric_sources dict, not as
    # dedicated Company attributes, because the number of such fields varies per run.
    "employees_confidence": "Stored in signal_confidences dict, not a dedicated attribute",
    "employees_source": "Stored in metric_sources dict, not a dedicated attribute",
    "ai_confidence": "Stored in signal_confidences dict, not a dedicated attribute",
    "ai_source": "Stored in metric_sources dict, not a dedicated attribute",
    "funding_confidence": "Stored in signal_confidences dict, not a dedicated attribute",
    "funding_source": "Stored in metric_sources dict, not a dedicated attribute",
    "valuation_confidence": "Stored in signal_confidences dict, not a dedicated attribute",
    "valuation_source": "Stored in metric_sources dict, not a dedicated attribute",
    "classification_confidence": "Classification confidence, not surfaced on Company",
    # AI maturity score is a raw input; ai_maturity (enum) and ai_score (float) are
    # the normalised outputs used downstream.
    "ai_maturity_score": "Intermediate field; ai_score and ai_maturity carry this value",
    # Internal classification label; not currently used in scoring pipeline.
    "classification": "Internal segmentation label; stored separately if needed",
    # Composite quality score is stored in enrichment_quality_metrics dict.
    "data_quality_score": "Stored in enrichment_quality_metrics dict",
    # revenue.timeline is an array of historical data points used to derive
    # growth_rate, revenue_cagr_3yr, revenue_cagr_5yr, and financials.revenue.
    # The raw timeline is not persisted on Company; derived scalars are.
    "revenue.timeline": "Historical series; derived into revenue, growth_rate, cagr fields",
    # Individual timeline entry sub-fields (year, eur_millions, yoy_growth_pct, confidence, source)
    # are part of the timeline array covered above. The leaf-path walker recurses into the first
    # element of the list, producing these dotted paths. They are all handled by the parent entry.
    "revenue.timeline.year": "Part of revenue.timeline array; covered by revenue.timeline allowlist entry",
    "revenue.timeline.eur_millions": "Part of revenue.timeline array; covered by revenue.timeline allowlist entry",
    "revenue.timeline.yoy_growth_pct": "Part of revenue.timeline array; derived into growth_rate",
    "revenue.timeline.confidence": "Part of revenue.timeline array; provenance metadata, not mapped",
    "revenue.timeline.source": "Part of revenue.timeline array; provenance metadata, not mapped",
    # github_url is informational metadata; not used in the scoring pipeline and
    # the Company domain model has no github_url attribute.
    "github_url": "Informational metadata; Company model has no github_url field (not used in scoring)",
    # profitability sub-fields for confidence/source provenance
    "profitability.confidence": "Stored in signal_confidences dict, not a dedicated attribute",
    "profitability.source": "Stored in metric_sources dict, not a dedicated attribute",
}

# Explicit expected mappings: json_field_path -> (company_attr, expected_type)
# json_field_path uses dot notation for nested fields.
EXPECTED_FIELD_MAPPINGS: dict[str, tuple[str, type]] = {
    # Basic identity
    "company_name": ("name", str),
    "country": ("headquarters", str),
    "industry": ("industry", str),
    "website": ("website", str),
    "description": ("description", str),
    "founded_year": ("founded_year", int),
    "folder": ("id", str),  # folder contributes to the id slug
    # Financial — top-level scalars (STORY-177 fix: ai_score as float)
    "ai_score": ("ai_score", float),
    "ai_maturity": ("ai_maturity", object),  # AIMaturity enum
    "growth_rate": ("financials.growth_rate", float),
    "profit_margin": ("financials.profit_margin", float),
    "employees": ("financials.employees", int),
    "enrichment_source_count": ("enrichment_source_count", int),
    # Revenue (from nested revenue dict)
    "revenue.cagr_3yr_pct": ("revenue_cagr_3yr", float),
    "revenue.cagr_5yr_pct": ("revenue_cagr_5yr", float),
    # Profitability nested fields (STORY-179 fix)
    "profitability.ebitda_margin_pct": ("ebitda_margin", float),
    "profitability.recurring_revenue_pct": ("recurring_revenue_pct", float),
    "profitability.revenue_per_employee_eur_k": ("revenue_per_employee_eur_k", float),
    # Funding (STORY-178 fix: raw EUR on top-level Company)
    "funding_raised": ("total_funding_raised_eur", float),
    "valuation": ("latest_valuation_eur", float),
    # Geographic
    "geographic_presence": ("geographic_presence", list),
}


def _load_raw_companies() -> list[dict]:
    with FIXTURE_PATH.open() as fh:
        data = json.load(fh)
    return data["competitors"]


def _get_leaf_paths(obj: object, prefix: str = "") -> set[str]:
    """Recursively collect all leaf field paths (dot-notation) from a JSON object."""
    paths: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                paths.update(_get_leaf_paths(v, path))
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                # Recurse into first element of list-of-dicts for schema discovery
                paths.update(_get_leaf_paths(v[0], path))
            else:
                paths.add(path)
    return paths


def _resolve_company_attr(company: object, attr_path: str) -> object:
    """Resolve a dotted attribute path on a Company (or nested) object."""
    parts = attr_path.split(".")
    obj = company
    for part in parts:
        obj = getattr(obj, part, None)
        if obj is None:
            return None
    return obj


def _load_companies():
    """Load Company objects using the converter (no DB or infrastructure required)."""
    raws = _load_raw_companies()
    return [convert_to_domain_company(raw, i) for i, raw in enumerate(raws)]


class TestFieldMappingParity:
    """Verify every JSON field is either mapped to a Company attribute or explicitly allowed."""

    @pytest.fixture(scope="class")
    def raw_companies(self):
        return _load_raw_companies()

    @pytest.fixture(scope="class")
    def companies(self):
        return _load_companies()

    def test_all_json_fields_are_accounted_for(self, raw_companies):
        """Every JSON leaf field must be in EXPECTED_FIELD_MAPPINGS or INTENTIONALLY_UNMAPPED."""
        sample = raw_companies[0]
        all_leaf_paths = _get_leaf_paths(sample)

        mapped_paths = set(EXPECTED_FIELD_MAPPINGS.keys())
        allowed_unmapped = set(INTENTIONALLY_UNMAPPED.keys())
        accounted_for = mapped_paths | allowed_unmapped

        missing = all_leaf_paths - accounted_for
        assert not missing, (
            "JSON fields with no mapping decision:\n"
            + "\n".join(f"  - {f}" for f in sorted(missing))
            + "\nAdd each to EXPECTED_FIELD_MAPPINGS (if it should be mapped) "
            "or INTENTIONALLY_UNMAPPED (with a documented reason)."
        )

    def test_mapped_fields_are_present_on_company(self, companies):
        """Every mapping in EXPECTED_FIELD_MAPPINGS must resolve to a non-None value."""
        company = companies[0]  # Eneve — fully-enriched fixture
        missing_attrs = []
        for json_path, (company_path, _) in EXPECTED_FIELD_MAPPINGS.items():
            value = _resolve_company_attr(company, company_path)
            if value is None:
                missing_attrs.append((json_path, company_path))

        assert not missing_attrs, "The following JSON fields are mapped but Company attribute is None:\n" + "\n".join(
            f"  {jp!r} -> {cp!r}" for jp, cp in missing_attrs
        )

    def test_ai_score_is_float_not_truncated(self, raw_companies, companies):
        """STORY-177: ai_score must be a float, never int-truncated."""
        for raw, company in zip(raw_companies, companies):
            raw_score = raw.get("ai_score")
            if raw_score is None:
                continue
            assert isinstance(company.ai_score, float), (
                f"{company.name}: ai_score should be float, got {type(company.ai_score).__name__}"
            )
            assert company.ai_score == float(raw_score), (
                f"{company.name}: ai_score {company.ai_score} != raw {raw_score}"
            )

    def test_funding_raised_maps_to_total_funding_eur(self, raw_companies, companies):
        """STORY-178: funding_raised (raw EUR) must appear on total_funding_raised_eur."""
        for raw, company in zip(raw_companies, companies):
            raw_funding = raw.get("funding_raised")
            if raw_funding is None:
                assert company.total_funding_raised_eur is None
            else:
                assert company.total_funding_raised_eur == float(raw_funding), (
                    f"{company.name}: total_funding_raised_eur {company.total_funding_raised_eur} != raw {raw_funding}"
                )

    def test_valuation_maps_to_latest_valuation_eur(self, raw_companies, companies):
        """STORY-178: valuation (raw EUR) must appear on latest_valuation_eur."""
        for raw, company in zip(raw_companies, companies):
            raw_val = raw.get("valuation")
            if raw_val is None:
                assert company.latest_valuation_eur is None
            else:
                assert company.latest_valuation_eur == float(raw_val), (
                    f"{company.name}: latest_valuation_eur {company.latest_valuation_eur} != raw {raw_val}"
                )

    def test_funding_normalized_to_millions_in_financials(self, raw_companies, companies):
        """financials.funding_raised stores EUR millions, not raw EUR."""
        for raw, company in zip(raw_companies, companies):
            raw_funding = raw.get("funding_raised")
            if raw_funding is None or company.financials.funding_raised is None:
                continue
            raw_millions = raw_funding / 1_000_000
            assert abs(company.financials.funding_raised - raw_millions) < 0.001, (
                f"{company.name}: financials.funding_raised should be in millions "
                f"({raw_millions:.2f}), got {company.financials.funding_raised}"
            )

    def test_ebitda_margin_maps_to_company_top_level(self, raw_companies, companies):
        """STORY-179: profitability.ebitda_margin_pct must be on company.ebitda_margin."""
        for raw, company in zip(raw_companies, companies):
            profitability = raw.get("profitability", {})
            raw_ebitda = profitability.get("ebitda_margin_pct")
            if raw_ebitda is None:
                assert company.ebitda_margin is None
            else:
                assert company.ebitda_margin == float(raw_ebitda), (
                    f"{company.name}: ebitda_margin {company.ebitda_margin} != raw {raw_ebitda}"
                )

    def test_recurring_revenue_pct_maps_to_company_top_level(self, raw_companies, companies):
        """STORY-179: profitability.recurring_revenue_pct must be on company.recurring_revenue_pct."""
        for raw, company in zip(raw_companies, companies):
            profitability = raw.get("profitability", {})
            raw_rrp = profitability.get("recurring_revenue_pct")
            if raw_rrp is None:
                assert company.recurring_revenue_pct is None
            else:
                assert company.recurring_revenue_pct == float(raw_rrp), (
                    f"{company.name}: recurring_revenue_pct {company.recurring_revenue_pct} != raw {raw_rrp}"
                )

    def test_revenue_per_employee_maps_to_company(self, raw_companies, companies):
        """STORY-179: profitability.revenue_per_employee_eur_k on company.revenue_per_employee_eur_k."""
        for raw, company in zip(raw_companies, companies):
            profitability = raw.get("profitability", {})
            raw_rpe = profitability.get("revenue_per_employee_eur_k")
            if raw_rpe is None:
                assert company.revenue_per_employee_eur_k is None
            else:
                assert company.revenue_per_employee_eur_k == float(raw_rpe), (
                    f"{company.name}: revenue_per_employee_eur_k {company.revenue_per_employee_eur_k} != raw {raw_rpe}"
                )

    def test_profitability_fields_sync_with_financials(self, companies):
        """Top-level profitability fields must match the nested financials values."""
        for company in companies:
            assert company.ebitda_margin == company.financials.ebitda_margin, (
                f"{company.name}: ebitda_margin top-level vs financials mismatch"
            )
            assert company.recurring_revenue_pct == company.financials.recurring_revenue_pct, (
                f"{company.name}: recurring_revenue_pct top-level vs financials mismatch"
            )

    def test_revenue_cagr_fields_mapped(self, raw_companies, companies):
        """revenue.cagr_3yr_pct and cagr_5yr_pct must be on company."""
        for raw, company in zip(raw_companies, companies):
            revenue = raw.get("revenue", {})
            raw_3yr = revenue.get("cagr_3yr_pct")
            raw_5yr = revenue.get("cagr_5yr_pct")
            if raw_3yr is not None:
                assert company.revenue_cagr_3yr == float(raw_3yr), f"{company.name}: revenue_cagr_3yr mismatch"
            if raw_5yr is not None:
                assert company.revenue_cagr_5yr == float(raw_5yr), f"{company.name}: revenue_cagr_5yr mismatch"

    def test_field_type_compatibility(self, raw_companies, companies):
        """Each mapped field must match the expected Python type on the Company."""
        sample_company = companies[0]

        type_violations = []
        for json_path, (company_path, expected_type) in EXPECTED_FIELD_MAPPINGS.items():
            value = _resolve_company_attr(sample_company, company_path)
            if value is None:
                continue
            if not isinstance(value, expected_type):
                type_violations.append(
                    f"  {json_path!r} -> {company_path!r}: "
                    f"expected {expected_type.__name__}, got {type(value).__name__}"
                )
        assert not type_violations, "Type mismatches found:\n" + "\n".join(type_violations)

    def test_no_silent_none_for_present_json_values(self, raw_companies, companies):
        """For each company, if a JSON field is present, the Company attribute must not be None."""
        check_pairs = [
            # (json_path, company_attr)
            ("ai_score", "ai_score"),
            ("funding_raised", "total_funding_raised_eur"),
            ("valuation", "latest_valuation_eur"),
        ]
        violations = []
        for raw, company in zip(raw_companies, companies):
            for json_key, company_attr in check_pairs:
                raw_val = raw.get(json_key)
                if raw_val is None:
                    continue
                company_val = getattr(company, company_attr, None)
                if company_val is None:
                    violations.append(
                        f"{company.name}: JSON[{json_key!r}]={raw_val} but company.{company_attr} is None"
                    )
        assert not violations, "Silent None mappings detected:\n" + "\n".join(violations)


def test_all_fixture_companies_load_without_error():
    """All companies in the fixture must load without error and have a name/id."""
    companies = _load_companies()
    assert len(companies) == 3
    for company in companies:
        assert company.name, "Company must have a non-empty name"
        assert company.id, "Company must have a non-empty id"
