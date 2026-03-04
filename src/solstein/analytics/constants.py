"""Constants for analytics, scoring, and classification thresholds."""

# Classification Score Thresholds
# Phoenix (High Growth): >= 7.01
# Salt (Stable): 4.5 - 7.0
# Lead (Legacy/Opportunity): < 4.5
PHOENIX_SCORE_THRESHOLD = 7.01  # High-growth companies
SALT_SCORE_THRESHOLD = 4.5  # Stable companies
LEAD_SCORE_THRESHOLD = 4.49  # Legacy/opportunity companies

# Score Range Bounds
MAX_SCORE = 10.0  # Maximum possible composite score
MIN_SCORE = 0.0  # Minimum possible composite score

# Confidence Thresholds
CONFIDENCE_HIGH = 0.9  # High confidence threshold
CONFIDENCE_MEDIUM = 0.7  # Medium confidence threshold
CONFIDENCE_LOW = 0.3  # Low confidence threshold
CONFIDENCE_TENTATIVE_THRESHOLD = 0.7  # Threshold for tentative classification

# Data Completeness Thresholds
COMPLETENESS_COMPLETE = 80  # 80-100% = complete
COMPLETENESS_PARTIAL = 50  # 50-79% = partial
COMPLETENESS_MINIMAL = 20  # 20-49% = minimal

# Confidence Integration Parameters
CONFIDENCE_SMOOTHING_FACTOR = 0.1  # Smoothing factor for confidence weighting
CONFIDENCE_MIN = 0.3  # Minimum confidence floor
CONFIDENCE_MAX = 0.99  # Maximum confidence ceiling

# Confidence Weighting by Data Quality
CONFIDENCE_CONFIRMED = 1.0  # Confirmed data
CONFIDENCE_ESTIMATED = 0.7  # Estimated/inferred data
CONFIDENCE_UNKNOWN = 0.3  # Unknown source data

# Valuation Model Constants
VALUATION_BASE_MULTIPLIER = 8.5  # Base EV/Revenue multiplier
VALUATION_GROWTH_MULTIPLIER = 2.0  # Growth adjustment multiplier
VALUATION_BOND_YIELD_BASE = 4.4  # Base bond yield for discount rate

# Valuation Discount Thresholds
VALUATION_DISCOUNT_SIGNIFICANT = 50  # >50% discount is significant
VALUATION_DISCOUNT_MODERATE = 20  # >20% discount is moderate

# Growth Momentum Thresholds
GROWTH_RATE_EXCEPTIONAL = 15  # Exceptional growth rate threshold

# Financial Health Thresholds
FINANCIAL_HEALTH_CONFIDENCE_HIGH = 0.9  # High confidence threshold
FINANCIAL_HEALTH_CONFIDENCE_MEDIUM = 0.7  # Medium confidence threshold

# Signal Extraction Confidence Scores
SIGNAL_CONFIDENCE_GITHUB_STARS = 0.8  # GitHub stars signal confidence
SIGNAL_CONFIDENCE_FUNDING = 0.85  # Funding signal confidence
SIGNAL_CONFIDENCE_REVENUE = 0.7  # Revenue signal confidence
SIGNAL_CONFIDENCE_EMPLOYEES = 0.9  # Employee count signal confidence
SIGNAL_CONFIDENCE_PATENTS = 0.85  # Patent signal confidence
SIGNAL_CONFIDENCE_NEWS = 0.75  # News signal confidence

# Signal Default Confidence
SIGNAL_DEFAULT_CONFIDENCE = 0.5  # Default confidence for signals

# Classification Distribution Targets
# Based on industry analysis: ~15% high-growth, ~65% stable, ~20% legacy
CLASSIFICATION_PHOENIX_MIN = 0.10  # Minimum Phoenix percentage (10%)
CLASSIFICATION_PHOENIX_MAX = 0.20  # Maximum Phoenix percentage (20%)
CLASSIFICATION_SALT_MIN = 0.60  # Minimum Salt percentage (60%)
CLASSIFICATION_SALT_MAX = 0.75  # Maximum Salt percentage (75%)
CLASSIFICATION_LEAD_MIN = 0.10  # Minimum Lead percentage (10%)
CLASSIFICATION_LEAD_MAX = 0.25  # Maximum Lead percentage (25%)

# Simulation Market Impact
SIMULATION_INFLATION_THRESHOLD = 0.02  # Normal inflation < 2%

# Readiness Score Thresholds
READINESS_SCORE_EXCELLENT = 85  # Excellent readiness
READINESS_SCORE_GOOD = 70  # Good readiness
READINESS_SCORE_FAIR = 50  # Fair readiness


# Classification to Threat Level Mapping
# Maps company classification and composite score to threat level
CLASSIFICATION_THREAT_MAPPING = {
    # Phoenix (high growth) = High or Critical threat
    ("Phoenix", 9.0): "CRITICAL",  # Phoenix with score >= 9.0
    ("Phoenix", 7.0): "HIGH",  # Phoenix with score >= 7.0
    # Salt (stable) = Medium or Low threat depending on score
    ("Salt", 6.0): "MEDIUM",  # Salt with score >= 6.0
    ("Salt", 0.0): "LOW",  # Salt with score < 6.0
    # Lead (legacy) = Low threat
    ("Lead", 0.0): "LOW",  # All Lead companies
}


def derive_threat_level(classification: str, composite_score: float) -> str:
    """Derive threat level from classification and composite score.

    Args:
        classification: Company classification (Phoenix, Salt, Lead)
        composite_score: Composite score (0-10)

    Returns:
        Threat level string matching ThreatLevel enum values (Critical, High, Medium, Low)
    """
    classification = classification.upper() if classification else "LEAD"

    if classification == "PHOENIX":
        return "Critical" if composite_score >= 9.0 else "High"
    elif classification == "SALT":
        return "Medium" if composite_score >= 6.0 else "Low"
    else:  # Lead or unknown
        return "Low"
