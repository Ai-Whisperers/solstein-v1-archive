import json
from pathlib import Path

from solstein.analytics.scoring import GrowthScorer
from solstein.domain.models import Company, MarketAnalysis
from solstein.exporters.excel import ExcelExporter
from solstein.extractors.markdown_extractor import BatchExtractor

from .discovery import DiscoveryCandidate, discover_companies
from .evidence import evaluate_market_evidence
from .gather import build_company_profile
from .reconcile import detect_market_contradictions


def run_market_intelligence(
    seed_company: str,
    market: str,
    output_dir: Path,
    max_companies: int = 25,
    extra_keywords: list[str] | None = None,
    strict_provenance: bool = True,
    min_readiness_score: float | None = None,
    max_contradictions: int | None = None,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates: list[DiscoveryCandidate] = discover_companies(
        seed_company=seed_company,
        market=market,
        max_companies=max_companies,
        extra_keywords=extra_keywords,
    )

    discovery_payload = [
        {
            "company_id": c.company_id,
            "name": c.name,
            "market": c.market,
            "ticker": c.ticker,
            "industry": c.industry,
            "region": c.region,
            "tags": c.tags,
            "seed_relevance": c.seed_relevance,
            "discovery_reason": c.discovery_reason,
            "source_links": c.source_links,
        }
        for c in candidates
    ]
    (output_dir / "discovery_candidates.json").write_text(
        json.dumps(discovery_payload, indent=2),
        encoding="utf-8",
    )

    companies: list[Company] = [build_company_profile(candidate) for candidate in candidates]

    extracted_path = output_dir / "extracted.json"
    extracted_path.write_text(
        json.dumps([company.model_dump(mode="json") for company in companies], indent=2),
        encoding="utf-8",
    )

    validator = BatchExtractor()
    violations = validator.validate_profiles_provenance(companies)
    (output_dir / "provenance_report.json").write_text(
        json.dumps(violations, indent=2),
        encoding="utf-8",
    )
    if strict_provenance and violations:
        raise RuntimeError(
            f"Provenance validation failed for {len(violations)} companies"
        )

    contradiction_report = detect_market_contradictions(companies)
    (output_dir / "contradictions_report.json").write_text(
        json.dumps(contradiction_report, indent=2),
        encoding="utf-8",
    )

    if max_contradictions is not None:
        total_contradictions = sum(
            len(items) for items in contradiction_report.values() if isinstance(items, list)
        )
        if total_contradictions > max_contradictions:
            raise RuntimeError(
                f"Detected {total_contradictions} contradictions, above threshold {max_contradictions}"
            )

    evidence_report = evaluate_market_evidence(companies)
    (output_dir / "evidence_readiness.json").write_text(
        json.dumps(evidence_report, indent=2),
        encoding="utf-8",
    )

    if min_readiness_score is not None:
        avg_readiness_raw = evidence_report.get("average_readiness_score", 0.0)
        if isinstance(avg_readiness_raw, float):
            avg_readiness = avg_readiness_raw
        elif isinstance(avg_readiness_raw, int):
            avg_readiness = avg_readiness_raw * 1.0
        else:
            avg_readiness = 0.0
        if avg_readiness < min_readiness_score:
            raise RuntimeError(
                f"Average readiness score {avg_readiness:.2f} is below required threshold {min_readiness_score:.2f}"
            )

    scorer = GrowthScorer()
    scored = [scorer.calculate_scores(company) for company in companies]
    (output_dir / "scored.json").write_text(
        json.dumps([company.model_dump(mode="json") for company in scored], indent=2),
        encoding="utf-8",
    )

    analysis = MarketAnalysis(market_name=market, companies=scored)
    (output_dir / "market_analysis.json").write_text(
        json.dumps(analysis.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )

    ExcelExporter().create_dashboard(scored, output_dir / "dashboard.xlsx")

    return {
        "market": market,
        "seed_company": seed_company,
        "discovered": len(candidates),
        "profiles": len(companies),
        "provenance_failures": len(violations),
        "contradicted_companies": len(contradiction_report),
        "total_contradictions": sum(
            len(items) for items in contradiction_report.values() if isinstance(items, list)
        ),
        "average_readiness_score": evidence_report["average_readiness_score"],
        "investment_ready_count": evidence_report["investment_ready_count"],
        "decision_support_ready_count": evidence_report[
            "decision_support_ready_count"
        ],
        "output_dir": str(output_dir),
    }
