"""
Comprehensive integration tests for data migration from JSON to PostgreSQL.

This test suite verifies that:
1. Migration script creates companies with correct data
2. Metrics and financial data are properly created
3. Relationships between entities are maintained
4. Migration is idempotent (can be run multiple times safely)
5. Data integrity is preserved throughout the process
6. Edge cases are handled correctly
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.database_config import get_test_database_url
from solstein.infrastructure.company_repository import CompanyRepository
from solstein.infrastructure.database_models import CompanyRecord
from solstein.migrations.load_competitor_data import load_competitor_data


@pytest.fixture
def test_db_url() -> str:
    """Provide test database URL in async format."""
    db_url = get_test_database_url()
    # Convert to async format for asyncpg, handling SSL parameters
    async_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    # asyncpg doesn't support sslmode in URL, it uses ssl parameter instead
    async_url = async_url.replace("?sslmode=require", "")
    return async_url


# ============================================================================
# TEST FIXTURES
# ============================================================================


@pytest.fixture
def sample_competitor_data() -> dict[str, Any]:
    """Provide sample competitor data matching the JSON structure."""
    return {
        "competitors": [
            {
                "company_name": "ACME Corp",
                "industry": "Energy Software",
                "country": "Germany",
                "founded_year": 2015,
                "employees": 150,
                "description": "Leading energy software provider",
                "website": "https://acme.de",
                "classification": "Phoenix",
                "ai_maturity": "STRONG",
                "ai_score": 8,
                "revenue": {
                    "timeline": [
                        {"year": 2020, "eur_millions": 2.0, "yoy_growth_pct": 0},
                        {"year": 2021, "eur_millions": 3.0, "yoy_growth_pct": 50},
                        {"year": 2022, "eur_millions": 4.0, "yoy_growth_pct": 33},
                        {"year": 2023, "eur_millions": 5.0, "yoy_growth_pct": 25},
                    ],
                    "cagr_3yr_pct": 40.0,
                    "cagr_5yr_pct": 25.0,
                },
                "growth_rate": 25.0,
                "profit_margin": 15.0,
                "profitability": {
                    "ebitda_margin_pct": 30.0,
                    "recurring_revenue_pct": 85.0,
                    "revenue_per_employee_eur_k": 333.0,
                },
                "funding_raised": 2000000.0,
                "valuation": 50000000.0,
            },
            {
                "company_name": "TechFlow GmbH",
                "industry": "Energy Software",
                "country": "Germany",
                "founded_year": 2016,
                "employees": 100,
                "description": "Innovative energy tech company",
                "website": "https://techflow.de",
                "classification": "Salt",
                "ai_maturity": "MODERATE",
                "ai_score": 6,
                "revenue": {
                    "timeline": [
                        {"year": 2020, "eur_millions": 1.5, "yoy_growth_pct": 0},
                        {"year": 2021, "eur_millions": 2.0, "yoy_growth_pct": 33},
                        {"year": 2022, "eur_millions": 2.5, "yoy_growth_pct": 25},
                        {"year": 2023, "eur_millions": 3.0, "yoy_growth_pct": 20},
                    ],
                    "cagr_3yr_pct": 20.0,
                    "cagr_5yr_pct": 20.0,
                },
                "growth_rate": 20.0,
                "profit_margin": 12.0,
                "profitability": {
                    "ebitda_margin_pct": 15.0,
                    "recurring_revenue_pct": 75.0,
                    "revenue_per_employee_eur_k": 300.0,
                },
                "funding_raised": 1500000.0,
                "valuation": 30000000.0,
            },
            {
                "company_name": "GreenEnergy Solutions",
                "industry": "Energy Software",
                "country": "UK",
                "founded_year": 2017,
                "employees": 80,
                "description": "Sustainable energy solutions",
                "website": "https://greenenergy.uk",
                "classification": "Lead",
                "ai_maturity": "LOW",
                "ai_score": 5,
                "revenue": {
                    "timeline": [
                        {"year": 2020, "eur_millions": 1.0, "yoy_growth_pct": 0},
                        {"year": 2021, "eur_millions": 1.2, "yoy_growth_pct": 20},
                        {"year": 2022, "eur_millions": 1.5, "yoy_growth_pct": 25},
                        {"year": 2023, "eur_millions": 2.0, "yoy_growth_pct": 33},
                    ],
                    "cagr_3yr_pct": 15.0,
                    "cagr_5yr_pct": 20.0,
                },
                "growth_rate": 15.0,
                "profit_margin": 10.0,
                "profitability": {
                    "ebitda_margin_pct": 12.0,
                    "recurring_revenue_pct": 65.0,
                    "revenue_per_employee_eur_k": 250.0,
                },
                "funding_raised": 1000000.0,
                "valuation": 20000000.0,
            },
        ]
    }


@pytest.fixture
def temp_json_file(sample_competitor_data: dict[str, Any]) -> Path:
    """Create a temporary JSON file with sample competitor data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_competitor_data, f)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink(missing_ok=True)


# ============================================================================
# TEST CASES
# ============================================================================


