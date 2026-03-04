"""
Task 17: Golden Dataset for Regression Testing

Defines a curated set of representative companies with expected scores
for regression testing to prevent score drift.
"""

from dataclasses import dataclass


@dataclass
class GoldenCompanyExpectation:
    """Expected values for a golden dataset company."""

    company_id: str
    company_name: str
    expected_classification: str
    expected_composite_score_min: float
    expected_composite_score_max: float
    expected_growth_score_min: float
    expected_growth_score_max: float
    expected_financial_health_min: float
    expected_financial_health_max: float
    expected_competitive_position_min: float
    expected_competitive_position_max: float
    expected_ai_score_min: int | None = None
    expected_ai_score_max: int | None = None
    expected_ai_maturity: str | None = None
    notes: str = ""

    def validate_composite_score(self, actual_score: float) -> bool:
        """Check if actual composite score is within expected range."""
        return self.expected_composite_score_min <= actual_score <= self.expected_composite_score_max

    def validate_growth_score(self, actual_score: float) -> bool:
        """Check if actual growth score is within expected range."""
        return self.expected_growth_score_min <= actual_score <= self.expected_growth_score_max

    def validate_financial_health_score(self, actual_score: float) -> bool:
        """Check if actual financial health score is within expected range."""
        return self.expected_financial_health_min <= actual_score <= self.expected_financial_health_max

    def validate_competitive_position_score(self, actual_score: float) -> bool:
        """Check if actual competitive position score is within expected range."""
        return self.expected_competitive_position_min <= actual_score <= self.expected_competitive_position_max

    def validate_classification(self, actual_classification: str) -> bool:
        """Check if actual classification matches expected."""
        return actual_classification == self.expected_classification

    def validate_ai_score(self, actual_score: int | None) -> bool:
        """Check if actual AI score is within expected range."""
        if self.expected_ai_score_min is None or self.expected_ai_score_max is None:
            return True  # No expectation set
        if actual_score is None:
            return False  # Expected a score but got None
        return self.expected_ai_score_min <= actual_score <= self.expected_ai_score_max

    def validate_ai_maturity(self, actual_maturity: str | None) -> bool:
        """Check if actual AI maturity matches expected."""
        if self.expected_ai_maturity is None:
            return True  # No expectation set
        return actual_maturity == self.expected_ai_maturity


