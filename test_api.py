#!/usr/bin/env python3
"""
Test SolStein FastAPI endpoints.

Quick test to verify all API endpoints are working correctly.
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer demo-token"}


def test_health():
    """Test health check endpoint."""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    return response.status_code == 200


def test_companies():
    """Test companies endpoint."""
    print("\nTesting /companies endpoint...")
    response = requests.get(f"{BASE_URL}/companies", headers=HEADERS)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Companies returned: {len(data)}")
        if data:
            print(f"  First company: {data[0]['name']}")
        return True
    else:
        print(f"  Error: {response.text}")
        return False


def test_market_analysis():
    """Test market analysis endpoint."""
    print("\nTesting /market/analysis endpoint...")
    response = requests.get(f"{BASE_URL}/market/analysis", headers=HEADERS)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Market analysis successful")
        print(f"  Total companies analyzed: {data.get('total_companies', 0)}")
        return True
    else:
        print(f"  Error: {response.text}")
        return False


def test_scoring():
    """Test scoring endpoint."""
    print("\nTesting scoring endpoint...")
    
    # First get a company ID
    response = requests.get(f"{BASE_URL}/companies", headers=HEADERS)
    if response.status_code != 200:
        print("  Cannot test scoring - no companies available")
        return False
    
    companies = response.json()
    if not companies:
        print("  Cannot test scoring - no companies available")
        return False
    
    company_id = companies[0]["id"]
    print(f"  Testing with company ID: {company_id}")
    
    response = requests.post(
        f"{BASE_URL}/scoring/company/{company_id}/score",
        headers=HEADERS
    )
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Scoring successful")
        print(f"  Growth score: {data.get('growth_score')}")
        print(f"  Classification: {data.get('classification')}")
        return True
    else:
        print(f"  Error: {response.text}")
        return False


def test_export():
    """Test export endpoint."""
    print("\nTesting /export/json endpoint...")
    response = requests.get(f"{BASE_URL}/export/json", headers=HEADERS)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Export successful")
        print(f"  Total companies exported: {data.get('total_companies', 0)}")
        return True
    else:
        print(f"  Error: {response.text}")
        return False


def test_search():
    """Test search endpoint."""
    print("\nTesting /search endpoint...")
    response = requests.get(
        f"{BASE_URL}/search",
        params={"query": "energy", "field": "name"},
        headers=HEADERS
    )
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Search successful")
        print(f"  Results found: {data.get('total_results', 0)}")
        return True
    else:
        print(f"  Error: {response.text}")
        return False


def test_stats():
    """Test statistics endpoint."""
    print("\nTesting /stats endpoint...")
    response = requests.get(f"{BASE_URL}/stats", headers=HEADERS)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Statistics retrieved")
        print(f"  Total companies: {data.get('total_companies', 0)}")
        print(f"  Total revenue: €{data.get('revenue_statistics', {}).get('total_revenue_eur_m', 0):,.0f}M")
        return True
    else:
        print(f"  Error: {response.text}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("SolStein API Test Suite")
    print("=" * 60)
    
    # Wait a moment for API to be ready
    print("Waiting for API to be ready...")
    time.sleep(2)
    
    tests = [
        test_health,
        test_companies,
        test_market_analysis,
        test_scoring,
        test_export,
        test_search,
        test_stats
    ]
    
    results = []
    for test in tests:
        try:
            success = test()
            results.append((test.__name__, success))
        except Exception as e:
            print(f"  Exception in test: {e}")
            results.append((test.__name__, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! SolStein API is working correctly.")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed.")
    
    return passed == len(results)


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        exit(1)