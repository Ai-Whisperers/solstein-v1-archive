#!/usr/bin/env python3
"""Test script for EPIC-013: Fix Data Quality and Validation"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.analytics.data_quality import DataQualityCalculator
from solstein.validation.company_validator import CompanyValidator


def test_data_validation():
    """Test company data validation."""
    print("=" * 60)
    print("EPIC-013: Data Validation Test")
    print("=" * 60)

    valid_company = {
        "company_name": "Test Company",
        "revenue": {"timeline": [{"eur_millions": 100}]},
        "employees": 50,
        "growth_rate": 25.0,
        "funding_raised": 10.0,
        "valuation": 50.0,
        "founded_year": 2015,
        "profit_margin": 15.0,
        "ebitda_margin": 20.0,
    }

    invalid_company = {
        "company_name": "Bad Company",
        "revenue": {"timeline": [{"eur_millions": -50}]},
        "employees": -10,
        "growth_rate": 2000.0,
        "funding_raised": 100.0,
        "valuation": 10.0,
        "founded_year": 2050,
        "profit_margin": 150.0,
    }

    try:
        print("\n1. Testing valid company data:")
        result_valid = CompanyValidator.validate(valid_company)
        print(f"   Is valid: {result_valid.is_valid}, Errors: {len(result_valid.errors)}")
        if not result_valid.errors:
            print("     ✓ No validation errors")

        print("\n2. Testing invalid company data:")
        result_invalid = CompanyValidator.validate(invalid_company)
        print(f"   Is valid: {result_invalid.is_valid}")
        print(f"   Errors: {len(result_invalid.errors)}")
        for issue in result_invalid.errors:
            print(f"     ✗ {issue.field}: {issue.message}")

        print("\n" + "=" * 60)
        print("✓ Data Validation is working")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_data_quality():
    """Test data quality scoring."""
    print("\n" + "=" * 60)
    print("EPIC-013: Data Quality Scoring Test")
    print("=" * 60)

    test_company = {
        "company_name": "Quality Test Co",
        "description": "A test company",
        "industry": "Software",
        "founded_year": 2015,
        "country": "USA",
        "website": "https://example.com",
        "revenue": 100.0,
        "growth_rate": 25.0,
        "profit_margin": 15.0,
        "funding_raised": 50.0,
        "valuation": 200.0,
        "employees": 100,
        "ai_maturity": "moderate",
        "ai_score": 6.5,
        "geographic_presence": ["US", "EU"],
        "classification": "Phoenix",
        "data_quality_score": 0.85,
        "enrichment_source_count": 3,
        "source_links": [{"source": "test", "type": "api"}],
    }

    try:
        calculator = DataQualityCalculator()
        report = calculator.calculate_quality(test_company)

        print(f"\n  Company: {report.company_name}")
        print(f"  Overall Score: {report.overall_score:.0%}")
        print(f"  Fields Present: {report.fields_present}/{report.fields_total}")
        print("\n  Category Scores:")
        for category, score in report.category_scores.items():
            print(f"    - {category}: {score:.0%}")

        print("\n" + "=" * 60)
        print("✓ Data Quality Scoring is working")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_market_report():
    """Test market-wide data quality report."""
    print("\n" + "=" * 60)
    print("EPIC-013: Market Quality Report Test")
    print("=" * 60)

    companies = [
        {"company_name": "Co A", "revenue": 100, "employees": 50},
        {"company_name": "Co B", "revenue": 200, "employees": 100},
        {"company_name": "Co C"},
    ]

    try:
        calculator = DataQualityCalculator()
        report = calculator.generate_market_report(companies)

        print(f"\n  Companies Analyzed: {report['companies_analyzed']}")
        print(f"  Market Average Score: {report['market_average_score']}")
        print("\n  Quality Distribution:")
        for quality, count in report["quality_distribution"].items():
            print(f"    - {quality.capitalize()}: {count}")

        print("\n" + "=" * 60)
        print("✓ Market Quality Reporting is working")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success1 = test_data_validation()
    success2 = test_data_quality()
    success3 = test_market_report()

    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("✓ EPIC-013: All Data Quality Tests PASSED")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
