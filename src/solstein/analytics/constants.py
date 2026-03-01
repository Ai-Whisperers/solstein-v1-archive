"""Constants for analytics, scoring, and classification thresholds."""

# Classification Score Thresholds
PHOENIX_SCORE_THRESHOLD = 7.0  # High-growth companies (top 15-25%)
SALT_SCORE_THRESHOLD = 5.5  # Stable companies (middle 60-70%)
LEAD_SCORE_THRESHOLD = 5.5  # Legacy/opportunity companies (bottom 10-20%)

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
CLASSIFICATION_PHOENIX_MIN = 0.15  # Minimum Phoenix percentage (15%)
CLASSIFICATION_PHOENIX_MAX = 0.25  # Maximum Phoenix percentage (25%)
CLASSIFICATION_SALT_MIN = 0.60  # Minimum Salt percentage (60%)
CLASSIFICATION_SALT_MAX = 0.70  # Maximum Salt percentage (70%)
CLASSIFICATION_LEAD_MIN = 0.10  # Minimum Lead percentage (10%)
CLASSIFICATION_LEAD_MAX = 0.20  # Maximum Lead percentage (20%)

# Simulation Market Impact
SIMULATION_INFLATION_THRESHOLD = 0.02  # Normal inflation < 2%

# Readiness Score Thresholds
READINESS_SCORE_EXCELLENT = 85  # Excellent readiness
READINESS_SCORE_GOOD = 70  # Good readiness
READINESS_SCORE_FAIR = 50  # Fair readiness
