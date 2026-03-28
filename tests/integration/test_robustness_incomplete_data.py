"""STORY-210: Robustness Tests for Incomplete Data Inputs.

Integration tests verifying the scoring pipeline handles incomplete,
missing, and edge-case data gracefully without crashing.

Validates that:
- Companies with individual None fields score with warnings
- Companies with all fields None still produce a score
- Negative and extreme growth rates are handled
- Mixed batches (complete + incomplete) all score
- Validation warnings are logged for each issue
- Export-style access to scored data doesn't crash
"""

from solstein.analytics.scoring import GrowthScorer, validate_before_scoring
from solstein.domain.models import Company, FinancialMetric

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_complete_company(id_suffix: str = "1") -> Company:
    """Create a fully populated company for comparison."""
    return Company(
        id=f"complete-{id_suffix}",
        name=f"Complete Corp {id_suffix}",
        industry="Software",
        financials=FinancialMetric(
            revenue=500.0,
            growth_rate=25.0,
            employees=2000,
            profit_margin=15.0,
            funding_raised=100.0,
        ),
    )


def _score(company: Company) -> Company:
    """Score a company and return it."""
    scorer = GrowthScorer()
    scorer.calculate_scores(company)
    return company


# ---------------------------------------------------------------------------
# Scenario 1: Company with None growth_rate
# ---------------------------------------------------------------------------


class TestNoneGrowthRate:
    """Company with None growth_rate but valid other fields."""

    def test_validation_detects_missing_growth_rate(self):
        """validate_before_scoring warns about missing growth_rate."""
        company = Company(
            id="no-growth",
            name="No Growth Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=None,
                employees=2000,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
        )
        warnings = validate_before_scoring(company)
        warning_text = " ".join(warnings).lower()
        assert "growth" in warning_text

    def test_scores_with_reduced_score(self):
        """Still produces a valid score, lower than a complete company."""
        incomplete = Company(
            id="no-growth",
            name="No Growth Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=None,
                employees=2000,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
        )
        complete = _make_complete_company()

        _score(incomplete)
        _score(complete)

        assert incomplete.composite_score is not None
        assert 0.0 <= incomplete.composite_score <= 10.0
        # Missing growth_rate should reduce growth_score
        assert incomplete.growth_score <= complete.growth_score

    def test_has_validation_warnings_in_breakdown(self):
        """Validation warnings stored in scoring_breakdown."""
        company = Company(
            id="no-growth",
            name="No Growth Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=None,
                employees=2000,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
        )
        _score(company)
        assert "validation_warnings" in company.scoring_breakdown
        assert len(company.scoring_breakdown["validation_warnings"]) > 0


# ---------------------------------------------------------------------------
# Scenario 2: Company with None revenue
# ---------------------------------------------------------------------------


class TestNoneRevenue:
    """Company with None revenue but valid other fields."""

    def test_validation_detects_missing_revenue(self):
        """validate_before_scoring warns about missing revenue."""
        company = Company(
            id="no-rev",
            name="No Revenue Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=25.0,
                employees=2000,
                profit_margin=15.0,
            ),
        )
        warnings = validate_before_scoring(company)
        warning_text = " ".join(warnings).lower()
        assert "revenue" in warning_text

    def test_scores_without_crash(self):
        """Produces a valid score despite missing revenue."""
        company = Company(
            id="no-rev",
            name="No Revenue Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=25.0,
                employees=2000,
                profit_margin=15.0,
            ),
        )
        _score(company)
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0


# ---------------------------------------------------------------------------
# Scenario 3: Company with ALL financial fields None
# ---------------------------------------------------------------------------


class TestAllFieldsNone:
    """Company with every financial field set to None."""

    def test_validation_produces_many_warnings(self):
        """All-None company produces warnings for each missing field."""
        company = Company(
            id="all-none",
            name="All None Corp",
            industry="Software",
            financials=FinancialMetric(allow_empty_primary=True),
        )
        warnings = validate_before_scoring(company)
        assert len(warnings) >= 3  # revenue, employees, growth at minimum

    def test_still_scores(self):
        """Even with all data missing, scoring doesn't crash."""
        company = Company(
            id="all-none",
            name="All None Corp",
            industry="Software",
            financials=FinancialMetric(allow_empty_primary=True),
        )
        _score(company)
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0

    def test_breakdown_has_warnings(self):
        """Scoring breakdown contains validation warnings."""
        company = Company(
            id="all-none",
            name="All None Corp",
            industry="Software",
            financials=FinancialMetric(allow_empty_primary=True),
        )
        _score(company)
        assert "validation_warnings" in company.scoring_breakdown
        warnings = company.scoring_breakdown["validation_warnings"]
        assert len(warnings) >= 3


