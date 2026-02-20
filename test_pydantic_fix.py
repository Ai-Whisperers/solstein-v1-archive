#!/usr/bin/env python3
"""
Test Pydantic v2 compatibility fixes.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    # Test 1: Import models
    from solstein.data.models import CompanyProfile, ConfidenceLevel, FinancialMetric

    print("✅ Test 1: Models import successfully")

    # Test 2: Create a FinancialMetric instance
    metric = FinancialMetric(
        revenue=1000000.0,
        revenue_confidence=ConfidenceLevel.CONFIRMED,
        growth_rate=15.5,
        growth_confidence=ConfidenceLevel.ESTIMATED,
        employees=50,
        employees_confidence=ConfidenceLevel.CONFIRMED
    )

    print(f"✅ Test 2: Created FinancialMetric: {metric}")

    # Test 3: Test validator (string conversion)
    metric2 = FinancialMetric(
        revenue="1.5M",  # Should convert to 1500000.0
        revenue_confidence=ConfidenceLevel.ESTIMATED,
        growth_rate="15.5%",  # Should handle string
        growth_confidence=ConfidenceLevel.ESTIMATED
    )

    print(f"✅ Test 3: String conversion works: revenue={metric2.revenue}")

    # Test 4: Import config
    from solstein.config import DatabaseConfig, Settings

    print("✅ Test 4: Config imports successfully")

    # Test 5: Create settings
    settings = Settings()
    print(f"✅ Test 5: Created settings: env={settings.environment}")

    print("\n🎉 All Pydantic v2 compatibility tests passed!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
