#!/usr/bin/env python3
"""
Integrate batch research results into main research_results.json
"""

import json
from pathlib import Path
from datetime import datetime


def integrate_research_results(
    batch_results_path: str, main_results_path: str = "data/research_results/research_results.json"
):
    """Integrate batch research results into main results file."""

    batch_path = Path(batch_results_path)
    main_path = Path(main_results_path)

    # Load batch results
    with open(batch_path) as f:
        batch_data = json.load(f)

    batch_companies = batch_data.get("companies", [])
    print(f"📊 Loaded {len(batch_companies)} companies from batch results")

    # Load existing main results or create new
    if main_path.exists():
        with open(main_path) as f:
            main_data = json.load(f)
        print(f"📂 Loaded existing main results with {len(main_data.get('companies', []))} companies")
    else:
        main_data = {"companies": [], "metadata": {}}
        print("📂 Creating new main results file")

    # Create lookup by company name
    existing_companies = {c.get("company_name", "").lower(): c for c in main_data.get("companies", [])}

    # Merge batch results
    integrated_count = 0
    updated_count = 0
    skipped_count = 0

    for company in batch_companies:
        name = company.get("company_name", "").lower()

        if not name:
            skipped_count += 1
            continue

        # Check if company already exists
        if name in existing_companies:
            existing = existing_companies[name]
            # Only update if new data has higher confidence
            new_conf = company.get("confidence_score", 0)
            old_conf = existing.get("confidence_score", 0)

            if new_conf > old_conf:
                existing_companies[name] = company
                updated_count += 1
            else:
                skipped_count += 1
        else:
            existing_companies[name] = company
            integrated_count += 1

    # Convert back to list
    main_data["companies"] = list(existing_companies.values())

    # Update metadata
    main_data["metadata"] = {
        "last_updated": datetime.now().isoformat(),
        "total_companies": len(main_data["companies"]),
        "batch_integration": {
            "timestamp": datetime.now().isoformat(),
            "source": str(batch_path),
            "integrated": integrated_count,
            "updated": updated_count,
            "skipped": skipped_count,
        },
    }

    # Save updated results
    main_path.parent.mkdir(parents=True, exist_ok=True)
    with open(main_path, "w") as f:
        json.dump(main_data, f, indent=2)

    print(f"\n✅ Integration complete:")
    print(f"   • New companies added: {integrated_count}")
    print(f"   • Existing companies updated: {updated_count}")
    print(f"   • Skipped (lower confidence): {skipped_count}")
    print(f"   • Total in main results: {len(main_data['companies'])}")
    print(f"\n💾 Results saved to: {main_path}")

    return main_data


def main():
    import sys

    if len(sys.argv) > 1:
        batch_path = sys.argv[1]
    else:
        batch_path = "data/research_results/batch_200/research_results.json"

    path = Path(batch_path)
    if not path.exists():
        print(f"❌ Batch results not found: {batch_path}")
        print("   Run batch research first or check the path")
        sys.exit(1)

    print(f"🔧 Integrating batch results from: {batch_path}")
    integrate_research_results(batch_path)


if __name__ == "__main__":
    main()
