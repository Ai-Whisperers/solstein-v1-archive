# 🔌 Solstein Extension & Integration Guide

**Add custom scoring dimensions, create exporters, integrate external data sources, and extend Solstein.**

---

## Extension Architecture

Solstein is designed for extensibility through **interface-based architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    Business Logic                        │
│  (Scoring, Analysis, Classification, Exporting)         │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
     ┌──▼──┐      ┌───▼────┐    ┌──▼─────┐
     │Score│      │ Export  │    │Data    │
     │Engine│     │ers      │    │Sources │
     └──┬──┘      └────┬────┘    └───┬────┘
        │              │            │
    [Interface]   [Interface]   [Interface]
        │              │            │
  ┌─────┴────────┬────┴──────┬──────┴────────┐
  │              │           │               │
Growth      Excel        Supabase      JSON Files
Financial   PDF          PostgreSQL    CSV
Competitive JSON         Redis Cache   API
Position    CSV          
```

Each layer implements an **abstract interface**, allowing swappable implementations without touching other code.

---

## Pattern 1: Add a New Scoring Dimension

**Goal:** Calculate a new score (e.g., "Environmental Score") and include it in classification.

### Step 1: Create Configuration

**File:** `src/solstein/core/scoring_config.py`

```python
class EnvironmentalScoringConfig(BaseModel):
    """Configuration for environmental impact score."""
    
    base_score: float = 5.0
    
    # ESG certification bonus
    has_esg_cert_bonus: float = 2.0
    has_iso_cert_bonus: float = 1.5
    
    # Carbon footprint thresholds (tons CO2 per year)
    carbon_low_threshold: float = 100.0  # < 100 tons
    carbon_low_bonus: float = 2.5
    carbon_high_threshold: float = 1000.0  # > 1000 tons
    carbon_high_penalty: float = -2.0


class ScoringSettings(BaseModel):
    """Main scoring configuration."""
    
    growth: GrowthScoringConfig = Field(default_factory=GrowthScoringConfig)
    financial_health: FinancialHealthConfig = Field(default_factory=FinancialHealthConfig)
    competitive_position: CompetitivePositionConfig = Field(default_factory=CompetitivePositionConfig)
    environmental: EnvironmentalScoringConfig = Field(default_factory=EnvironmentalScoringConfig)  # NEW
```

### Step 2: Extend Domain Model

**File:** `src/solstein/domain/models.py`

```python
@dataclass
class Company:
    """Company domain entity."""
    
    # ... existing fields ...
    
    # Scoring dimensions
    growth_score: float | None = None
    financial_health_score: float | None = None
    competitive_position_score: float | None = None
    environmental_score: float | None = None  # NEW
    
    # Classifications
    classification: str = "Neutral"  # Rocket/Neutral/Dinosaur
    environmental_classification: str = "Unknown"  # Eco/Standard/Heavy  # NEW
    
    # Explanations
    scoring_breakdown: dict[str, Any] = field(default_factory=dict)
    environmental_breakdown: dict[str, Any] = field(default_factory=dict)  # NEW