# Golden Dataset: 10 representative companies
GOLDEN_DATASET = [
    # Phoenix companies (high-growth, AI-native)
    GoldenCompanyExpectation(
        company_id="eneve-1",
        company_name="Eneve",
        expected_classification="Phoenix",
        expected_composite_score_min=8.0,
        expected_composite_score_max=10.0,
        expected_growth_score_min=9.0,
        expected_growth_score_max=10.0,
        expected_financial_health_min=8.0,
        expected_financial_health_max=10.0,
        expected_competitive_position_min=7.0,
        expected_competitive_position_max=9.5,
        expected_ai_score_min=7,
        expected_ai_score_max=10,
        expected_ai_maturity="Strong",
        notes="High-growth AI-native company with strong market traction",
    ),
    GoldenCompanyExpectation(
        company_id="envision-digital-1",
        company_name="Envision Digital",
        expected_classification="Phoenix",
        expected_composite_score_min=7.0,
        expected_composite_score_max=8.5,
        expected_growth_score_min=7.0,
        expected_growth_score_max=9.0,
        expected_financial_health_min=6.0,
        expected_financial_health_max=8.5,
        expected_competitive_position_min=7.0,
        expected_competitive_position_max=8.5,
        expected_ai_score_min=6,
        expected_ai_score_max=9,
        expected_ai_maturity="Strong",
        notes="Rapid growth with strong AI capabilities",
    ),
    # Salt companies (stable, mature)
    GoldenCompanyExpectation(
        company_id="octopus-energy-1",
        company_name="Octopus Energy",
        expected_classification="Salt",
        expected_composite_score_min=5.0,
        expected_composite_score_max=7.0,
        expected_growth_score_min=4.0,
        expected_growth_score_max=6.5,
        expected_financial_health_min=5.0,
        expected_financial_health_max=7.0,
        expected_competitive_position_min=5.0,
        expected_competitive_position_max=7.0,
        expected_ai_score_min=4,
        expected_ai_score_max=7,
        expected_ai_maturity="Moderate",
        notes="Stable energy company with moderate growth",
    ),
    GoldenCompanyExpectation(
        company_id="shell-1",
        company_name="Shell",
        expected_classification="Salt",
        expected_composite_score_min=4.5,
        expected_composite_score_max=6.5,
        expected_growth_score_min=3.0,
        expected_growth_score_max=5.5,
        expected_financial_health_min=5.0,
        expected_financial_health_max=7.0,
        expected_competitive_position_min=4.0,
        expected_competitive_position_max=6.5,
        expected_ai_score_min=3,
        expected_ai_score_max=6,
        expected_ai_maturity="Moderate",
        notes="Large established energy company with steady performance",
    ),
    # Lead companies (legacy, transformation opportunity)
    GoldenCompanyExpectation(
        company_id="legacy-energy-1",
        company_name="Legacy Energy Company",
        expected_classification="Lead",
        expected_composite_score_min=2.0,
        expected_composite_score_max=4.0,
        expected_growth_score_min=1.0,
        expected_growth_score_max=3.5,
        expected_financial_health_min=2.0,
        expected_financial_health_max=4.5,
        expected_competitive_position_min=2.0,
        expected_competitive_position_max=4.0,
        expected_ai_score_min=0,
        expected_ai_score_max=3,
        expected_ai_maturity="Low",
        notes="Traditional energy company with legacy systems",
    ),
    GoldenCompanyExpectation(
        company_id="old-software-1",
        company_name="Old Software Company",
        expected_classification="Lead",
        expected_composite_score_min=2.5,
        expected_composite_score_max=4.0,
        expected_growth_score_min=1.5,
        expected_growth_score_max=3.5,
        expected_financial_health_min=2.5,
        expected_financial_health_max=4.5,
        expected_competitive_position_min=2.0,
        expected_competitive_position_max=4.0,
        expected_ai_score_min=0,
        expected_ai_score_max=2,
        expected_ai_maturity="None",
        notes="Legacy software with minimal AI adoption",
    ),
    # Edge cases
    GoldenCompanyExpectation(
        company_id="sparse-data-1",
        company_name="Sparse Data Company",
        expected_classification="Salt",
        expected_composite_score_min=4.0,
        expected_composite_score_max=6.0,
        expected_growth_score_min=3.0,
        expected_growth_score_max=5.5,
        expected_financial_health_min=3.0,
        expected_financial_health_max=5.5,
        expected_competitive_position_min=3.0,
        expected_competitive_position_max=5.5,
        expected_ai_score_min=None,
        expected_ai_score_max=None,
        expected_ai_maturity=None,
        notes="Company with limited available data",
    ),
    GoldenCompanyExpectation(
        company_id="high-growth-startup-1",
        company_name="High Growth Startup",
        expected_classification="Phoenix",
        expected_composite_score_min=7.5,
        expected_composite_score_max=9.0,
        expected_growth_score_min=8.0,
        expected_growth_score_max=9.5,
        expected_financial_health_min=6.0,
        expected_financial_health_max=8.0,
        expected_competitive_position_min=7.0,
        expected_competitive_position_max=8.5,
        expected_ai_score_min=7,
        expected_ai_score_max=10,
        expected_ai_maturity="Very Strong",
        notes="Rapid growth startup with strong AI focus",
    ),
    GoldenCompanyExpectation(
        company_id="mid-market-1",
        company_name="Mid-Market Company",
        expected_classification="Salt",
        expected_composite_score_min=5.5,
        expected_composite_score_max=6.5,
        expected_growth_score_min=4.5,
        expected_growth_score_max=6.0,
        expected_financial_health_min=5.0,
        expected_financial_health_max=6.5,
        expected_competitive_position_min=5.5,
        expected_competitive_position_max=6.5,
        expected_ai_score_min=5,
        expected_ai_score_max=7,
        expected_ai_maturity="Moderate",
        notes="Mid-market company with balanced growth and stability",
    ),
    GoldenCompanyExpectation(
        company_id="turnaround-1",
        company_name="Turnaround Company",
        expected_classification="Lead",
        expected_composite_score_min=3.0,
        expected_composite_score_max=4.0,
        expected_growth_score_min=2.0,
        expected_growth_score_max=4.0,
        expected_financial_health_min=2.5,
        expected_financial_health_max=4.5,
        expected_competitive_position_min=3.0,
        expected_competitive_position_max=4.5,
        expected_ai_score_min=1,
        expected_ai_score_max=4,
        expected_ai_maturity="Low",
        notes="Legacy company undergoing transformation",
    ),
]


def get_golden_dataset() -> list[GoldenCompanyExpectation]:
    """Get the complete golden dataset."""
    return GOLDEN_DATASET


def get_golden_company_by_id(company_id: str) -> GoldenCompanyExpectation | None:
    """Get a golden company expectation by ID."""
    for company in GOLDEN_DATASET:
        if company.company_id == company_id:
            return company
    return None


def get_golden_company_by_name(company_name: str) -> GoldenCompanyExpectation | None:
    """Get a golden company expectation by name."""
    for company in GOLDEN_DATASET:
        if company.company_name.lower() == company_name.lower():
            return company
    return None
