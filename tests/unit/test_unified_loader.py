"""
Task 2: Unit Tests for Unified Company Loader

Tests the merge logic for JSON and Markdown data sources with conflict resolution.
Priority: Markdown > JSON (when conflicts exist)

Test Coverage:
- Load JSON companies only
- Load Markdown companies only
- Merge companies with no conflicts
- Merge companies with conflicts (Markdown priority)
- Handle missing Markdown companies
- Handle missing JSON companies
- Track data sources correctly
- Document merge conflicts
"""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from solstein.data.unified_loader import UnifiedCompany, UnifiedCompanyLoader
from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)
from tests.factories import make_company, make_financial_metric


class TestUnifiedCompanyModel:
    """Test the UnifiedCompany extended model."""

    def test_unified_company_has_data_source_tracking(self):
        """UnifiedCompany should track where each field came from."""
        company = UnifiedCompany(
            id="test-1",
            name="Test Corp",
            data_source_per_field={"revenue": "Markdown", "growth_rate": "JSON"},
            merge_conflicts=["revenue"],
        )
        assert company.data_source_per_field == {"revenue": "Markdown", "growth_rate": "JSON"}
        assert company.merge_conflicts == ["revenue"]

    def test_unified_company_has_merge_timestamp(self):
        """UnifiedCompany should record when merge occurred."""
        now = datetime.now(timezone.utc)
        company = UnifiedCompany(
            id="test-1",
            name="Test Corp",
            merge_timestamp=now,
        )
        assert company.merge_timestamp == now

    def test_unified_company_inherits_from_company(self):
        """UnifiedCompany should be a valid Company subclass."""
        company = UnifiedCompany(
            id="test-1",
            name="Test Corp",
            tier=CompanyTier.TIER_2,
            ai_maturity=AIMaturity.STRONG,
        )
        assert isinstance(company, Company)
        assert company.tier == CompanyTier.TIER_2
        assert company.ai_maturity == AIMaturity.STRONG


class TestUnifiedCompanyLoaderInit:
    """Test UnifiedCompanyLoader initialization."""

    def test_loader_initializes_with_json_loader(self):
        """Loader should initialize with CompetitorDataLoader."""
        loader = UnifiedCompanyLoader()
        assert loader.json_loader is not None

    def test_loader_initializes_with_markdown_extractor(self):
        """Loader should initialize with MarkdownExtractor."""
        loader = UnifiedCompanyLoader()
        assert loader.markdown_extractor is not None

    def test_loader_sets_markdown_directory(self):
        """Loader should set markdown_dir to dutch_market."""
        loader = UnifiedCompanyLoader()
        assert loader.markdown_dir.name == "dutch_market"
        assert "custom_market_runs" in str(loader.markdown_dir)


class TestLoadMarkdownCompanies:
    """Test loading Markdown companies."""

    def test_load_markdown_companies_returns_list(self):
        """_load_markdown_companies should return a list."""
        loader = UnifiedCompanyLoader()
        with patch.object(loader.markdown_extractor, "extract_from_file", return_value=None):
            result = loader._load_markdown_companies()
            assert isinstance(result, list)

    def test_load_markdown_companies_handles_missing_directory(self):
        """_load_markdown_companies should handle missing directory gracefully."""
        loader = UnifiedCompanyLoader()
        with patch.object(loader, "markdown_dir") as mock_dir:
            mock_dir.exists.return_value = False
            result = loader._load_markdown_companies()
            assert result == []

    def test_load_markdown_companies_processes_md_files(self):
        """_load_markdown_companies should process all .md files."""
        loader = UnifiedCompanyLoader()

        # Create mock companies
        mock_company_1 = make_company(id="eneve", name="Eneve")
        mock_company_2 = make_company(id="dexter", name="Dexter Energy")

        # Mock the extraction process
        with patch.object(loader, "markdown_dir") as mock_dir:
            mock_dir.exists.return_value = True
            mock_dir.glob.return_value = [
                Path("eneve.md"),
                Path("dexter-energy.md"),
            ]

            with (
                patch.object(
                    loader.markdown_extractor,
                    "extract_from_file",
                    side_effect=[
                        {"name": "Eneve"},
                        {"name": "Dexter Energy"},
                    ],
                ),
                patch.object(
                    loader.markdown_extractor,
                    "to_company_profile",
                    side_effect=[mock_company_1, mock_company_2],
                ),
            ):
                result = loader._load_markdown_companies()
                assert len(result) == 2
                assert result[0].id == "eneve"
                assert result[1].id == "dexter"

    def test_load_markdown_companies_handles_extraction_errors(self):
        """_load_markdown_companies should skip files that fail to extract."""
        loader = UnifiedCompanyLoader()
        mock_company = make_company(id="eneve", name="Eneve")

        with patch.object(loader, "markdown_dir") as mock_dir:
            mock_dir.exists.return_value = True
            mock_dir.glob.return_value = [
                Path("eneve.md"),
                Path("bad-file.md"),
            ]

            # First succeeds, second raises exception
            with (
                patch.object(
                    loader.markdown_extractor,
                    "extract_from_file",
                    side_effect=[
                        {"name": "Eneve"},
                        Exception("Parse error"),
                    ],
                ),
                patch.object(
                    loader.markdown_extractor,
                    "to_company_profile",
                    return_value=mock_company,
                ),
            ):
                result = loader._load_markdown_companies()
                # Should only have the successful one
                assert len(result) == 1


