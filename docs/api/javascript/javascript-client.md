# JavaScript/TypeScript API Client Examples

Complete JavaScript examples for integrating Solstein API into web applications.

## Prerequisites

```bash
npm install axios
# or
yarn add axios
```

## Basic Client (JavaScript)

```javascript
// solstein-client.js
class SolsteinClient {
  constructor(baseUrl = 'http://localhost:8000', apiKey = null) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.headers = {
      'Content-Type': 'application/json'
    };
    if (apiKey) {
      this.headers['Authorization'] = `Bearer ${apiKey}`;
    }
  }

  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async listCompanies(skip = 0, limit = 100) {
    const params = new URLSearchParams({ skip, limit });
    const response = await fetch(
      `${this.baseUrl}/companies?${params}`,
      { headers: this.headers }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getCompany(companyId) {
    const response = await fetch(
      `${this.baseUrl}/companies/${companyId}`,
      { headers: this.headers }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async scoreCompany(companyId) {
    const response = await fetch(
      `${this.baseUrl}/scoring/company/${companyId}/score`,
      {
        method: 'POST',
        headers: this.headers
      }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getMarketAnalysis(industry = null) {
    const params = industry ? `?industry=${encodeURIComponent(industry)}` : '';
    const response = await fetch(
      `${this.baseUrl}/market/analysis${params}`,
      { headers: this.headers }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async searchCompanies(query, field = 'name') {
    const params = new URLSearchParams({ query, field });
    const response = await fetch(
      `${this.baseUrl}/market/search?${params}`,
      { headers: this.headers }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}

// Usage
const client = new SolsteinClient('http://localhost:8000');

// Health check
client.healthCheck()
  .then(data => console.log('API Status:', data.status))
  .catch(err => console.error('Health check failed:', err));

// List companies
client.listCompanies(0, 10)
  .then(companies => {
    console.log(`Found ${companies.length} companies`);
    companies.forEach(c => console.log(`- ${c.name}`));
  });

// Score a company
client.scoreCompany('acme-energy-bv')
  .then(scores => {
    console.log('Classification:', scores.classification);
    console.log('Growth Score:', scores.growth_score);
  });
```

## TypeScript Client

```typescript
// solstein-client.ts

interface Company {
  id: string;
  name: string;
  industry: string;
  tier: string;
  ai_maturity: string;
  saas_maturity: number;
  growth_score?: number;
  financial_health_score?: number;
  competitive_position_score?: number;
  classification?: 'Phoenix' | 'Salt' | 'Lead';
  financials: {
    revenue: number;
    growth_rate: number;
    profit_margin: number;
  };
}

interface ScoreResponse {
  company_id: string;
  growth_score: number;
  financial_health_score: number;
  competitive_position_score: number;
  classification: 'Phoenix' | 'Salt' | 'Lead';
  calculated_at: string;
}

interface MarketAnalysis {
  industry: string;
  total_companies: number;
  summary: string;
  swot_analysis: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
    threats: string[];
  };
  key_trends: string[];
}

class SolsteinClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(baseUrl: string = 'http://localhost:8000', apiKey?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.headers = {
      'Content-Type': 'application/json'
    };
    if (apiKey) {
      this.headers['Authorization'] = `Bearer ${apiKey}`;
    }
  }

  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async listCompanies(skip: number = 0, limit: number = 100): Promise<Company[]> {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    const response = await fetch(
      `${this.baseUrl}/companies?${params}`,
      { headers: this.headers }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getCompany(companyId: string): Promise<Company> {
    const response = await fetch(
      `${this.baseUrl}/companies/${companyId}`,
      { headers: this.headers }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async scoreCompany(companyId: string): Promise<ScoreResponse> {
    const response = await fetch(
      `${this.baseUrl}/scoring/company/${companyId}/score`,
      {
        method: 'POST',
        headers: this.headers
      }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getMarketAnalysis(industry?: string): Promise<MarketAnalysis> {
    const params = industry ? `?industry=${encodeURIComponent(industry)}` : '';
    const response = await fetch(
      `${this.baseUrl}/market/analysis${params}`,
      { headers: this.headers }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}

export { SolsteinClient, Company, ScoreResponse, MarketAnalysis };
```

## React Hook Example

```jsx
// useSolstein.js
import { useState, useEffect } from 'react';

const useSolstein = (baseUrl = 'http://localhost:8000') => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCompanies = async (skip = 0, limit = 100) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ skip, limit });
      const response = await fetch(`${baseUrl}/companies?${params}`);
      if (!response.ok) throw new Error('Failed to fetch companies');
      const data = await response.json();
      setCompanies(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const scoreCompany = async (companyId) => {
    try {
      const response = await fetch(
        `${baseUrl}/scoring/company/${companyId}/score`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Scoring failed');
      return await response.json();
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  return { companies, loading, error, fetchCompanies, scoreCompany };
};

export default useSolstein;
```

```jsx
// CompaniesList.jsx
import React, { useEffect } from 'react';
import useSolstein from './useSolstein';

const CompaniesList = () => {
  const { companies, loading, error, fetchCompanies, scoreCompany } = useSolstein();

  useEffect(() => {
    fetchCompanies();
  }, []);

  const handleScore = async (companyId) => {
    const scores = await scoreCompany(companyId);
    if (scores) {
      alert(`Classification: ${scores.classification}`);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Companies ({companies.length})</h2>
      <ul>
        {companies.map(company => (
          <li key={company.id}>
            {company.name} - {company.industry}
            <button onClick={() => handleScore(company.id)}>
              Score
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CompaniesList;
```

## Vue.js Composable

```javascript
// useSolstein.js (Vue 3)
import { ref, computed } from 'vue';

export function useSolstein(baseUrl = 'http://localhost:8000') {
  const companies = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const phoenixCompanies = computed(() =>
    companies.value.filter(c => c.classification === 'Phoenix')
  );

  const fetchCompanies = async (skip = 0, limit = 100) => {
    loading.value = true;
    error.value = null;
    try {
      const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
      const response = await fetch(`${baseUrl}/companies?${params}`);
      if (!response.ok) throw new Error('Failed to fetch');
      companies.value = await response.json();
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  return {
    companies,
    loading,
    error,
    phoenixCompanies,
    fetchCompanies
  };
}
```

## Error Handling with Retry

```javascript
async function fetchWithRetry(url, options = {}, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.ok) return response.json();

      if (response.status === 500 && i < maxRetries - 1) {
        console.log(`Retry ${i + 1}/${maxRetries}...`);
        await new Promise(r => setTimeout(r, 1000 * (i + 1)));
        continue;
      }

      throw new Error(`HTTP ${response.status}`);
    } catch (err) {
      if (i === maxRetries - 1) throw err;
    }
  }
}

// Usage
fetchWithRetry('http://localhost:8000/companies')
  .then(data => console.log(data))
  .catch(err => console.error('Failed after retries:', err));
```

## Batch Operations

```javascript
async function batchScoreCompanies(client, companyIds) {
  const results = await Promise.allSettled(
    companyIds.map(id => client.scoreCompany(id))
  );

  return results.map((result, index) => ({
    companyId: companyIds[index],
    status: result.status,
    data: result.status === 'fulfilled' ? result.value : null,
    error: result.status === 'rejected' ? result.reason : null
  }));
}

// Usage
const ids = ['company-1', 'company-2', 'company-3'];
const results = await batchScoreCompanies(client, ids);

const successCount = results.filter(r => r.status === 'fulfilled').length;
console.log(`Scored ${successCount}/${ids.length} companies`);
```

---

**Next:** See the [Examples README](../README.md) for command-line and workflow references
