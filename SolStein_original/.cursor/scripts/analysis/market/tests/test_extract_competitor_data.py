"""Tests for extract_competitor_data.py -- core parsing functions."""

import pytest

from extract_competitor_data import (
    extract_growth_scorecard,
    extract_revenue_timeline,
    extract_employees,
    extract_funding,
    extract_saas_metrics,
    extract_geographic,
    extract_profitability,
    extract_company_name,
    extract_data_availability,
    find_section,
    parse_markdown_table,
    parse_number,
    parse_percentage,
)


# ---------------------------------------------------------------------------
# parse_number
# ---------------------------------------------------------------------------

class TestParseNumber:
    def test_plain_integer(self):
        assert parse_number("42") == 42.0

    def test_plain_float(self):
        assert parse_number("7.3") == 7.3

    def test_eur_millions(self):
        assert parse_number("EUR 143M") == 143.0

    def test_eur_billions(self):
        assert parse_number("EUR 2B") == 2000.0

    def test_percentage_like(self):
        assert parse_number("22%") == 22.0

    def test_tilde_prefix(self):
        assert parse_number("~EUR 10M") == 10.0

    def test_range_with_m(self):
        result = parse_number("EUR 25-30M")
        assert result == pytest.approx(27.5)

    def test_none_input(self):
        assert parse_number(None) is None

    def test_empty_string(self):
        assert parse_number("") is None

    def test_no_number(self):
        assert parse_number("N/A") is None

    def test_assume_millions_large_value(self):
        result = parse_number("€36,322,612", assume_millions=True)
        assert result is not None
        assert result == pytest.approx(36.3, abs=0.5)

    def test_k_suffix(self):
        assert parse_number("500K") == 0.5


# ---------------------------------------------------------------------------
# parse_percentage
# ---------------------------------------------------------------------------

class TestParsePercentage:
    def test_simple(self):
        assert parse_percentage("22%") == 22.0

    def test_with_plus(self):
        assert parse_percentage("+12%") == 12.0

    def test_with_tilde(self):
        assert parse_percentage("~15.4%") == 15.4

    def test_none(self):
        assert parse_percentage(None) is None

    def test_empty(self):
        assert parse_percentage("") is None

    def test_no_percentage(self):
        assert parse_percentage("hello") is None


# ---------------------------------------------------------------------------
# parse_markdown_table
# ---------------------------------------------------------------------------

class TestParseMarkdownTable:
    def test_simple_table(self):
        table = (
            "| Name | Score |\n"
            "|---|---|\n"
            "| Alpha | 7 |\n"
            "| Beta | 5 |\n"
        )
        rows = parse_markdown_table(table)
        assert len(rows) == 2
        assert rows[0]["Name"] == "Alpha"
        assert rows[0]["Score"] == "7"

    def test_empty_string(self):
        assert parse_markdown_table("") == []

    def test_header_only(self):
        table = "| Name |\n|---|\n"
        assert parse_markdown_table(table) == []


# ---------------------------------------------------------------------------
# find_section
# ---------------------------------------------------------------------------

class TestFindSection:
    def test_finds_h2_section(self):
        content = "## Intro\nSome text\n## Revenue Timeline\nRevenue data here\n## Next\n"
        result = find_section(content, "Revenue Timeline")
        assert result is not None
        assert "Revenue data here" in result

    def test_finds_h3_section(self):
        content = "### Growth Scorecard\nScorecard data\n### Other\n"
        result = find_section(content, "Growth Scorecard")
        assert result is not None
        assert "Scorecard data" in result

    def test_returns_none_for_missing_section(self):
        content = "## Intro\nSome text\n"
        assert find_section(content, "Nonexistent") is None


# ---------------------------------------------------------------------------
# extract_growth_scorecard (parse_scorecard equivalent)
# ---------------------------------------------------------------------------

SCORECARD_MD = """\
## Growth Scorecard

| Dimension | Score (1-10) | Evidence Summary |
|---|---|---|
| Revenue Growth | 7 | Strong growth |
| Funding Momentum | 8 | Series C closed |
| Employee Growth | 6 | Moderate |
| Geographic Expansion | 5 | 3 countries |
| M&A Activity | 4 | One acquisition |
| SaaS Maturity | 7 | 80% cloud |
| **COMPOSITE** | **6.2** | **Riser** |

## Next Section
"""