class TestConvertToUnified:
    """Test converting Company to UnifiedCompany."""

    def test_convert_json_company_to_unified(self):
        """_convert_to_unified should mark all fields as JSON source."""
        loader = UnifiedCompanyLoader()
        company = make_company(id="test-1", name="Test Corp")

        unified = loader._convert_to_unified(company, source="JSON")

        assert isinstance(unified, UnifiedCompany)
        assert unified.data_source_per_field["revenue"] == "JSON"
        assert unified.data_source_per_field["growth_rate"] == "JSON"
        assert unified.data_source_per_field["employees"] == "JSON"
        assert unified.merge_conflicts == []

    def test_convert_markdown_company_to_unified(self):
        """_convert_to_unified should mark all fields as Markdown source."""
        loader = UnifiedCompanyLoader()
        company = make_company(id="eneve", name="Eneve")

        unified = loader._convert_to_unified(company, source="Markdown")

        assert isinstance(unified, UnifiedCompany)
        assert unified.data_source_per_field["revenue"] == "Markdown"
        assert unified.data_source_per_field["tier"] == "Markdown"
        assert unified.merge_conflicts == []

    def test_convert_sets_merge_timestamp(self):
        """_convert_to_unified should set merge_timestamp."""
        loader = UnifiedCompanyLoader()
        company = make_company(id="test-1")

        before = datetime.now(timezone.utc)
        unified = loader._convert_to_unified(company, source="JSON")
        after = datetime.now(timezone.utc)

        assert before <= unified.merge_timestamp <= after


class TestMergeFinancials:
    """Test merging financial metrics."""

    def test_merge_financials_no_conflicts(self):
        """_merge_financials should use JSON when Markdown values match."""
        loader = UnifiedCompanyLoader()

        json_fin = make_financial_metric(
            revenue=100.0,
            growth_rate=15.0,
            employees=50,
        )
        markdown_fin = make_financial_metric(
            revenue=100.0,
            growth_rate=15.0,
            employees=50,
        )

        conflicts = []
        data_sources = {}

        merged = loader._merge_financials(json_fin, markdown_fin, conflicts, data_sources)

        assert merged.revenue == 100.0
        assert merged.growth_rate == 15.0
        assert merged.employees == 50
        assert conflicts == []
        assert data_sources["revenue"] == "JSON"
        assert data_sources["growth_rate"] == "JSON"

    def test_merge_financials_markdown_priority_revenue(self):
        """_merge_financials should use Markdown revenue when different."""
        loader = UnifiedCompanyLoader()

        json_fin = make_financial_metric(revenue=100.0)
        markdown_fin = make_financial_metric(revenue=120.0)

        conflicts = []
        data_sources = {}

        merged = loader._merge_financials(json_fin, markdown_fin, conflicts, data_sources)

        assert merged.revenue == 120.0
        assert "revenue" in conflicts
        assert data_sources["revenue"] == "Markdown"

    def test_merge_financials_markdown_priority_growth(self):
        """_merge_financials should use Markdown growth_rate when different."""
        loader = UnifiedCompanyLoader()

        json_fin = make_financial_metric(growth_rate=10.0)
        markdown_fin = make_financial_metric(growth_rate=22.0)

        conflicts = []
        data_sources = {}

        merged = loader._merge_financials(json_fin, markdown_fin, conflicts, data_sources)

        assert merged.growth_rate == 22.0
        assert "growth_rate" in conflicts
        assert data_sources["growth_rate"] == "Markdown"

    def test_merge_financials_markdown_priority_employees(self):
        """_merge_financials should use Markdown employees when different."""
        loader = UnifiedCompanyLoader()

        json_fin = make_financial_metric(employees=100)
        markdown_fin = make_financial_metric(employees=130)

        conflicts = []
        data_sources = {}

        merged = loader._merge_financials(json_fin, markdown_fin, conflicts, data_sources)

        assert merged.employees == 130
        assert "employees" in conflicts
        assert data_sources["employees"] == "Markdown"

    def test_merge_financials_ignores_none_markdown_values(self):
        """_merge_financials should ignore None values from Markdown."""
        loader = UnifiedCompanyLoader()

        json_fin = make_financial_metric(revenue=100.0)
        markdown_fin = FinancialMetric(revenue=None, allow_empty_primary=True)

        conflicts = []
        data_sources = {}

        merged = loader._merge_financials(json_fin, markdown_fin, conflicts, data_sources)

        assert merged.revenue == 100.0
        assert "revenue" not in conflicts
        assert data_sources["revenue"] == "JSON"

    def test_merge_financials_preserves_confidence_levels(self):
        """_merge_financials should preserve confidence levels from Markdown."""
        loader = UnifiedCompanyLoader()

        json_fin = make_financial_metric(revenue=100.0)
        markdown_fin = FinancialMetric(
            revenue=120.0,
            revenue_confidence=ConfidenceLevel.CONFIRMED,
        )

        conflicts = []
        data_sources = {}

        merged = loader._merge_financials(json_fin, markdown_fin, conflicts, data_sources)

        assert merged.revenue == 120.0
        assert merged.revenue_confidence == ConfidenceLevel.CONFIRMED


