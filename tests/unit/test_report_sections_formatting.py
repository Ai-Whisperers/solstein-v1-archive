from solstein.domain.models import Company
from solstein.exporters.markdown.report_sections import ReportSectionGenerator


class _Formatter:
    def format_score(self, value):
        if value is None:
            return "N/A"
        return f"{float(value):.2f}"


def _company(company_id: str, name: str, composite: float, ai: float, saas: int) -> Company:
    return Company(
        id=company_id,
        name=name,
        industry="Tech",
        financials={"revenue": 100.0, "valuation": 500.0},
        classification="Salt",
        composite_score=composite,
        growth_score=6.126,
        financial_health_score=7.444,
        ai_score=ai,
        saas_maturity=saas,
        revenue_cagr_3yr=12.345,
    )


def test_client_profile_uses_two_decimal_score_formatting() -> None:
    generator = ReportSectionGenerator(_Formatter())
    client = _company("cmp-601", "Acme", 7.138888, 8.366666, 7)
    competitors = [_company("cmp-602", "Beta", 6.333333, 6.777777, 5)]

    section = generator.generate_client_profile(
        client,
        competitors,
        lambda *_: "#1",
        lambda *_: "#1",
        lambda *_: "#1",
        lambda *_: "#1",
        lambda *_: "#1",
    )

    assert "7.14" in section
    assert "8.37/10" in section
    assert "7.00/10" in section


def test_appendix_uses_two_decimal_score_formatting() -> None:
    generator = ReportSectionGenerator(_Formatter())
    companies = [
        _company("cmp-701", "Acme", 7.138888, 8.366666, 7),
        _company("cmp-702", "Beta", 5.555555, 6.111111, 4),
    ]

    section = generator.generate_appendix(companies, lambda *_: "Medium")

    assert "8.37/10" in section
    assert "6.11/10" in section
    assert "7.00/10" in section
    assert "4.00/10" in section
