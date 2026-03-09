from solstein.migrations.load_competitor_data import _build_company_record


def test_build_company_record_preserves_decimal_ai_score() -> None:
    competitor = {
        "company_name": "Acme",
        "industry": "Tech",
        "ai_score": 7.75,
        "country": "US",
        "revenue": {"timeline": [{"eur_millions": 42.5}]},
    }

    record = _build_company_record(competitor)

    assert record.name == "Acme"
    assert record.ai_score == 7.75


def test_build_company_record_maps_funding_and_profitability_fields() -> None:
    competitor = {
        "company_name": "Beta",
        "funding_raised": 125000000.0,
        "profitability": {
            "ebitda_margin_pct": 18.4,
            "recurring_revenue_pct": 61.2,
            "revenue_per_employee_eur_k": 540.0,
        },
        "revenue": {"timeline": [{"eur_millions": 90.0}], "cagr_3yr_pct": 24.2},
    }

    record = _build_company_record(competitor)

    assert record.total_funding_raised_eur == 125000000.0
    assert record.ebitda_margin_pct == 18.4
    assert record.recurring_revenue_pct == 61.2
    assert record.revenue_per_employee_eur_k == 540.0
    assert record.revenue_cagr_3yr == 24.2
