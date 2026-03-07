"""Test data factories using factory-boy.

EPIC-029 Story 1: Comprehensive test data factories for all models.

Usage:
    from tests.factories import CompanyFactory, ScoringRecordFactory

    # Create single company
    company = CompanyFactory()

    # Create company with relationships
    company = CompanyFactory(with_financials=True, with_scoring=True)

    # Create batch
    companies = CompanyFactory.create_batch(10)
"""

from typing import Any

from factory.base import Factory
from factory.declarations import SelfAttribute, Sequence, SubFactory
from factory.faker import Faker
from factory.helpers import post_generation

from solstein.domain.models import (
    Company,
    CompanyClassification,
    CompanyTier,
    FinancialMetric,
)
from solstein.infrastructure.database_models import (
    CompanyRecord,
    ScoringRecord,
    SignalRecord,
)


class FinancialMetricFactory(Factory[FinancialMetric]):
    """Factory for FinancialMetric domain model."""

    class Meta:
        model = FinancialMetric

    revenue = Faker("pyfloat", positive=True, max_value=1000)
    growth_rate = Faker("pyfloat", min_value=-50, max_value=200)
    profit_margin = Faker("pyfloat", min_value=-20, max_value=50)
    burn_rate = Faker("pyfloat", min_value=0, max_value=100)
    cash_on_hand = Faker("pyfloat", min_value=0, max_value=500)
    debt_to_equity = Faker("pyfloat", min_value=0, max_value=3)
    ltv = Faker("pyfloat", min_value=0, max_value=1000)
    cac = Faker("pyfloat", min_value=0, max_value=100)
    mrr = Faker("pyfloat", min_value=0, max_value=100)
    magic_number = Faker("pyfloat", min_value=-1, max_value=5)


class CompanyFactory(Factory[Company]):
    """Factory for Company domain model."""

    class Meta:
        model = Company

    id = Sequence(lambda n: f"company-{n:06d}")
    name = Faker("company")
    website = Faker("url")
    description = Faker("catch_phrase")
    industry = Faker("bs")
    sector = Faker("job")
    subsector = Faker("word")
    country_code = Faker("country_code")
    region = Faker("state")
    city = Faker("city")
    employee_count = Faker("random_int", min=10, max=10000)
    founded_year = Faker("random_int", min=1990, max=2024)
    funding_stage = Faker("random_element", elements=["Seed", "A", "B", "C", "D+"])
    funding_total = Faker("pyfloat", positive=True, max_value=1000)
    valuation = Faker("pyfloat", positive=True, max_value=5000)
    revenue = Faker("pyfloat", positive=True, max_value=1000)
    growth_rate = Faker("pyfloat", min_value=-50, max_value=200)
    competitors_count = Faker("random_int", min=0, max=20)
    classification = Faker(
        "random_element",
        elements=[CompanyClassification.PHOENIX, CompanyClassification.SALT, CompanyClassification.LEAD],
    )
    tier = Faker("random_element", elements=[CompanyTier.TIER_1, CompanyTier.TIER_2, CompanyTier.TIER_3])
    ai_sustainability_score = Faker("pyfloat", min_value=0, max_value=10)
    ai_growth_score = Faker("pyfloat", min_value=0, max_value=10)
    ai_competitive_position = Faker("pyfloat", min_value=0, max_value=10)
    ai_innovation_index = Faker("pyfloat", min_value=0, max_value=10)
    ai_data_quality_score = Faker("pyfloat", min_value=0, max_value=10)
    analysis_date = Faker("date_time_this_year")

    @post_generation
    def with_financials(self, create: bool, extracted: object, **kwargs: Any) -> None:
        """Add financial metrics after creation."""
        if create and extracted:
            self.financials = FinancialMetricFactory()

    @post_generation
    def with_competitors(self, create: bool, extracted: object, **kwargs: Any) -> None:
        """Add competitors after creation."""
        if create and extracted:
            count = extracted if isinstance(extracted, int) else 3
            self.competitors = [CompanyFactory() for _ in range(count)]


