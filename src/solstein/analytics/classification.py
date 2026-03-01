"""
Task 9-11: Classification System with Confidence Scoring

Implements balanced classification (Phoenix/Salt/Lead) with confidence scoring
based on data quality and score distribution.

Classification Boundaries (based on percentile analysis):
- Phoenix (High Growth): >= 7.5 (top 15-20%)
- Salt (Stable): 4.5 - 7.49 (middle 60-70%)
- Lead (Legacy/Opportunity): < 4.5 (bottom 15-20%)

Classification Confidence:
- Based on data completeness (from Task 3)
- High completeness (>80%) → high confidence (0.8-1.0)
- Medium completeness (50-80%) → medium confidence (0.5-0.8)
- Low completeness (<50%) → low confidence (0.3-0.5)
"""

from src.solstein.domain.models import Company
from .constants import (
    CLASSIFICATION_PHOENIX_MIN,
    CLASSIFICATION_PHOENIX_MAX,
    CLASSIFICATION_SALT_MIN,
    CLASSIFICATION_SALT_MAX,
    CLASSIFICATION_LEAD_MIN,
    CLASSIFICATION_LEAD_MAX,
)


def classify_company_balanced(composite_score: float | None) -> str:
    """Classify company based on balanced score boundaries.

    DEPRECATED: Use solstein.analytics.scoring.classify_company() instead.
    This function is kept for backward compatibility.

    Args:
        composite_score: Composite score (0-10)

    Returns:
        Classification: 'Phoenix', 'Salt', or 'Lead'
    """
    # Delegate to the canonical classification function
    from .scoring import classify_company
    return classify_company(composite_score)


def calculate_classification_confidence(
    composite_score: float | None,
    data_completeness: float | None,
) -> float:
    """Calculate confidence in classification based on score and data quality.

    Args:
        composite_score: Composite score (0-10)
        data_completeness: Data completeness percentage (0-100)

    Returns:
        Confidence score (0-1)
    """
    if composite_score is None or data_completeness is None:
        return 0.3  # Low confidence for missing data

    # Normalize completeness to 0-1
    completeness_factor = data_completeness / 100.0

    # Score certainty: higher scores are more certain
    # Scores near boundaries (4.5, 7.5) are less certain
    score_certainty = 1.0
    if 4.4 <= composite_score <= 4.6 or 7.4 <= composite_score <= 7.6:  # Near Salt/Lead or Phoenix boundary
        score_certainty = 0.7

    # Combine factors: 70% data quality, 30% score certainty
    confidence = (0.7 * completeness_factor) + (0.3 * score_certainty)

    # Clamp to 0-1 range
    return max(0.0, min(1.0, confidence))


def get_classification_with_confidence(
    company: Company,
) -> tuple[str, float]:
    """Get classification and confidence for a company.

    Args:
        company: Company object with composite_score and data_quality_tier

    Returns:
        Tuple of (classification, confidence)
    """
    # Get classification
    from .scoring import classify_company
    classification = classify_company(company.composite_score)

    # Estimate data completeness from data_quality_tier
    completeness_map = {
        "COMPLETE": 90.0,
        "PARTIAL": 65.0,
        "MINIMAL": 35.0,
        "INSUFFICIENT": 15.0,
        "unknown": 50.0,
    }

    completeness = completeness_map.get(company.data_quality_tier, 50.0)

    # Calculate confidence
    confidence = calculate_classification_confidence(
        company.composite_score,
        completeness,
    )

    return classification, confidence


def is_tentative_classification(confidence: float, threshold: float = 0.7) -> bool:
    """Check if classification is tentative (low confidence).

    Args:
        confidence: Classification confidence (0-1)
        threshold: Confidence threshold for tentative classification

    Returns:
        True if confidence < threshold
    """
    return confidence < threshold


def format_classification_with_confidence(
    classification: str,
    confidence: float,
) -> str:
    """Format classification with confidence for display.

    Args:
        classification: Classification name
        confidence: Confidence score (0-1)

    Returns:
        Formatted string like "Phoenix (92% confidence)"
    """
    confidence_pct = int(confidence * 100)
    return f"{classification} ({confidence_pct}% confidence)"


def get_classification_distribution(companies: list[Company]) -> dict[str, int]:
    """Get distribution of classifications across companies.

    Args:
        companies: List of Company objects

    Returns:
        Dict with counts: {'Phoenix': N, 'Salt': N, 'Lead': N}
    """
    from .scoring import classify_company
    distribution = {"Phoenix": 0, "Salt": 0, "Lead": 0}

    for company in companies:
        classification = classify_company(company.composite_score)
        distribution[classification] += 1

    return distribution


