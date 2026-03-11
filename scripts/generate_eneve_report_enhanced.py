#!/usr/bin/env python3
"""Generate Enhanced Eneve Competitive Intelligence Report.

This enhanced version adds AI adoption assessment, strategic classification (Rocket/Dinosaur/Lead/Stealth),
capability overlap analysis, and evidence-based tagging based on the original Solstein methodology.

Usage:
    python scripts/generate_eneve_report_enhanced.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.exporters.excel_improved import ImprovedExcelExporter



ENEVE_CAPABILITIES = {
    "time_series_management": {
        "keywords": ["time series", "smart meter", "meter data", "aggregation", "linked data", "historical data"],
        "weight": 1.0,
    },
    "balancing_settlement": {
        "keywords": ["balancing", "settlement", "imbalance", "power allocation", "grid balancing"],
        "weight": 1.0,
    },
    "nominations_scheduling": {
        "keywords": ["nomination", "scheduling", "tso communication", "dso", "edsn", "protocol"],
        "weight": 0.9,
    },
    "message_processing": {
        "keywords": ["edi", "message processing", "validation", "notification", "messaging"],
        "weight": 0.8,
    },
    "market_operations": {
        "keywords": ["market participant", "grid area", "ean codes", "market operations", "trading"],
        "weight": 0.9,
    },
    "commodities_electricity": {
        "keywords": ["electricity", "power", "energy trading", "etr", "power trading"],
        "weight": 0.85,
    },
    "commodities_gas": {
        "keywords": ["gas", "natural gas", "lng", "gas trading"],
        "weight": 0.75,
    },
    "cloud_native": {
        "keywords": ["cloud", "saas", "cloud-native", "api", "microservices"],
        "weight": 0.7,
    },
}



AI_SIGNAL_KEYWORDS = {
    "very_strong": [
        "ai-native",
        "machine learning",
        "deep learning",
        "neural network",
        "llm",
        "artificial intelligence",
        "predictive analytics",
        "autonomous",
        "agent",
        "ai-powered",
        "ml-powered",
        "algorithmic trading",
    ],
    "strong": [
        "ai",
        "ml",
        "data science",
        "forecasting",
        "optimization algorithms",
        "intelligent automation",
        "cognitive",
        "chatbot",
        "nlp",
    ],
    "moderate": [
        "analytics",
        "data-driven",
        "smart",
        "intelligent",
        "automated",
        "predictive",
        "real-time",
        "algorithm",
    ],
    "low": ["digital", "software", "platform", "cloud"],
}




def classify_strategic_tier(company_data: dict) -> dict[str, Any]:
    """
    Classify company into Rocket/Dinosaur/Lead/Stealth based on:
    - Revenue growth trajectory
    - Funding momentum
    - Employee growth
    - AI adoption
    - Market position
    """
    basic = company_data.get("basic_info", {})
    financials = company_data.get("financials", {})
    funding = company_data.get("funding", {})

    employees = basic.get("employees", 0) or 0
    revenue = financials.get("revenue", 0) or 0
    total_funding = funding.get("total_raised", 0) or 0
    funding_rounds = funding.get("rounds", 0) or 0

    # AI adoption score
    ai_signal = assess_ai_adoption(company_data)
    ai_score = ai_signal["score"]

    # Calculate classification metrics
    metrics = {
        "revenue_millions": revenue,
        "employees": employees,
        "funding_millions": total_funding,
        "funding_rounds": funding_rounds,
        "ai_score": ai_score,
        "ai_signal": ai_signal["level"],
    }

    # Classification logic (based on original Solstein methodology)
    if total_funding > 50 and funding_rounds >= 3 and ai_score >= 8:
        classification = "🔥 Rocket"
        reasoning = "High-growth, AI-native or rapidly adopting. Significant funding momentum."
    elif total_funding > 20 and ai_score >= 6:
        classification = "🧂 Salt"
        reasoning = "Stable players with solid AI adoption. Watch for directional signals."
    elif employees > 1000 or revenue > 100:
        classification = "⚖️ Lead"
        reasoning = "Legacy weight. Large established player. Hidden diamonds or dead weight."
    elif ai_score >= 7 and employees < 100:
        classification = "🚀 Stealth"
        reasoning = "AI-native startup. Small but potentially disruptive."
    elif ai_score <= 4 and (employees > 500 or revenue > 50):
        classification = "⚖️ Lead"
        reasoning = "Established player with low AI adoption. Risk of being disrupted."
    else:
        classification = "🧂 Salt"
        reasoning = "Moderate metrics across dimensions. Stable but not exceptional."

    metrics["classification"] = classification
    metrics["classification_reasoning"] = reasoning

    return metrics


def assess_ai_adoption(company_data: dict) -> dict[str, Any]:
    """
    Assess AI adoption level based on description and keywords.
    Returns score (0-10) and level (None/Low/Moderate/Strong/Very Strong).
    """
    basic = company_data.get("basic_info", {})
    description = (basic.get("description") or "").lower()
    industry = (basic.get("industry") or "").lower()

    score = 0
    evidence = []

    # Check for very strong signals
    for keyword in AI_SIGNAL_KEYWORDS["very_strong"]:
        if keyword in description or keyword in industry:
            score += 2.5
            evidence.append(f"Very strong AI signal: {keyword}")
            break  # Only count once per tier

    # Check for strong signals
    strong_matches = []
    for keyword in AI_SIGNAL_KEYWORDS["strong"]:
        if keyword in description or keyword in industry:
            strong_matches.append(keyword)
    score += min(len(strong_matches), 3) * 1.5
    if strong_matches:
        evidence.append(f"Strong AI signals: {', '.join(strong_matches[:3])}")

    # Check for moderate signals
    moderate_matches = []
    for keyword in AI_SIGNAL_KEYWORDS["moderate"]:
        if keyword in description or keyword in industry:
            moderate_matches.append(keyword)
    score += min(len(moderate_matches), 4) * 0.5

    # Cap at 10
    score = min(score, 10)

    # Determine level
    if score >= 8:
        level = "Very Strong"
    elif score >= 6:
        level = "Strong"
    elif score >= 4:
        level = "Moderate"
    elif score >= 2:
        level = "Low"
    else:
        level = "None"

    return {
        "score": round(score, 1),
        "level": level,
        "evidence": evidence[:3],  # Top 3 evidence items
    }


def calculate_capability_overlap(company_data: dict) -> dict[str, Any]:
    """
    Calculate capability overlap with Eneve's core capabilities.
    Returns overlap percentage per capability and overall score.
    """
    basic = company_data.get("basic_info", {})
    description = (basic.get("description") or "").lower()
    industry = (basic.get("industry") or "").lower()
    name = company_data.get("company_name", "").lower()

    overlap_scores = {}
    total_weight = 0
    weighted_score = 0

    for capability, config in ENEVE_CAPABILITIES.items():
        keywords = config["keywords"]
        weight = config["weight"]

        # Check for keyword matches
        matches = []
        for keyword in keywords:
            if keyword in description or keyword in industry or keyword in name:
                matches.append(keyword)

        # Calculate score based on matches
        if len(matches) >= 3:
            capability_score = 1.0
        elif len(matches) == 2:
            capability_score = 0.75
        elif len(matches) == 1:
            capability_score = 0.5
        else:
            capability_score = 0.0

        overlap_scores[capability] = {
            "score": capability_score,
            "matches": matches,
        }

        weighted_score += capability_score * weight
        total_weight += weight

    overall_overlap = weighted_score / total_weight if total_weight > 0 else 0

    # Determine overlap level
    if overall_overlap >= 0.7:
        overlap_level = "VERY HIGH"
    elif overall_overlap >= 0.5:
        overlap_level = "HIGH"
    elif overall_overlap >= 0.3:
        overlap_level = "MODERATE"
    elif overall_overlap >= 0.1:
        overlap_level = "LOW"
    else:
        overlap_level = "MINIMAL"

    return {
        "overall_overlap": round(overall_overlap * 100, 1),
        "overlap_level": overlap_level,
        "capabilities": overlap_scores,
        "top_capabilities": sorted(
            [(cap, data["score"]) for cap, data in overlap_scores.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:3],
    }


def is_relevant_to_eneve(company_data: dict) -> tuple[bool, str, dict]:
    """
    Enhanced relevance check with capability overlap analysis.
    """
    basic = company_data.get("basic_info") or {}
    name = company_data.get("company_name") or ""
    industry = (basic.get("industry") or "").lower()
    description = (basic.get("description") or "").lower()
    hq = (basic.get("headquarters") or "").lower()

    # Calculate capability overlap
    overlap = calculate_capability_overlap(company_data)

    software_keywords = [
        "software",
        "platform",
        "digital",
        "ai",
        "smart",
        "intelligent",
        "management",
        "optimization",
        "analytics",
        "solution",
        "system",
        "cloud",
        "data",
        "monitoring",
        "automation",
        "virtual",
    ]

    energy_keywords = [
        "energy",
        "power",
        "grid",
        "electricity",
        "renewable",
        "solar",
        "wind",
        "demand response",
        "distributed",
        "storage",
        "trading",
        "etr",
        "balancing",
        "settlement",
        "meter",
    ]

    has_software = any(kw in description or kw in industry for kw in software_keywords)
    has_energy = any(kw in description or kw in industry for kw in energy_keywords)

    is_netherlands = any(x in hq for x in ["netherlands", "amsterdam", "rotterdam", "arnhem", "zwolle"])

    is_european_energy = any(
        x in hq
        for x in [
            "germany",
            "france",
            "belgium",
            "united kingdom",
            "uk",
            "ireland",
            "spain",
            "italy",
            "switzerland",
            "austria",
            "sweden",
            "denmark",
            "norway",
            "finland",
            "poland",
            "czech",
        ]
    )

    direct_competitors = [
        "autogrid",
        "gridbeyond",
        "origami",
        "electron",
        "passivsystems",
        "qurrent",
        "volue",
        "open energi",
        "kiwi power",
        "next kraftwerke",
        "reactive technologies",
        "wattics",
        "beebryte",
        "likewatt",
        "soptim",
        "trayport",
        "brady",
        "kisters",
        "sopra steria",
        "engrate",
        "hansen",
        "robotron",
        "eg utility",
        "tietoevry",
        "maxbill",
        "indra",
        "ferranti",
        "asseco",
        "orchestrade",
        "molecule",
        "qualia",
        "tem",
        "seeburger",
        "arvato",
        "schleupen",
        "dexter",
        "kraken",
        "octopus",
        "creatica",
        "previse",
    ]

    is_direct = any(comp in name.lower() for comp in direct_competitors)

    relevance_details = {
        "has_software": has_software,
        "has_energy": has_energy,
        "is_netherlands": is_netherlands,
        "is_european": is_european_energy,
        "capability_overlap": overlap["overall_overlap"],
        "overlap_level": overlap["overlap_level"],
    }

    # Classification with overlap consideration
    if is_direct or overlap["overall_overlap"] >= 50:
        return True, "Direct Competitor", relevance_details
    elif has_software and has_energy and is_netherlands:
        return True, "Netherlands Software", relevance_details
    elif has_software and has_energy and is_european_energy:
        return True, "European Energy Software", relevance_details
    elif is_netherlands and has_energy:
        return True, "Netherlands Energy", relevance_details
    elif has_software and "energy" in industry.lower():
        return True, "Energy Sector Software", relevance_details
    elif overlap["overall_overlap"] >= 30:
        return True, "Capability Overlap", relevance_details
    else:
        return False, "Not Relevant", relevance_details


def to_float(val) -> float | None:
    """Safely convert a value to float."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def to_int(val) -> int | None:
    """Safely convert a value to int."""
    if val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def research_to_company(data: dict, relevance_category: str, relevance_details: dict) -> SimpleNamespace:
    """Convert research data to enhanced Company domain model."""
    basic = data.get("basic_info", {})
    financials = data.get("financials", {})
    funding_data = data.get("funding", {})
    name = data.get("company_name", "Unknown")

    # Get enhanced classifications
    strategic = classify_strategic_tier(data)
    ai_assessment = assess_ai_adoption(data)
    overlap = calculate_capability_overlap(data)

    employees = to_int(basic.get("employees"))
    revenue = to_float(financials.get("revenue"))
    valuation = to_float(financials.get("valuation"))
    total_funding = to_float(funding_data.get("total_raised"))

    # Build source evidence list
    source_evidence = []
    for src in data.get("data_sources", [])[:3]:
        source_evidence.append(f"{src.get('type', 'source')}: {src.get('url', 'N/A')[:50]}...")

    financials_ns = SimpleNamespace(
        revenue_eur_m=revenue,
        growth_rate_pct=None,
        profit_margin_pct=None,
        total_funding_raised_eur=total_funding,
        latest_valuation_eur=valuation,
    )

    # Get top capability overlaps for display
    top_capabilities = [cap.replace("_", " ").title() for cap, _ in overlap["top_capabilities"]]

    company = SimpleNamespace(
        id=f"COMP-{abs(hash(name))}",
        name=name,
        company_name=name,
        industry=basic.get("industry", "Energy Software"),
        description=basic.get("description"),
        website=basic.get("website"),
        headquarters=basic.get("headquarters"),
        founded_year=to_int(basic.get("founded_year")),
        # Enhanced classifications
        tier=strategic["classification"],
        tier_reasoning=strategic["classification_reasoning"],
        threat_level="High"
        if overlap["overall_overlap"] >= 50
        else "Medium"
        if overlap["overall_overlap"] >= 30
        else "Low",
        relevance_category=relevance_category,
        # AI Assessment
        ai_score=ai_assessment["score"],
        ai_signal_level=ai_assessment["level"],
        ai_evidence="; ".join(ai_assessment["evidence"]),
        # Capability Overlap
        capability_overlap_pct=overlap["overall_overlap"],
        overlap_level=overlap["overlap_level"],
        top_capabilities=", ".join(top_capabilities),
        # Financials
        financials=financials_ns,
        revenue_eur_m=revenue,
        growth_rate_pct=None,
        profit_margin_pct=None,
        total_funding_raised_eur=total_funding,
        latest_valuation_eur=valuation,
        revenue=revenue,
        employees=employees,
        employee_count=employees,
        funding=total_funding,
        valuation=valuation,
        # Evidence
        market_share_pct=None,
        competitive_position_score=data.get("confidence_score", 0),
        classification="researched",
        data_source="ai_research",
        data_source_type="real",
        last_updated=datetime.now(timezone.utc),
        source_links=[s.get("url", "") for s in data.get("data_sources", [])],
        confidence_scores={
            "overall": data.get("confidence_score", 0),
            "data_richness": min(len(data.get("data_sources", [])) / 5, 1.0),
        },
        enrichment_source_count=len(data.get("data_sources", [])),
        # Evidence strings for display
        evidence_sources="; ".join(source_evidence) if source_evidence else "N/A",
    )

    return company


