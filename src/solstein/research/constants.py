"""Constants for research, discovery, and evidence gathering."""

# Discovery Configuration
DISCOVERY_MAX_COMPANIES = 25  # Maximum companies to discover
DISCOVERY_SCORE_BOOST_TECH_MATCH = 3.0  # Score boost for tech stack match
DISCOVERY_SCORE_BOOST_INDUSTRY_MATCH = 3.0  # Score boost for industry match
DISCOVERY_SCORE_BOOST_MINOR = 0.5  # Minor score boost

# Evidence Readiness Thresholds
EVIDENCE_READINESS_EXCELLENT = 85  # Excellent readiness threshold
EVIDENCE_READINESS_GOOD = 70  # Good readiness threshold
EVIDENCE_READINESS_FAIR = 50  # Fair readiness threshold

# Gather Configuration
GATHER_MARKET_CAP_THRESHOLD = 10_000_000_000  # Market cap threshold (€10B)
GATHER_GROWTH_RATE_EXCEPTIONAL = 20  # Exceptional growth rate
GATHER_GROWTH_RATE_GOOD = 8  # Good growth rate
GATHER_SAAS_MATURITY_DEFAULT = 5  # Default SaaS maturity score

# Signal Sourcing
SIGNAL_WELL_SOURCED_MIN = 3  # Minimum sources for well-sourced signal

# Signal Confidence Thresholds
SIGNAL_CONFIDENCE_EXCELLENT = 8  # Excellent signal confidence
SIGNAL_CONFIDENCE_GOOD = 6  # Good signal confidence
SIGNAL_CONFIDENCE_FAIR = 4  # Fair signal confidence

# Pipeline Configuration
PIPELINE_MAX_COMPANIES = 25  # Maximum companies in pipeline
PIPELINE_BATCH_ID_LENGTH = 12  # Length of batch ID

# Reconciliation
RECONCILIATION_NUMERIC_DIVERGENCE_THRESHOLD = 0.20  # 20% divergence threshold

# Aggregate Configuration
AGGREGATE_AGREEMENT_TOLERANCE = 0.10  # 10% agreement tolerance
AGGREGATE_CONTRADICTION_TOLERANCE = 0.25  # 25% contradiction tolerance

# Signal Confidence Defaults
SIGNAL_DEFAULT_CONFIDENCE = 0.5  # Default signal confidence
SIGNAL_LOW_CONFIDENCE = 0.4  # Low signal confidence