# ---------------------------------------------------------------------------
# Scenario 4: Negative growth rate
# ---------------------------------------------------------------------------


class TestNegativeGrowthRate:
    """Company with negative growth rate."""

    def test_negative_growth_scores_low(self):
        """Negative growth rate produces a low but valid growth score."""
        company = Company(
            id="neg-growth",
            name="Declining Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=-20.0,
                employees=2000,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
        )
        _score(company)
        assert company.growth_score is not None
        assert 0.0 <= company.growth_score <= 10.0
        # Negative growth should produce a low growth score
        assert company.growth_score < 5.0

    def test_extreme_negative_growth_doesnt_crash(self):
        """Very negative growth rate (-100%) doesn't crash."""
        company = Company(
            id="extreme-neg",
            name="Collapsing Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=-100.0,
                employees=2000,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
        )
        _score(company)
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0


# ---------------------------------------------------------------------------
# Scenario 5: Growth rate > 100%
# ---------------------------------------------------------------------------


class TestHighGrowthRate:
    """Company with very high growth rate (hypergrowth)."""

    def test_hypergrowth_scores_high(self):
        """Growth rate of 200% scores high but is clamped to [0, 10]."""
        company = Company(
            id="hyper",
            name="Hypergrowth Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=200.0,
                employees=2000,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
        )
        _score(company)
        assert company.growth_score is not None
        assert 0.0 <= company.growth_score <= 10.0
        # 200% growth should score well above median
        assert company.growth_score > 3.0

    def test_extreme_growth_clamped(self):
        """Growth rate of 999% doesn't produce score > 10."""
        company = Company(
            id="extreme-high",
            name="Rocket Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=999.0,
                employees=2000,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
        )
        _score(company)
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0


# ---------------------------------------------------------------------------
# Scenario 6: Mixed batch (50% complete, 50% incomplete)
# ---------------------------------------------------------------------------


class TestMixedBatch:
    """Mixed batch of complete and incomplete companies."""

    def test_all_companies_score(self):
        """All companies in a mixed batch produce valid scores."""
        companies = [
            _make_complete_company("1"),
            Company(
                id="incomplete-1",
                name="Incomplete 1",
                industry="Software",
                financials=FinancialMetric(
                    revenue=None,
                    growth_rate=25.0,
                    employees=100,
                    profit_margin=10.0,
                ),
            ),
            _make_complete_company("2"),
            Company(
                id="incomplete-2",
                name="Incomplete 2",
                industry="Software",
                financials=FinancialMetric(
                    revenue=300.0,
                    growth_rate=None,
                    employees=500,
                    profit_margin=12.0,
                    funding_raised=50.0,
                ),
            ),
        ]

        scorer = GrowthScorer()
        for company in companies:
            scorer.calculate_scores(company)

        for company in companies:
            assert company.composite_score is not None, f"{company.name} has no score"
            assert 0.0 <= company.composite_score <= 10.0, (
                f"{company.name} score out of range: {company.composite_score}"
            )

    def test_complete_companies_score_higher(self):
        """Complete companies generally score higher than incomplete ones."""
        complete = _make_complete_company("cmp")
        incomplete = Company(
            id="incomplete-cmp",
            name="Incomplete For Compare",
            industry="Software",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=None,
                employees=100,
                profit_margin=10.0,
            ),
        )

        _score(complete)
        _score(incomplete)

        # Complete company should have higher composite score
        assert complete.composite_score > incomplete.composite_score

    def test_incomplete_companies_have_warnings(self):
        """Incomplete companies in the batch have validation warnings."""
        incomplete = Company(
            id="incomplete-warn",
            name="Incomplete With Warnings",
            industry="Software",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=None,
                employees=100,
                profit_margin=10.0,
            ),
        )
        _score(incomplete)
        assert "validation_warnings" in incomplete.scoring_breakdown
        assert len(incomplete.scoring_breakdown["validation_warnings"]) > 0


