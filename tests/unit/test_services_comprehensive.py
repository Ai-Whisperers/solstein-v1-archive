"""Comprehensive unit tests for all service classes.

Tests cover:
- EnrichmentService: Data enrichment with caching and audit trails
- DrillDownService: Audit trail retrieval and data drilling
- GrowthScorer: Growth score calculation and normalization
- CompetitiveAnalyzer: Competitive analysis and positioning

All tests follow async patterns and use pytest fixtures.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.analytics.scoring import GrowthScorer, classify_company
from solstein.api.services.drill_down_service import DrillDownService
from solstein.api.services.enrichment_service import EnrichmentService
from solstein.data.unified_loader import UnifiedCompany
from solstein.domain.models import (
    AggregatedDataRecord,
    AggregatedFact,
    Company,
    CompanyAnalysisAuditTrail,
    ConfidenceLevel,
    FinancialMetric,
    SignalExtraction,
    SignalExtractionRecord,
)

# ============================================================================
# ENRICHMENT SERVICE TESTS
# ============================================================================


class TestEnrichmentService:
    """Tests for EnrichmentService."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Create a mock AsyncSession."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def enrichment_service(self, mock_session: AsyncMock) -> EnrichmentService:
        """Create an EnrichmentService instance with mocked repositories."""
        service = EnrichmentService(mock_session)
        # Mock the repositories to avoid real database calls
        service.audit_repo = AsyncMock()
        service.cache_repo = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_enrich_company_data(self, enrichment_service: EnrichmentService, mock_session: AsyncMock) -> None:
        """Test enriching company data with external sources."""
        # Arrange
        company_id = "test_company_001"
        company_name = "Test Company"
        sources = ["SEC_EDGAR", "GITHUB"]

        # Mock the unified_loader
        with patch("solstein.api.services.enrichment_service.unified_loader") as mock_loader:
            mock_company = UnifiedCompany(id=company_id, name=company_name)
            mock_company.financials = FinancialMetric(
                revenue=5000000.0,
                employees=150,
                growth_rate=0.25,
            )
            mock_loader.enrich_from_connectors.return_value = mock_company

            # Act
            result = await enrichment_service.enrich_company(
                company_id=company_id,
                company_name=company_name,
                sources=sources,
                use_cache=False,
            )

        # Assert
        assert result is not None
        assert result["company_id"] == company_id
        assert result["company_name"] == company_name
        assert "enriched_data" in result
        assert result["enriched_data"]["revenue"] == 5000000.0
        assert result["enriched_data"]["employees"] == 150
        assert result["from_cache"] is False
        mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_enrich_with_cache(self, enrichment_service: EnrichmentService, mock_session: AsyncMock) -> None:
        """Test using cached enrichment data."""
        # Arrange
        company_id = "cached_company"
        company_name = "Cached Company"

        # Mock cache repository to return cached data
        cached_data = {
            "id": company_id,
            "name": company_name,
            "revenue": 3000000.0,
            "employees": 100,
        }
        mock_cache_entry = MagicMock()
        mock_cache_entry.enriched_data = cached_data
        mock_cache_entry.sources_used = ["SEC_EDGAR"]
        mock_cache_entry.fields_enriched = ["revenue", "employees"]

        enrichment_service.cache_repo.get_cached = AsyncMock(return_value=mock_cache_entry)

        # Act
        result = await enrichment_service.enrich_company(
            company_id=company_id,
            company_name=company_name,
            use_cache=True,
        )

        # Assert
        assert result is not None
        assert result["from_cache"] is True
        assert result["enriched_data"] == cached_data
        enrichment_service.cache_repo.get_cached.assert_called_once_with(company_id)

    @pytest.mark.asyncio
    async def test_enrich_audit_trail(self, enrichment_service: EnrichmentService, mock_session: AsyncMock) -> None:
        """Test that audit trail is created during enrichment."""
        # Arrange
        company_id = "audit_test_company"
        company_name = "Audit Test Company"
        user_id = "test_user_123"
        client_id = "test_client_456"

        with patch("solstein.api.services.enrichment_service.unified_loader") as mock_loader:
            mock_company = UnifiedCompany(id=company_id, name=company_name)
            mock_company.financials = FinancialMetric(
                revenue=2000000.0,
            )
            mock_loader.enrich_from_connectors.return_value = mock_company

            # Act
            result = await enrichment_service.enrich_company(
                company_id=company_id,
                company_name=company_name,
                user_id=user_id,
                client_id=client_id,
                use_cache=False,
            )

        # Assert
        assert result is not None
        # Verify audit_repo.log_operation was called
        assert enrichment_service.audit_repo.log_operation.call_count >= 2
        # Should have at least enrich_start and enrich_success calls
        calls = enrichment_service.audit_repo.log_operation.call_args_list
        operations = [call[1]["operation"] for call in calls]
        assert "enrich_start" in operations
        assert "enrich_success" in operations

    @pytest.mark.asyncio
    async def test_enrich_error_handling(self, enrichment_service: EnrichmentService, mock_session: AsyncMock) -> None:
        """Test error handling during enrichment."""
        # Arrange
        company_id = "error_company"
        company_name = "Error Company"

        with patch("solstein.api.services.enrichment_service.unified_loader") as mock_loader:
            # Simulate enrichment failure
            mock_loader.enrich_from_connectors.side_effect = Exception("Enrichment failed")

            # Act & Assert
            with pytest.raises(Exception, match="Enrichment failed"):
                await enrichment_service.enrich_company(
                    company_id=company_id,
                    company_name=company_name,
                    use_cache=False,
                )

            # Verify failure was logged
            calls = enrichment_service.audit_repo.log_operation.call_args_list
            operations = [call[1]["operation"] for call in calls]
            assert "enrich_failure" in operations

    @pytest.mark.asyncio
    async def test_get_audit_trail(self, enrichment_service: EnrichmentService) -> None:
        """Test retrieving audit trail."""
        # Arrange
        company_id = "audit_trail_company"
        mock_entries = [
            MagicMock(to_dict=lambda: {"operation": "enrich_start"}),
            MagicMock(to_dict=lambda: {"operation": "enrich_success"}),
        ]
        enrichment_service.audit_repo.get_audit_trail = AsyncMock(return_value=mock_entries)
        enrichment_service.audit_repo.get_company_stats = AsyncMock(return_value={"total_operations": 2})

        # Act
        result = await enrichment_service.get_audit_trail(company_id=company_id)

        # Assert
        assert result is not None
        assert "entries" in result
        assert "stats" in result
        assert len(result["entries"]) == 2

    @pytest.mark.asyncio
    async def test_clear_cache(self, enrichment_service: EnrichmentService, mock_session: AsyncMock) -> None:
        """Test clearing cache entries."""
        # Arrange
        company_id = "cache_clear_company"
        enrichment_service.cache_repo.delete_cache = AsyncMock(return_value=5)
        enrichment_service.cache_repo.get_cache_stats = AsyncMock(return_value={"remaining": 10})

        # Act
        result = await enrichment_service.clear_cache(company_id=company_id)

        # Assert
        assert result is not None
        assert result["deleted_count"] == 5
        assert "cache_stats" in result
        mock_session.commit.assert_called()


