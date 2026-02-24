# Python API Client Examples

Complete Python examples for interacting with the Solstein API.

## Prerequisites

```bash
pip install requests
```

## Basic Client Setup

```python
import requests
from typing import Dict, List, Optional

class SolsteinClient:
    """Python client for Solstein API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def health_check(self) -> Dict:
        """Check API health status."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def list_companies(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """List all companies with pagination."""
        params = {"skip": skip, "limit": limit}
        response = requests.get(f"{self.base_url}/companies", params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_company(self, company_id: str) -> Dict:
        """Get a specific company by ID."""
        response = requests.get(f"{self.base_url}/companies/{company_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def score_company(self, company_id: str) -> Dict:
        """Score a specific company."""
        response = requests.post(
            f"{self.base_url}/scoring/company/{company_id}/score",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_market_analysis(self, industry: Optional[str] = None) -> Dict:
        """Get market-wide analysis."""
        params = {}
        if industry:
            params["industry"] = industry
        response = requests.get(f"{self.base_url}/market/analysis", params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def search_companies(self, query: str, field: str = "name") -> Dict:
        """Search companies by keyword."""
        params = {"query": query, "field": field}
        response = requests.get(f"{self.base_url}/market/search", params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()


# Usage Examples

if __name__ == "__main__":
    # Initialize client
    client = SolsteinClient(base_url="http://localhost:8000")
    
    # 1. Health check
    health = client.health_check()
    print(f"API Status: {health['status']}")
    
    # 2. List all companies
    companies = client.list_companies(limit=10)
    print(f"\nFound {len(companies)} companies")
    
    # 3. Get specific company
    try:
        company = client.get_company("acme-energy-bv")
        print(f"\nCompany: {company['name']}")
        print(f"Classification: {company.get('classification', 'Not scored')}")
    except requests.HTTPError as e:
        print(f"Company not found: {e}")
    
    # 4. Score a company
    try:
        scores = client.score_company("acme-energy-bv")
        print(f"\nScores for {scores['company_id']}:")
        print(f"  Growth: {scores['growth_score']}")
        print(f"  Financial Health: {scores['financial_health_score']}")
        print(f"  Classification: {scores['classification']}")
    except requests.HTTPError as e:
        print(f"Scoring failed: {e}")
    
    # 5. Market analysis
    analysis = client.get_market_analysis(industry="Energy Software")
    print(f"\nMarket Analysis:")
    print(f"  Total Companies: {analysis.get('total_companies', 'N/A')}")
    
    # 6. Search companies
    results = client.search_companies("energy", field="industry")
    print(f"\nSearch Results: {results['total_results']} matches")
```

## Advanced Examples

### Batch Scoring Multiple Companies

```python
def batch_score_companies(client: SolsteinClient, company_ids: List[str]) -> List[Dict]:
    """Score multiple companies and return results."""
    results = []
    
    for company_id in company_ids:
        try:
            score = client.score_company(company_id)
            results.append({
                "company_id": company_id,
                "status": "success",
                "classification": score["classification"],
                "growth_score": score["growth_score"]
            })
        except requests.HTTPError as e:
            results.append({
                "company_id": company_id,
                "status": "error",
                "error": str(e)
            })
    
    return results

# Usage
company_ids = ["company-1", "company-2", "company-3"]
results = batch_score_companies(client, company_ids)

phoenix_count = sum(1 for r in results if r.get("classification") == "Phoenix")
print(f"Found {phoenix_count} Phoenix companies out of {len(results)}")
```

### Filter Companies by Classification

```python
def get_companies_by_classification(client: SolsteinClient, classification: str) -> List[Dict]:
    """Get all companies with a specific classification."""
    all_companies = client.list_companies(limit=1000)
    
    # Score companies that haven't been scored yet
    scored_companies = []
    for company in all_companies:
        if "classification" not in company or not company["classification"]:
            try:
                score = client.score_company(company["id"])
                company.update(score)
            except requests.HTTPError:
                continue
        
        if company.get("classification") == classification:
            scored_companies.append(company)
    
    return scored_companies

# Get all Phoenix companies
phoenix_companies = get_companies_by_classification(client, "Phoenix")
print(f"\n🔥 Phoenix Companies ({len(phoenix_companies)}):")
for company in phoenix_companies:
    print(f"  - {company['name']} (Growth: {company['growth_score']})")
```

### Export Data for Analysis

```python
import json

def export_company_data(client: SolsteinClient, filename: str = "companies_export.json"):
    """Export all company data to JSON file."""
    companies = client.list_companies(limit=1000)
    
    # Enrich with scores
    enriched_data = []
    for company in companies:
        try:
            scores = client.score_company(company["id"])
            company_data = {**company, **scores}
            enriched_data.append(company_data)
        except requests.HTTPError:
            enriched_data.append(company)
    
    # Export to file
    with open(filename, 'w') as f:
        json.dump({
            "exported_at": "2026-02-24T00:00:00Z",
            "total_companies": len(enriched_data),
            "companies": enriched_data
        }, f, indent=2)
    
    print(f"Exported {len(enriched_data)} companies to {filename}")

# Usage
export_company_data(client, "my_companies.json")
```

### Error Handling Best Practices

```python
from requests.exceptions import HTTPError, ConnectionError, Timeout

def robust_api_call(client: SolsteinClient, company_id: str, max_retries: int = 3):
    """Make API call with retry logic."""
    for attempt in range(max_retries):
        try:
            return client.score_company(company_id)
        except ConnectionError:
            if attempt < max_retries - 1:
                print(f"Connection failed, retrying... ({attempt + 1}/{max_retries})")
                continue
            raise
        except Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout, retrying... ({attempt + 1}/{max_retries})")
                continue
            raise
        except HTTPError as e:
            if e.response.status_code == 404:
                print(f"Company {company_id} not found")
                return None
            if e.response.status_code == 500:
                if attempt < max_retries - 1:
                    print(f"Server error, retrying... ({attempt + 1}/{max_retries})")
                    continue
            raise
    
    return None
```

## Testing with Mock Data

```python
from unittest.mock import Mock, patch

def test_client():
    """Test client with mocked responses."""
    client = SolsteinClient()
    
    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {
        "company_id": "test-corp",
        "growth_score": 8.5,
        "classification": "Phoenix"
    }
    mock_response.raise_for_status.return_value = None
    
    with patch('requests.post', return_value=mock_response):
        result = client.score_company("test-corp")
        assert result["classification"] == "Phoenix"
        print("✓ Test passed!")

test_client()
```

---

**Next:** See [JavaScript Examples](javascript-examples.md) for frontend integration