class CompanyRecordFactory(Factory[CompanyRecord]):
    """Factory for CompanyRecord database model."""

    class Meta:
        model = CompanyRecord

    company_id = Sequence(lambda n: f"comp-{n:06d}")
    name = Faker("company")
    website = Faker("url")
    description = Faker("catch_phrase")
    industry = Faker("bs")
    sector = Faker("job")
    country_code = Faker("country_code")
    employee_count = Faker("random_int", min=10, max=10000)
    founded_year = Faker("random_int", min=1990, max=2024)
    revenue_eur_m = Faker("pyfloat", positive=True, max_value=1000)
    growth_rate = Faker("pyfloat", min_value=-50, max_value=200)
    funding_stage = Faker("random_element", elements=["Seed", "A", "B", "C", "D+"])
    funding_total_eur_m = Faker("pyfloat", positive=True, max_value=1000)
    valuation_eur_m = Faker("pyfloat", positive=True, max_value=5000)
    competitors_count = Faker("random_int", min=0, max=20)
    classification = Faker("random_element", elements=["Phoenix", "Salt", "Lead"])
    tier = Faker("random_element", elements=["Tier 1", "Tier 2", "Tier 3"])
    ai_sustainability_score = Faker("pyfloat", min_value=0, max_value=10)
    ai_growth_score = Faker("pyfloat", min_value=0, max_value=10)
    ai_competitive_position = Faker("pyfloat", min_value=0, max_value=10)
    ai_innovation_index = Faker("pyfloat", min_value=0, max_value=10)
    ai_data_quality_score = Faker("pyfloat", min_value=0, max_value=10)


class ScoringRecordFactory(Factory[ScoringRecord]):
    """Factory for ScoringRecord database model."""

    class Meta:
        model = ScoringRecord

    company_id = Sequence(lambda n: f"comp-{n:06d}")
    overall_score = Faker("pyfloat", min_value=0, max_value=10)
    growth_score = Faker("pyfloat", min_value=0, max_value=10)
    financial_health_score = Faker("pyfloat", min_value=0, max_value=10)
    competitive_position_score = Faker("pyfloat", min_value=0, max_value=10)
    innovation_score = Faker("pyfloat", min_value=0, max_value=10)
    sustainability_score = Faker("pyfloat", min_value=0, max_value=10)
    classification = Faker("random_element", elements=["Phoenix", "Salt", "Lead"])
    explanation = Faker("paragraph")


class SignalRecordFactory(Factory[SignalRecord]):
    """Factory for SignalRecord database model."""

    class Meta:
        model = SignalRecord

    scoring_record_id = SelfAttribute("scoring_record.id")
    signal_type = Faker("random_element", elements=["financial", "growth", "competitive", "innovation"])
    signal_value = Faker("pyfloat", min_value=-1, max_value=1)
    confidence = Faker("pyfloat", min_value=0, max_value=1)
    weight = Faker("pyfloat", min_value=0, max_value=1)
    extracted_at = Faker("date_time_this_year")

    class Params:
        scoring_record = SubFactory(ScoringRecordFactory)


# Traits for common scenarios
class PhoenixCompanyFactory(CompanyFactory):
    """Factory for Phoenix-classified companies."""

    classification = CompanyClassification.PHOENIX
    ai_sustainability_score = Faker("pyfloat", min_value=7, max_value=10)
    ai_growth_score = Faker("pyfloat", min_value=7, max_value=10)
    ai_competitive_position = Faker("pyfloat", min_value=7, max_value=10)
    growth_rate = Faker("pyfloat", min_value=50, max_value=200)


class SaltCompanyFactory(CompanyFactory):
    """Factory for Salt-classified companies."""

    classification = CompanyClassification.SALT
    ai_sustainability_score = Faker("pyfloat", min_value=4, max_value=7)
    ai_growth_score = Faker("pyfloat", min_value=4, max_value=7)
    ai_competitive_position = Faker("pyfloat", min_value=4, max_value=7)
    growth_rate = Faker("pyfloat", min_value=20, max_value=50)


class LeadCompanyFactory(CompanyFactory):
    """Factory for Lead-classified companies."""

    classification = CompanyClassification.LEAD
    ai_sustainability_score = Faker("pyfloat", min_value=0, max_value=4)
    ai_growth_score = Faker("pyfloat", min_value=0, max_value=4)
    ai_competitive_position = Faker("pyfloat", min_value=0, max_value=4)
    growth_rate = Faker("pyfloat", min_value=-50, max_value=20)


def make_company(**overrides: Any) -> Company:
    return CompanyFactory(**overrides)