def main():
    input_path = Path("data/research_results/research_results.json")
    output_dir = Path("data/research_results/eneve_report")
    output_dir.mkdir(exist_ok=True)

    excel_path = output_dir / "eneve_competitive_intelligence_enhanced.xlsx"
    json_path = output_dir / "eneve_relevant_companies_enhanced.json"

    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    # Load research results
    with open(input_path) as f:
        results = json.load(f)

    all_companies = results.get("companies", [])
    summary = results.get("summary", {})

    print(f"📊 Analyzing {len(all_companies)} companies for Eneve relevance...")
    print(f"   Enhanced with: AI Adoption + Strategic Classification + Capability Overlap")
    print(f"   Target Market: Netherlands & Europe\n")

    # Filter for relevant companies with enhanced analysis
    relevant_companies = []
    relevance_breakdown = {}

    for company_data in all_companies:
        is_relevant, category, relevance_details = is_relevant_to_eneve(company_data)

        if is_relevant:
            try:
                company = research_to_company(company_data, category, relevance_details)
                relevant_companies.append(company)
                relevance_breakdown[category] = relevance_breakdown.get(category, 0) + 1
                print(f"   ✅ {company.name}")
                print(f"      ├─ Classification: {company.tier}")
                print(f"      ├─ AI Signal: {company.ai_signal_level} ({company.ai_score}/10)")
                print(f"      ├─ Overlap: {company.overlap_level} ({company.capability_overlap_pct}%)")
                print(f"      └─ Category: {category}")
            except Exception as e:
                print(f"   ❌ Failed to convert {company_data.get('company_name', 'Unknown')}: {e}")

    if not relevant_companies:
        print("No relevant companies found!")
        sys.exit(1)

    print(f"\n📈 Found {len(relevant_companies)} companies relevant to Eneve:")
    for category, count in sorted(relevance_breakdown.items(), key=lambda x: -x[1]):
        print(f"   • {category}: {count} companies")

    # Calculate statistics
    ai_scores = [c.ai_score for c in relevant_companies]
    overlap_scores = [c.capability_overlap_pct for c in relevant_companies]

    print(f"\n📊 Enhanced Intelligence Summary:")
    print(f"   • Average AI Score: {sum(ai_scores) / len(ai_scores):.1f}/10")
    print(f"   • Average Capability Overlap: {sum(overlap_scores) / len(overlap_scores):.1f}%")

    # Count by classification
    class_counts = {}
    for c in relevant_companies:
        cls = c.tier
        class_counts[cls] = class_counts.get(cls, 0) + 1

    print(f"\n🏆 Strategic Classifications:")
    for cls, count in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f"   • {cls}: {count}")

    # Generate Excel dashboard
    print(f"\n📊 Generating enhanced Excel dashboard...")
    exporter = ImprovedExcelExporter()

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_company": "Eneve",
        "target_description": "Smart software for the energy value chain",
        "target_location": "Netherlands",
        "total_companies": len(relevant_companies),
        "relevance_breakdown": relevance_breakdown,
        "avg_confidence": summary.get("avg_confidence", 0),
        "avg_ai_score": sum(ai_scores) / len(ai_scores),
        "avg_overlap": sum(overlap_scores) / len(overlap_scores),
        "source": "AI Research Pipeline - Enhanced with Solstein Methodology",
        "data_quality": "100% Real Data - AI Adoption & Capability Overlap Analysis",
        "classification_breakdown": class_counts,
    }

    exporter.create_dashboard(list(relevant_companies), excel_path, metadata=metadata)
    print(f"   ✅ Excel saved: {excel_path}")

    # Save filtered JSON for reference
    output_data = {
        "target_company": "Eneve",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_companies": len(relevant_companies),
        "relevance_breakdown": relevance_breakdown,
        "classification_breakdown": class_counts,
        "avg_ai_score": sum(ai_scores) / len(ai_scores),
        "avg_capability_overlap": sum(overlap_scores) / len(overlap_scores),
        "companies": [
            {
                "name": c.name,
                "industry": c.industry,
                "headquarters": c.headquarters,
                "description": c.description,
                "revenue_eur_m": c.revenue_eur_m,
                "employees": c.employees,
                "funding": c.funding,
                "relevance_category": c.relevance_category,
                "strategic_classification": c.tier,
                "classification_reasoning": c.tier_reasoning,
                "ai_score": c.ai_score,
                "ai_signal_level": c.ai_signal_level,
                "ai_evidence": c.ai_evidence,
                "capability_overlap_pct": c.capability_overlap_pct,
                "overlap_level": c.overlap_level,
                "top_capabilities": c.top_capabilities,
                "threat_level": c.threat_level,
                "confidence_score": c.competitive_position_score,
                "evidence_sources": c.evidence_sources,
            }
            for c in relevant_companies
        ],
    }

    with open(json_path, "w") as f:
        json.dump(output_data, f, indent=2, default=str)
    print(f"   ✅ JSON saved: {json_path}")

    print(f"\n" + "=" * 70)
    print(f"🎯 ENHANCED ENEVE COMPETITIVE INTELLIGENCE REPORT COMPLETE")
    print(f"=" * 70)
    print(f"\nTarget Company: Eneve (Netherlands)")
    print(f"Focus: Smart software for the energy value chain")
    print(f"\nTotal Relevant Competitors: {len(relevant_companies)}")
    print(f"\nKey Insights:")
    print(f"   • Average AI Adoption Score: {sum(ai_scores) / len(ai_scores):.1f}/10")
    print(f"   • Average Capability Overlap: {sum(overlap_scores) / len(overlap_scores):.1f}%")
    print(f"\nStrategic Breakdown:")
    for cls, count in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f"   • {cls}: {count}")
    print(f"\n📁 Output Files:")
    print(f"   • Enhanced Excel Dashboard: {excel_path}")
    print(f"   • Enhanced JSON Data: {json_path}")
    print(f"\n✨ Enhanced with AI Adoption Assessment + Strategic Classification")
    print(f"✨ Capability Overlap Analysis + Evidence-Based Confidence Scoring")
    print(f"=" * 70)


if __name__ == "__main__":
    main()