class TestExtractGrowthScorecard:
    def test_dimensions_extracted(self):
        result = extract_growth_scorecard(SCORECARD_MD)
        assert "dimensions" in result
        assert len(result["dimensions"]) == 6

    def test_composite_score(self):
        result = extract_growth_scorecard(SCORECARD_MD)
        assert result["composite_score"] == pytest.approx(6.2)

    def test_classification_derived(self):
        result = extract_growth_scorecard(SCORECARD_MD)
        assert result["classification"] == "Riser"

    def test_empty_content(self):
        assert extract_growth_scorecard("## Something Else\nNo scorecard") == {}


# ---------------------------------------------------------------------------
# extract_revenue_timeline (parse_revenue_timeline equivalent)
# ---------------------------------------------------------------------------

REVENUE_MD = """\
## Revenue Timeline

| Year | EUR Equivalent | YoY Growth | Confidence |
|---|---|---|---|
| 2024 | EUR 150M | +25% | High |
| 2023 | EUR 120M | +20% | High |
| 2022 | EUR 100M | +18% | Medium |

- **Revenue CAGR (3yr)**: ~22%
- **Revenue CAGR (5yr)**: ~18%

## Next Section
"""


class TestExtractRevenueTimeline:
    def test_timeline_length(self):
        result = extract_revenue_timeline(REVENUE_MD)
        assert len(result["timeline"]) == 3

    def test_first_entry_values(self):
        result = extract_revenue_timeline(REVENUE_MD)
        first = result["timeline"][0]
        assert first["year"] == "2024"
        assert first["eur_millions"] == pytest.approx(150.0)
        assert first["yoy_growth_pct"] == pytest.approx(25.0)

    def test_cagr_3yr(self):
        result = extract_revenue_timeline(REVENUE_MD)
        assert result["cagr_3yr_pct"] == pytest.approx(22.0)

    def test_latest_revenue(self):
        result = extract_revenue_timeline(REVENUE_MD)
        assert result["latest_revenue_eur_m"] == pytest.approx(150.0)

    def test_empty_content(self):
        assert extract_revenue_timeline("## Other\n") == {}


# ---------------------------------------------------------------------------
# extract_employees (parse_employee_timeline equivalent)
# ---------------------------------------------------------------------------

EMPLOYEE_MD = """\
## Employee Timeline

| Year | Headcount |
|---|---|
| 2024 | 350 |
| 2023 | 300 |
| 2022 | 260 |

- **Employee CAGR (3yr)**: ~16%
- **Open Positions**: 45

## Next Section
"""


class TestExtractEmployees:
    def test_timeline_length(self):
        result = extract_employees(EMPLOYEE_MD)
        assert len(result["timeline"]) == 3

    def test_headcount_values(self):
        result = extract_employees(EMPLOYEE_MD)
        assert result["timeline"][0]["headcount"] == pytest.approx(350.0)

    def test_latest_headcount(self):
        result = extract_employees(EMPLOYEE_MD)
        assert result["latest_headcount"] == pytest.approx(350.0)

    def test_cagr(self):
        result = extract_employees(EMPLOYEE_MD)
        assert result["employee_cagr_pct"] == pytest.approx(16.0)

    def test_empty_content(self):
        assert extract_employees("## Other\n") == {}


# ---------------------------------------------------------------------------
# extract_funding (parse_funding_history equivalent)
# ---------------------------------------------------------------------------

FUNDING_MD = """\
## Funding & Investment History

| Date | Round | Amount | Valuation | Lead Investor(s) |
|---|---|---|---|---|
| 2023-06 | Series C | EUR 50M | EUR 300M | Tiger Global |
| 2021-01 | Series B | EUR 20M | EUR 100M | Sequoia |

**Total Raised**: EUR 80M
**Latest Valuation**: EUR 300M
**War Chest Signals**: Aggressive hiring in AI team

## Next Section
"""


