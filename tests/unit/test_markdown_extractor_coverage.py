import asyncio

import pytest

from solstein.domain.models import AIMaturity, CompanyTier, ConfidenceLevel, ThreatLevel
from solstein.extractors.markdown_extractor import BatchExtractor, MarkdownExtractor


@pytest.fixture
def sample_markdown():
    return """# Acme Corp

Acme Corp is a leading provider of widgets.
Industry: Technology

Geographic Presence: US, UK, DE
Tech Stack: Python, React, PostgreSQL

Revenue: 1.5B (Estimated)
Growth Rate: 25.5% (Confirmed)
Employees: 1,500
Profit Margin: 15%
Funding Raised: $500M
Valuation: €5T
AI Maturity: Very Strong
Threat Level: Critical
Tier: Tier 1

## Sources

- https://example.com/company
- https://finance.yahoo.com/quote/ACME/

## Metric Sources

- revenue: https://finance.yahoo.com/quote/ACME/
- growth_rate: https://finance.yahoo.com/quote/ACME/
- employees: https://example.com/company

## Estimation Notes

- profit_margin: Derived from latest available estimate.
- funding: Private rounds not fully disclosed.
- valuation: Estimated from market comps.
"""


def test_markdown_extractor_parse(sample_markdown, tmp_path):
    md_file = tmp_path / "acme.md"
    md_file.write_text(sample_markdown)

    extractor = MarkdownExtractor()
    extracted = extractor.extract_from_file(md_file)
    assert extracted is not None

    assert extracted["name"] == "Acme Corp"
    assert "provider of widgets" in extracted["description"]
    assert extracted["revenue"] == "1.5B"
    assert extracted["geographic_presence"] == ["US", "UK", "DE"]
    assert extracted["tech_stack"] == ["Python", "React", "PostgreSQL"]
    assert isinstance(extracted["confidence_levels"], dict)
    assert extracted["source_links"]
    assert isinstance(extracted["metric_sources"], dict)

    profile = extractor.to_company_profile(extracted)
    assert profile.name == "Acme Corp"
    assert profile.financials is not None
    assert profile.financials.revenue_confidence == ConfidenceLevel.UNKNOWN
    assert profile.financials.growth_rate is None
    assert profile.financials.profit_margin is None
    assert profile.financials.funding_raised is None
    assert profile.financials.valuation is None
    assert profile.financials.employees is None
    assert isinstance(profile.metric_observations, dict)
    assert isinstance(profile.metric_justifications, dict)


def test_markdown_extractor_parse_numeric():
    extractor = MarkdownExtractor()
    assert extractor._converter.parse_numeric("1.5K") == 1500.0
    assert extractor._converter.parse_numeric("1.5M") == 1500000.0
    assert extractor._converter.parse_numeric("1.5B") == 1500000000.0
    assert extractor._converter.parse_numeric("1.5T") == 1500000000000.0
    assert extractor._converter.parse_numeric("100") == 100.0
    assert extractor._converter.parse_numeric("invalid") is None
    assert extractor._converter.parse_numeric(None) is None


def test_markdown_extractor_parse_percentage():
    extractor = MarkdownExtractor()
    assert extractor._converter.parse_percentage("25.5%") == 0.255
    assert extractor._converter.parse_percentage("invalid") is None
    assert extractor._converter.parse_percentage(None) is None


def test_markdown_extractor_parse_enums():
    extractor = MarkdownExtractor()
    assert extractor._converter.parse_ai_maturity("advanced") == AIMaturity.VERY_STRONG
    assert extractor._converter.parse_ai_maturity("intermediate") == AIMaturity.MODERATE
    assert extractor._converter.parse_ai_maturity("emerging") == AIMaturity.LOW
    assert extractor._converter.parse_ai_maturity("unknown") == AIMaturity.NONE
    assert extractor._converter.parse_ai_maturity(None) == AIMaturity.NONE

    assert extractor._converter.parse_threat_level("HIGH") == ThreatLevel.HIGH
    assert extractor._converter.parse_threat_level("low") == ThreatLevel.LOW
    assert extractor._converter.parse_threat_level("unknown") == ThreatLevel.MEDIUM
    assert extractor._converter.parse_threat_level(None) == ThreatLevel.MEDIUM

    assert extractor._converter.parse_tier("phoenix") == CompanyTier.TIER_1
    assert extractor._converter.parse_tier("salt") == CompanyTier.TIER_2
    assert extractor._converter.parse_tier("lead") == CompanyTier.TIER_3
    assert extractor._converter.parse_tier("unknown") == CompanyTier.TIER_3
    assert extractor._converter.parse_tier(None) == CompanyTier.TIER_3


def test_markdown_extractor_file_error(tmp_path):
    extractor = MarkdownExtractor()
    assert extractor.extract_from_file(tmp_path / "nonexistent.md") is None


def test_batch_extractor(tmp_path, sample_markdown):
    md_file = tmp_path / "acme.md"
    md_file.write_text(sample_markdown)

    batch = BatchExtractor()

    # test extract_directory
    profiles = batch.extract_directory(tmp_path)
    assert len(profiles) == 1

    # test missing dir
    assert batch.extract_directory(tmp_path / "missing") == []

    # test save_to_json
    out_json = tmp_path / "out.json"
    batch.save_to_json(profiles, out_json)
    assert out_json.exists()

    prof = asyncio.run(batch._process_file(md_file))
    assert prof is not None


def test_batch_extractor_errors(tmp_path):
    md_file = tmp_path / "corrupt.md"

    # force extractor to fail by mocking
    class BadExtractor(MarkdownExtractor):
        def extract_from_file(self, file_path):
            # Normal extract works
            return {"name": "dummy"}

        def to_company_profile(self, extracted_data):
            # Generating profile fails (which is caught in extract_directory try block)
            raise Exception("Fail")

    batch = BatchExtractor(extractor=BadExtractor())
    md_file.write_text("dummy")

    # directory iteration catches error
    res = batch.extract_directory(tmp_path)
    assert len(res) == 0

    prof = asyncio.run(batch._process_file(md_file))
    assert prof is None


def test_save_json_error(tmp_path, monkeypatch):
    import json

    def mock_dump(*args, **kwargs):
        raise TypeError("Not serializable")

    monkeypatch.setattr(json, "dump", mock_dump)

    batch = BatchExtractor()
    with pytest.raises(TypeError):
        batch.save_to_json([], tmp_path / "out.json")
