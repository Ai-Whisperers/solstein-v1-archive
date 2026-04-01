#!/usr/bin/env python3
"""
Validate research results for real vs synthetic data.
Run this after batch research completes.
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def validate_research_results(results_path: str) -> dict:
    """Validate research results and report on real vs synthetic data."""

    with open(results_path) as f:
        data = json.load(f)

    companies = data.get("companies", [])
    errors = data.get("errors", [])
    data.get("summary", {})

    # Categorize companies
    real_companies = []
    synthetic_companies = []
    low_confidence = []

    for company in companies:
        is_synthetic = company.get("is_synthetic", True)
        confidence = company.get("confidence_score", 0)
        name = company.get("company_name", "Unknown")

        if is_synthetic:
            synthetic_companies.append({"name": name, "confidence": confidence, "reason": "Marked as synthetic"})
        elif confidence < 0.3:
            low_confidence.append({"name": name, "confidence": confidence, "reason": "Low confidence score"})
        else:
            real_companies.append(
                {"name": name, "confidence": confidence, "sources": len(company.get("data_sources", []))}
            )

    # Calculate statistics
    total = len(companies)
    real_count = len(real_companies)
    synthetic_count = len(synthetic_companies)
    low_conf_count = len(low_confidence)

    real_percentage = (real_count / total * 100) if total > 0 else 0

    # Confidence distribution
    confidence_scores = [c.get("confidence_score", 0) for c in companies]
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

    confidence_distribution = Counter()
    for score in confidence_scores:
        if score >= 0.7:
            confidence_distribution["high (>=0.7)"] += 1
        elif score >= 0.4:
            confidence_distribution["medium (0.4-0.7)"] += 1
        else:
            confidence_distribution["low (<0.4)"] += 1

    report = {
        "validation_timestamp": datetime.now().isoformat(),
        "summary": {
            "total_companies": total,
            "real_data_count": real_count,
            "synthetic_data_count": synthetic_count,
            "low_confidence_count": low_conf_count,
            "errors_count": len(errors),
            "real_data_percentage": round(real_percentage, 2),
            "average_confidence": round(avg_confidence, 3),
        },
        "confidence_distribution": dict(confidence_distribution),
        "real_companies": real_companies[:20],  # Top 20
        "synthetic_companies": synthetic_companies[:20],  # Top 20 problematic
        "low_confidence_companies": low_confidence[:20],
        "errors": errors[:10],  # First 10 errors
    }

    return report


def print_validation_report(report: dict):
    """Print formatted validation report."""

    print("\n" + "=" * 70)
    print(" RESEARCH RESULTS VALIDATION REPORT")
    print("=" * 70)

    summary = report["summary"]
    print("\n📊 OVERVIEW")
    print(f"   Total Companies: {summary['total_companies']}")
    print(f"   ✅ Real Data: {summary['real_data_count']} ({summary['real_data_percentage']}%)")
    print(f"   ⚠️  Synthetic Data: {summary['synthetic_data_count']}")
    print(f"   ⚠️  Low Confidence: {summary['low_confidence_count']}")
    print(f"   ❌ Errors: {summary['errors_count']}")
    print(f"   📈 Average Confidence: {summary['average_confidence']}")

    print("\n📊 CONFIDENCE DISTRIBUTION")
    for category, count in report["confidence_distribution"].items():
        print(f"   {category}: {count}")

    if report["real_companies"]:
        print("\n✅ TOP REAL DATA COMPANIES (by confidence)")
        sorted_real = sorted(report["real_companies"], key=lambda x: x["confidence"], reverse=True)
        for company in sorted_real[:10]:
            print(f"   • {company['name']}: {company['confidence']:.2f} ({company['sources']} sources)")

    if report["synthetic_companies"]:
        print("\n⚠️  SYNTHETIC DATA COMPANIES")
        for company in report["synthetic_companies"][:10]:
            print(f"   • {company['name']}: {company['confidence']:.2f}")

    if report["low_confidence_companies"]:
        print("\n⚠️  LOW CONFIDENCE COMPANIES")
        for company in report["low_confidence_companies"][:10]:
            print(f"   • {company['name']}: {company['confidence']:.2f}")

    if report["errors"]:
        print("\n❌ SAMPLE ERRORS")
        for error in report["errors"][:5]:
            print(f"   • {error.get('company', 'Unknown')}: {error.get('error', 'Unknown error')[:80]}")

    print("\n" + "=" * 70)

    # Quality assessment
    real_pct = summary["real_data_percentage"]
    if real_pct >= 80:
        print("🟢 QUALITY ASSESSMENT: EXCELLENT (>80% real data)")
    elif real_pct >= 60:
        print("🟡 QUALITY ASSESSMENT: GOOD (60-80% real data)")
    elif real_pct >= 40:
        print("🟠 QUALITY ASSESSMENT: FAIR (40-60% real data)")
    else:
        print("🔴 QUALITY ASSESSMENT: POOR (<40% real data)")
        print("   Consider: Adding more data sources, improving search queries,")
        print("   or checking API rate limits")

    print("=" * 70 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        results_path = sys.argv[1]
    else:
        results_path = "data/research_results/batch_200/research_results.json"

    path = Path(results_path)
    if not path.exists():
        print(f"❌ Results file not found: {results_path}")
        print("   Research may still be in progress...")
        sys.exit(1)

    print(f"🔍 Validating research results from: {results_path}")

    try:
        report = validate_research_results(results_path)
        print_validation_report(report)

        # Save detailed report
        report_path = path.parent / "validation_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"💾 Detailed report saved to: {report_path}")

        # Exit with error code if quality is poor
        if report["summary"]["real_data_percentage"] < 40:
            sys.exit(2)

    except json.JSONDecodeError:
        print("❌ Invalid JSON in results file - research may still be in progress")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