# ---------------------------------------------------------------------------
# Scenario 7: Completely empty company
# ---------------------------------------------------------------------------


class TestCompletelyEmptyCompany:
    """Company with minimal data — all financials None."""

    def test_empty_company_scores(self):
        """Company with all-None financials still produces a score."""
        company = Company(
            id="empty",
            name="Empty Corp",
            industry="Software",
            financials=FinancialMetric(allow_empty_primary=True),
        )
        _score(company)
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0

    def test_empty_company_has_all_score_types(self):
        """Even empty company has growth, financial, competitive scores set."""
        company = Company(
            id="empty",
            name="Empty Corp",
            industry="Software",
            financials=FinancialMetric(allow_empty_primary=True),
        )
        _score(company)
        assert company.growth_score is not None
        assert company.financial_health_score is not None
        assert company.competitive_position_score is not None

    def test_empty_company_breakdown_accessible(self):
        """scoring_breakdown is populated and accessible (export-safe)."""
        company = Company(
            id="empty",
            name="Empty Corp",
            industry="Software",
            financials=FinancialMetric(allow_empty_primary=True),
        )
        _score(company)
        assert "growth" in company.scoring_breakdown
        assert "financial" in company.scoring_breakdown
        assert "competitive" in company.scoring_breakdown
        # Each breakdown is a ScoringExplanation with accessible fields
        for key in ("growth", "financial", "competitive"):
            expl = company.scoring_breakdown[key]
            assert hasattr(expl, "base_score")
            assert hasattr(expl, "components")
            assert hasattr(expl, "final_score")


# ---------------------------------------------------------------------------
# Scenario 8: Zero values (edge case)
# ---------------------------------------------------------------------------


class TestZeroValues:
    """Companies with zero values in key fields."""

    def test_zero_revenue_scores(self):
        """Company with revenue=0 still scores."""
        company = Company(
            id="zero-rev",
            name="Zero Revenue Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=0.0,
                growth_rate=25.0,
                employees=100,
                profit_margin=10.0,
            ),
        )
        _score(company)
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0

    def test_zero_employees_scores(self):
        """Company with employees=0 still scores."""
        company = Company(
            id="zero-emp",
            name="Zero Employees Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=25.0,
                employees=0,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
        )
        _score(company)
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0

    def test_zero_growth_rate_scores(self):
        """Company with growth_rate=0 still scores."""
        company = Company(
            id="zero-growth",
            name="Flat Growth Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=0.0,
                employees=2000,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
        )
        _score(company)
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0


# ---------------------------------------------------------------------------
# Scenario 9: Export-style data access after scoring
# ---------------------------------------------------------------------------


class TestExportSafeAccess:
    """Verify scored data is accessible without crashes (export simulation)."""

    def test_incomplete_company_dict_access(self):
        """Accessing scored company attributes for export doesn't crash."""
        company = Company(
            id="export-test",
            name="Export Test Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=None,
                employees=100,
                profit_margin=10.0,
            ),
        )
        _score(company)

        # Simulate export field access
        export_row = {
            "id": company.id,
            "name": company.name,
            "composite_score": company.composite_score,
            "growth_score": company.growth_score,
            "financial_health_score": company.financial_health_score,
            "competitive_position_score": company.competitive_position_score,
            "revenue": company.financials.revenue,
            "growth_rate": company.financials.growth_rate,
            "employees": company.financials.employees,
        }
        # All values should be accessible (None is fine)
        assert export_row["id"] == "export-test"
        assert export_row["composite_score"] is not None

    def test_narrative_generation_on_incomplete(self):
        """format_narrative() works on scored incomplete company."""
        company = Company(
            id="narrative-test",
            name="Narrative Test Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=None,
                employees=100,
                profit_margin=10.0,
            ),
        )
        _score(company)

        # Growth explanation should have format_narrative
        growth_expl = company.scoring_breakdown["growth"]
        narrative = growth_expl.format_narrative()
        assert isinstance(narrative, str)
        assert len(narrative) > 10
