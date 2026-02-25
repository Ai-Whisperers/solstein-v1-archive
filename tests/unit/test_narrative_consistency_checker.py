"""
Task 15: Narrative Consistency Checker - Test Suite

Tests for validating report narratives and ensuring consistency
between data, classification, and narrative tone.
"""

import pytest
from solstein.presentation.narrative_consistency_checker import NarrativeConsistencyChecker
from solstein.domain.models import Company, FinancialMetric, AIMaturity


class TestNarrativeConsistencyChecker:
    """Test narrative consistency validation."""

    @pytest.fixture
    def consistent_phoenix_company(self):
        """Phoenix company with consistent data."""
        return Company(
            id="phoenix-1",
            name="Phoenix Company",
            industry="Energy Software",
            composite_score=8.0,
            classification="Phoenix",
            ai_maturity=AIMaturity.VERY_STRONG,
            ai_score=9,
            financials=FinancialMetric(revenue=500, employees=200),
        )

    @pytest.fixture
    def consistent_salt_company(self):
        """Salt company with consistent data."""
        return Company(
            id="salt-1",
            name="Salt Company",
            industry="Energy Software",
            composite_score=5.5,
            classification="Salt",
            ai_maturity=AIMaturity.MODERATE,
            ai_score=5,
            financials=FinancialMetric(revenue=100, employees=50),
        )

    @pytest.fixture
    def consistent_lead_company(self):
        """Lead company with consistent data."""
        return Company(
            id="lead-1",
            name="Lead Company",
            industry="Energy Software",
            composite_score=2.5,
            classification="Lead",
            ai_maturity=AIMaturity.LOW,
            ai_score=2,
            financials=FinancialMetric(revenue=50, employees=30),
        )

    @pytest.fixture
    def contradictory_ai_company(self):
        """Company with contradictory AI data."""
        return Company(
            id="contradiction-1",
            name="Contradiction Company",
            industry="Energy Software",
            composite_score=5.5,
            classification="Salt",
            ai_maturity=AIMaturity.STRONG,  # Expects 6-8
            ai_score=1,  # But score is 1 (should be 6-8)
            financials=FinancialMetric(revenue=100, employees=50),
        )

    @pytest.fixture
    def contradictory_classification_company(self):
        """Company with contradictory classification."""
        return Company(
            id="classification-1",
            name="Classification Company",
            industry="Energy Software",
            composite_score=2.0,  # Lead range: 0-4
            classification="Phoenix",  # But classified as Phoenix (expects 7+)
            ai_maturity=AIMaturity.NONE,
            ai_score=0,
            financials=FinancialMetric(revenue=50, employees=30),
        )

    def test_ai_consistency_check_aligned(self, consistent_phoenix_company):
        """Aligned AI maturity and score should have no contradictions."""
        contradictions = NarrativeConsistencyChecker.check_ai_consistency(consistent_phoenix_company)
        assert len(contradictions) == 0

    def test_ai_consistency_check_misaligned(self, contradictory_ai_company):
        """Misaligned AI maturity and score should have contradictions."""
        contradictions = NarrativeConsistencyChecker.check_ai_consistency(contradictory_ai_company)
        assert len(contradictions) > 0
        assert "AI Contradiction" in contradictions[0]

    def test_ai_consistency_check_missing_data(self):
        """Missing AI score should have no contradictions."""
        company = Company(
            id="missing-1",
            name="Missing Company",
            industry="Energy Software",
            ai_maturity=AIMaturity.STRONG,
            ai_score=None,  # Missing score
        )
        contradictions = NarrativeConsistencyChecker.check_ai_consistency(company)
        assert len(contradictions) == 0

    def test_classification_consistency_check_aligned(self, consistent_phoenix_company):
        """Aligned classification and score should have no contradictions."""
        contradictions = NarrativeConsistencyChecker.check_classification_consistency(consistent_phoenix_company)
        assert len(contradictions) == 0

    def test_classification_consistency_check_misaligned(self, contradictory_classification_company):
        """Misaligned classification and score should have contradictions."""
        contradictions = NarrativeConsistencyChecker.check_classification_consistency(
            contradictory_classification_company
        )
        assert len(contradictions) > 0
        assert "Classification Contradiction" in contradictions[0]

    def test_classification_consistency_check_missing_data(self):
        """Missing classification data should have no contradictions."""
        company = Company(
            id="missing-1",
            name="Missing Company",
            industry="Energy Software",
            classification=None,
            composite_score=None,
        )
        contradictions = NarrativeConsistencyChecker.check_classification_consistency(company)
        assert len(contradictions) == 0

    def test_narrative_tone_consistency_phoenix(self, consistent_phoenix_company):
        """Phoenix narrative should use high-growth language."""
        narrative = "This high-growth company demonstrates exceptional market traction."
        contradictions = NarrativeConsistencyChecker.check_narrative_tone_consistency(
            consistent_phoenix_company, narrative
        )
        assert len(contradictions) == 0

    def test_narrative_tone_consistency_salt(self, consistent_salt_company):
        """Salt narrative should use stable language."""
        narrative = "This stable, mature company demonstrates consistent performance."
        contradictions = NarrativeConsistencyChecker.check_narrative_tone_consistency(
            consistent_salt_company, narrative
        )
        assert len(contradictions) == 0

    def test_narrative_tone_consistency_lead(self, consistent_lead_company):
        """Lead narrative should use transformation language."""
        narrative = "This legacy company has opportunities for modernization and transformation."
        contradictions = NarrativeConsistencyChecker.check_narrative_tone_consistency(
            consistent_lead_company, narrative
        )
        assert len(contradictions) == 0

    def test_narrative_tone_mismatch_salt_with_phoenix_language(self, consistent_salt_company):
        """Salt company with Phoenix language should have contradiction."""
        narrative = "This exceptional, high-growth company demonstrates rapid market expansion."
        contradictions = NarrativeConsistencyChecker.check_narrative_tone_consistency(
            consistent_salt_company, narrative
        )
        assert any("Narrative Contradiction" in c for c in contradictions)

    def test_narrative_tone_mismatch_lead_with_phoenix_language(self, consistent_lead_company):
        """Lead company with Phoenix language should have contradiction."""
        narrative = "This exceptional, high-growth company demonstrates rapid market expansion."
        contradictions = NarrativeConsistencyChecker.check_narrative_tone_consistency(
            consistent_lead_company, narrative
        )
        assert any("Narrative Contradiction" in c for c in contradictions)

    def test_check_all_contradictions_consistent(self, consistent_phoenix_company):
        """Consistent company should have no contradictions."""
        narrative = "This high-growth company demonstrates exceptional market traction."
        contradictions = NarrativeConsistencyChecker.check_all_contradictions(consistent_phoenix_company, narrative)
        assert len(contradictions) == 0

    def test_check_all_contradictions_multiple(self, contradictory_ai_company):
        """Company with multiple contradictions should report all."""
        narrative = "This exceptional, high-growth company demonstrates rapid market expansion."
        contradictions = NarrativeConsistencyChecker.check_all_contradictions(contradictory_ai_company, narrative)
        # Should have at least AI contradiction
        assert len(contradictions) > 0

    def test_is_consistent_true(self, consistent_phoenix_company):
        """Consistent company should return True."""
        narrative = "This high-growth company demonstrates exceptional market traction."
        is_consistent = NarrativeConsistencyChecker.is_consistent(consistent_phoenix_company, narrative)
        assert is_consistent is True

    def test_is_consistent_false(self, contradictory_ai_company):
        """Contradictory company should return False."""
        is_consistent = NarrativeConsistencyChecker.is_consistent(contradictory_ai_company)
        assert is_consistent is False

    def test_get_consistency_report_consistent(self, consistent_phoenix_company):
        """Consistent company should have positive report."""
        report = NarrativeConsistencyChecker.get_consistency_report(consistent_phoenix_company)
        assert "✓" in report
        assert "consistent" in report.lower()

    def test_get_consistency_report_contradictory(self, contradictory_ai_company):
        """Contradictory company should have negative report."""
        report = NarrativeConsistencyChecker.get_consistency_report(contradictory_ai_company)
        assert "✗" in report
        assert "contradiction" in report.lower()

    def test_validate_ai_maturity_score_alignment_true(self, consistent_phoenix_company):
        """Aligned AI data should validate as True."""
        is_aligned = NarrativeConsistencyChecker.validate_ai_maturity_score_alignment(consistent_phoenix_company)
        assert is_aligned is True

    def test_validate_ai_maturity_score_alignment_false(self, contradictory_ai_company):
        """Misaligned AI data should validate as False."""
        is_aligned = NarrativeConsistencyChecker.validate_ai_maturity_score_alignment(contradictory_ai_company)
        assert is_aligned is False

    def test_validate_classification_score_alignment_true(self, consistent_phoenix_company):
        """Aligned classification should validate as True."""
        is_aligned = NarrativeConsistencyChecker.validate_classification_score_alignment(consistent_phoenix_company)
        assert is_aligned is True

    def test_validate_classification_score_alignment_false(self, contradictory_classification_company):
        """Misaligned classification should validate as False."""
        is_aligned = NarrativeConsistencyChecker.validate_classification_score_alignment(
            contradictory_classification_company
        )
        assert is_aligned is False

    def test_fix_ai_score_for_maturity_very_strong(self, consistent_phoenix_company):
        """Very Strong maturity should suggest score 8-9."""
        suggested_score = NarrativeConsistencyChecker.fix_ai_score_for_maturity(consistent_phoenix_company)
        assert 8 <= suggested_score <= 9

    def test_fix_ai_score_for_maturity_strong(self, consistent_salt_company):
        """Strong maturity should suggest score 6-7."""
        company = Company(
            id="strong-1",
            name="Strong Company",
            ai_maturity=AIMaturity.STRONG,
            ai_score=2,  # Wrong
        )
        suggested_score = NarrativeConsistencyChecker.fix_ai_score_for_maturity(company)
        assert 6 <= suggested_score <= 7

    def test_fix_ai_score_for_maturity_none(self):
        """None maturity should suggest score 0-1."""
        company = Company(
            id="none-1",
            name="None Company",
            ai_maturity=AIMaturity.NONE,
            ai_score=5,  # Wrong
        )
        suggested_score = NarrativeConsistencyChecker.fix_ai_score_for_maturity(company)
        assert 0 <= suggested_score <= 1

    def test_fix_classification_for_score_phoenix(self):
        """Score 7+ should suggest Phoenix."""
        company = Company(
            id="phoenix-1",
            name="Phoenix Company",
            composite_score=8.0,
            classification="Salt",  # Wrong
        )
        suggested_classification = NarrativeConsistencyChecker.fix_classification_for_score(company)
        assert suggested_classification == "Phoenix"

    def test_fix_classification_for_score_salt(self):
        """Score 4-7 should suggest Salt."""
        company = Company(
            id="salt-1",
            name="Salt Company",
            composite_score=5.5,
            classification="Phoenix",  # Wrong
        )
        suggested_classification = NarrativeConsistencyChecker.fix_classification_for_score(company)
        assert suggested_classification == "Salt"

    def test_fix_classification_for_score_lead(self):
        """Score <4 should suggest Lead."""
        company = Company(
            id="lead-1",
            name="Lead Company",
            composite_score=2.0,
            classification="Phoenix",  # Wrong
        )
        suggested_classification = NarrativeConsistencyChecker.fix_classification_for_score(company)
        assert suggested_classification == "Lead"

    def test_all_companies_have_consistency_check(
        self, consistent_phoenix_company, consistent_salt_company, consistent_lead_company
    ):
        """All companies should be checkable for consistency."""
        for company in [consistent_phoenix_company, consistent_salt_company, consistent_lead_company]:
            is_consistent = NarrativeConsistencyChecker.is_consistent(company)
            assert isinstance(is_consistent, bool)

    def test_no_strong_ai_with_zero_score(self):
        """Strong AI maturity with 0 score should be flagged."""
        company = Company(
            id="contradiction-1",
            name="Contradiction Company",
            ai_maturity=AIMaturity.STRONG,
            ai_score=0,
        )
        contradictions = NarrativeConsistencyChecker.check_ai_consistency(company)
        assert len(contradictions) > 0
        assert "0" in contradictions[0]

    def test_no_phoenix_with_low_score(self):
        """Phoenix classification with low score should be flagged."""
        company = Company(
            id="contradiction-1",
            name="Contradiction Company",
            composite_score=2.0,
            classification="Phoenix",
        )
        contradictions = NarrativeConsistencyChecker.check_classification_consistency(company)
        assert len(contradictions) > 0