```

### Step 3: Implement Scoring Logic

**File:** `src/solstein/analytics/scoring.py`

```python
class GrowthScorer:
    """Calculate growth scores for companies."""
    
    def calculate_scores(self, profile: Company) -> Company:
        """Calculate all scores for a company profile."""
        
        # ... existing scoring logic ...
        
        # Calculate environmental score
        env_score, env_expl = self._calculate_environmental_score(profile)
        profile.environmental_score = env_score
        profile.scoring_breakdown["environmental"] = env_expl
        
        # Apply environmental classification
        profile.environmental_classification = self._classify_environmental(env_score)
        
        return profile
    
    def _calculate_environmental_score(self, profile: Company) -> tuple[float, ScoringExplanation]:
        """Calculate environmental score (0-10) with explanation."""
        cfg = self.config.environmental
        score = cfg.base_score
        explanation = ScoringExplanation(base_score=score)
        
        # ESG Certifications
        if hasattr(profile, 'has_esg_cert') and profile.has_esg_cert:
            score += cfg.has_esg_cert_bonus
            explanation.components.append(ScoreComponent(
                name="ESG Certification",
                value=cfg.has_esg_cert_bonus,
                formula=f"+{cfg.has_esg_cert_bonus}",
                reasoning="Company has ESG certification"
            ))
        
        # Carbon Footprint
        if hasattr(profile, 'annual_carbon_emissions'):
            emissions = profile.annual_carbon_emissions
            if emissions < cfg.carbon_low_threshold:
                score += cfg.carbon_low_bonus
                explanation.components.append(ScoreComponent(
                    name="Low Carbon Footprint",
                    value=cfg.carbon_low_bonus,
                    formula=f"+{cfg.carbon_low_bonus} (< {cfg.carbon_low_threshold} tons CO2/year)",
                    reasoning=f"Carbon emissions: {emissions} tons/year"
                ))
            elif emissions > cfg.carbon_high_threshold:
                score += cfg.carbon_high_penalty
                explanation.components.append(ScoreComponent(
                    name="High Carbon Footprint",
                    value=cfg.carbon_high_penalty,
                    formula=f"{cfg.carbon_high_penalty} (> {cfg.carbon_high_threshold} tons CO2/year)",
                    reasoning=f"Carbon emissions: {emissions} tons/year"
                ))
        
        # Cap score at 10
        score = min(score, 10.0)
        
        return score, explanation
    
    def _classify_environmental(self, score: float | None) -> str:
        """Classify based on environmental score."""
        if score is None:
            return "Unknown"
        if score >= 7.0:
            return "Eco-Leader"
        elif score <= 4.0:
            return "High-Impact"
        return "Standard"
```

### Step 4: Update API Response Schema

**File:** `src/solstein/api/schemas.py`

```python
class CompanySchema(BaseModel):
    """Company API response schema."""
    
    # ... existing fields ...
    
    growth_score: float | None = None
    financial_health_score: float | None = None
    competitive_position_score: float | None = None
    environmental_score: float | None = None  # NEW
    
    classification: str = "Neutral"
    environmental_classification: str = "Unknown"  # NEW
```

### Step 5: Create API Endpoint (Optional)

**File:** `src/solstein/api/routers/scoring.py`

```python
@router.get("/stats/environmental")
async def environmental_scoring_stats(
    repo: CompanyRepository = Depends(get_repository)
) -> dict[str, Any]:
    """Get environmental scoring statistics."""
    companies = repo.find_all()
    
    eco_leaders = sum(1 for c in companies if c.environmental_score and c.environmental_score >= 7.0)
    standard = sum(1 for c in companies if c.environmental_score and 4.0 <= c.environmental_score < 7.0)
    high_impact = sum(1 for c in companies if c.environmental_score and c.environmental_score <= 4.0)
    
    return {
        "eco_leaders": eco_leaders,
        "standard": standard,
        "high_impact": high_impact,
        "total": len(companies),
        "avg_environmental_score": statistics.mean([
            c.environmental_score for c in companies if c.environmental_score
        ]) if any(c.environmental_score for c in companies) else None,
    }
```

### Step 6: Add Unit Tests

**File:** `tests/unit/test_environmental_scoring.py`

```python
import pytest
from solstein.analytics.scoring import GrowthScorer
from solstein.domain.models import Company, FinancialMetric
from solstein.core.scoring_config import ScoringSettings


@pytest.fixture
def scorer():
    return GrowthScorer(ScoringSettings())


def test_environmental_score_with_esg_cert(scorer):
    """ESG certification should add bonus."""
    company = Company(id="eco-corp", name="Eco Corp")
    company.financials = FinancialMetric()
    company.has_esg_cert = True
    
    result = scorer.calculate_scores(company)
    
    assert result.environmental_score is not None
    assert result.environmental_score > 5.0  # Above base score
    assert "ESG Certification" in str(result.environmental_breakdown)


def test_environmental_classification(scorer):
    """Classification should reflect environmental score."""
    company = Company(id="eco", name="Eco Friendly Inc")
    company.financials = FinancialMetric()
    company.annual_carbon_emissions = 50.0  # Low
    company.has_esg_cert = True
    
    result = scorer.calculate_scores(company)
    
    assert result.environmental_classification == "Eco-Leader"
    assert result.environmental_score >= 7.0


