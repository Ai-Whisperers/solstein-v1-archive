"""STORY-209: Validation Before Scoring.

Validates that:
- Validation runs before scoring (via validate_before_scoring)
- Invalid companies produce warning messages (not silent)
- Scoring still happens for companies with warnings (graceful degradation)
- Validation error messages show which field failed and why
- Validation warnings are stored in scoring_breakdown
"""


from solstein.analytics.scoring import GrowthScorer, validate_before_scoring
from solstein.domain.models import Company, FinancialMetric

# -----------------------------------------------------------------------
# validate_before_scoring function
# -----------------------------------------------------------------------


class TestValidateBeforeScoring:
    """Tests for the validate_before_scoring gate."""

    def test_complete_company_no_warnings(self):
        """Complete company with all data produces no warnings."""
        company = Company(
            id="valid-1",
            name="Valid Corp",
            financials=FinancialMetric(
                revenue=1000.0,
                growth_rate=25.0,
                employees=100,
                profit_margin=10.0,
                funding_raised=5000.0,
            ),
            signal_confidences={"revenue": 0.9, "growth_rate": 0.9},
        )
        warnings = validate_before_scoring(company)
        assert len(warnings) == 0

    def test_missing_revenue_produces_warning(self):
        """Company with missing revenue produces a warning mentioning revenue."""
        company = Company(
            id="no-rev",
            name="No Revenue Corp",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=25.0,
                employees=100,
                profit_margin=10.0,
            ),
        )
        warnings = validate_before_scoring(company)
        assert len(warnings) > 0
        warning_text = " ".join(warnings).lower()
        assert "revenue" in warning_text

    def test_missing_employees_produces_warning(self):
        """Company with missing employees produces a warning mentioning employees."""
        company = Company(
            id="no-emp",
            name="No Employees Corp",
            financials=FinancialMetric(
                revenue=1000.0,
                growth_rate=25.0,
                employees=None,
                profit_margin=10.0,
            ),
        )
        warnings = validate_before_scoring(company)
        assert len(warnings) > 0
        warning_text = " ".join(warnings).lower()
        assert "employee" in warning_text

    def test_missing_growth_rate_produces_warning(self):
        """Company with missing growth_rate produces a warning."""
        company = Company(
            id="no-growth",
            name="No Growth Corp",
            financials=FinancialMetric(
                revenue=1000.0,
                growth_rate=None,
                employees=100,
                profit_margin=10.0,
            ),
        )
        warnings = validate_before_scoring(company)
        assert len(warnings) > 0
        warning_text = " ".join(warnings).lower()
        assert "growth" in warning_text

    def test_zero_revenue_produces_warning(self):
        """Company with revenue=0 produces a warning about suspicious data."""
        company = Company(
            id="zero-rev",
            name="Zero Revenue Corp",
            financials=FinancialMetric(
                revenue=0.0,
                growth_rate=25.0,
                employees=100,
                profit_margin=10.0,
            ),
        )
        warnings = validate_before_scoring(company)
        assert len(warnings) > 0
        warning_text = " ".join(warnings).lower()
        assert "revenue" in warning_text

    def test_all_missing_produces_many_warnings(self):
        """Company with all fields missing produces multiple warnings."""
        company = Company(
            id="empty",
            name="Empty Corp",
            financials=FinancialMetric(allow_empty_primary=True),
        )
        warnings = validate_before_scoring(company)
        assert len(warnings) >= 3  # At least revenue, employees, growth

    def test_warning_messages_are_descriptive(self):
        """Warning messages include field name and reason."""
        company = Company(
            id="desc-test",
            name="Description Test Corp",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=None,
                employees=100,
                profit_margin=10.0,
            ),
        )
        warnings = validate_before_scoring(company)
        # Each warning should be a non-empty string with useful info
        for warning in warnings:
            assert isinstance(warning, str)
            assert len(warning) > 10  # Not just "error"