def validate_classification_distribution(
    companies: list[Company],
    phoenix_min: float = CLASSIFICATION_PHOENIX_MIN,
    phoenix_max: float = CLASSIFICATION_PHOENIX_MAX,
    salt_min: float = CLASSIFICATION_SALT_MIN,
    salt_max: float = CLASSIFICATION_SALT_MAX,
    lead_min: float = CLASSIFICATION_LEAD_MIN,
    lead_max: float = CLASSIFICATION_LEAD_MAX,
) -> dict[str, bool]:
    """Validate that classification distribution meets targets.

    Args:
        companies: List of Company objects
        phoenix_min/max: Target Phoenix percentage range
        salt_min/max: Target Salt percentage range
        lead_min/max: Target Lead percentage range

    Returns:
        Dict with validation results
    """
    dist = get_classification_distribution(companies)
    total = len(companies)

    phoenix_pct = dist["Phoenix"] / total
    salt_pct = dist["Salt"] / total
    lead_pct = dist["Lead"] / total

    return {
        "phoenix_valid": phoenix_min <= phoenix_pct <= phoenix_max,
        "salt_valid": salt_min <= salt_pct <= salt_max,
        "lead_valid": lead_min <= lead_pct <= lead_max,
        "phoenix_pct": phoenix_pct,
        "salt_pct": salt_pct,
        "lead_pct": lead_pct,
        "phoenix_count": dist["Phoenix"],
        "salt_count": dist["Salt"],
        "lead_count": dist["Lead"],
        "total": total,
    }


def report_classification_distribution(companies: list[Company]) -> str:
    """Generate a human-readable report of classification distribution.

    Args:
        companies: List of Company objects

    Returns:
        Formatted string with distribution report
    """
    validation = validate_classification_distribution(companies)

    lines = [
        "=" * 50,
        "CLASSIFICATION DISTRIBUTION REPORT",
        "=" * 50,
        "",
        f"Total Companies: {validation['total']}",
        "",
        "Distribution:",
        f"  Phoenix: {validation['phoenix_count']} ({validation['phoenix_pct']*100:.1f}%) "
        f"{'✓' if validation['phoenix_valid'] else '✗'}",
        f"  Salt:    {validation['salt_count']} ({validation['salt_pct']*100:.1f}%) "
        f"{'✓' if validation['salt_valid'] else '✗'}",
        f"  Lead:    {validation['lead_count']} ({validation['lead_pct']*100:.1f}%) "
        f"{'✓' if validation['lead_valid'] else '✗'}",
        "",
        "Target Ranges:",
        f"  Phoenix: {CLASSIFICATION_PHOENIX_MIN*100:.0f}% - {CLASSIFICATION_PHOENIX_MAX*100:.0f}%",
        f"  Salt:    {CLASSIFICATION_SALT_MIN*100:.0f}% - {CLASSIFICATION_SALT_MAX*100:.0f}%",
        f"  Lead:    {CLASSIFICATION_LEAD_MIN*100:.0f}% - {CLASSIFICATION_LEAD_MAX*100:.0f}%",
        "",
        "Status:",
    ]

    if all([validation['phoenix_valid'], validation['salt_valid'], validation['lead_valid']]):
        lines.append("  ✓ All classifications within target ranges")
    else:
        lines.append("  ✗ Some classifications outside target ranges:")
        if not validation['phoenix_valid']:
            lines.append(f"    - Phoenix: {validation['phoenix_pct']*100:.1f}% (target: {CLASSIFICATION_PHOENIX_MIN*100:.0f}%-{CLASSIFICATION_PHOENIX_MAX*100:.0f}%)")
        if not validation['salt_valid']:
            lines.append(f"    - Salt: {validation['salt_pct']*100:.1f}% (target: {CLASSIFICATION_SALT_MIN*100:.0f}%-{CLASSIFICATION_SALT_MAX*100:.0f}%)")
        if not validation['lead_valid']:
            lines.append(f"    - Lead: {validation['lead_pct']*100:.1f}% (target: {CLASSIFICATION_LEAD_MIN*100:.0f}%-{CLASSIFICATION_LEAD_MAX*100:.0f}%)")

    lines.append("=" * 50)

    return "\n".join(lines)