class TestExtractFunding:
    def test_rounds_count(self):
        result = extract_funding(FUNDING_MD)
        assert len(result["rounds"]) == 2

    def test_lead_investors_extracted(self):
        result = extract_funding(FUNDING_MD)
        assert "Tiger Global" in result["lead_investors"]
        assert "Sequoia" in result["lead_investors"]

    def test_total_raised(self):
        result = extract_funding(FUNDING_MD)
        assert result["total_raised_text"] is not None
        assert "80M" in result["total_raised_text"]

    def test_war_chest(self):
        result = extract_funding(FUNDING_MD)
        assert result["war_chest_signals"] is not None
        assert "hiring" in result["war_chest_signals"].lower()

    def test_empty_content(self):
        assert extract_funding("## Other\n") == {}


# ---------------------------------------------------------------------------
# extract_saas_metrics
# ---------------------------------------------------------------------------

SAAS_MD = """\
## SaaS Transition Metrics

| Data Point | Value |
|---|---|
| Deployment Model | SaaS (cloud-native) |
| Cloud Revenue % (current) | 85% |

## Next Section
"""


class TestExtractSaasMetrics:
    def test_deployment_model(self):
        result = extract_saas_metrics(SAAS_MD)
        assert result["deployment_model"] == "SaaS"

    def test_cloud_revenue_pct(self):
        result = extract_saas_metrics(SAAS_MD)
        assert result["cloud_revenue_pct"] == pytest.approx(85.0)

    def test_hybrid_detected(self):
        md = "## SaaS Transition Metrics\n| Data Point | Value |\n|---|---|\n| Deployment Model | Hybrid (on-prem + SaaS) |\n"
        result = extract_saas_metrics(md)
        assert result["deployment_model"] == "Hybrid"

    def test_empty_content(self):
        result = extract_saas_metrics("## Other\n")
        assert result["deployment_model"] is None
        assert result["cloud_revenue_pct"] is None


# ---------------------------------------------------------------------------
# extract_geographic
# ---------------------------------------------------------------------------

GEOGRAPHIC_MD = """\
## Geographic & Market Expansion

**International Revenue %**: ~40%

Active in 12+ countries across Europe.

| Year | Expansion Event | Details |
|---|---|---|
| 2023 | Market entry | Germany, France |

## Next Section
"""


class TestExtractGeographic:
    def test_international_revenue(self):
        result = extract_geographic(GEOGRAPHIC_MD)
        assert result["international_revenue_pct"] == pytest.approx(40.0)

    def test_countries_count(self):
        result = extract_geographic(GEOGRAPHIC_MD)
        assert result["countries_count"] == 12

    def test_empty_content(self):
        result = extract_geographic("## Other\n")
        assert result["international_revenue_pct"] is None
        assert result["countries_count"] is None


# ---------------------------------------------------------------------------
# extract_profitability
# ---------------------------------------------------------------------------

PROFITABILITY_MD = """\
## Profitability

| Data Point | Value |
|---|---|
| EBITDA Margin (2024) | ~12% |
| Revenue per Employee (2024) | ~EUR 118K |
| Recurring Revenue % | 75% |

## Next Section
"""


class TestExtractProfitability:
    def test_ebitda_margin(self):
        result = extract_profitability(PROFITABILITY_MD)
        assert result["ebitda_margin_pct"] == pytest.approx(12.0)

    def test_revenue_per_employee(self):
        result = extract_profitability(PROFITABILITY_MD)
        assert result["revenue_per_employee_eur_k"] == pytest.approx(118.0)

    def test_recurring_revenue(self):
        result = extract_profitability(PROFITABILITY_MD)
        assert result["recurring_revenue_pct"] == pytest.approx(75.0)

    def test_empty_content(self):
        assert extract_profitability("## Other\n") == {}


# ---------------------------------------------------------------------------
# extract_company_name
# ---------------------------------------------------------------------------

class TestExtractCompanyName:
    def test_standard_heading(self):
        md = "# Financial & Growth Deep-Dive - Acme Energy\n\nBody"
        assert extract_company_name(md) == "Acme Energy"

    def test_plain_h1(self):
        md = "# Some Company Report\n\nBody"
        assert extract_company_name(md) == "Some Company Report"

    def test_no_heading(self):
        assert extract_company_name("No heading here") == "Unknown"


# ---------------------------------------------------------------------------
# extract_data_availability
# ---------------------------------------------------------------------------

class TestExtractDataAvailability:
    def test_found(self):
        md = "**Data Availability**: High\n"
        assert extract_data_availability(md) == "High"

    def test_not_found(self):
        assert extract_data_availability("No data availability line") is None
