
from solstein.analytics.classification_service import (
    ClassificationResult,
    ClassificationService,
    classification_service,
    classify_company,
)
from solstein.domain.models import Company, FinancialMetric


def test_classify_phoenix_above_threshold() -> None:
    service = ClassificationService()
    assert service.classify(8.0) == "Phoenix"
    assert service.classify(7.0) == "Phoenix"


def test_classify_salt_in_middle_range() -> None:
    service = ClassificationService()
    assert service.classify(6.0) == "Salt"
    assert service.classify(4.5) == "Salt"


def test_classify_lead_below_threshold() -> None:
    service = ClassificationService()
    assert service.classify(4.0) == "Lead"
    assert service.classify(0.0) == "Lead"


def test_classify_none_returns_lead() -> None:
    service = ClassificationService()
    assert service.classify(None) == "Lead"


def test_calculate_confidence_with_complete_data() -> None:
    service = ClassificationService()
    # Score not near boundary, high completeness
    confidence = service.calculate_confidence(8.0, 90.0)
    assert 0.9 <= confidence <= 1.0


def test_calculate_confidence_near_boundary() -> None:
    service = ClassificationService()
    # Score near Phoenix boundary (6.9-7.1)
    confidence = service.calculate_confidence(7.0, 90.0)
    # Should be lower due to boundary uncertainty
    assert 0.7 <= confidence < 0.9


def test_calculate_confidence_with_missing_data() -> None:
    service = ClassificationService()
    confidence = service.calculate_confidence(None, None)
    assert confidence == 0.3


def test_get_completeness_from_tier() -> None:
    service = ClassificationService()
    assert service.get_completeness_from_tier("COMPLETE") == 90.0
    assert service.get_completeness_from_tier("PARTIAL") == 65.0
    assert service.get_completeness_from_tier("MINIMAL") == 35.0
    assert service.get_completeness_from_tier("INSUFFICIENT") == 15.0
    assert service.get_completeness_from_tier(None) == 50.0


def _make_company(composite_score: float, tier: str) -> Company:
    return Company(
        id="test-1",
        name="Test Co",
        industry="Energy",
        data_quality_tier=tier,
        financials=FinancialMetric(
            revenue=10.0,
            employees=20,
            growth_rate=15.0,
            profit_margin=10.0,
            valuation=100.0,
        ),
        composite_score=composite_score,
    )


def test_classify_company_returns_full_result() -> None:
    service = ClassificationService()
    company = _make_company(8.5, "COMPLETE")

    result = service.classify_company(company)

    assert isinstance(result, ClassificationResult)
    assert result.label == "Phoenix"
    assert result.composite_score == 8.5
    assert result.data_completeness == 90.0
    assert result.threat_level in ("Critical", "High")


def test_get_distribution() -> None:
    service = ClassificationService()
    companies = [
        _make_company(8.0, "COMPLETE"),  # Phoenix
        _make_company(8.5, "COMPLETE"),  # Phoenix
        _make_company(5.0, "PARTIAL"),  # Salt
        _make_company(3.0, "MINIMAL"),  # Lead
    ]

    dist = service.get_distribution(companies)

    assert dist["Phoenix"] == 2
    assert dist["Salt"] == 1
    assert dist["Lead"] == 1


def test_validate_distribution() -> None:
    service = ClassificationService()
    # Create distribution that should be valid
    companies = [
        _make_company(8.0, "COMPLETE"),  # Phoenix (15%)
        _make_company(5.0, "PARTIAL"),  # Salt (70%)
        _make_company(5.5, "PARTIAL"),
        _make_company(5.8, "PARTIAL"),
        _make_company(5.9, "PARTIAL"),
        _make_company(5.2, "PARTIAL"),
        _make_company(5.3, "PARTIAL"),
        _make_company(3.0, "MINIMAL"),  # Lead (15%)
        _make_company(3.5, "MINIMAL"),
    ]

    validation = service.validate_distribution(companies)

    assert validation["phoenix_count"] == 1
    assert validation["salt_count"] == 6
    assert validation["lead_count"] == 2
    assert validation["total"] == 9


def test_validate_distribution_empty_list() -> None:
    service = ClassificationService()
    validation = service.validate_distribution([])

    assert validation["total"] == 0
    assert validation["phoenix_valid"] is False


def test_is_tentative_below_threshold() -> None:
    service = ClassificationService()
    assert service.is_tentative(0.5) is True
    assert service.is_tentative(0.69) is True


def test_is_tentative_above_threshold() -> None:
    service = ClassificationService()
    assert service.is_tentative(0.7) is False
    assert service.is_tentative(0.9) is False


def test_global_singleton_works() -> None:
    # Test the global singleton instance
    assert classification_service.classify(8.0) == "Phoenix"


def test_backward_compat_function() -> None:
    # Test backward compatibility function
    assert classify_company(8.0) == "Phoenix"
    assert classify_company(4.0) == "Lead"
    assert classify_company(None) == "Lead"
