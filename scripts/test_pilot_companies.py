#!/usr/bin/env python3
"""
Pilot Company Test - Test evidence system with 5 real companies.

This script tests the evidence pipeline with actual company websites.
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.evidence import (
    EvidenceService,
    get_evidence_service,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# 5 pilot companies with public websites
PILOT_COMPANIES = [
    {
        "id": "stripe",
        "name": "Stripe",
        "website": "https://stripe.com",
        "expected_fields": ["revenue", "employee_count", "founded_year"],
    },
    {
        "id": "notion",
        "name": "Notion",
        "website": "https://notion.so",
        "expected_fields": ["revenue", "employee_count", "founded_year"],
    },
    {
        "id": "figma",
        "name": "Figma",
        "website": "https://figma.com",
        "expected_fields": ["revenue", "employee_count", "founded_year"],
    },
    {
        "id": "linear",
        "name": "Linear",
        "website": "https://linear.app",
        "expected_fields": ["revenue", "employee_count", "founded_year"],
    },
    {
        "id": "vercel",
        "name": "Vercel",
        "website": "https://vercel.com",
        "expected_fields": ["revenue", "employee_count", "founded_year"],
    },
]


async def test_company(service: EvidenceService, company: dict) -> dict:
    """Test evidence collection for a single company."""
    company_id = company["id"]
    website = company["website"]

    print(f"\n{'=' * 60}")
    print(f"Testing: {company['name']} ({website})")
    print(f"{'=' * 60}")

    try:
        # Research the company
        result = await service.research_company(
            company_id=company_id,
            website_url=website,
            max_pages=3,  # Limit to 3 pages per company for testing
        )

        print("✅ Success!")
        print(f"   Pages crawled: {result['pages_crawled']}")
        print(f"   Claims extracted: {result['claims_extracted']}")
        print(f"   Claims stored: {result['claims_stored']}")
        print(f"   Contradictions: {result['contradictions_detected']}")
        print(f"   Readiness: {result['evidence_readiness'].level}")

        return {
            "company_id": company_id,
            "success": True,
            **result,
        }

    except Exception as e:
        logger.error(f"Failed to research {company_id}: {e}")
        print(f"❌ Failed: {e}")
        return {
            "company_id": company_id,
            "success": False,
            "error": str(e),
        }


async def main():
    """Run pilot test with 5 companies."""

    print("\n" + "=" * 60)
    print("PILOT COMPANY TEST - 5 COMPANIES")
    print("=" * 60)

    # Initialize service
    print("\nInitializing Evidence Service...")
    service = get_evidence_service()
    service.initialize()
    print("✅ Service ready\n")

    # Test each company
    results = []
    for company in PILOT_COMPANIES:
        result = await test_company(service, company)
        results.append(result)

        # Brief pause between companies
        await asyncio.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print("PILOT TEST SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    print(f"\nTotal companies: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if successful:
        total_claims = sum(r.get("claims_stored", 0) for r in successful)
        total_contradictions = sum(r.get("contradictions_detected", 0) for r in successful)

        print(f"\nTotal claims stored: {total_claims}")
        print(f"Total contradictions detected: {total_contradictions}")
        print(f"Avg claims per company: {total_claims / len(successful):.1f}")

    if failed:
        print("\nFailed companies:")
        for r in failed:
            print(f"  - {r['company_id']}: {r.get('error', 'Unknown error')}")

    # Cleanup
    service.close()

    print("\n✅ Pilot test complete!")

    # Return exit code
    return 0 if len(successful) == len(results) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
