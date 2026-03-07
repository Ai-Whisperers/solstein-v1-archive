#!/usr/bin/env python3
"""
Demo script for Evidence Graph System.

This script demonstrates the complete evidence pipeline:
1. Initialize infrastructure (Neo4j + Qdrant)
2. Crawl a company website
3. Extract claims
4. Store in graph and vector database
5. Search and retrieve evidence

Usage:
    python demo_evidence.py

Requirements:
    - Docker running with Neo4j, Qdrant, Redis
    - Virtual environment activated
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.evidence import (
    EvidenceService,
    get_evidence_service,
    ClaimStatus,
    create_claim,
    SourceType,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def demo():
    """Run the evidence system demo."""

    print("=" * 60)
    print("SOLSTEIN EVIDENCE GRAPH SYSTEM - DEMO")
    print("=" * 60)
    print()

    # Initialize service
    print("1. Initializing Evidence Service...")
    service = get_evidence_service()
    service.initialize()
    print("   ✅ Service initialized")
    print()

    # Research a company
    company_id = "demo-company-001"
    website_url = "https://example.com"  # Replace with real URL for actual demo

    print(f"2. Researching company: {company_id}")
    print(f"   Website: {website_url}")
    print()

    # Note: For demo purposes, we'll create synthetic claims
    # In production, this would crawl the actual website
    print("   (Using synthetic claims for demo)")

    # Create synthetic claims
    claims = [
        create_claim(
            entity_id=company_id,
            field="revenue",
            value="$10M",
            source_url=f"{website_url}/about",
            snippet="Our revenue reached $10M in 2024",
            source_type=SourceType.WEBSITE,
            extraction_method="demo",
        ),
        create_claim(
            entity_id=company_id,
            field="employee_count",
            value="150",
            source_url=f"{website_url}/careers",
            snippet="Join our team of 150 employees",
            source_type=SourceType.WEBSITE,
            extraction_method="demo",
        ),
        create_claim(
            entity_id=company_id,
            field="headquarters",
            value="San Francisco, CA",
            source_url=f"{website_url}/contact",
            snippet="Our headquarters is in San Francisco",
            source_type=SourceType.WEBSITE,
            extraction_method="demo",
        ),
        create_claim(
            entity_id=company_id,
            field="founded_year",
            value="2019",
            source_url=f"{website_url}/about",
            snippet="Founded in 2019",
            source_type=SourceType.WEBSITE,
            extraction_method="demo",
        ),
        # Add a conflicting claim for demonstration
        create_claim(
            entity_id=company_id,
            field="revenue",
            value="$12M",
            source_url=f"{website_url}/press",
            snippet="Annual revenue of $12M",
            source_type=SourceType.PRESS_RELEASE,
            extraction_method="demo",
        ),
    ]

    # Set confidence scores
    for i, claim in enumerate(claims):
        claim.overall_confidence = 0.7 + (i * 0.05)
        if claim.overall_confidence > 1.0:
            claim.overall_confidence = 0.95

    print(f"   Created {len(claims)} synthetic claims")
    print()

    # Store claims
    print("3. Storing claims in evidence graph...")
    for claim in claims:
        service.graph.create_claim(claim)
        service.vector_store.index_claim(claim)
    print(f"   ✅ Stored {len(claims)} claims")
    print()

    # Detect contradictions
    print("4. Detecting contradictions...")
    contradictions = service._detect_contradictions(company_id)
    print(f"   Found {len(contradictions)} contradictions:")
    for con in contradictions:
        print(f"     - Field: {con['field']}")
        print(f"       Values: {con['values']}")
        print(f"       Severity: {con['severity']}")
    print()

    # Calculate evidence readiness
    print("5. Calculating evidence readiness...")
    readiness = service.calculate_evidence_readiness(company_id)
    print(f"   Total claims: {readiness.total_claims}")
    print(f"   Avg confidence: {readiness.avg_confidence:.2f}")
    print(f"   Readiness level: {readiness.level}")
    print()

    # Retrieve claims
    print("6. Retrieving claims from graph...")
    stored_claims = service.get_claims(company_id)
    print(f"   Retrieved {len(stored_claims)} claims:")
    for claim in stored_claims[:5]:
        print(
            f"     - {claim.get('field')}: {claim.get('value')} (confidence: {claim.get('overall_confidence', 0):.2f})"
        )
    print()

    # Search claims
    print("7. Searching claims semantically...")
    search_results = service.search_claims(
        query="company revenue financial",
        company_id=company_id,
        limit=5,
    )
    print(f"   Found {len(search_results)} matching claims:")
    for result in search_results:
        print(f"     - {result['field']}: {result['value']} (similarity: {result['similarity_score']:.2f})")
    print()

    # Get evidence lineage
    if stored_claims:
        print("8. Getting evidence lineage...")
        first_claim_id = stored_claims[0].get("id")
        lineage = service.get_evidence_lineage(first_claim_id)
        print(f"   Claim: {lineage.get('claim', {}).get('field')}")
        print(f"   Source: {lineage.get('source', {}).get('url')}")
        print()

    # Summary
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  - Claims created: {len(claims)}")
    print(f"  - Claims stored: {len(stored_claims)}")
    print(f"  - Contradictions detected: {len(contradictions)}")
    print(f"  - Evidence readiness: {readiness.level}")
    print()
    print("Infrastructure:")
    print("  - Neo4j: http://localhost:7474")
    print("  - Qdrant: http://localhost:6333")
    print()
    print("Next steps:")
    print("  1. Open Neo4j Browser to explore the graph")
    print("  2. Run real crawls on actual company websites")
    print("  3. Implement LLM-based claim extraction")
    print("  4. Add more source types (news, filings, etc.)")
    print()

    # Cleanup
    service.close()
    print("✅ Demo finished successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise
