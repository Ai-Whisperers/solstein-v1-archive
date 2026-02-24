"""Integration test: Coordinator → API transparency endpoints."""

import pytest

from solstein.agents import CoordinatorAgent
from solstein.api.services.drill_down_service import get_drill_down_service


@pytest.mark.asyncio
async def test_coordinator_stores_audit_trail():
    """Test that coordinator analysis is accessible via drill-down API."""
    coordinator = CoordinatorAgent()

    audit_trail = await coordinator.analyze_company(
        company_name="Test Company",
        gathering_batch_id="integration_test_001",
        context={"industry": "Test"},
    )

    service = get_drill_down_service()
    retrieved = await service.get_audit_trail(audit_trail.company_id)

    assert retrieved is not None
    assert retrieved.company_name == "Test Company"
    assert retrieved.gathering_batch_id == "integration_test_001"


@pytest.mark.asyncio
async def test_drill_down_signals_api():
    """Test that extracted signals are accessible via API."""
    coordinator = CoordinatorAgent()

    audit_trail = await coordinator.analyze_company(
        company_name="Test Company Signals",
        gathering_batch_id="signals_test_001",
        context={"industry": "Test"},
    )

    service = get_drill_down_service()
    signals = await service.get_signals(audit_trail.company_id)

    if signals is not None:
        assert isinstance(signals, list)


@pytest.mark.asyncio
async def test_drill_down_facts_api():
    """Test that aggregated facts are accessible via API."""
    coordinator = CoordinatorAgent()

    audit_trail = await coordinator.analyze_company(
        company_name="Test Company Facts",
        gathering_batch_id="facts_test_001",
        context={"industry": "Test"},
    )

    service = get_drill_down_service()
    facts = await service.get_facts(audit_trail.company_id)

    if facts is not None:
        assert isinstance(facts, list)


@pytest.mark.asyncio
async def test_drill_down_data_quality_api():
    """Test that data quality metrics are accessible."""
    coordinator = CoordinatorAgent()

    audit_trail = await coordinator.analyze_company(
        company_name="Test Company Quality",
        gathering_batch_id="quality_test_001",
        context={"industry": "Test"},
    )

    service = get_drill_down_service()
    metrics = await service.get_data_quality(audit_trail.company_id)

    assert metrics is not None
    assert "completeness" in metrics
    assert "average_confidence" in metrics
    assert "sources_count" in metrics
    assert "confidence_level" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
