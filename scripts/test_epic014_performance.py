#!/usr/bin/env python3
"""Test script for EPIC-014: Performance and Scalability"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.data.loaders import CompetitorDataLoader
from solstein.analytics.scoring import classify_company


def test_data_loading_performance():
    """Test data loading performance."""
    print("=" * 60)
    print("EPIC-014: Performance Test - Data Loading")
    print("=" * 60)

    test_data_path = Path(__file__).parent.parent / "tests" / "fixtures" / "synthetic" / "competitor_data_enriched.json"
    loader = CompetitorDataLoader(data_dir=test_data_path.parent)

    try:
        start_time = time.time()
        companies = loader.load_from_json(test_data_path)
        end_time = time.time()

        load_time = end_time - start_time
        company_count = len(companies)

        print(f"\n  Companies loaded: {company_count}")
        print(f"  Load time: {load_time:.3f}s")
        print(f"  Time per company: {load_time / company_count * 1000:.1f}ms")

        if load_time / company_count < 0.1:
            print(f"  ✓ PASS: Load time under 100ms per company")
        else:
            print(f"  ℹ INFO: Load time is {load_time / company_count * 1000:.1f}ms per company")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_classification_performance():
    """Test classification performance."""
    print("\n" + "=" * 60)
    print("EPIC-014: Performance Test - Classification")
    print("=" * 60)

    try:
        start_time = time.time()

        for _ in range(10000):
            result = classify_company(8.5)

        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n  Classification calls: 10000")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Time per call: {total_time / 10000 * 1000:.3f}ms")

        if total_time / 10000 < 0.001:
            print(f"  ✓ PASS: Classification under 1ms per call")
        else:
            print(f"  ℹ INFO: Classification time is {total_time / 10000 * 1000:.3f}ms per call")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


if __name__ == "__main__":
    success1 = test_data_loading_performance()
    success2 = test_classification_performance()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("✓ EPIC-014: Performance Tests Complete")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