def test_environmental_score_without_data(scorer):
    """Should use base score when data missing."""
    company = Company(id="unknown", name="Unknown Corp")
    company.financials = FinancialMetric()
    
    result = scorer.calculate_scores(company)
    
    assert result.environmental_score == 5.0  # Base score
    assert result.environmental_classification == "Standard"
```

### Step 7: Update Documentation

**File:** `docs/architecture/decisions.md`

Add new ADR:

```markdown
## ADR-009: Environmental Scoring Dimension

**Date:** 2026-Q2
**Status:** Accepted

**Context:** Client requested ESG/environmental impact analysis alongside financial metrics.

**Decision:** Add environmental score as fourth dimension, following existing scoring pattern.

**Rationale:**
- Follows established pattern (GrowthScorer calculates all dimensions)
- Configuration-driven thresholds allow easy tuning
- Classification hierarchy mirrors growth/financial/competitive dimensions
- Optional fields (has_esg_cert, annual_carbon_emissions) won't break existing data

**Consequences:** 
- Company model has 4 scores instead of 3
- API responses include environmental data
- Tests require new assertions for environmental classification
- Scoring calculation is ~10% slower (one more dimension)

**Related ADRs:** ADR-001 (FastAPI), ADR-006 (Millions units)
```

### Step 8: Add to CHANGELOG

**File:** `CHANGELOG.md`

```markdown
## [0.2.0] - 2026-02-28

### Added
- **Environmental Score dimension** — 4th scoring axis alongside Growth, Financial Health, and Competitive Position
  - Measures ESG compliance and carbon footprint
  - Three environmental classifications: Eco-Leader, Standard, High-Impact
  - Fully configurable thresholds in `scoring_config.py`
- Environmental scoring API endpoint: `GET /scoring/stats/environmental`

### Changed
- `Company` domain model now includes `environmental_score`, `environmental_classification`, `environmental_breakdown`

### Technical
- See [ADR-009](docs/architecture/decisions.md) for design rationale
```

---

## Pattern 2: Create a Custom Exporter

**Goal:** Export company data as PDF, JSON, or other format beyond Excel.

### Example: PDF Exporter

**File:** `src/solstein/exporters/pdf_exporter.py`

```python
"""PDF exporter for Solstein reports."""

from pathlib import Path
from typing import Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from ..config import Settings
from ..domain.models import Company


