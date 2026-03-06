#!/usr/bin/env python3
"""
Test script for EPIC-004: Data Conversion Pipeline Fix

Verifies that all confidence, source, and quality fields are properly
mapped from raw JSON to Company domain model.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.data.loaders import CompetitorDataLoader


def test_field_mapping():
    """Test that all fields are properly mapped from JSON to Company model."""
    print("=" * 60)
    print("EPIC-004: Data Conversion Pipeline Test")
    print("=" * 60)

    # Use test fixture data directly
    test_data_path = Path(__file__).parent.parent / "tests" / "fixtures" / "synthetic" / "competitor_data_enriched.json"
    loader = CompetitorDataLoader(data_dir=test_data_path.parent)

    try:
        # Load directly from the test fixture
        companies = loader.load_from_json(test_data_path)
        print(f"\n✓ Loaded {len(companies)} companies")

        if not companies:
            print("✗ No companies loaded!")
            return False

        # Test first company
        company = companies[0]
        print(f"\n✓ Testing company: {company.name}")

        errors = []

        # Test 1: confidence_scores should be populated
        if not company.confidence_scores:
            errors.append("confidence_scores is empty")
        else:
            print(f"  ✓ confidence_scores: {company.confidence_scores}")

        # Test 2: metric_sources should be populated
        if not company.metric_sources:
            errors.append("metric_sources is empty")
        else:
            print(f"  ✓ metric_sources: {company.metric_sources}")

        # Test 3: enrichment_quality_metrics should be populated
        if not company.enrichment_quality_metrics:
            errors.append("enrichment_quality_metrics is empty")
        else:
            print(f"  ✓ enrichment_quality_metrics: {company.enrichment_quality_metrics}")

        # Test 4: source_links should be list of strings (not objects)
        if company.source_links:
            if all(isinstance(link, str) for link in company.source_links):
                print(f"  ✓ source_links: {len(company.source_links)} string entries")
            else:
                errors.append("source_links contains non-string entries")
        else:
            print("  ℹ source_links is empty (may be OK depending on data)")

        # Test 5: data_quality_tier should be set
        if company.data_quality_tier == "unknown":
            errors.append("data_quality_tier is 'unknown' (not mapped)")
        else:
            print(f"  ✓ data_quality_tier: {company.data_quality_tier}")

        # Test 6: enrichment_source_count should be > 0
        if company.enrichment_source_count == 0:
            errors.append("enrichment_source_count is 0 (not mapped)")
        else:
            print(f"  ✓ enrichment_source_count: {company.enrichment_source_count}")

        print("\n" + "=" * 60)
        if errors:
            print("✗ ERRORS FOUND:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("✓ ALL TESTS PASSED!")
            print("✓ EPIC-004: Data Conversion Pipeline Fix is working")
            return True

    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_field_mapping()
    sys.exit(0 if success else 1)
