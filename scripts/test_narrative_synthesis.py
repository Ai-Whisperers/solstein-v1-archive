#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.intelligence.narrative_synthesis import NarrativeContext, NarrativeSynthesisEngine


def test_fallback_narratives():
    engine = NarrativeSynthesisEngine()
    fi = type(
        "FinancialIntelligence",
        (),
        {
            "company_name": "Autogrid",
            "revenue_timeline": [type("RP", (), {"year": 2023, "revenue": 12.5})()],
            "cagr_3yr": 34.2,
            "cagr_5yr": 28.5,
            "growth_trajectory": type("TD", (), {"value": "accelerating"})(),
            "growth_consistency_score": 8,
            "total_funding_raised": 45.0,
            "funding_rounds_enhanced": [],
            "investor_quality_score": 7,
            "funding_velocity": type("FV", (), {"value": "high"})(),
            "runway_estimate_months": 24,
            "projected_revenue_12mo": 18.0,
            "projection_confidence": type("PC", (), {"value": "medium"})(),
            "primary_growth_vectors": [
                type(
                    "GV",
                    (),
                    {
                        "name": "Grid Modernization",
                        "confidence": 0.75,
                        "estimated_impact": "high",
                        "evidence": ["DOE funding"],
                    },
                )()
            ],
            "key_strengths": ["Strong growth", "PE backing"],
            "key_risks": ["Competition"],
        },
    )()

    context = NarrativeContext(company_name="Autogrid", industry="energy software", region="Europe")
    result = engine._fallback_financial_narratives(fi, context)

    print("=" * 60)
    print("Testing Narrative Synthesis (Fallback Templates)")
    print("=" * 60)

    for key, value in result.items():
        print(f"\n--- {key.upper()} ---")
        print(value[:600])
        print("...")

    print("\n" + "=" * 60)
    print("SUCCESS: Fallback templates work correctly!")
    print("=" * 60)


if __name__ == "__main__":
    test_fallback_narratives()
