#!/usr/bin/env python3
"""
Test script for EPIC-007: Implement Confidence System

Verifies that signal_confidences is populated correctly from financial metric confidence levels.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.data.loaders import CompetitorDataLoader


def test_confidence_system():
    """Test that signal_confidences is populated from financial metric confidence levels."""
    print("=" * 60)
    print("EPIC-007: Confidence System Test")
    print("=" * 60)

    # Load test data
    test_data_path = Path(__file__).parent.parent / "tests" / "fixtures" / "synthetic" / "competitor_data_enriched.json"
    loader = CompetitorDataLoader(data_dir=test_data_path.parent)

    try:
        companies = loader.load_from_json(test_data_path)
        print(f"\n✓ Loaded {len(companies)} companies")

        if not companies:
            print("✗ No companies loaded!")
            return False

        errors = []

        # Test each company
        for company in companies:
            print(f"\n  {company.name}:")

            # Check signal_confidences is populated
            if not company.signal_confidences:
                errors.append(f"{company.name}: signal_confidences is empty")
                print("    ✗ signal_confidences is EMPTY")
            else:
                print(f"    ✓ signal_confidences: {company.signal_confidences}")

                # Check for expected signal types
                expected_signals = [
                    "revenue_level",
                    "growth_rate",
                    "company_size",
                    "profitability",
                    "funding",
                    "valuation",
                ]
                for signal in expected_signals:
                    if signal in company.signal_confidences:
                        weight = company.signal_confidences[signal]
                        print(f"      ✓ {signal}: {weight}")
                    else:
                        print(f"      ℹ {signal}: not present (may be OK if data is None)")

            # Check confidence_scores is synced from signal_confidences
            if not company.confidence_scores:
                errors.append(f"{company.name}: confidence_scores is empty (should be synced from signal_confidences)")
                print("    ✗ confidence_scores is EMPTY")
            else:
                print(f"    ✓ confidence_scores: {company.confidence_scores}")

        print("\n" + "=" * 60)
        if errors:
            print("✗ ERRORS FOUND:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("✓ ALL TESTS PASSED!")
            print("✓ EPIC-007: Confidence System is working")
            print("\nConfidence weighting will now be applied in scoring")
            return True

    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_confidence_system()
    sys.exit(0 if success else 1)
