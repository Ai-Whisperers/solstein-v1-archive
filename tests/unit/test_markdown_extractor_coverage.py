import pytest
from pathlib import Path
from solstein.extractors.markdown_extractor import MarkdownExtractor, BatchExtractor
from solstein.domain.models import AIMaturity, ThreatLevel, CompanyTier, ConfidenceLevel

@pytest.fixture
def sample_markdown():
    return """# Acme Corp

Acme Corp is a leading provider of widgets.

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
"""

def test_markdown_extractor_parse(sample_markdown, tmp_path):
    md_file = tmp_path / "acme.md"
    md_file.write_text(sample_markdown)
    
    extractor = MarkdownExtractor()
    extracted = extractor.extract_from_file(md_file)
    
    assert extracted["name"] == "Acme Corp"
    assert "provider of widgets" in extracted["description"]
    assert extracted["revenue"] == "1.5B"
    assert extracted["geographic_presence"] == ["US", "UK", "DE"]
    assert extracted["tech_stack"] == ["Python", "React", "PostgreSQL"]
    assert extracted["confidence"]["revenue"] == "Estimated"
    
    profile = extractor.to_company_profile(extracted)
    assert profile.name == "Acme Corp"
    assert profile.financials.revenue == 1.5e9
    assert profile.financials.revenue_confidence == ConfidenceLevel.ESTIMATED
    assert profile.financials.growth_rate == 25.5
    assert profile.financials.profit_margin == 15.0
    assert profile.financials.funding_raised == 500e6
    assert profile.financials.valuation == 5e12
    assert profile.financials.employees == 1500
    assert profile.ai_maturity == AIMaturity.VERY_STRONG
    assert profile.threat_level == ThreatLevel.CRITICAL
    assert profile.tier == CompanyTier.TIER_1

def test_markdown_extractor_parse_numeric():
    extractor = MarkdownExtractor()
    assert extractor._parse_numeric("1.5K") == 1500.0
    assert extractor._parse_numeric("1.5M") == 1500000.0
    assert extractor._parse_numeric("1.5B") == 1500000000.0
    assert extractor._parse_numeric("1.5T") == 1500000000000.0
    assert extractor._parse_numeric("100") == 100.0
    assert extractor._parse_numeric("invalid") is None
    assert extractor._parse_numeric(None) is None

def test_markdown_extractor_parse_percentage():
    extractor = MarkdownExtractor()
    assert extractor._parse_percentage("25.5%") == 25.5
    assert extractor._parse_percentage("invalid") is None
    assert extractor._parse_percentage(None) is None

def test_markdown_extractor_parse_enums():
    extractor = MarkdownExtractor()
    assert extractor._parse_ai_maturity("strong") == AIMaturity.STRONG
    assert extractor._parse_ai_maturity("moderate") == AIMaturity.MODERATE
    assert extractor._parse_ai_maturity("low") == AIMaturity.LOW
    assert extractor._parse_ai_maturity("unknown") == AIMaturity.NONE
    assert extractor._parse_ai_maturity(None) == AIMaturity.NONE
    
    assert extractor._parse_threat_level("HIGH") == ThreatLevel.HIGH
    assert extractor._parse_threat_level("low threat") == ThreatLevel.LOW
    assert extractor._parse_threat_level("unknown") == ThreatLevel.MEDIUM
    assert extractor._parse_threat_level(None) == ThreatLevel.MEDIUM
    
    assert extractor._parse_tier("Tier 2") == CompanyTier.TIER_2
    assert extractor._parse_tier("Tier 3") == CompanyTier.TIER_3
    assert extractor._parse_tier("Tier 4") == CompanyTier.TIER_4
    assert extractor._parse_tier("unknown") == CompanyTier.TIER_3
    assert extractor._parse_tier(None) == CompanyTier.TIER_3

def test_markdown_extractor_file_error(tmp_path):
    extractor = MarkdownExtractor()
    assert extractor.extract_from_file(tmp_path / "nonexistent.md") is None

@pytest.mark.asyncio
async def test_batch_extractor(tmp_path, sample_markdown):
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
    
    # test async process_file
    prof = await BatchExtractor.process_file(md_file)
    assert prof is not None

@pytest.mark.asyncio
async def test_batch_extractor_errors(tmp_path):
    md_file = tmp_path / "corrupt.md"
    # force extractor to fail by mocking
    class BadExtractor(MarkdownExtractor):
        def extract_from_file(self, path):
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
    
    prof = await BatchExtractor.process_file(md_file, extractor=BadExtractor())
    assert prof is None
        
def test_save_json_error(tmp_path, monkeypatch):
    import json
    def mock_dumps(*args, **kwargs):
        raise TypeError("Not serializable")
    monkeypatch.setattr(json, "dumps", mock_dumps)
    
    batch = BatchExtractor()
    with pytest.raises(TypeError):
        batch.save_to_json([], tmp_path / "out.json")
