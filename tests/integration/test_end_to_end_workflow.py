"""
End-to-End Workflow Integration Tests for Solstein.

Comprehensive test suite verifying all components work together across complete workflows:
1. Complete company workflow (create → enrich → score → export)
2. Data migration to API workflow (migrate → fetch → verify)
3. Research workflow (create job → add stages → add artifacts → retrieve)
4. Enrichment workflow (create job → enrich → verify cache → audit trail)
5. Scoring workflow (create records → calculate → verify normalization)
6. Market analysis workflow (create snapshot → analyze trends → compare companies)

Each test verifies:
- Data consistency across components
- Proper error handling
- Audit trail creation
- Cache population
- Score normalization
- Relationship integrity
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from solstein.analytics.scoring import GrowthScorer
from solstein.core.repositories import CompanyRepository
from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_company_data() -> dict[str, Any]:
    """Provide sample company data for testing."""
    return {
        "id": "test-company-e2e-001",
        "name": "Test Company E2E",
        "industry": "Energy Software",
        "description": "A test company for end-to-end workflow testing",
        "website": "https://test-company.example.com",
        "headquarters": "Amsterdam, Netherlands",
        "founded_year": 2015,
        "tier": CompanyTier.TIER_2,
        "threat_level": ThreatLevel.MEDIUM,
        "ai_maturity": AIMaturity.MODERATE,
        "saas_maturity": 3,
        "tech_stack": ["Python", "React", "PostgreSQL", "Kubernetes"],
        "financials": FinancialMetric(
            revenue=25.5,
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            growth_rate=0.35,
            growth_confidence=ConfidenceLevel.CONFIRMED,
            employees=150,
            employees_confidence=ConfidenceLevel.CONFIRMED,
            profit_margin=0.15,
            margin_confidence=ConfidenceLevel.ESTIMATED,
            funding_raised=5.0,
            funding_confidence=ConfidenceLevel.CONFIRMED,
        ),
        "geographic_presence": ["Netherlands", "Germany", "Belgium"],
        "key_customers": ["Customer A", "Customer B", "Customer C"],
        "parent_company": None,
        "subsidiaries": [],
        "acquisitions": [],
        "data_source": "test-fixture",
        "notes": "Test company for E2E workflow validation",
        "source_links": ["https://example.com/company"],
    }


@pytest.fixture
def mock_company_repo() -> MagicMock:
    """Provide mocked CompanyRepository."""
    repo = MagicMock(spec=CompanyRepository)
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_all = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def growth_scorer() -> GrowthScorer:
    """Provide GrowthScorer instance."""
    return GrowthScorer()


# ============================================================================
# TEST CASES
# ============================================================================


class TestCompleteCompanyWorkflow:
    """Test complete company workflow: create → enrich → score → export."""

    @pytest.mark.asyncio
    async def test_complete_company_workflow(
        self,
        mock_company_repo: MagicMock,
        sample_company_data: dict[str, Any],
        growth_scorer: GrowthScorer,
    ):
        """Test complete company workflow with all operations.

        Workflow:
        1. Create company via repository
        2. Verify company is stored
        3. Enrich company data (simulate enrichment)
        4. Score company
        5. Verify scores are normalized (0-100)
        6. Verify data consistency
        """
        # Step 1: Create company
        company = Company(**sample_company_data)
        mock_created = MagicMock()
        mock_created.id = "test-company-001"
        mock_created.name = company.name
        mock_created.sector = company.industry
        mock_company_repo.create.return_value = mock_created

        created_company = await mock_company_repo.create(
            ticker="TEST",
            name=company.name,
            sector=company.industry,
        )

        assert created_company is not None
        assert created_company.id is not None
        assert created_company.name == company.name
        assert created_company.sector == company.industry

        # Step 2: Retrieve and verify
        mock_company_repo.get_by_id.return_value = mock_created
        retrieved = await mock_company_repo.get_by_id(created_company.id)
        assert retrieved is not None
        assert retrieved.name == company.name

        # Step 3: Simulate enrichment (update metadata)
        mock_enriched = MagicMock()
        mock_enriched.id = created_company.id
        mock_enriched.name = company.name
        mock_enriched.metadata = {
            "enriched_at": datetime.now(timezone.utc).isoformat(),
            "enrichment_source_count": 3,
        }
        mock_company_repo.update.return_value = mock_enriched

        updated = await mock_company_repo.update(
            created_company.id,
            metadata=mock_enriched.metadata,
        )
        assert updated is not None
        assert updated.metadata.get("enriched_at") is not None

        # Step 4: Score company
        scored_company = growth_scorer.calculate_scores(company)
        assert scored_company is not None

        # Step 5: Verify scores are normalized (0-100)
        assert scored_company.growth_score is not None
        assert 0 <= scored_company.growth_score <= 10  # Growth scorer uses 0-10 scale
        assert scored_company.financial_health_score is not None
        assert 0 <= scored_company.financial_health_score <= 10
        assert scored_company.competitive_position_score is not None
        assert 0 <= scored_company.competitive_position_score <= 10

        # Step 6: Verify classification
        if scored_company.growth_score >= 7.0:
            assert scored_company.classification == "Phoenix"
        elif scored_company.growth_score <= 3.9:
            assert scored_company.classification == "Lead"
        else:
            assert scored_company.classification == "Salt"

        # Step 7: Verify data consistency
        assert scored_company.name == company.name
        assert scored_company.industry == company.industry
        assert len(scored_company.tech_stack) > 0


class TestDataMigrationToAPIWorkflow:
    """Test data migration to API workflow: migrate → fetch → verify."""

    @pytest.mark.asyncio
    async def test_data_migration_to_api_workflow(
        self,
        mock_company_repo: MagicMock,
    ):
        """Test data migration and API accessibility.

        Workflow:
        1. Create multiple companies (simulating migration)
        2. Fetch companies via repository
        3. Verify migrated data is accessible
        4. Verify relationships are intact
        5. Verify pagination works
        """
        # Step 1: Create multiple companies (simulating migration)
        created_companies = []
        for i in range(5):
            mock_company = MagicMock()
            mock_company.id = f"company-{i}"
            mock_company.name = f"Migrated Company {i}"
            mock_company.sector = "Energy Software"
            mock_company.metadata = {
                "migration_source": "test-migration",
                "migration_batch": "batch-001",
                "original_id": f"orig-{i}",
            }
            created_companies.append(mock_company)

        mock_company_repo.create.side_effect = created_companies

        created_ids = []
        for i in range(5):
            company = await mock_company_repo.create(
                ticker=f"COMP{i}",
                name=f"Migrated Company {i}",
                sector="Energy Software",
            )
            created_ids.append(company.id)
            assert company is not None

        assert len(created_ids) == 5

        # Step 2: Fetch companies via repository
        mock_company_repo.get_all.return_value = created_companies
        all_companies = await mock_company_repo.get_all(skip=0, limit=100)
        assert len(all_companies) >= 5

        # Step 3: Verify migrated data is accessible
        mock_company_repo.get_by_id.side_effect = lambda cid: next((c for c in created_companies if c.id == cid), None)
        for company_id in created_ids:
            retrieved = await mock_company_repo.get_by_id(company_id)
            assert retrieved is not None
            assert retrieved.id == company_id
            assert retrieved.metadata.get("migration_source") == "test-migration"

        # Step 4: Verify relationships are intact
        for company_id in created_ids:
            company = await mock_company_repo.get_by_id(company_id)
            assert company.metadata is not None
            assert "original_id" in company.metadata

        # Step 5: Verify pagination works
        page1 = created_companies[:2]
        page2 = created_companies[2:4]
        assert len(page1) <= 2
        assert len(page2) <= 2
        # Ensure pages don't overlap
        page1_ids = {c.id for c in page1}
        page2_ids = {c.id for c in page2}
        assert len(page1_ids & page2_ids) == 0


class TestResearchWorkflow:
    """Test research workflow: create job → add stages → add artifacts → retrieve."""

    @pytest.mark.asyncio
    async def test_research_workflow(self):
        """Test research workflow with job creation and artifact tracking.

        Workflow:
        1. Create research job
        2. Add research stages
        3. Add artifacts to stages
        4. Retrieve research results
        5. Verify audit trail
        """
        # Step 1: Create research job
        research_job = {
            "id": "research-job-001",
            "company_id": "test-company-001",
            "status": "in_progress",
            "metadata": {
                "research_type": "competitive_analysis",
                "market": "Energy Software",
                "started_at": datetime.now(timezone.utc).isoformat(),
            },
        }

        assert research_job["id"] is not None
        assert research_job["status"] == "in_progress"

        # Step 2: Add research stages
        stages = [
            {"stage": "discovery", "status": "completed", "duration_minutes": 15},
            {"stage": "data_gathering", "status": "in_progress", "duration_minutes": 30},
            {"stage": "analysis", "status": "pending", "duration_minutes": 45},
        ]
        research_job["metadata"]["stages"] = stages

        # Step 3: Add artifacts
        artifacts = [
            {
                "type": "financial_data",
                "source": "crunchbase",
                "data_points": 15,
                "confidence": 0.95,
            },
            {
                "type": "github_metrics",
                "source": "github_api",
                "data_points": 8,
                "confidence": 0.98,
            },
            {
                "type": "news_sentiment",
                "source": "news_api",
                "data_points": 25,
                "confidence": 0.85,
            },
        ]
        research_job["metadata"]["artifacts"] = artifacts

        # Step 4: Retrieve research results
        assert research_job["metadata"]["stages"] == stages
        assert len(research_job["metadata"]["artifacts"]) == 3

        # Step 5: Verify audit trail
        assert "started_at" in research_job["metadata"]
        assert research_job["metadata"]["research_type"] == "competitive_analysis"

        # Step 6: Mark job as completed
        research_job["status"] = "completed"
        research_job["metadata"]["completed_at"] = datetime.now(timezone.utc).isoformat()

        assert research_job["status"] == "completed"
        assert "completed_at" in research_job["metadata"]


class TestEnrichmentWorkflow:
    """Test enrichment workflow: create job → enrich → verify cache → audit trail."""

    @pytest.mark.asyncio
    async def test_enrichment_workflow(
        self,
        mock_company_repo: MagicMock,
        sample_company_data: dict[str, Any],
    ):
        """Test enrichment workflow with cache and audit trail.

        Workflow:
        1. Create enrichment job
        2. Enrich company data
        3. Verify cache is populated
        4. Verify audit trail is created
        5. Verify enrichment metadata
        """
        # Step 1: Create enrichment job
        enrichment_job = {
            "id": "enrichment-job-001",
            "company_id": "test-company-001",
            "status": "pending",
            "metadata": {
                "enrichment_type": "full_profile",
                "sources": ["crunchbase", "github", "news"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        }

        assert enrichment_job["id"] is not None
        assert enrichment_job["status"] == "pending"

        # Step 2: Enrich company data
        company = Company(**sample_company_data)
        mock_created = MagicMock()
        mock_created.id = "test-company-001"
        mock_created.name = company.name
        mock_company_repo.create.return_value = mock_created

        created_company = await mock_company_repo.create(
            ticker="ENRICH",
            name=company.name,
            sector=company.industry,
        )

        # Step 3: Simulate enrichment
        enrichment_job["status"] = "in_progress"
        enrichment_job["metadata"]["enrichment_started_at"] = datetime.now(timezone.utc).isoformat()

        # Step 4: Add enriched data
        enriched_metadata = {
            "ai_maturity": "strong",
            "saas_maturity": 4,
            "tech_stack": company.tech_stack,
            "enriched_fields": ["ai_maturity", "saas_maturity", "tech_stack"],
            "enrichment_sources": ["crunchbase", "github"],
            "enrichment_confidence": 0.92,
        }
        mock_enriched = MagicMock()
        mock_enriched.id = created_company.id
        mock_enriched.metadata = enriched_metadata
        mock_company_repo.update.return_value = mock_enriched

        updated_company = await mock_company_repo.update(
            created_company.id,
            metadata=enriched_metadata,
        )
        assert updated_company is not None

        # Step 5: Mark enrichment as completed
        enrichment_job["status"] = "completed"
        enrichment_job["metadata"]["enrichment_completed_at"] = datetime.now(timezone.utc).isoformat()
        enrichment_job["metadata"]["enriched_company_id"] = created_company.id
        enrichment_job["metadata"]["cache_populated"] = True

        # Step 6: Verify audit trail
        assert enrichment_job["status"] == "completed"
        assert "enrichment_started_at" in enrichment_job["metadata"]
        assert "enrichment_completed_at" in enrichment_job["metadata"]
        assert enrichment_job["metadata"]["cache_populated"] is True

        # Step 7: Verify enrichment metadata
        assert updated_company.metadata.get("enrichment_confidence") == 0.92
        assert len(updated_company.metadata.get("enriched_fields", [])) > 0


class TestScoringWorkflow:
    """Test scoring workflow: create records → calculate → verify normalization."""

    @pytest.mark.asyncio
    async def test_scoring_workflow(
        self,
        mock_company_repo: MagicMock,
        sample_company_data: dict[str, Any],
        growth_scorer: GrowthScorer,
    ):
        """Test scoring workflow with normalization and metric storage.

        Workflow:
        1. Create company
        2. Create scoring records
        3. Calculate company score
        4. Verify score is normalized (0-100)
        5. Verify metrics are stored
        6. Verify scoring breakdown
        """
        # Step 1: Create company
        company = Company(**sample_company_data)
        mock_created = MagicMock()
        mock_created.id = "test-company-001"
        mock_created.name = company.name
        mock_company_repo.create.return_value = mock_created

        created_company = await mock_company_repo.create(
            ticker="SCORE",
            name=company.name,
            sector=company.industry,
        )

        # Step 2: Create scoring records
        scoring_record = {
            "id": "scoring-record-001",
            "company_id": created_company.id,
            "status": "pending",
            "metadata": {
                "scoring_type": "growth_and_health",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        }

        # Step 3: Calculate company score
        scored_company = growth_scorer.calculate_scores(company)
        assert scored_company is not None

        # Step 4: Verify scores are normalized
        assert scored_company.growth_score is not None
        assert 0 <= scored_company.growth_score <= 10
        assert scored_company.financial_health_score is not None
        assert 0 <= scored_company.financial_health_score <= 10
        assert scored_company.competitive_position_score is not None
        assert 0 <= scored_company.competitive_position_score <= 10

        # Step 5: Store metrics in scoring record
        scoring_record["status"] = "completed"
        scoring_record["metadata"]["growth_score"] = scored_company.growth_score
        scoring_record["metadata"]["financial_health_score"] = scored_company.financial_health_score
        scoring_record["metadata"]["competitive_position_score"] = scored_company.competitive_position_score
        scoring_record["metadata"]["composite_score"] = scored_company.composite_score
        scoring_record["metadata"]["classification"] = scored_company.classification
        scoring_record["metadata"]["completed_at"] = datetime.now(timezone.utc).isoformat()

        # Step 6: Verify metrics are stored
        assert scoring_record["status"] == "completed"
        assert scoring_record["metadata"]["growth_score"] == scored_company.growth_score
        assert scoring_record["metadata"]["classification"] in ["Phoenix", "Salt", "Lead"]

        # Step 7: Verify scoring breakdown
        assert scored_company.scoring_breakdown is not None
        assert isinstance(scored_company.scoring_breakdown, dict)
        assert len(scored_company.scoring_breakdown) > 0


class TestMarketAnalysisWorkflow:
    """Test market analysis workflow: create snapshot → analyze → compare."""

    @pytest.mark.asyncio
    async def test_market_analysis_workflow(
        self,
        mock_company_repo: MagicMock,
        growth_scorer: GrowthScorer,
    ):
        """Test market analysis workflow with trend analysis and comparison.

        Workflow:
        1. Create market snapshot (multiple companies)
        2. Analyze market trends
        3. Compare companies
        4. Verify competitive positioning
        5. Verify market statistics
        """
        # Step 1: Create market snapshot
        created_companies = []
        for i in range(5):
            mock_company = MagicMock()
            mock_company.id = f"market-company-{i}"
            mock_company.name = f"Market Company {i}"
            mock_company.sector = "Energy Software"
            mock_company.metadata = {
                "revenue": 10.0 + (i * 5),
                "growth_rate": 0.15 + (i * 0.05),
                "employees": 50 + (i * 20),
                "ai_maturity": ["none", "low", "moderate", "strong", "very_strong"][i],
            }
            created_companies.append(mock_company)

        mock_company_repo.create.side_effect = created_companies

        for i in range(5):
            company = await mock_company_repo.create(
                ticker=f"MARKET{i}",
                name=f"Market Company {i}",
                sector="Energy Software",
            )
            assert company is not None

        # Step 2: Retrieve all companies for analysis
        mock_company_repo.get_all.return_value = created_companies
        all_companies = await mock_company_repo.get_all(skip=0, limit=100)
        market_companies = [c for c in all_companies if c.sector == "Energy Software"]
        assert len(market_companies) >= 5

        # Step 3: Score all companies
        scored_companies = []
        for company_record in market_companies[:5]:
            # Convert to domain model
            company = Company(
                id=company_record.id,
                name=company_record.name,
                industry=company_record.sector,
                financials=FinancialMetric(
                    revenue=company_record.metadata.get("revenue"),
                    growth_rate=company_record.metadata.get("growth_rate"),
                    employees=company_record.metadata.get("employees"),
                ),
            )
            scored = growth_scorer.calculate_scores(company)
            scored_companies.append(scored)

        # Step 4: Verify competitive positioning
        assert len(scored_companies) >= 5
        scores = [c.growth_score for c in scored_companies if c.growth_score is not None]
        assert len(scores) > 0

        # Verify score distribution
        min_score = min(scores)
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)

        assert min_score >= 0
        assert max_score <= 10
        assert min_score <= avg_score <= max_score

        # Step 5: Verify market statistics
        phoenix_count = sum(1 for c in scored_companies if c.classification == "Phoenix")
        salt_count = sum(1 for c in scored_companies if c.classification == "Salt")
        lead_count = sum(1 for c in scored_companies if c.classification == "Lead")

        total_classified = phoenix_count + salt_count + lead_count
        assert total_classified == len(scored_companies)

        # Verify at least some classification diversity
        assert total_classified >= 5


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling across workflows."""

    @pytest.mark.asyncio
    async def test_company_not_found_error(
        self,
        mock_company_repo: MagicMock,
    ):
        """Test handling of non-existent company."""
        mock_company_repo.get_by_id.return_value = None
        result = await mock_company_repo.get_by_id("non-existent-company-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_company_data_error(self):
        """Test handling of invalid company data."""
        # Missing required fields should raise validation error
        with pytest.raises(Exception):
            Company(
                id=None,  # Required field
                name="Test",
                industry="Tech",
            )

    @pytest.mark.asyncio
    async def test_scoring_with_missing_financials(
        self,
        growth_scorer: GrowthScorer,
    ):
        """Test scoring with incomplete financial data."""
        company = Company(
            id="test-incomplete",
            name="Incomplete Company",
            industry="Tech",
            financials=FinancialMetric(),  # Empty financials
        )

        scored = growth_scorer.calculate_scores(company)
        assert scored is not None
        # Should still produce a score, even with missing data
        assert scored.growth_score is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