class TestMergeCompanies:
    """Test merging complete companies."""

    def test_merge_companies_no_conflicts(self):
        """_merge_companies should handle companies with no conflicts."""
        loader = UnifiedCompanyLoader()

        json_company = make_company(
            id="test-1",
            name="Test Corp",
            tier=CompanyTier.TIER_2,
            ai_maturity=AIMaturity.MODERATE,
        )
        markdown_company = make_company(
            id="test-1",
            name="Test Corp",
            tier=CompanyTier.TIER_2,
            ai_maturity=AIMaturity.MODERATE,
        )

        merged = loader._merge_companies(json_company, markdown_company)

        assert merged.id == "test-1"
        assert merged.name == "Test Corp"
        assert merged.merge_conflicts == []

    def test_merge_companies_tier_conflict_markdown_priority(self):
        """_merge_companies should use Markdown tier when different."""
        loader = UnifiedCompanyLoader()

        json_company = make_company(
            id="test-1",
            tier=CompanyTier.TIER_2,
        )
        markdown_company = make_company(
            id="test-1",
            tier=CompanyTier.TIER_3,
        )

        merged = loader._merge_companies(json_company, markdown_company)

        assert merged.tier == CompanyTier.TIER_3
        assert "tier" in merged.merge_conflicts
        assert merged.data_source_per_field["tier"] == "Markdown"

    def test_merge_companies_ai_maturity_conflict_markdown_priority(self):
        """_merge_companies should use Markdown ai_maturity when different."""
        loader = UnifiedCompanyLoader()

        json_company = make_company(
            id="test-1",
            ai_maturity=AIMaturity.LOW,
        )
        markdown_company = make_company(
            id="test-1",
            ai_maturity=AIMaturity.STRONG,
        )

        merged = loader._merge_companies(json_company, markdown_company)

        assert merged.ai_maturity == AIMaturity.STRONG
        assert "ai_maturity" in merged.merge_conflicts
        assert merged.data_source_per_field["ai_maturity"] == "Markdown"

    def test_merge_companies_threat_level_conflict_markdown_priority(self):
        """_merge_companies should use Markdown threat_level when different."""
        loader = UnifiedCompanyLoader()

        json_company = make_company(
            id="test-1",
            threat_level=ThreatLevel.LOW,
        )
        markdown_company = make_company(
            id="test-1",
            threat_level=ThreatLevel.HIGH,
        )

        merged = loader._merge_companies(json_company, markdown_company)

        assert merged.threat_level == ThreatLevel.HIGH
        assert "threat_level" in merged.merge_conflicts
        assert merged.data_source_per_field["threat_level"] == "Markdown"

    def test_merge_companies_geographic_presence_conflict_markdown_priority(self):
        """_merge_companies should use Markdown geographic_presence when different."""
        loader = UnifiedCompanyLoader()

        json_company = make_company(
            id="test-1",
            geographic_presence=["US", "UK"],
        )
        markdown_company = make_company(
            id="test-1",
            geographic_presence=["DE", "FR", "NL", "BE", "AT", "CH", "SE"],
        )

        merged = loader._merge_companies(json_company, markdown_company)

        assert merged.geographic_presence == ["DE", "FR", "NL", "BE", "AT", "CH", "SE"]
        assert "geographic_presence" in merged.merge_conflicts
        assert merged.data_source_per_field["geographic_presence"] == "Markdown"

    def test_merge_companies_multiple_conflicts(self):
        """_merge_companies should track multiple conflicts."""
        loader = UnifiedCompanyLoader()

        json_company = make_company(
            id="test-1",
            tier=CompanyTier.TIER_2,
            ai_maturity=AIMaturity.LOW,
            threat_level=ThreatLevel.LOW,
        )
        markdown_company = make_company(
            id="test-1",
            tier=CompanyTier.TIER_3,
            ai_maturity=AIMaturity.STRONG,
            threat_level=ThreatLevel.HIGH,
        )

        merged = loader._merge_companies(json_company, markdown_company)

        assert len(merged.merge_conflicts) == 3
        assert "tier" in merged.merge_conflicts
        assert "ai_maturity" in merged.merge_conflicts
        assert "threat_level" in merged.merge_conflicts

    def test_merge_companies_sets_timestamp(self):
        """_merge_companies should set merge_timestamp."""
        loader = UnifiedCompanyLoader()

        json_company = make_company(id="test-1")
        markdown_company = make_company(id="test-1")

        before = datetime.now(timezone.utc)
        merged = loader._merge_companies(json_company, markdown_company)
        after = datetime.now(timezone.utc)

        assert before <= merged.merge_timestamp <= after


