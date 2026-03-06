"""
Test script to verify classification system works correctly.

Usage:
    python scripts/test_classification.py
"""

import sys

sys.path.insert(0, "src")

from solstein.analytics.scoring import classify_company
from solstein.analytics.constants import (
    PHOENIX_SCORE_THRESHOLD,
    LEAD_SCORE_THRESHOLD,
)


def test_classification_thresholds():
    """Test classification thresholds."""
    print("Testing Classification Thresholds...")
    print("=" * 60)

    print(f"\nThresholds:")
    print(f"  Phoenix: >= {PHOENIX_SCORE_THRESHOLD}")
    print(f"  Salt: {LEAD_SCORE_THRESHOLD + 0.01} - {PHOENIX_SCORE_THRESHOLD - 0.01}")
    print(f"  Lead: <= {LEAD_SCORE_THRESHOLD}")

    test_cases = [
        (2.0, "Lead"),
        (4.0, "Lead"),
        (4.49, "Lead"),  # Exactly at Lead threshold (<= 4.49)
        (4.5, "Salt"),   # Just above Lead threshold
        (5.0, "Salt"),
        (6.5, "Salt"),
        (6.99, "Salt"),  # Just below Phoenix threshold
        (7.0, "Phoenix"), # Exactly at Phoenix threshold (>= 7.0)
        (8.5, "Phoenix"),
        (9.5, "Phoenix"),
    ]
    print(f"\nThresholds:")
    print(f"  Phoenix: >= {PHOENIX_SCORE_THRESHOLD}")
    print(f"  Salt: {LEAD_SCORE_THRESHOLD + 0.01} - {PHOENIX_SCORE_THRESHOLD - 0.01}")
    print(f"  Lead: <= {LEAD_SCORE_THRESHOLD}")
    print(f"\nTest Cases:")
    all_passed = True
    for score, expected in test_cases:
        result = classify_company(score)
        status = "✅" if result == expected else "❌"
        print(f"  Score {score:4.1f} -> {result:8} (expected: {expected}) {status}")
        if result != expected:
            all_passed = False

    return all_passed
    return all_passed


def test_classification_distribution():
    """Test classification with realistic score distribution."""
    print("\n\nTesting Classification Distribution...")
    print("=" * 60)

    import random

    random.seed(42)

    # Simulate 199 companies with realistic score distribution
    scores = []
    for _ in range(199):
        # Normal distribution around 5.5, std dev 2.0
        score = random.gauss(5.5, 2.0)
        score = max(0.0, min(10.0, score))  # Clamp to 0-10
        scores.append(score)

    # Classify all
    classifications = [classify_company(s) for s in scores]

    # Count distribution
    phoenix = sum(1 for c in classifications if c == "Phoenix")
    salt = sum(1 for c in classifications if c == "Salt")
    lead = sum(1 for c in classifications if c == "Lead")

    print(f"\nDistribution (199 companies):")
    print(f"  Phoenix: {phoenix} ({phoenix / 199 * 100:.1f}%)")
    print(f"  Salt:    {salt} ({salt / 199 * 100:.1f}%)")
    print(f"  Lead:    {lead} ({lead / 199 * 100:.1f}%)")

    # Check if distribution is reasonable
    # Expected: ~20% Phoenix, ~60-70% Salt, ~15-20% Lead
    checks = [
        (10 <= phoenix <= 50, f"Phoenix count {phoenix} not in expected range (10-50)"),
        (100 <= salt <= 150, f"Salt count {salt} not in expected range (100-150)"),
        (20 <= lead <= 60, f"Lead count {lead} not in expected range (20-60)"),
    ]

    all_passed = True
    for passed, msg in checks:
        if not passed:
            print(f"  ❌ {msg}")
            all_passed = False

    if all_passed:
        print("\n  ✅ Distribution looks reasonable")

    return all_passed


def test_edge_cases():
    """Test edge cases."""
    print("\n\nTesting Edge Cases...")
    print("=" * 60)

    edge_cases = [
        (None, "Salt", "None score"),
        (0.0, "Lead", "Zero score"),
        (10.0, "Phoenix", "Max score"),
        (7.0, "Phoenix", "Exactly at Phoenix threshold"),
        (4.49, "Lead", "Exactly at Lead threshold (4.49)"),
        (4.5, "Salt", "Just above Lead threshold"),
    ]

    all_passed = True
    for score, expected, description in edge_cases:
        result = classify_company(score)
        passed = result == expected
        status = "✅" if passed else "❌"
        print(f"  {description:30} Score: {str(score):6} -> {result:8} {status}")
        if not passed:
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("=" * 60)
    print("Classification System Tests")
    print("=" * 60)

    results = []
    results.append(("Thresholds", test_classification_thresholds()))
    results.append(("Distribution", test_classification_distribution()))
    results.append(("Edge Cases", test_edge_cases()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:30} {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 Classification system is working correctly!")
        print(f"\nThresholds:")
        print(f"  Phoenix: >= {PHOENIX_SCORE_THRESHOLD}")
        print(f"  Salt:    {LEAD_SCORE_THRESHOLD + 0.01} - {PHOENIX_SCORE_THRESHOLD - 0.01}")
        print(f"  Lead:    <= {LEAD_SCORE_THRESHOLD}")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed.")
        sys.exit(1)