class PDFExporter:
    """Export company profiles as PDF reports."""
    
    def __init__(self):
        self.settings = Settings()
    
    def export(self, companies: list[Company], output_path: Path | None = None) -> Path:
        """Generate PDF report from company list."""
        
        if output_path is None:
            output_path = (
                self.settings.data.export_dir / 
                f"solstein_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
        
        # Create PDF
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        elements = []
        
        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('4b0082'),
            spaceAfter=30,
        )
        title = Paragraph("SolStein Market Intelligence Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Create summary table
        data = [
            ["Company", "Industry", "Growth Score", "Classification"]
        ]
        
        for company in companies:
            data.append([
                company.name,
                company.industry,
                f"{company.growth_score:.1f}" if company.growth_score else "N/A",
                company.classification or "Unknown"
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        return output_path
```

### Register Exporter

**File:** `src/solstein/api/routers/export.py`

```python
from ..exporters.pdf_exporter import PDFExporter

@router.post("/pdf", tags=["Export"])
async def export_pdf(
    filters: CompanyFilter = Body(...),
    repo: CompanyRepository = Depends(get_repository),
) -> dict[str, Any]:
    """Export market analysis as PDF."""
    
    companies = repo.find_all(filters)
    
    exporter = PDFExporter()
    pdf_path = exporter.export(companies)
    
    return {
        "status": "success",
        "format": "pdf",
        "file_path": str(pdf_path),
        "company_count": len(companies),
    }
```

---

## Pattern 3: Integrate External Data Source

**Goal:** Load company data from external API (Crunchbase, PitchBook, etc.) alongside JSON files.

### Example: Crunchbase Integration

**File:** `src/solstein/data/crunchbase_loader.py`

```python
"""Load company data from Crunchbase API."""

import os
import requests
from typing import Any
from loguru import logger

from ..domain.models import Company, FinancialMetric


class CrunchbaseLoader:
    """Fetch company data from Crunchbase."""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("CRUNCHBASE_API_KEY")
        self.base_url = "https://api.crunchbase.com/v4"
        
        if not self.api_key:
            raise ValueError("CRUNCHBASE_API_KEY not set in environment")
    
    def fetch_company(self, company_name: str) -> Company | None:
        """Fetch company by name from Crunchbase."""
        
        endpoint = f"{self.base_url}/searches/entities"
        
        headers = {
            "X-Crunchbase-API-Key": self.api_key,
            "Accept": "application/json",
        }
        
        payload = {
            "entity_types": ["Company"],
            "limit": 1,
            "query": company_name
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("entities"):
                logger.warning(f"Company not found in Crunchbase: {company_name}")
                return None
            
            entity = data["entities"][0]
            
            return self._parse_crunchbase_entity(entity)
            
        except requests.RequestException as e:
            logger.error(f"Crunchbase API error: {e}")
            return None
    
    def _parse_crunchbase_entity(self, entity: dict[str, Any]) -> Company:
        """Convert Crunchbase data to Company domain model."""
        
        properties = entity.get("properties", {})
        
        company = Company(
            id=entity.get("uuid", "unknown"),
            name=properties.get("name", "Unknown"),
            industry=properties.get("primary_category", "Unknown"),
            headquarters=properties.get("location", {}).get("name"),
            website=properties.get("website", {}).get("value"),
            founded_year=properties.get("founded_year"),
            description=properties.get("short_description"),
        )
        
        # Financial data
        company.financials = FinancialMetric(
            revenue=properties.get("revenue_usd"),
            funding_raised=properties.get("funding_total", {}).get("value_usd"),
            valuation=properties.get("valuation", {}).get("value_usd"),
            employees=properties.get("employee_count"),
        )
        
        # Tech stack
        if "technology" in properties:
            company.tech_stack = [
                tech.get("name", "") 
                for tech in properties.get("technology", [])
            ]
        
        return company
```

### Register Data Loader

**File:** `src/solstein/data/loaders.py`

```python
from .crunchbase_loader import CrunchbaseLoader

class CompetitorDataLoader:
    """Load company data from multiple sources."""
    
    def load_companies(self) -> list[Company]:
        """Load from all available sources."""
        companies = []
        
        # Load from JSON
        json_companies = self._load_json()
        companies.extend(json_companies)
        
        # Load from Crunchbase (if API key available)
        try:
            cb_loader = CrunchbaseLoader()
            for company in json_companies:
                # Enrich JSON data with Crunchbase data
                cb_company = cb_loader.fetch_company(company.name)
                if cb_company:
                    # Merge data (prefer JSON, fallback to Crunchbase)
                    company = self._merge_companies(company, cb_company)
            companies = [self._merge_companies(c, cb_company) for c in companies]
        except ValueError:
            logger.info("Crunchbase API key not set, skipping enrichment")
        
        return companies
    
    def _merge_companies(self, primary: Company, enrichment: Company) -> Company:
        """Merge two company records."""
        # Keep primary data, fill in gaps from enrichment
        if not primary.website:
            primary.website = enrichment.website
        if not primary.founded_year:
            primary.founded_year = enrichment.founded_year
        if not primary.tech_stack:
            primary.tech_stack = enrichment.tech_stack
        # ... etc
        return primary
```

---

## Pattern 4: Add Custom Classification Logic

**Goal:** Implement your own classification system instead of Rocket/Neutral/Dinosaur.

**File:** `src/solstein/analytics/custom_classifiers.py`

```python
"""Custom classification strategies."""

from typing import Protocol
from ..domain.models import Company


class CompanyClassifier(Protocol):
    """Protocol for company classification strategies."""
    
    def classify(self, company: Company) -> str:
        """Classify company based on its profile."""
        ...


class MaturityLevelClassifier:
    """Classify by technology maturity: Emerging, Growth, Mature."""
    
    def classify(self, company: Company) -> str:
        """Classify based on tech stack and AI adoption."""
        
        if company.ai_maturity == "Very Strong" or company.saas_maturity >= 8:
            return "Mature"
        elif company.saas_maturity >= 5:
            return "Growth"
        else:
            return "Emerging"


class InvestmentRiskClassifier:
    """Classify by investment risk: Low, Medium, High."""
    
    def classify(self, company: Company) -> str:
        """Assess investment risk profile."""
        
        risk_factors = 0
        
        # Profitability risk
        if company.financials.profit_margin and company.financials.profit_margin < 0:
            risk_factors += 2
        elif not company.financials.profit_margin:
            risk_factors += 1
        
        # Growth risk
        if company.financials.growth_rate and company.financials.growth_rate < 5:
            risk_factors += 1
        
        # Funding cushion risk
        if company.financials.funding_raised:
            monthly_burn = (company.financials.revenue or 0) * 0.1 / 12
            if monthly_burn > 0:
                runway_months = company.financials.funding_raised / monthly_burn
                if runway_months < 12:
                    risk_factors += 2
        
        if risk_factors >= 4:
            return "High"
        elif risk_factors >= 2:
            return "Medium"
        else:
            return "Low"


# Use custom classifier in scoring
class CustomScorer:
    """Scorer using custom classification."""
    
    def __init__(self, classifier: CompanyClassifier):
        self.classifier = classifier
    
    def classify_company(self, company: Company) -> str:
        """Use injected classifier."""
        return self.classifier.classify(company)
```

---

## Best Practices for Extensions

### 1. Use Dependency Injection

❌ **Bad** — Hard to test, tightly coupled:

```python
def score_companies():
    repo = SupabaseRepository()  # ❌ Concrete dependency
    companies = repo.find_all()
    # ...
```

✅ **Good** — Testable, extensible:

```python
def score_companies(repo: CompanyRepository = Depends(get_repository)):
    companies = repo.find_all()  # ✅ Interface dependency
    # ...
```

### 2. Keep Domain Model Pure

❌ **Bad** — Domain coupled to frameworks:

```python
from sqlalchemy import Column, String
from pydantic import BaseModel

class Company(BaseModel):
    id: str = Column(String, primary_key=True)  # ❌ SQLAlchemy leak
```

✅ **Good** — Framework-agnostic domain:

```python
from dataclasses import dataclass

@dataclass
class Company:
    id: str  # ✅ Pure Python
    name: str
```

### 3. Make Configuration External

❌ **Bad** — Hard-coded thresholds:

```python
if growth_score >= 7.0:  # ❌ Magic number
    classification = "Rocket"
```

✅ **Good** — Configurable thresholds:

```python
class ScoringConfig:
    rocket_threshold: float = 7.0

if growth_score >= self.config.rocket_threshold:  # ✅ Configurable
    classification = "Rocket"
```

### 4. Test Extensions Independently

Create tests that don't depend on the whole system:

```python
# ✅ GOOD — Minimal dependencies
def test_environmental_score():
    scorer = GrowthScorer(ScoringSettings())
    company = Company(id="test", name="Test")
    result = scorer.calculate_scores(company)
    assert result.environmental_score is not None

# ❌ BAD — Full system test
def test_api_endpoint():
    response = client.get("/companies/test")
    assert "environmental_score" in response.json()
```

### 5. Document Your Extension

Create an ADR explaining:
- **Why** the extension exists (use case)
- **How** it integrates
- **Consequences** (breaking changes? performance impact?)
- **Future plans**

---

## Extension Checklist

When adding a new extension, verify:

- [ ] Interface properly defined (Abstract base class or Protocol)
- [ ] Configuration externalized (Pydantic model or settings)
- [ ] Domain model updated (if needed)
- [ ] API routes added (if user-facing)
- [ ] Unit tests cover happy path and edge cases
- [ ] Integration tests with mocked dependencies
- [ ] Documentation and ADR created
- [ ] CHANGELOG updated
- [ ] No hard-coded values or paths
- [ ] Error handling for failures
- [ ] Example code provided

---

## Example: Full Extension Walkthrough

See `/docs/examples/custom_scoring_dimension_example.py` *(coming soon)* for a complete, runnable example of adding a scoring dimension.

---

## References

- [Architecture Decisions](../architecture/decisions.md) — Design patterns
- [Developer Guide](developer.md) — Code structure
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — Review process

---

*Last Updated: February 20, 2026*
*Maintained by: Architecture & Extensions Team*

