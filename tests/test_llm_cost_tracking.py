#!/usr/bin/env python3
"""Simple test for LLM cost tracking."""

import sys

sys.path.insert(0, "/home/ai-whisperers/solstein/src")

from solstein.llm import get_usage_tracker, UsageTracker


def test_usage_tracker():
    """Test usage tracking and cost calculation."""
    print("Testing UsageTracker...")

    tracker = UsageTracker()

    # Test OpenAI GPT-4o-mini
    cost1 = tracker.record_usage(
        provider="openai",
        model="gpt-4o-mini",
        input_tokens=1000,
        output_tokens=500,
    )
    expected1 = (1000 / 1000) * 0.00015 + (500 / 1000) * 0.0006
    assert abs(cost1 - expected1) < 0.00001, f"Expected {expected1}, got {cost1}"
    print(f"  ✓ GPT-4o-mini: ${cost1:.6f}")

    # Test Groq
    cost2 = tracker.record_usage(
        provider="groq",
        model="llama-3.3-70b-versatile",
        input_tokens=2000,
        output_tokens=1000,
    )
    expected2 = (2000 / 1000) * 0.00059 + (1000 / 1000) * 0.00079
    assert abs(cost2 - expected2) < 0.00001, f"Expected {expected2}, got {cost2}"
    print(f"  ✓ Groq Llama 3.3 70B: ${cost2:.6f}")

    # Test Ollama (local - should be free)
    cost3 = tracker.record_usage(
        provider="ollama",
        model="llama3.2:latest",
        input_tokens=1000,
        output_tokens=1000,
    )
    assert cost3 == 0.0, f"Expected 0.0 for local model, got {cost3}"
    print(f"  ✓ Ollama (local): ${cost3:.6f}")

    # Check summary
    summary = tracker.get_summary()
    assert summary["total_requests"] == 3
    assert summary["total_input_tokens"] == 4000
    assert summary["total_output_tokens"] == 2500
    assert summary["total_cost_usd"] > 0

    print(f"  ✓ Total requests: {summary['total_requests']}")
    print(f"  ✓ Total cost: ${summary['total_cost_usd']:.6f}")
    print(f"  ✓ Costs by provider: {summary['costs_by_provider']}")

    print("\nAll UsageTracker tests passed!")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running LLM Cost Tracking Tests")
    print("=" * 60 + "\n")

    try:
        test_usage_tracker()
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