class TestLoadUnifiedCompanies:
    """Test the main load_unified_companies method."""

    def test_load_unified_companies_returns_list(self):
        """load_unified_companies should return a list."""
        loader = UnifiedCompanyLoader()

        with (
            patch.object(loader.json_loader, "load_companies", return_value=[]),
            patch.object(loader, "_load_markdown_companies", return_value=[]),
        ):
            result = loader.load_unified_companies()
            assert isinstance(result, list)

    def test_load_unified_companies_json_only(self):
        """load_unified_companies should handle JSON-only companies."""
        loader = UnifiedCompanyLoader()

        json_company = make_company(id="test-1", name="Test Corp")

        with (
            patch.object(loader.json_loader, "load_companies", return_value=[json_company]),
            patch.object(loader, "_load_markdown_companies", return_value=[]),
        ):
            result = loader.load_unified_companies()

            assert len(result) == 1
            assert result[0].id == "test-1"
            assert result[0].data_source_per_field["revenue"] == "JSON"

    def test_load_unified_companies_markdown_only(self):
        """load_unified_companies should handle Markdown-only companies."""
        loader = UnifiedCompanyLoader()

        markdown_company = make_company(id="eneve", name="Eneve")

        with (
            patch.object(loader.json_loader, "load_companies", return_value=[]),
            patch.object(loader, "_load_markdown_companies", return_value=[markdown_company]),
        ):
            result = loader.load_unified_companies()

            assert len(result) == 1
            assert result[0].id == "eneve"
            assert result[0].data_source_per_field["revenue"] == "Markdown"

    def test_load_unified_companies_merges_overlapping(self):
        """load_unified_companies should merge overlapping companies."""
        loader = UnifiedCompanyLoader()

        json_company = make_company(
            id="eneve",
            name="Eneve",
            tier=CompanyTier.TIER_2,
            financials=make_financial_metric(revenue=32.5),
        )
        markdown_company = make_company(
            id="eneve",
            name="Eneve",
            tier=CompanyTier.TIER_3,
            financials=make_financial_metric(revenue=30.0),
        )

        with (
            patch.object(loader.json_loader, "load_companies", return_value=[json_company]),
            patch.object(loader, "_load_markdown_companies", return_value=[markdown_company]),
        ):
            result = loader.load_unified_companies()

            assert len(result) == 1
            assert result[0].id == "eneve"
            # Markdown priority: should use Markdown tier and revenue
            assert result[0].tier == CompanyTier.TIER_3
            assert result[0].financials.revenue == 30.0
            assert "tier" in result[0].merge_conflicts
            assert "revenue" in result[0].merge_conflicts

    def test_load_unified_companies_handles_multiple_companies(self):
        """load_unified_companies should handle multiple companies correctly."""
        loader = UnifiedCompanyLoader()

        json_companies = [
            make_company(id="test-1", name="Test 1"),
            make_company(id="test-2", name="Test 2"),
            make_company(id="eneve", name="Eneve"),
        ]
        markdown_companies = [
            make_company(id="eneve", name="Eneve"),
            make_company(id="dexter", name="Dexter Energy"),
        ]

        with (
            patch.object(loader.json_loader, "load_companies", return_value=json_companies),
            patch.object(loader, "_load_markdown_companies", return_value=markdown_companies),
        ):
            result = loader.load_unified_companies()

            # Should have: test-1 (JSON), test-2 (JSON), eneve (merged), dexter (Markdown)
            assert len(result) == 4

            ids = {c.id for c in result}
            assert ids == {"test-1", "test-2", "eneve", "dexter"}

            # Verify eneve is merged
            eneve = next(c for c in result if c.id == "eneve")
            assert isinstance(eneve, UnifiedCompany)


