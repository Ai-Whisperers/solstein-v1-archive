# 📚 Solstein Examples Repository

**Runnable code examples demonstrating common Solstein tasks and patterns.**

---

## Overview

This directory contains production-quality examples for:
- Using the Python client API
- Implementing custom scoring dimensions
- Writing tests
- Building exporters
- Integrating data sources

Each example is **self-contained**, **fully commented**, and **runnable**.

---

## Quick Index

### For Data Scientists & Analysts

| Example | Purpose | Time |
|---------|---------|------|
| [`python_client_quickstart.py`](#python_client_quickstart) | Query Solstein from Python | 10 min |
| [`batch_scoring_workflow.py`](#batch_scoring_workflow) | Score 100+ companies | 15 min |
| [`market_analysis_cookbook.md`](#market_analysis_cookbook) | Common analysis patterns | 20 min |

### For Backend Developers

| Example | Purpose | Time |
|---------|---------|------|
| [`custom_scoring_dimension.py`](#custom_scoring_dimension) | Add new scoring axis | 30 min |
| [`test_scoring_dimension.py`](#test_scoring_dimension) | Complete test example | 15 min |
| [`data_source_integration.py`](#data_source_integration) | Integrate external data | 25 min |

### For Operators

| Example | Purpose | Time |
|---------|---------|------|
| [`docker_deployment.sh`](#docker_deployment) | Deploy with Docker | 10 min |
| [`monitoring_setup.py`](#monitoring_setup) | Configure monitoring | 20 min |

---

## Python Client Quickstart

**File:** `python_client_quickstart.py`

Quick example of using Solstein from Python:

```python
# 1. Import the client
from solstein.data.repositories import SupabaseRepository
from solstein.analytics.scoring import GrowthScorer

# 2. Initialize
repo = SupabaseRepository()
scorer = GrowthScorer()

# 3. Load companies
all_companies = repo.find_all()

# 4. Score them
for company in all_companies:
    scored = scorer.calculate_scores(company)
    repo.save(scored)
    print(f"{company.name}: {scored.classification}")

# 5. Filter results
rockets = [c for c in all_companies if c.classification == "Rocket"]
print(f"Found {len(rockets)} Rockets")
```

**Next:** See full example in `python_client_quickstart.py`

---

## Batch Scoring Workflow

**File:** `batch_scoring_workflow.py`

Score entire markets and export results:

```python
import asyncio
from solstein.data.repositories import SupabaseRepository
from solstein.analytics.scoring import GrowthScorer
from solstein.exporters.excel_exporter import ExcelExporter
from solstein.core.repositories import CompanyFilter

async def score_market(market: str, output_file: str):
    """Score all companies in a market and export to Excel."""
    
    # 1. Load companies
    repo = SupabaseRepository()
    filters = CompanyFilter(market=market)
    companies = repo.find_all(filters)
    
    print(f"Scoring {len(companies)} companies in {market}...")
    
    # 2. Score each
    scorer = GrowthScorer()
    for i, company in enumerate(companies):
        scored = scorer.calculate_scores(company)
        repo.save(scored)
        
        # Progress
        if (i + 1) % 10 == 0:
            print(f"  Scored {i + 1}/{len(companies)}")
    
    # 3. Export
    exporter = ExcelExporter()
    output_path = exporter.export(companies, output_file)
    
    print(f"✓ Export complete: {output_path}")
    
    # 4. Summary
    rockets = sum(1 for c in companies if c.classification == "Rocket")
    dinosaurs = sum(1 for c in companies if c.classification == "Dinosaur")
    
    print(f"\nResults:")
    print(f"  🚀 Rockets: {rockets}")
    print(f"  ⚖️  Neutral: {len(companies) - rockets - dinosaurs}")
    print(f"  🦕 Dinosaurs: {dinosaurs}")

# Run it
if __name__ == "__main__":
    asyncio.run(score_market("European Energy Software", "output.xlsx"))
```

**Next:** See full example in `batch_scoring_workflow.py`

---

## Market Analysis Cookbook

**File:** `market_analysis_cookbook.md`

Collection of common analysis patterns with code:

```python
# Pattern 1: Find high-growth companies
high_growth = [c for c in companies if c.financials.growth_rate and c.financials.growth_rate > 30]

# Pattern 2: Segment by classification
segments = {}
for classification in ["Rocket", "Neutral", "Dinosaur"]:
    segments[classification] = [c for c in companies if c.classification == classification]

# Pattern 3: Financial metrics analysis
avg_revenue = sum(c.financials.revenue or 0 for c in companies) / len(companies)
avg_growth = sum(c.financials.growth_rate or 0 for c in companies) / len(companies)

# Pattern 4: Competitive overlap
def find_competitors(company: Company, all_companies: list[Company]) -> list[Company]:
    """Find companies with overlapping attributes."""
    return [
        c for c in all_companies
        if c.id != company.id
        and c.industry == company.industry
        and abs((c.financials.revenue or 0) - (company.financials.revenue or 0)) < 50
    ]

# Pattern 5: Risk analysis
risky_companies = [
    c for c in companies
    if (c.financial_health_score or 0) < 4.0
    and (c.growth_score or 0) < 5.0
]
```

**Next:** See full examples in `market_analysis_cookbook.md`

---

## Custom Scoring Dimension

**File:** `custom_scoring_dimension.py`

Complete walkthrough of adding a new scoring dimension (Environmental Score):

```python
from dataclasses import dataclass
from solstein.core.scoring_config import ScoringSettings, GrowthScoringConfig
from solstein.domain.models import Company, ScoringExplanation, ScoreComponent

# Step 1: Configuration
@dataclass
class EnvironmentalConfig:
    base_score: float = 5.0
    has_esg_cert_bonus: float = 2.0
    carbon_low_bonus: float = 2.5
    carbon_high_penalty: float = -2.0

# Step 2: Calculation function
def calculate_environmental_score(
    company: Company,
    config: EnvironmentalConfig
) -> tuple[float, ScoringExplanation]:
    """Calculate environmental impact score."""
    
    score = config.base_score
    explanation = ScoringExplanation(base_score=score)
    
    # ESG Certification bonus
    if hasattr(company, 'has_esg_cert') and company.has_esg_cert:
        score += config.has_esg_cert_bonus
        explanation.components.append(ScoreComponent(
            name="ESG Certification",
            value=config.has_esg_cert_bonus,
            formula=f"+{config.has_esg_cert_bonus}",
            reasoning="Company has ESG certification"
        ))
    
    # Carbon footprint
    if hasattr(company, 'annual_carbon_emissions'):
        emissions = company.annual_carbon_emissions
        if emissions < 100:  # Low threshold
            score += config.carbon_low_bonus
        elif emissions > 1000:  # High threshold
            score += config.carbon_high_penalty
    
    return min(score, 10.0), explanation

# Step 3: Integration
def score_with_environmental(company: Company) -> Company:
    """Score company including environmental dimension."""
    config = EnvironmentalConfig()
    score, explanation = calculate_environmental_score(company, config)
    
    company.environmental_score = score
    company.scoring_breakdown["environmental"] = explanation
    
    return company
```

**Next:** See full example in `custom_scoring_dimension.py`

---

## Testing Custom Dimension

**File:** `test_scoring_dimension.py`

Complete test suite for the custom dimension:

```python
import pytest
from solstein.domain.models import Company, FinancialMetric

def test_environmental_score_base():
    """Base score without additional data."""
    company = Company(id="test", name="Test")
    company.financials = FinancialMetric()
    
    from custom_scoring_dimension import score_with_environmental
    result = score_with_environmental(company)
    
    assert result.environmental_score == 5.0  # Base score

def test_environmental_score_with_esg():
    """ESG certification adds bonus."""
    company = Company(id="test", name="Green Corp")
    company.financials = FinancialMetric()
    company.has_esg_cert = True
    
    from custom_scoring_dimension import score_with_environmental
    result = score_with_environmental(company)
    
    assert result.environmental_score > 5.0

def test_environmental_score_low_carbon():
    """Low carbon footprint adds bonus."""
    company = Company(id="test", name="Eco Friendly")
    company.financials = FinancialMetric()
    company.annual_carbon_emissions = 50.0  # Low
    
    from custom_scoring_dimension import score_with_environmental
    result = score_with_environmental(company)
    
    assert result.environmental_score > 5.0

@pytest.mark.parametrize("emissions,expected_impact", [
    (50.0, "positive"),    # Low → bonus
    (500.0, "neutral"),    # Medium → no change
    (1500.0, "negative"),  # High → penalty
])
def test_environmental_score_carbon_levels(emissions, expected_impact):
    """Carbon thresholds affect score correctly."""
    company = Company(id="test", name="Test")
    company.financials = FinancialMetric()
    company.annual_carbon_emissions = emissions
    
    from custom_scoring_dimension import score_with_environmental
    result = score_with_environmental(company)
    
    base_score = 5.0
    if expected_impact == "positive":
        assert result.environmental_score > base_score
    elif expected_impact == "neutral":
        assert result.environmental_score == base_score
    elif expected_impact == "negative":
        assert result.environmental_score < base_score
```

**Next:** See full test suite in `test_scoring_dimension.py`

---

## Data Source Integration

**File:** `data_source_integration.py`

Integrate companies from external API (example: Crunchbase):

```python
import requests
from solstein.domain.models import Company, FinancialMetric

class CrunchbaseLoader:
    """Fetch company data from Crunchbase API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.crunchbase.com/v4"
    
    def fetch_company(self, company_name: str) -> Company | None:
        """Fetch company by name."""
        
        headers = {"X-Crunchbase-API-Key": self.api_key}
        payload = {
            "entity_types": ["Company"],
            "query": company_name,
            "limit": 1
        }
        
        response = requests.post(
            f"{self.base_url}/searches/entities",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if not response.ok:
            return None
        
        data = response.json()
        if not data.get("entities"):
            return None
        
        entity = data["entities"][0]
        return self._parse_entity(entity)
    
    def _parse_entity(self, entity: dict) -> Company:
        """Convert Crunchbase data to Company domain model."""
        props = entity.get("properties", {})
        
        company = Company(
            id=entity.get("uuid", ""),
            name=props.get("name", ""),
            industry=props.get("primary_category", ""),
            website=props.get("website", {}).get("value"),
        )
        
        company.financials = FinancialMetric(
            revenue=props.get("revenue_usd"),
            funding_raised=props.get("funding_total", {}).get("value_usd"),
        )
        
        return company

# Usage
if __name__ == "__main__":
    import os
    api_key = os.getenv("CRUNCHBASE_API_KEY")
    
    loader = CrunchbaseLoader(api_key)
    company = loader.fetch_company("Stripe")
    
    if company:
        print(f"{company.name}: ${company.financials.funding_raised}M raised")
```

**Next:** See full example in `data_source_integration.py`

---

## Docker Deployment

**File:** `docker_deployment.sh`

Complete Docker setup and deployment:

```bash
#!/bin/bash

# Build Docker image
docker build -t solstein:latest .

# Run with Docker Compose (includes API, PostgreSQL, Redis)
docker compose up -d

# Verify services are running
docker ps

# Check API health
curl http://localhost:8000/health

# View logs
docker logs -f solstein-api

# Stop services
docker compose down
```

**Next:** See full setup script in `docker_deployment.sh`

---

## Monitoring Setup

**File:** `monitoring_setup.py`

Configure Prometheus metrics and health checks:

```python
from prometheus_client import Counter, Histogram, start_http_server
from solstein.api.main import app
import time

# Define metrics
request_count = Counter(
    'solstein_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'solstein_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

score_calculations = Counter(
    'solstein_scores_calculated_total',
    'Total scores calculated'
)

# Middleware to collect metrics
@app.middleware("http")
async def track_metrics(request, call_next):
    start = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

# Start Prometheus metrics endpoint
if __name__ == "__main__":
    start_http_server(8001)  # Metrics on port 8001
    # ... start API ...
```

**Next:** See full monitoring setup in `monitoring_setup.py`

---

## Running Examples

### Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Set environment
export SOLSTEIN_DATABASE__URL=postgresql://localhost/solstein
export SOLSTEIN_REDIS__URL=redis://localhost:6379/0
```

### Run Individual Examples

```bash
# Python client
python docs/examples/python_client_quickstart.py

# Batch scoring
python docs/examples/batch_scoring_workflow.py

# Custom dimension
python docs/examples/custom_scoring_dimension.py

# Tests
pytest docs/examples/test_scoring_dimension.py -v
```

---

## Organization

```
docs/examples/
├── README.md                              ← This file
├── python_client_quickstart.py           ← Client usage example
├── batch_scoring_workflow.py             ← Market scoring workflow
├── market_analysis_cookbook.md           ← Analysis patterns
├── custom_scoring_dimension.py           ← Add custom dimension
├── test_scoring_dimension.py             ← Testing examples
├── data_source_integration.py            ← External data integration
├── docker_deployment.sh                  ← Docker setup
├── monitoring_setup.py                   ← Monitoring configuration
└── utils.py                              ← Shared test utilities
```

---

## When to Use Which Example

| Situation | Use Example |
|-----------|------------|
| New to Solstein API | `python_client_quickstart.py` |
| Score entire market | `batch_scoring_workflow.py` |
| Analyze companies | `market_analysis_cookbook.md` |
| Add scoring feature | `custom_scoring_dimension.py` |
| Write tests | `test_scoring_dimension.py` |
| Integrate data | `data_source_integration.py` |
| Deploy | `docker_deployment.sh` |
| Monitor production | `monitoring_setup.py` |

---

## Contributing Examples

To add a new example:

1. Create file: `docs/examples/my_example.py`
2. Include docstring explaining the example
3. Add comments throughout code
4. Update this README with entry
5. Include unit tests if applicable
6. Ensure code passes `ruff format` and `mypy`

---

## References

- [Developer Guide](../guides/developer.md) — Setup and architecture
- [API Reference](../api/reference.md) — Endpoint documentation
- [Extending Solstein](../guides/extending-solstein.md) — Custom features
- [Code Conventions](../guides/code-conventions.md) — Style guide

---

*Last Updated: February 20, 2026*
*Maintained by: Dev Evangelism Team*

