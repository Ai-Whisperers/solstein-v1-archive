"""Factory Boy factories for creating test data.

This module provides centralized factories for creating test data
without manual mock setup.

Usage:
    from tests.factories import CompanyFactory
    
    # Create a company with default values
    company = CompanyFactory()
    
    # Create a company with specific values
    company = CompanyFactory(name="Test Corp", tier=CompanyTier.TIER_1)
    
    # Create multiple companies
    companies = CompanyFactory.create_batch(10)
"""

import factory
from factory import Faker, Sequence
from solstein.domain.models import (
    Company,
    CompanyTier,
    AIMaturity,
    ThreatLevel,
    FinancialMetric,
    ConfidenceLevel,
)


class FinancialMetricFactory(factory.Factory):
    """Factory for creating FinancialMetric instances."""
    
    class Meta:
        model = FinancialMetric
    
    revenue = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    revenue_confidence = ConfidenceLevel.CONFIRMED
    growth_rate = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    growth_confidence = ConfidenceLevel.ESTIMATED
    employees = factory.Faker('random_int', min=10, max=10000)
    employees_confidence = ConfidenceLevel.CONFIRMED


class CompanyFactory(factory.Factory):
    """Factory for creating Company instances.
    
    Creates realistic company data with sensible defaults.
    All fields can be overridden.
    
    Examples:
        >>> # Default company
        >>> company = CompanyFactory()
        
        >>> # Company with specific tier
        >>> company = CompanyFactory(tier=CompanyTier.TIER_1)
        
        >>> # Create 10 companies
        >>> companies = CompanyFactory.create_batch(10)
    """
    
    class Meta:
        model = Company
    
    id = Sequence(lambda n: f"comp_{n:03d}")
    name = Faker('company')
    industry = Faker('bs')
    description = Faker('catch_phrase')
    website = Faker('url')
    headquarters = Faker('city')
    founded_year = Faker('year')
    
    tier = factory.Iterator(CompanyTier)
    ai_maturity = factory.Iterator(AIMaturity)
    threat_level = factory.Iterator(ThreatLevel)
    
    financials = factory.SubFactory(FinancialMetricFactory)
    
    geographic_presence = factory.List([
        Faker('country').generate() for _ in range(3)
    ])
    
    @factory.post_generation
    def set_composite_score(obj, create, extracted, **kwargs):
        """Calculate composite score after creation."""
        if obj.growth_score and obj.financial_health_score:
            obj.composite_score = (
                obj.growth_score * 0.4 +
                obj.financial_health_score * 0.3 +
                obj.competitive_position_score * 0.3
            )


class CompanyFactoryHighGrowth(CompanyFactory):
    """Factory for high-growth companies (Phoenix type)."""
    
    growth_score = 8.5
    financial_health_score = 7.0
    tier = CompanyTier.TIER_1
    ai_maturity = AIMaturity.STRONG


class CompanyFactoryDistressed(CompanyFactory):
    """Factory for distressed companies."""
    
    growth_score = 2.0
    financial_health_score = 3.0
    tier = CompanyTier.TIER_4
    threat_level = ThreatLevel.HIGH


__all__ = [
    'CompanyFactory',
    'CompanyFactoryHighGrowth',
    'CompanyFactoryDistressed',
    'FinancialMetricFactory',
]
