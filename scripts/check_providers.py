#!/usr/bin/env python3
"""Test working LLM providers and show status."""

import sys
from pathlib import Path as _Path

# Resolve src dynamically: scripts/check_providers.py → project root/src
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "src"))

import asyncio

from solstein.config import get_settings
from solstein.llm import get_health_checker

# Provider test results from manual API testing
PROVIDER_STATUS = {
    "openai": {
        "working": True,
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
        "best_for": "General purpose, reliable",
        "cost": "Medium",
    },
    "fireworks": {
        "working": True,
        "models": ["qwen2-72b-instruct", "mixtral-8x22b-instruct"],
        "best_for": "Cost-effective, large context",
        "cost": "Low",
    },
    "groq": {
        "working": False,
        "error": "Invalid API Key",
        "action": "Update API key in .env",
    },
    "mistral": {
        "working": True,
        "models": ["mistral-large-2411", "pixtral-large-2411", "codestral-2508"],
        "best_for": "European provider, good for EU data",
        "cost": "Medium",
    },
    "deepinfra": {
        "working": True,
        "models": ["meta-llama/Llama-3.3-70B-Instruct", "meta-llama/Llama-4-Scout"],
        "best_for": "Latest Llama models",
        "cost": "Low",
    },
    "gemini": {
        "working": True,
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"],
        "best_for": "Large context (1M tokens), multimodal",
        "cost": "Low",
    },
}


def print_status():
    """Print provider status."""
    print("=" * 70)
    print("🔐 Ivan's API Keystore - Provider Status")
    print("=" * 70)
    print()

    working = []
    not_working = []

    for provider, info in PROVIDER_STATUS.items():
        if info["working"]:
            working.append((provider, info))
        else:
            not_working.append((provider, info))

    print("✅ WORKING PROVIDERS:")
    print("-" * 70)
    for provider, info in working:
        print(f"\n  🔹 {provider.upper()}")
        print("     Status: ✓ Working")
        print(f"     Models: {', '.join(info['models'][:3])}")
        print(f"     Best for: {info['best_for']}")
        print(f"     Cost: {info['cost']}")

    if not_working:
        print("\n")
        print("❌ NOT WORKING:")
        print("-" * 70)
        for provider, info in not_working:
            print(f"\n  🔸 {provider.upper()}")
            print(f"     Status: ✗ {info['error']}")
            print(f"     Action: {info['action']}")

    print("\n")
    print("=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70)
    print("""
  🥇 PRIMARY: Fireworks (qwen2-72b-instruct)
     - Cheapest option
     - Good quality
     - Reliable

  🥈 SECONDARY: OpenAI (gpt-4o-mini)
     - Best quality
     - Fast
     - More expensive

  🥉 FALLBACK: Mistral or DeepInfra
     - Alternative providers
     - Good for redundancy
    """)

    print("=" * 70)
    print(f"Total Working: {len(working)}/{len(PROVIDER_STATUS)}")
    print("=" * 70)


async def test_health_checker():
    """Test the health checker status."""
    print("\n")
    print("=" * 70)
    print("🔍 HEALTH CHECKER STATUS:")
    print("=" * 70)

    settings = get_settings()
    print(f"\n  LLM_PROVIDER setting: {settings.llm_provider}")
    print()

    checker = get_health_checker()
    health = await checker.check_all_providers()

    for name, h in health.items():
        status = "✓" if h.is_available else "✗"
        print(f"  {status} {name}: {h.status.value}")
        if h.last_error:
            print(f"      Last error: {h.last_error.value}")

    available = checker.get_available_providers()
    print(f"\n  Available for use: {available if available else 'None'}")
    print(f"  Best provider: {checker.get_best_provider()}")


if __name__ == "__main__":
    print_status()
    asyncio.run(test_health_checker())