class TestEneve4CountryScenario:
    """Test the specific Eneve scenario with 4 overlapping companies."""

    def test_eneve_markdown_priority_over_json(self):
        """Eneve should use Markdown values (€30M, 22%, 130 employees) over JSON."""
        loader = UnifiedCompanyLoader()

        # JSON version: €32.5M, 44% growth, 135 employees, Salt 4.82/10
        json_eneve = make_company(
            id="eneve",
            name="Eneve",
            tier=CompanyTier.TIER_2,
            ai_maturity=AIMaturity.MODERATE,
            financials=make_financial_metric(
                revenue=32.5,
                growth_rate=44.0,
                employees=135,
            ),
        )

        # Markdown version: €30M, 22% growth, 130 employees, Strong AI
        markdown_eneve = make_company(
            id="eneve",
            name="Eneve",
            tier=CompanyTier.TIER_3,
            ai_maturity=AIMaturity.STRONG,
            financials=make_financial_metric(
                revenue=30.0,
                growth_rate=22.0,
                employees=130,
            ),
        )

        merged = loader._merge_companies(json_eneve, markdown_eneve)

        # Verify Markdown priority
        assert merged.financials.revenue == 30.0
        assert merged.financials.growth_rate == 22.0
        assert merged.financials.employees == 130
        assert merged.ai_maturity == AIMaturity.STRONG
        assert merged.tier == CompanyTier.TIER_3

        # Verify conflicts tracked
        assert "revenue" in merged.merge_conflicts
        assert "growth_rate" in merged.merge_conflicts
        assert "employees" in merged.merge_conflicts
        assert "ai_maturity" in merged.merge_conflicts
        assert "tier" in merged.merge_conflicts

    def test_all_4_dutch_companies_merge_correctly(self):
        """All 4 Dutch companies should merge with correct Markdown priority."""
        loader = UnifiedCompanyLoader()

        # Create 4 companies with JSON and Markdown versions
        companies_data = [
            ("eneve", "Eneve", 32.5, 30.0),
            ("dexter-energy", "Dexter Energy", 3.5, 3.2),
            ("energyworx", "Energyworx", 4.5, 4.2),
            ("withthegrid", "Withthegrid", 5.0, None),  # Markdown has no revenue
        ]

        json_companies = []
        markdown_companies = []

        for company_id, name, json_revenue, markdown_revenue in companies_data:
            json_company = make_company(
                id=company_id,
                name=name,
                financials=make_financial_metric(revenue=json_revenue),
            )
            json_companies.append(json_company)

            if markdown_revenue is not None:
                markdown_company = make_company(
                    id=company_id,
                    name=name,
                    financials=make_financial_metric(revenue=markdown_revenue),
                )
                markdown_companies.append(markdown_company)

        with (
            patch.object(loader.json_loader, "load_companies", return_value=json_companies),
            patch.object(loader, "_load_markdown_companies", return_value=markdown_companies),
        ):
            result = loader.load_unified_companies()

            assert len(result) == 4

            # Verify each company
            eneve = next(c for c in result if c.id == "eneve")
            assert eneve.financials.revenue == 30.0  # Markdown priority

            dexter = next(c for c in result if c.id == "dexter-energy")
            assert dexter.financials.revenue == 3.2  # Markdown priority

            energyworx = next(c for c in result if c.id == "energyworx")
            assert energyworx.financials.revenue == 4.2  # Markdown priority

            withthegrid = next(c for c in result if c.id == "withthegrid")
            assert withthegrid.financials.revenue == 5.0  # JSON (Markdown is None)
