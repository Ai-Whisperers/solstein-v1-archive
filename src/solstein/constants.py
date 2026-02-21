"""Constants for SolStein."""

from enum import Enum


class ScoringWeights(Enum):
    """Weighting for composite scoring."""

    GROWTH = 0.4
    FINANCIAL_HEALTH = 0.3
    COMPETITIVE_POSITION = 0.3


class Thresholds(Enum):
    """Threshold values for scoring."""

    REVENUE_PER_EMPLOYEE_EXCEPTIONAL = 250
    REVENUE_PER_EMPLOYEE_GOOD = 150
    GROWTH_RATE_EXCEPTIONAL = 30
    GROWTH_RATE_GOOD = 15
    EMPLOYEE_CAGR_EXCEPTIONAL = 25
    EMPLOYEE_CAGR_GOOD = 10


class Classification(Enum):
    """Company classification based on composite score."""

    PHOENIX = "Phoenix"
    SALT = "Salt"
    LEAD = "Lead"


class CompanyTier(Enum):
    """Company tier based on revenue."""

    TIER_1 = "Tier 1"  # >€1B
    TIER_1B = "Tier 1b"  # €500M-€1B
    TIER_2 = "Tier 2"  # €100M-€500M
    TIER_3 = "Tier 3"  # <€100M


class ThreatLevel(Enum):
    """Competitive threat level."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


# Scoring thresholds
REVENUE_PER_EMPLOYEE_EXCEPTIONAL = 250
REVENUE_PER_EMPLOYEE_GOOD = 150
REVENUE_PER_EMPLOYEE_AVERAGE = 100

GROWTH_RATE_EXCEPTIONAL = 30
GROWTH_RATE_GOOD = 15
GROWTH_RATE_AVERAGE = 5

# AI Score thresholds
AI_EXCEPTIONAL = 8
AI_ADVANCED = 6
AI_EMERGING = 3
AI_NONE = 0

# SaaS Maturity thresholds
SAAS_NATIVE = 8
SAAS_ADVANCED = 6
SAAS_HYBRID = 4
SAAS_LEGACY = 2
