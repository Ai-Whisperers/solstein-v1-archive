#!/usr/bin/env python3
"""
Test script for data source connectors.

This script tests all implemented connectors to verify they work correctly.
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.connectors import get_registry, initialize_default_connectors

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_connector(name: str, query: str):
    """Test a single connector."""
    registry = get_registry()
    connector = registry.get(name)

    if not connector:
        print(f"❌ {name}: Not registered")
        return False

    print(f"\nTesting {name}...")
    print(f"  Query: {query}")

    try:
        # Test connection
        connected = await connector.connect()
        if not connected:
            print("  ❌ Connection failed")
            return False
        print("  ✅ Connected")

        # Test search
        result = await connector.search(query, limit=3)

        if result.success:
            print("  ✅ Search successful")
            print(f"     Results: {len(result.data)}")
            print(f"     Total found: {result.total_found}")

            # Show first result
            if result.data:
                normalized = connector.normalize(result.data[0])
                print(f"     First result: {normalized.get('title', normalized.get('company_name', 'N/A'))[:60]}...")

            return True
        else:
            print(f"  ❌ Search failed: {result.error_message}")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


async def main():
    """Run connector tests."""

    print("=" * 60)
    print("DATA SOURCE CONNECTOR TESTS")
    print("=" * 60)

    # Initialize connectors
    print("\nInitializing connectors...")
    registry = await initialize_default_connectors()
    print(f"✅ Initialized {len(registry.list_connectors())} connectors")
    print(f"   Available: {', '.join(registry.list_connectors())}")

    # Test each connector
    test_cases = [
        ("yahoo_finance", "AAPL"),
        ("semantic_scholar", "machine learning"),
        ("arxiv", "transformer architecture"),
    ]

    results = []
    for name, query in test_cases:
        success = await test_connector(name, query)
        results.append((name, success))
        await asyncio.sleep(1)  # Be polite

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")

    # Cleanup
    await registry.close_all()

    print("\n✅ Tests complete!")
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