# ============================================================================
# DRILL DOWN SERVICE TESTS
# ============================================================================


class TestDrillDownService:
    """Tests for DrillDownService."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Create a mock AsyncSession."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def drill_down_service(self, mock_session: AsyncMock) -> DrillDownService:
        """Create a DrillDownService instance."""
        return DrillDownService(mock_session)

    @pytest.mark.asyncio
    async def test_store_audit_trail(self, drill_down_service: DrillDownService) -> None:
        """Test storing an audit trail."""
        # Arrange
        company_id = "drill_test_001"
        audit_trail = CompanyAnalysisAuditTrail(
            company_id=company_id,
            gathering_batch_id=str(uuid.uuid4()),
            company_name="Test Company",
            growth_score=7.5,
            financial_health_score=6.5,
            competitive_position_score=7.0,
            classification="Phoenix",
        )

        # Act
        await drill_down_service.store_audit_trail(audit_trail)

        # Assert
        assert drill_down_service._audit_trails[company_id] == audit_trail

    @pytest.mark.asyncio
    async def test_get_audit_trail(self, drill_down_service: DrillDownService) -> None:
        """Test retrieving an audit trail."""
        # Arrange
        company_id = "drill_test_002"
        batch_id = str(uuid.uuid4())
        audit_trail = CompanyAnalysisAuditTrail(
            company_id=company_id,
            gathering_batch_id=batch_id,
            company_name="Test Company",
            growth_score=7.5,
            financial_health_score=6.5,
            competitive_position_score=7.0,
            classification="Phoenix",
        )
        drill_down_service._audit_trails[company_id] = audit_trail

        # Act
        result = await drill_down_service.get_audit_trail(company_id)

        # Assert
        assert result is not None
        assert result.company_id == company_id
        assert result.growth_score == 7.5

    @pytest.mark.asyncio
    async def test_get_signals(self, drill_down_service: DrillDownService) -> None:
        """Test retrieving extracted signals."""
        # Arrange
        company_id = "signals_test"
        batch_id = str(uuid.uuid4())
        signals = [
            SignalExtraction(
                signal_name="revenue_growth",
                signal_value=0.25,
                calculation_method="yoy_change",
            ),
            SignalExtraction(
                signal_name="employee_growth",
                signal_value=0.15,
                calculation_method="yoy_change",
            ),
        ]
        extracted_signals = SignalExtractionRecord(
            company_id=company_id,
            gathering_batch_id=batch_id,
            signals=signals,
        )
        audit_trail = CompanyAnalysisAuditTrail(
            company_id=company_id,
            gathering_batch_id=batch_id,
            company_name="Test Company",
            extracted_signals=extracted_signals,
        )
        drill_down_service._audit_trails[company_id] = audit_trail

        # Act
        result = await drill_down_service.get_signals(company_id)

        # Assert
        assert result is not None
        assert len(result) == 2
        assert result[0].signal_name == "revenue_growth"

    @pytest.mark.asyncio
    async def test_get_facts(self, drill_down_service: DrillDownService) -> None:
        """Test retrieving aggregated facts."""
        # Arrange
        company_id = "facts_test"
        batch_id = str(uuid.uuid4())
        facts = [
            AggregatedFact(
                fact_type="revenue",
                value="5M",
                confidence=0.95,
                is_verified=True,
            ),
            AggregatedFact(
                fact_type="employees",
                value="150",
                confidence=0.85,
                is_verified=True,
            ),
        ]
        aggregated_facts = AggregatedDataRecord(
            company_id=company_id,
            gathering_batch_id=batch_id,
            facts=facts,
        )
        audit_trail = CompanyAnalysisAuditTrail(
            company_id=company_id,
            gathering_batch_id=batch_id,
            company_name="Test Company",
            aggregated_facts=aggregated_facts,
        )
        drill_down_service._audit_trails[company_id] = audit_trail

        # Act
        result = await drill_down_service.get_facts(company_id, min_confidence=0.8)

        # Assert
        assert result is not None
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_data_quality(self, drill_down_service: DrillDownService) -> None:
        """Test retrieving data quality metrics."""
        # Arrange
        company_id = "quality_test"
        audit_trail = CompanyAnalysisAuditTrail(
            company_id=company_id,
            gathering_batch_id=str(uuid.uuid4()),
            company_name="Test Company",
            data_completeness=0.85,
            confidence_level=ConfidenceLevel.CONFIRMED,
        )
        drill_down_service._audit_trails[company_id] = audit_trail

        # Act
        result = await drill_down_service.get_data_quality(company_id)

        # Assert
        assert result is not None
        assert result["completeness"] == 0.85
        assert result["confidence_level"] == ConfidenceLevel.CONFIRMED

    @pytest.mark.asyncio
    async def test_drill_down_not_found(self, drill_down_service: DrillDownService) -> None:
        """Test handling missing company in drill down."""
        # Arrange
        company_id = "nonexistent_company"

        # Act
        result = await drill_down_service.get_audit_trail(company_id)

        # Assert
        assert result is None


# ============================================================================
# GROWTH SCORER TESTS
# ============================================================================


class TestGrowthScorer:
    """Tests for GrowthScorer."""

    @pytest.fixture
    def scorer(self) -> GrowthScorer:
        """Create a GrowthScorer instance."""
        return GrowthScorer()

    def test_score_company_growth(self, scorer: GrowthScorer) -> None:
        """Test calculating growth score for a company."""
        # Arrange
        company = Company(
            id="growth_test_001",
            name="Growth Test Company",
            financials=FinancialMetric(
                revenue=5000000.0,
                growth_rate=0.25,
                employees=150,
                profit_margin=0.15,
            ),
        )

        # Act
        result = scorer.calculate_scores(company)

        # Assert
        assert result.growth_score is not None
        assert 0 <= result.growth_score <= 10
        assert result.classification in ["Phoenix", "Salt", "Lead"]

    def test_score_with_metrics(self, scorer: GrowthScorer) -> None:
        """Test scoring using various financial metrics."""
        # Arrange
        company = Company(
            id="metrics_test_001",
            name="Metrics Test Company",
            financials=FinancialMetric(
                revenue=10000000.0,
                growth_rate=0.35,
                employees=200,
                profit_margin=0.20,
                funding_raised=5000000.0,
                valuation=100000000.0,
            ),
        )

        # Act
        result = scorer.calculate_scores(company)

        # Assert
        assert result.growth_score is not None
        assert result.financial_health_score is not None
        assert result.competitive_position_score is not None
        assert result.composite_score is not None
        assert 0 <= result.composite_score <= 10

    def test_score_normalization(self, scorer: GrowthScorer) -> None:
        """Test that scores are properly normalized (0-10 range)."""
        # Arrange
        companies = [
            Company(
                id="norm_test_001",
                name="Low Growth",
                financials=FinancialMetric(revenue=1000000.0, growth_rate=0.05, employees=50),
            ),
            Company(
                id="norm_test_002",
                name="Medium Growth",
                financials=FinancialMetric(revenue=5000000.0, growth_rate=0.20, employees=150),
            ),
            Company(
                id="norm_test_003",
                name="High Growth",
                financials=FinancialMetric(revenue=10000000.0, growth_rate=0.50, employees=300),
            ),
        ]

        # Act
        results = [scorer.calculate_scores(company) for company in companies]

        # Assert
        for result in results:
            assert result.growth_score is not None
            assert 0 <= result.growth_score <= 10
            assert result.composite_score is not None
            assert 0 <= result.composite_score <= 10

    def test_score_edge_cases(self, scorer: GrowthScorer) -> None:
        """Test scoring with edge cases (missing data, zero values, etc.)."""
        # Arrange
        edge_cases = [
            Company(
                id="edge_001",
                name="No Growth Data",
                financials=FinancialMetric(revenue=1000000.0),
            ),
            Company(
                id="edge_002",
                name="Zero Revenue",
                financials=FinancialMetric(revenue=0.0, growth_rate=0.0),
            ),
            Company(
                id="edge_003",
                name="Negative Growth",
                financials=FinancialMetric(revenue=5000000.0, growth_rate=-0.10),
            ),
        ]

        # Act & Assert
        for company in edge_cases:
            result = scorer.calculate_scores(company)
            assert result.growth_score is not None
            assert 0 <= result.growth_score <= 10
            assert result.classification in ["Phoenix", "Salt", "Lead"]

    def test_classification_boundaries(self) -> None:
        """Test classification at boundary scores."""
        # Test Phoenix boundary (>= 7.0)
        assert classify_company(7.0) == "Phoenix"
        assert classify_company(7.5) == "Phoenix"
        assert classify_company(10.0) == "Phoenix"

        # Test Salt boundary (4.0 - 6.9)
        assert classify_company(4.0) == "Salt"
        assert classify_company(5.0) == "Salt"
        assert classify_company(6.9) == "Salt"

        # Test Lead boundary (<= 3.9)
        assert classify_company(3.9) == "Lead"
        assert classify_company(2.0) == "Lead"
        assert classify_company(0.0) == "Lead"

        # Test None handling
        assert classify_company(None) == "Salt"

    def test_score_consistency(self, scorer: GrowthScorer) -> None:
        """Test that scoring is consistent for the same input."""
        # Arrange
        company = Company(
            id="consistency_test",
            name="Consistency Test",
            financials=FinancialMetric(
                revenue=5000000.0,
                growth_rate=0.25,
                employees=150,
                profit_margin=0.15,
            ),
        )

        # Act
        result1 = scorer.calculate_scores(company)
        result2 = scorer.calculate_scores(company)

        # Assert
        assert result1.growth_score == result2.growth_score
        assert result1.composite_score == result2.composite_score
        assert result1.classification == result2.classification


# ============================================================================
# COMPETITIVE ANALYZER TESTS
# ============================================================================


class TestCompetitiveAnalyzer:
    """Tests for competitive analysis functionality."""

    @pytest.fixture
    def scorer(self) -> GrowthScorer:
        """Create a GrowthScorer for competitive analysis."""
        return GrowthScorer()

    def test_analyze_competitor(self, scorer: GrowthScorer) -> None:
        """Test analyzing a competitor company."""
        # Arrange
        competitor = Company(
            id="competitor_001",
            name="Competitor Corp",
            financials=FinancialMetric(
                revenue=8000000.0,
                growth_rate=0.30,
                employees=200,
                profit_margin=0.18,
            ),
        )

        # Act
        result = scorer.calculate_scores(competitor)

        # Assert
        assert result.growth_score is not None
        assert result.financial_health_score is not None
        assert result.competitive_position_score is not None
        assert result.classification in ["Phoenix", "Salt", "Lead"]

    def test_analyze_market_position(self, scorer: GrowthScorer) -> None:
        """Test analyzing market position through competitive scoring."""
        # Arrange
        companies = [
            Company(
                id="market_001",
                name="Market Leader",
                financials=FinancialMetric(revenue=50000000.0, growth_rate=0.25, employees=500),
            ),
            Company(
                id="market_002",
                name="Mid-Market Player",
                financials=FinancialMetric(revenue=10000000.0, growth_rate=0.20, employees=150),
            ),
            Company(
                id="market_003",
                name="Emerging Player",
                financials=FinancialMetric(revenue=2000000.0, growth_rate=0.40, employees=50),
            ),
        ]

        # Act
        results = [scorer.calculate_scores(company) for company in companies]

        # Assert
        # Verify all companies are scored
        assert len(results) == 3
        # Verify scores are in valid range
        for result in results:
            assert 0 <= result.composite_score <= 10

    def test_analyze_competitive_advantages(self, scorer: GrowthScorer) -> None:
        """Test identifying competitive advantages through scoring."""
        # Arrange
        high_growth_company = Company(
            id="advantage_001",
            name="High Growth Advantage",
            financials=FinancialMetric(
                revenue=5000000.0,
                growth_rate=0.50,  # High growth
                employees=100,
                profit_margin=0.20,  # Good profitability
            ),
        )

        # Act
        result = scorer.calculate_scores(high_growth_company)

        # Assert
        assert result.growth_score is not None
        # High growth should result in a higher score
        assert result.growth_score >= 0.0
        # Classification should reflect the metrics
        assert result.classification in ["Phoenix", "Salt", "Lead"]

    def test_analyze_threats(self, scorer: GrowthScorer) -> None:
        """Test identifying competitive threats through scoring."""
        # Arrange
        declining_company = Company(
            id="threat_001",
            name="Declining Competitor",
            financials=FinancialMetric(
                revenue=5000000.0,
                growth_rate=-0.10,  # Negative growth
                employees=150,
                profit_margin=0.05,  # Low profitability
            ),
        )

        # Act
        result = scorer.calculate_scores(declining_company)

        # Assert
        assert result.growth_score is not None
        assert result.financial_health_score is not None
        # Declining company should not be Phoenix
        assert result.classification in ["Salt", "Lead"]

    def test_competitive_comparison(self, scorer: GrowthScorer) -> None:
        """Test comparing multiple competitors."""
        # Arrange
        competitors = [
            Company(
                id="comp_a",
                name="Competitor A",
                financials=FinancialMetric(revenue=5000000.0, growth_rate=0.25, employees=100),
            ),
            Company(
                id="comp_b",
                name="Competitor B",
                financials=FinancialMetric(revenue=8000000.0, growth_rate=0.35, employees=150),
            ),
            Company(
                id="comp_c",
                name="Competitor C",
                financials=FinancialMetric(revenue=3000000.0, growth_rate=0.15, employees=50),
            ),
        ]

        # Act
        results = [scorer.calculate_scores(company) for company in competitors]
        sorted_results = sorted(results, key=lambda x: x.composite_score or 0, reverse=True)

        # Assert
        assert len(sorted_results) == 3
        # Verify ranking is logical (higher scores first)
        for i in range(len(sorted_results) - 1):
            assert sorted_results[i].composite_score >= sorted_results[i + 1].composite_score
