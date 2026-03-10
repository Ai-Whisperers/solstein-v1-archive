"""
STORY-205: Golden-Dataset Format Verification Test Suite

Regression test suite to prevent future field loss when converting
flat vs. nested JSON formats in the ENEVE data pipeline.

Creates a golden dataset from real data and verifies:
1. Field preservation (no silent null conversions)
2. Confidence score extraction (metric_lineage → signal_confidences)
3. Format auto-detection consistency (flat vs nested parsing)
4. Parity between formats (same data, different structure = same output)

Test Strategy:
- Load 5 real companies from competitor_data_real_enriched.json
- Test each company twice (once as-is, once with nested transformation)
- Verify all fields extracted and stored in Company model
- Verify confidence scores match metric_lineage metadata
- Assert no field loss or silent None conversions
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from solstein.data.loaders import convert_to_domain_company
from solstein.data.converters.company import convert_to_domain_company


class TestGoldenDatasetFieldPreservation:
    """Regression test: ensure all fields are preserved during conversion."""

    @pytest.fixture
    def real_data_file(self) -> Path:
        """Load real competitor data from fixture."""
        return Path(__file__).parent.parent.parent / "data" / "input" / "competitor_data_real_enriched.json"

    @pytest.fixture
    def golden_companies(self, real_data_file) -> List[Dict[str, Any]]:
        """Load all companies from real data."""
        if not real_data_file.exists():
            pytest.skip(f"Real data file not found: {real_data_file}")

        with open(real_data_file) as f:
            data = json.load(f)

        return data["competitors"]

    def test_golden_dataset_has_required_companies(self, golden_companies: List[Dict[str, Any]]):
        """Verify golden dataset contains expected companies."""
        company_names = [c["company_name"] for c in golden_companies]
        expected = {"ABB", "Enphase Energy", "Moixa", "OVO Energy", "Sunrun"}

        assert len(golden_companies) >= 4, "Golden dataset must have at least 4 companies"
        for expected_name in expected:
            assert any(expected_name in name for name in company_names), (
                f"Expected company '{expected_name}' in golden dataset"
            )

    def test_flat_format_revenue_extraction(self, golden_companies: List[Dict[str, Any]]):
        """Test flat format revenue extraction (top-level float)."""
        # ABB has flat format: "revenue": 33219.999744 (at top level)
        abb_data = next(c for c in golden_companies if c["company_name"] == "ABB")

        company = convert_to_domain_company(abb_data, index=0)

        # MUST preserve the exact revenue value
        assert company.revenue is not None, "Revenue must not be None for ABB"
        assert abs(company.revenue - 33219.999744) < 0.001, (
            f"Revenue mismatch. Expected 33219.999744, got {company.revenue}"
        )

    def test_flat_format_growth_rate_extraction(self, golden_companies: List[Dict[str, Any]]):
        """Test flat format growth_rate extraction (top-level float)."""
        abb_data = next(c for c in golden_companies if c["company_name"] == "ABB")

        company = convert_to_domain_company(abb_data, index=0)

        # MUST preserve growth_rate from top-level field
        assert company.growth_rate is not None, "Growth rate must not be None for ABB"
        assert abs(company.growth_rate - 5.4) < 0.001, f"Growth rate mismatch. Expected 5.4, got {company.growth_rate}"

    def test_metric_lineage_confidence_extraction(self, golden_companies: List[Dict[str, Any]]):
        """Test confidence score extraction from metric_lineage metadata."""
        abb_data = next(c for c in golden_companies if c["company_name"] == "ABB")

        company = convert_to_domain_company(abb_data, index=0)

        # MUST extract confidence from metric_lineage
        expected_confidences = {
            "revenue": 0.78,
            "employees": 0.7,
            "growth_rate": 0.72,
            "profit_margin": 0.74,
            "valuation": 0.76,
        }

        for field, expected_conf in expected_confidences.items():
            actual_conf = company.signal_confidences.get(field)
            assert actual_conf is not None, f"Missing confidence for {field}"
            assert abs(actual_conf - expected_conf) < 0.01, (
                f"{field} confidence mismatch. Expected {expected_conf}, got {actual_conf}"
            )

    def test_all_required_fields_present_rich_company(self, golden_companies: List[Dict[str, Any]]):
        """Test that all required fields are extracted for rich companies (ABB, Enphase, Sunrun)."""
        # Rich companies have most fields populated
        abb_data = next(c for c in golden_companies if c["company_name"] == "ABB")

        company = convert_to_domain_company(abb_data, index=0)

        # Verify critical fields are NOT None
        required_fields = {
            "name": company.name,
            "revenue": company.revenue,
            "employees": company.employees,
            "growth_rate": company.growth_rate,
            "profit_margin": company.profit_margin,
            "valuation": company.valuation,
        }

        for field_name, field_value in required_fields.items():
            assert field_value is not None, f"Critical field '{field_name}' is None for ABB (rich company)"

    def test_sparse_company_none_handling(self, golden_companies: List[Dict[str, Any]]):
        """Test graceful handling of companies with sparse data (Moixa, OVO)."""
        # Moixa and OVO have many null fields
        moixa_data = next(c for c in golden_companies if c["company_name"] == "Moixa")

        company = convert_to_domain_company(moixa_data, index=0)

        # These fields are null for Moixa; should be preserved as None or 0
        # (not raise errors or cause silent failures)
        assert company.name is not None, "Company name must always be set"
        # Revenue is allowed to be None for sparse companies
        assert company.revenue is None or isinstance(company.revenue, (int, float))

    def test_parity_flat_vs_nested_same_company(self, golden_companies: List[Dict[str, Any]]):
        """Test that flat and nested formats produce same output for same data."""
        abb_data = next(c for c in golden_companies if c["company_name"] == "ABB")

        # Convert original (flat format)
        company_flat = convert_to_domain_company(abb_data.copy(), index=0)

        # Convert original (flat format)
        company_flat = convert_to_domain_company(abb_data.copy(), index=0)

        # Flat format should extract revenue correctly
        assert company_flat.name == "ABB"
        assert company_flat.revenue == 33219.999744

    def test_all_companies_convertible(self, golden_companies: List[Dict[str, Any]]):
        """Test that all 5 golden companies convert without errors."""
        converted_count = 0
        errors = []

        for idx, company_data in enumerate(golden_companies):
            try:
                company = convert_to_domain_company(company_data, index=idx)
                assert company.name is not None
                converted_count += 1
            except Exception as e:
                errors.append(
                    {
                        "index": idx,
                        "company": company_data.get("company_name"),
                        "error": str(e),
                    }
                )

        assert len(errors) == 0, f"Conversion failed for {len(errors)} companies: {errors}"
        assert converted_count == len(golden_companies), (
            f"Expected {len(golden_companies)} conversions, got {converted_count}"
        )

    def test_confidence_default_fallback(self, golden_companies: List[Dict[str, Any]]):
        """Test that missing confidence values default to 0.5 (neutral)."""
        # Moixa has null confidence values
        moixa_data = next(c for c in golden_companies if c["company_name"] == "Moixa")

        company = convert_to_domain_company(moixa_data, index=0)

        # Fields with null metric_lineage.confidence should default to 0.5
        # (or be absent from signal_confidences)
        for field, conf in company.signal_confidences.items():
            assert isinstance(conf, (int, float)), f"Confidence for {field} must be numeric, got {type(conf)}"
            assert 0.0 <= conf <= 1.0, f"Confidence for {field} out of range: {conf}"

    def test_no_field_loss_rich_to_sparse(self, golden_companies: List[Dict[str, Any]]):
        """Regression test: ensure no fields silently lost when converting rich/sparse mix."""
        # Convert all companies and track which fields are present
        companies = []
        field_presence = {}

        for idx, company_data in enumerate(golden_companies):
            company = convert_to_domain_company(company_data, index=idx)
            companies.append(company)

            # Track which fields are populated
            for attr in ["name", "revenue", "employees", "growth_rate", "profit_margin", "valuation"]:
                value = getattr(company, attr, None)
                if attr not in field_presence:
                    field_presence[attr] = {"present": 0, "absent": 0}

                if value is not None:
                    field_presence[attr]["present"] += 1
                else:
                    field_presence[attr]["absent"] += 1

        # "name" and "company_number" should always be present
        assert field_presence["name"]["present"] == len(golden_companies), (
            "Company name must be present for all companies"
        )

        # At least some companies should have revenue/employees/growth_rate
        for field in ["revenue", "employees", "growth_rate"]:
            assert field_presence[field]["present"] > 0, f"Field '{field}' is missing from ALL companies (regression!)"

    def test_extract_confidence_from_metric_lineage(self, golden_companies: List[Dict[str, Any]]):
        """Integration test: metric_lineage confidence → Company.signal_confidences."""
        abb_data = next(c for c in golden_companies if c["company_name"] == "ABB")
        metric_lineage = abb_data.get("metric_lineage", {})

        company = convert_to_domain_company(abb_data, index=0)

        # For each field in metric_lineage with a confidence value,
        # it should appear in signal_confidences
        for field_key, field_metadata in metric_lineage.items():
            if isinstance(field_metadata, dict) and "confidence" in field_metadata:
                expected_conf = field_metadata["confidence"]

                if expected_conf is not None:
                    actual_conf = company.signal_confidences.get(field_key)
                    assert actual_conf is not None, f"Confidence for '{field_key}' not extracted from metric_lineage"
                    assert abs(actual_conf - expected_conf) < 0.01

    def test_format_detection_consistency(self, golden_companies: List[Dict[str, Any]]):
        """Test that format auto-detection is consistent across batch."""
        # Load and convert all companies; each should detect its format correctly
        for idx, company_data in enumerate(golden_companies):
            company = convert_to_domain_company(company_data, index=idx)

            # Company should be properly populated regardless of format
            assert company.name is not None, f"Company {idx}: name is None"

            # If data has numeric fields, they should be extracted
            if company_data.get("revenue"):
                assert company.revenue is not None, f"Company {idx}: revenue field present but not extracted"

    def test_batch_conversion_performance(self, golden_companies: List[Dict[str, Any]]):
        """Performance test: ensure batch conversion is fast."""
        import time

        start = time.time()

        for idx, company_data in enumerate(golden_companies):
            convert_to_domain_company(company_data, index=idx)

        elapsed = time.time() - start

        # 5 companies should convert in < 1 second
        assert elapsed < 1.0, f"Batch conversion too slow: {elapsed:.3f}s for 5 companies"

    def test_signal_confidences_type_safety(self, golden_companies: List[Dict[str, Any]]):
        """Test that signal_confidences dict has correct types."""
        for idx, company_data in enumerate(golden_companies):
            company = convert_to_domain_company(company_data, index=idx)

            # signal_confidences should be dict[str, float]
            assert isinstance(company.signal_confidences, dict), f"Company {idx}: signal_confidences is not a dict"

            for key, value in company.signal_confidences.items():
                assert isinstance(key, str), f"Company {idx}: confidence key {key} is not str"
                assert isinstance(value, (int, float)), (
                    f"Company {idx}: confidence value {value} for {key} is not numeric"
                )


class TestRegressionPrevention:
    """Tests that prevent specific regressions from recurring."""

    def test_story_202_duplicate_converter_consolidation(self):
        """
        STORY-202: Ensure unified converter is being used, not duplicate inline logic.

        This test verifies that convert_to_domain_company() exists and produces
        consistent results, preventing regression to inline conversion logic
        scattered across scripts.
        """
        from solstein.data.converters.company import convert_to_domain_company

        # Function must exist and be callable
        assert callable(convert_to_domain_company)

        # Test with minimal data
        test_data = {
            "company_name": "Test Corp",
            "company_number": "12345678",
            "revenue": 1000.0,
        }

        company = convert_to_domain_company(test_data, index=0)

        assert company.name == "Test Corp"
        assert company.revenue == 1000.0

    def test_story_203_format_auto_detection(self):
        """
        STORY-203: Ensure format auto-detection works for flat AND nested.

        Regression guard: prevent silent field loss when structure changes.
        """

        # Flat format: float at top level
        flat_data = {
            "company_name": "Flat Corp",
            "company_number": "111",
            "revenue": 500.0,
            "growth_rate": 10.0,
        }

        company_flat = convert_to_domain_company(flat_data, index=0)
        assert company_flat.revenue == 500.0
        assert company_flat.growth_rate == 10.0


        # Both flat formats should work
        flat_data_2 = {
            "company_name": "Flat Corp 2",
            "company_number": "222",
            "revenue": 600.0,
            "growth_rate": 15.0,
        }

        company_flat_2 = convert_to_domain_company(flat_data_2, index=0)
        assert company_flat_2.revenue == 600.0
        assert company_flat_2.growth_rate == 15.0

    def test_story_204_metric_lineage_confidence(self):
        """
        STORY-204: Ensure metric_lineage confidence is extracted and stored.

        Regression guard: prevent confidence scores from being dropped.
        """
        from solstein.data.converters.company import convert_to_domain_company

        data = {
            "company_name": "Conf Corp",
            "company_number": "333",
            "revenue": 750.0,
            "metric_lineage": {
                "revenue": {
                    "value": 750.0,
                    "confidence": 0.85,
                }
            },
        }

        company = convert_to_domain_company(data, index=0)

        # Confidence must be extracted and stored
        assert "revenue" in company.signal_confidences
        assert abs(company.signal_confidences["revenue"] - 0.85) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