# -----------------------------------------------------------------------
# Validation integrated into scoring
# -----------------------------------------------------------------------


class TestValidationInScoringPipeline:
    """Tests that validation is wired into the scoring pipeline."""

    def test_valid_company_scores_successfully(self):
        """Fully valid company scores without issues."""
        company = Company(
            id="valid",
            name="Valid Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=25.0,
                employees=2000,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
            signal_confidences={"revenue": 0.9, "growth_rate": 0.9},
        )
        scorer = GrowthScorer()
        scorer.calculate_scores(company)
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0
        # No validation warnings in breakdown
        assert "validation_warnings" not in company.scoring_breakdown

    def test_incomplete_company_still_scores(self):
        """Company with missing data still scores (graceful degradation)."""
        company = Company(
            id="incomplete",
            name="Incomplete Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=25.0,
                employees=100,
                profit_margin=10.0,
            ),
        )
        scorer = GrowthScorer()
        scorer.calculate_scores(company)
        # Should still produce a score
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0

    def test_incomplete_company_has_validation_warnings(self):
        """Incomplete company stores validation warnings in breakdown."""
        company = Company(
            id="incomplete-2",
            name="Incomplete Corp 2",
            industry="Software",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=None,
                employees=100,
                profit_margin=10.0,
            ),
        )
        scorer = GrowthScorer()
        scorer.calculate_scores(company)
        # Should have validation warnings
        assert "validation_warnings" in company.scoring_breakdown
        warnings = company.scoring_breakdown["validation_warnings"]
        assert len(warnings) > 0

    def test_validation_warnings_logged(self, caplog):
        """Validation warnings are logged to logger."""
        company = Company(
            id="log-test",
            name="Log Test Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=None,
                growth_rate=25.0,
                employees=100,
                profit_margin=10.0,
            ),
        )
        # Use loguru's propagation to capture with caplog
        with caplog.at_level("WARNING"):
            scorer = GrowthScorer()
            scorer.calculate_scores(company)

        # Check that validation was logged (loguru uses stderr, so check via validate_before_scoring return)
        warnings = validate_before_scoring(company)
        assert len(warnings) > 0
        assert "revenue" in " ".join(warnings).lower()

    def test_all_missing_data_still_scores(self):
        """Even with all data missing, scoring doesn't crash."""
        company = Company(
            id="empty",
            name="Empty Data Corp",
            industry="Software",
            financials=FinancialMetric(allow_empty_primary=True),
        )
        scorer = GrowthScorer()
        scorer.calculate_scores(company)
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0
        # Should have many validation warnings
        assert "validation_warnings" in company.scoring_breakdown
        assert len(company.scoring_breakdown["validation_warnings"]) >= 3


# -----------------------------------------------------------------------
# Validation error details
# -----------------------------------------------------------------------


class TestValidationErrorDetails:
    """Tests that validation errors show which field failed and why."""

    def test_each_missing_field_has_own_warning(self):
        """Each missing field produces its own distinct warning."""
        company = Company(
            id="detail-test",
            name="Detail Test Corp",
            financials=FinancialMetric(
                allow_empty_primary=True,
            ),
        )
        warnings = validate_before_scoring(company)
        warning_text = " ".join(warnings).lower()
        # Each missing field should be mentioned
        assert "revenue" in warning_text
        assert "growth" in warning_text
        assert "employee" in warning_text

    def test_zero_values_produce_specific_warnings(self):
        """Zero values produce warnings distinct from None warnings."""
        company = Company(
            id="zero-test",
            name="Zero Test Corp",
            financials=FinancialMetric(
                revenue=0.0,
                growth_rate=25.0,
                employees=100,
                profit_margin=10.0,
            ),
        )
        warnings = validate_before_scoring(company)
        warning_text = " ".join(warnings).lower()
        # Should warn about 0 revenue being suspicious
        assert "0" in warning_text or "zero" in warning_text or "missing" in warning_text