class TestMigrationCreatesCompanies:
    """Test that migration creates companies with correct data."""

    @pytest.mark.asyncio
    async def test_migration_creates_companies(self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str):
        """Test that migration creates 3 companies in database."""
        # Run migration
        await load_competitor_data(temp_json_file, test_db_url)

        # Verify companies created
        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        assert len(companies) == 3, f"Expected 3 companies, got {len(companies)}"

    @pytest.mark.asyncio
    async def test_migration_creates_correct_company_names(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that companies have correct names."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()
        company_names = {c.name for c in companies}

        expected_names = {"ACME Corp", "TechFlow GmbH", "GreenEnergy Solutions"}
        assert company_names == expected_names, f"Expected {expected_names}, got {company_names}"

    @pytest.mark.asyncio
    async def test_migration_creates_correct_industries(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that all companies have correct industry."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        for company in companies:
            assert company.industry == "Energy Software", f"Company {company.name} has industry {company.industry}"

    @pytest.mark.asyncio
    async def test_migration_creates_correct_classifications(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that companies have correct classifications."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        classifications = {c.name: c.classification for c in companies}

        assert classifications["ACME Corp"] == "Phoenix"
        assert classifications["TechFlow GmbH"] == "Salt"
        assert classifications["GreenEnergy Solutions"] == "Salt"


class TestMigrationCreatesMetrics:
    """Test that migration creates metrics for each company."""

    @pytest.mark.asyncio
    async def test_migration_creates_ai_scores(self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str):
        """Test that AI scores are created for each company."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        ai_scores = {c.name: c.ai_score for c in companies}

        assert ai_scores["ACME Corp"] == 8
        assert ai_scores["TechFlow GmbH"] == 6
        assert ai_scores["GreenEnergy Solutions"] == 5

    @pytest.mark.asyncio
    async def test_migration_creates_ai_maturity(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that AI maturity levels are created."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        maturity_levels = {c.name: c.ai_maturity for c in companies}

        assert maturity_levels["ACME Corp"] == "STRONG"
        assert maturity_levels["TechFlow GmbH"] == "MODERATE"
        assert maturity_levels["GreenEnergy Solutions"] == "LOW"

    @pytest.mark.asyncio
    async def test_migration_creates_employee_counts(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that employee counts are created."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        employee_counts = {c.name: c.employee_count for c in companies}

        assert employee_counts["ACME Corp"] == 150
        assert employee_counts["TechFlow GmbH"] == 100
        assert employee_counts["GreenEnergy Solutions"] == 80


class TestMigrationCreatesFinancials:
    """Test that migration creates financial data."""

    @pytest.mark.asyncio
    async def test_migration_creates_revenue_data(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that revenue data is created."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        revenues = {c.name: c.revenue_eur_m for c in companies}

        assert revenues["ACME Corp"] == 5.0
        assert revenues["TechFlow GmbH"] == 3.0
        assert revenues["GreenEnergy Solutions"] == 2.0

    @pytest.mark.asyncio
    async def test_migration_creates_growth_rates(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that growth rates are created."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        growth_rates = {c.name: c.growth_rate_pct for c in companies}

        assert growth_rates["ACME Corp"] == 0.25
        assert growth_rates["TechFlow GmbH"] == 0.20
        assert growth_rates["GreenEnergy Solutions"] == 0.15

    @pytest.mark.asyncio
    async def test_migration_creates_profit_margins(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that profit margins are created."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        margins = {c.name: c.profit_margin_pct for c in companies}

        assert margins["ACME Corp"] == 0.15
        assert margins["TechFlow GmbH"] == 0.12
        assert margins["GreenEnergy Solutions"] == 0.10

    @pytest.mark.asyncio
    async def test_migration_creates_revenue_timeline(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that revenue timeline is stored."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        acme = next(c for c in companies if c.name == "ACME Corp")
        assert acme.revenue_timeline is not None
        assert len(acme.revenue_timeline) == 4
        assert acme.revenue_timeline[-1]["eur_millions"] == 5.0

    @pytest.mark.asyncio
    async def test_migration_creates_cagr_values(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that CAGR values are created."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        acme = next(c for c in companies if c.name == "ACME Corp")
        assert acme.revenue_cagr_3yr == 40.0
        assert acme.revenue_cagr_5yr == 25.0


class TestMigrationIdempotency:
    """Test that migration is idempotent."""

    @pytest.mark.asyncio
    async def test_migration_idempotent(self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str):
        """Test that running migration twice creates no duplicates."""
        # Run migration twice
        await load_competitor_data(temp_json_file, test_db_url)
        await load_competitor_data(temp_json_file, test_db_url)

        # Verify no duplicates
        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        assert len(companies) == 3, f"Expected 3 companies, got {len(companies)}"

    @pytest.mark.asyncio
    async def test_migration_idempotent_data_consistency(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that data is consistent after running migration twice."""
        # Run migration twice
        await load_competitor_data(temp_json_file, test_db_url)
        companies_first = await db_session.execute(select(CompanyRecord))
        first_run = companies_first.scalars().all()

        await load_competitor_data(temp_json_file, test_db_url)
        companies_second = await db_session.execute(select(CompanyRecord))
        second_run = companies_second.scalars().all()

        # Verify same number of companies
        assert len(first_run) == len(second_run)

        # Verify data is identical
        for c1, c2 in zip(first_run, second_run, strict=False):
            assert c1.name == c2.name
            assert c1.revenue_eur_m == c2.revenue_eur_m
            assert c1.ai_score == c2.ai_score


class TestMigrationWithEmptyDatabase:
    """Test migration with empty database."""

    @pytest.mark.asyncio
    async def test_migration_with_empty_database(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that migration works with empty database."""
        # Verify database is empty
        result = await db_session.execute(select(CompanyRecord))
        initial_companies = result.scalars().all()
        assert len(initial_companies) == 0

        # Run migration
        await load_competitor_data(temp_json_file, test_db_url)

        # Verify all data is created
        repo = CompanyRepository(db_session)
        companies = await repo.get_all()
        assert len(companies) == 3

    @pytest.mark.asyncio
    async def test_migration_creates_all_required_fields(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that all required fields are populated."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        for company in companies:
            assert company.company_id is not None
            assert company.name is not None
            assert company.industry is not None
            assert company.classification is not None
            assert company.ai_maturity is not None
            assert company.revenue_eur_m is not None


class TestMigrationPreservesRelationships:
    """Test that relationships are preserved."""

    @pytest.mark.asyncio
    async def test_migration_preserves_company_data_integrity(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that company data integrity is maintained."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        # Verify each company has consistent data
        for company in companies:
            # Revenue should match latest timeline entry
            if company.revenue_timeline:
                latest_revenue = company.revenue_timeline[-1].get("eur_millions")
                assert company.revenue_eur_m == latest_revenue

    @pytest.mark.asyncio
    async def test_migration_preserves_profitability_metrics(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that profitability metrics are preserved."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        acme = next(c for c in companies if c.name == "ACME Corp")
        assert acme.ebitda_margin_pct == 30.0
        assert acme.recurring_revenue_pct == 85.0
        assert acme.revenue_per_employee_eur_k == 333.0

    @pytest.mark.asyncio
    async def test_migration_preserves_funding_data(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that funding data is preserved."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        acme = next(c for c in companies if c.name == "ACME Corp")
        assert acme.total_funding_raised_eur == 2000000.0
        assert acme.latest_valuation_eur == 50000000.0


class TestMigrationEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_migration_with_missing_optional_fields(self, db_session: AsyncSession, test_db_url: str):
        """Test migration handles missing optional fields gracefully."""
        minimal_data = {
            "competitors": [
                {
                    "company_name": "Minimal Corp",
                    "industry": "Energy Software",
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(minimal_data, f)
            temp_path = Path(f.name)

        try:
            await load_competitor_data(temp_path, test_db_url)

            repo = CompanyRepository(db_session)
            companies = await repo.get_all()
            assert len(companies) == 1
            assert companies[0].name == "Minimal Corp"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_migration_with_nonexistent_file(self, test_db_url: str):
        """Test migration raises error for nonexistent file."""
        nonexistent_path = Path("/nonexistent/path/data.json")

        with pytest.raises(FileNotFoundError):
            import asyncio

            asyncio.run(load_competitor_data(nonexistent_path, test_db_url))

    @pytest.mark.asyncio
    async def test_migration_with_invalid_json(self, test_db_url: str):
        """Test migration raises error for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)

        try:
            with pytest.raises(json.JSONDecodeError):
                await load_competitor_data(temp_path, test_db_url)
        finally:
            temp_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_migration_with_missing_competitors_key(self, test_db_url: str):
        """Test migration raises error when 'competitors' key is missing."""
        invalid_data = {"data": []}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(invalid_data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="competitors"):
                await load_competitor_data(temp_path, test_db_url)
        finally:
            temp_path.unlink(missing_ok=True)


class TestMigrationDataQuality:
    """Test data quality after migration."""

    @pytest.mark.asyncio
    async def test_migration_creates_timestamps(self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str):
        """Test that created_at and last_updated timestamps are set."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        for company in companies:
            assert company.created_at is not None
            assert company.last_updated is not None
            assert isinstance(company.created_at, datetime)
            assert isinstance(company.last_updated, datetime)

    @pytest.mark.asyncio
    async def test_migration_sets_data_source(self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str):
        """Test that data_source is set correctly."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        for company in companies:
            assert company.data_source == "competitor_data.json"

    @pytest.mark.asyncio
    async def test_migration_numeric_fields_are_correct_type(
        self, db_session: AsyncSession, temp_json_file: Path, test_db_url: str
    ):
        """Test that numeric fields have correct types."""
        await load_competitor_data(temp_json_file, test_db_url)

        repo = CompanyRepository(db_session)
        companies = await repo.get_all()

        acme = next(c for c in companies if c.name == "ACME Corp")

        assert isinstance(acme.revenue_eur_m, (int, float))
        assert isinstance(acme.growth_rate_pct, (int, float))
        assert isinstance(acme.ai_score, int)
        assert isinstance(acme.employee_count, int)
