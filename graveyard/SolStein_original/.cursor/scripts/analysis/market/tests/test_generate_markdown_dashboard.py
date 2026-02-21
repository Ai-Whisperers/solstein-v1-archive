"""Tests for generate_markdown_dashboard.py -- table rendering, Mermaid charts, section output."""

import pytest

from generate_markdown_dashboard import (
    bold_if_eneve,
    build_classification_matrix,
    build_employee_leaderboard,
    build_funding_leaderboard,
    build_meteor_warning,
    build_missing_data,
    build_quadrant_chart,
    build_revenue_leaderboard,
    build_saas_ranking,
    fmt_eur,
    fmt_pct,
    fmt_score,
    mermaid_safe_name,
)


# ---------------------------------------------------------------------------
# fmt_score
# ---------------------------------------------------------------------------

class TestFmtScore:
    def test_integer_score(self):
        assert fmt_score(7.0) == "7"

    def test_decimal_score(self):
        assert fmt_score(6.3) == "6.3"

    def test_none(self):
        assert fmt_score(None) == "N/A"


# ---------------------------------------------------------------------------
# fmt_pct
# ---------------------------------------------------------------------------

class TestFmtPct:
    def test_percentage(self):
        assert fmt_pct(22.5) == "22.5%"

    def test_none(self):
        assert fmt_pct(None) == "N/A"


# ---------------------------------------------------------------------------
# fmt_eur
# ---------------------------------------------------------------------------

class TestFmtEur:
    def test_millions(self):
        assert fmt_eur(150.0) == "EUR 150M"

    def test_billions(self):
        assert fmt_eur(1500.0) == "EUR 1.5B"

    def test_none(self):
        assert fmt_eur(None) == "N/A"


# ---------------------------------------------------------------------------
# bold_if_eneve
# ---------------------------------------------------------------------------

class TestBoldIfEneve:
    def test_eneve_gets_bold(self, eneve_competitor):
        result = bold_if_eneve("test", eneve_competitor)
        assert result == "**test**"

    def test_non_eneve_unchanged(self, sample_competitor):
        result = bold_if_eneve("test", sample_competitor)
        assert result == "test"


# ---------------------------------------------------------------------------
# mermaid_safe_name
# ---------------------------------------------------------------------------

class TestMermaidSafeName:
    def test_strips_formerly(self):
        assert "formerly" not in mermaid_safe_name("Eneve (formerly Energy21)")

    def test_shortens_long_name(self):
        result = mermaid_safe_name("Very Long Company Name Here")
        assert result == "Very"

    def test_two_word_name(self):
        result = mermaid_safe_name("Acme Energy")
        assert result == "AcmeEnergy"

    def test_single_word(self):
        assert mermaid_safe_name("Tibber") == "Tibber"


# ---------------------------------------------------------------------------
# build_classification_matrix
# ---------------------------------------------------------------------------

class TestBuildClassificationMatrix:
    def test_contains_section_header(self, competitors_list):
        md = build_classification_matrix(competitors_list)
        assert "## Growth Classification Matrix" in md

    def test_contains_table_rows(self, competitors_list):
        md = build_classification_matrix(competitors_list)
        assert "Acme Energy" in md
        assert "Eneve" in md

    def test_empty_list(self):
        md = build_classification_matrix([])
        assert "## Growth Classification Matrix" in md

    def test_classification_subheadings(self, competitors_list):
        md = build_classification_matrix(competitors_list)
        # sample is Riser, eneve is Dinosaur
        assert "Riser" in md
        assert "Dinosaur" in md


# ---------------------------------------------------------------------------
# build_revenue_leaderboard
# ---------------------------------------------------------------------------

class TestBuildRevenueLeaderboard:
    def test_contains_header(self, competitors_list):
        md = build_revenue_leaderboard(competitors_list)
        assert "## Revenue Growth Leaderboard" in md

    def test_contains_table(self, competitors_list):
        md = build_revenue_leaderboard(competitors_list)
        assert "| Rank |" in md
        assert "Acme Energy" in md

    def test_mermaid_chart_present(self, competitors_list):
        md = build_revenue_leaderboard(competitors_list)
        assert "```mermaid" in md
        assert "xychart-beta" in md


# ---------------------------------------------------------------------------
# build_funding_leaderboard
# ---------------------------------------------------------------------------

class TestBuildFundingLeaderboard:
    def test_contains_header(self, competitors_list):
        md = build_funding_leaderboard(competitors_list)
        assert "## Funding Leaderboard" in md

    def test_contains_table(self, competitors_list):
        md = build_funding_leaderboard(competitors_list)
        assert "| Rank |" in md


# ---------------------------------------------------------------------------
# build_employee_leaderboard
# ---------------------------------------------------------------------------

class TestBuildEmployeeLeaderboard:
    def test_contains_header(self, competitors_list):
        md = build_employee_leaderboard(competitors_list)
        assert "## Employee Growth Leaderboard" in md

    def test_contains_table(self, competitors_list):
        md = build_employee_leaderboard(competitors_list)
        assert "| Rank |" in md


# ---------------------------------------------------------------------------
# build_saas_ranking
# ---------------------------------------------------------------------------

class TestBuildSaasRanking:
    def test_contains_header(self, competitors_list):
        md = build_saas_ranking(competitors_list)
        assert "## SaaS Maturity Ranking" in md


# ---------------------------------------------------------------------------
# build_quadrant_chart
# ---------------------------------------------------------------------------

class TestBuildQuadrantChart:
    def test_contains_header(self, competitors_list):
        md = build_quadrant_chart(competitors_list)
        assert "## Growth vs Size Quadrant" in md

    def test_insufficient_data_message_for_small_list(self, empty_competitor):
        md = build_quadrant_chart([empty_competitor])
        assert "Insufficient data" in md


# ---------------------------------------------------------------------------
# build_meteor_warning
# ---------------------------------------------------------------------------

class TestBuildMeteorWarning:
    def test_contains_header(self, competitors_list):
        md = build_meteor_warning(competitors_list)
        assert "## The Meteor Warning" in md

    def test_contains_eneve_reference(self, competitors_list):
        md = build_meteor_warning(competitors_list)
        assert "Eneve" in md

    def test_contains_action_items(self, competitors_list):
        md = build_meteor_warning(competitors_list)
        assert "Accelerate SaaS" in md


# ---------------------------------------------------------------------------
# build_missing_data
# ---------------------------------------------------------------------------

class TestBuildMissingData:
    def test_with_missing(self):
        missing = [{"folder": "no-data-corp", "tier": "Tier 2"}]
        md = build_missing_data(missing)
        assert "## Missing Data" in md
        assert "no-data-corp" in md

    def test_empty_missing(self):
        assert build_missing_data([]) == ""
