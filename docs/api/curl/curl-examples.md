# cURL Command Examples

Command-line examples for interacting with the Solstein API using cURL.

## Health Check

```bash
# Basic health check
curl http://localhost:8000/health

# With verbose output
curl -v http://localhost:8000/health

# Pretty print JSON
curl http://localhost:8000/health | jq .
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-02-24T12:00:00Z"
}
```

## Companies API

### List All Companies

```bash
# Basic listing
curl http://localhost:8000/companies

# With pagination
curl "http://localhost:8000/companies?skip=0&limit=10"

# Filter by industry
curl "http://localhost:8000/companies?industry=Energy%20Software"

# Filter by tier
curl "http://localhost:8000/companies?tier=Tier%201"

# Filter by minimum revenue
curl "http://localhost:8000/companies?min_revenue=10"

# Combine filters
curl "http://localhost:8000/companies?industry=Software&min_revenue=5&limit=50"

# Pretty print
curl http://localhost:8000/companies | jq .

# Save to file
curl http://localhost:8000/companies -o companies.json
```

### Get Single Company

```bash
# Get specific company
curl http://localhost:8000/companies/acme-energy-bv

# With authentication
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/companies/acme-energy-bv

# Pretty print
curl http://localhost:8000/companies/acme-energy-bv | jq .
```

### Create Company

```bash
# Create new company
curl -X POST http://localhost:8000/companies \
  -H "Content-Type: application/json" \
  -d '{
    "id": "new-corp-bv",
    "name": "New Corporation BV",
    "industry": "Energy Software",
    "tier": "Tier 2",
    "ai_maturity": "Medium",
    "saas_maturity": 7,
    "financials": {
      "revenue": 25.5,
      "growth_rate": 15.0,
      "profit_margin": 12.0
    }
  }'
```

## Scoring API

### Score a Company

```bash
# Score specific company
curl -X POST http://localhost:8000/scoring/company/acme-energy-bv/score

# With verbose output
curl -v -X POST http://localhost:8000/scoring/company/acme-energy-bv/score

# Pretty print
curl -X POST http://localhost:8000/scoring/company/acme-energy-bv/score | jq .
```

**Expected Response:**
```json
{
  "company_id": "acme-energy-bv",
  "growth_score": 8.2,
  "financial_health_score": 7.4,
  "competitive_position_score": 8.0,
  "classification": "Phoenix",
  "calculated_at": "2026-02-24T12:00:00Z"
}
```

### Get Scoring Statistics

```bash
# Market-wide statistics
curl http://localhost:8000/scoring/stats

# Pretty print with jq
curl http://localhost:8000/scoring/stats | jq .

# Extract specific field
curl http://localhost:8000/scoring/stats | jq '.growth_classification'
```

### Batch Scoring

```bash
# Queue batch scoring job
curl "http://localhost:8000/scoring/batch?industry=Energy%20Software"

# With minimum revenue filter
curl "http://localhost:8000/scoring/batch?min_revenue=10"

# Combine filters
curl "http://localhost:8000/scoring/batch?industry=Software&min_revenue=5"
```

## Market Analysis API

### Get Market Analysis

```bash
# Full market analysis
curl http://localhost:8000/market/analysis

# Filter by industry
curl "http://localhost:8000/market/analysis?industry=Energy%20Software"

# Filter by region
curl "http://localhost:8000/market/analysis?region=Europe"

# Pretty print
curl http://localhost:8000/market/analysis | jq .

# Extract SWOT analysis
curl http://localhost:8000/market/analysis | jq '.swot_analysis'

# Extract key trends
curl http://localhost:8000/market/analysis | jq '.key_trends'
```

### Search Companies

```bash
# Search by name
curl "http://localhost:8000/market/search?query=acme"

# Search by industry
curl "http://localhost:8000/market/search?query=energy&field=industry"

# Search by description
curl "http://localhost:8000/market/search?query=software&field=description"

# Pretty print
curl "http://localhost:8000/market/search?query=energy" | jq .
```

### Competitive Overlap

```bash
# Get competitive overlap for company
curl http://localhost:8000/market/overlap/acme-energy-bv

# Limit results
curl "http://localhost:8000/market/overlap/acme-energy-bv?top_n=5"

# Pretty print
curl http://localhost:8000/market/overlap/acme-energy-bv | jq .
```

## Export API

### Export to Excel

```bash
# Trigger Excel export
curl http://localhost:8000/export/excel

# With industry filter
curl "http://localhost:8000/export/excel?industry=Energy%20Software"

# Without charts
curl "http://localhost:8000/export/excel?include_charts=false"
```

### Export to JSON

```bash
# Export all companies as JSON
curl http://localhost:8000/export/json

# Filter by industry
curl "http://localhost:8000/export/json?industry=Software"

# Save to file
curl http://localhost:8000/export/json -o export.json

# Pretty print
curl http://localhost:8000/export/json | jq . > export_pretty.json
```

## Advanced Usage

### Authentication

```bash
# With Bearer token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/companies

# With token stored in variable
TOKEN="your-jwt-token"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/companies
```

### Error Handling

```bash
# Follow redirects
curl -L http://localhost:8000/companies

# Show HTTP headers
curl -I http://localhost:8000/health

# Show headers and body
curl -i http://localhost:8000/health

# Silent mode (no progress meter)
curl -s http://localhost:8000/health | jq .

# Handle errors gracefully
curl -f http://localhost:8000/companies/nonexistent || echo "Company not found"
```

### Scripts and Automation

```bash
#!/bin/bash
# score_all_companies.sh

API_URL="http://localhost:8000"

# Get all company IDs
company_ids=$(curl -s "${API_URL}/companies?limit=1000" | jq -r '.[].id')

# Score each company
for id in $company_ids; do
  echo "Scoring company: $id"
  curl -s -X POST "${API_URL}/scoring/company/${id}/score" | jq -c '{id: .company_id, classification: .classification, score: .growth_score}'
  sleep 0.5  # Rate limiting
done
```

```bash
#!/bin/bash
# export_daily.sh

API_URL="http://localhost:8000"
DATE=$(date +%Y%m%d)
OUTPUT_DIR="/backup/solstein"

# Create directory if needed
mkdir -p "$OUTPUT_DIR"

# Export JSON
echo "Exporting companies..."
curl -s "${API_URL}/export/json" -o "${OUTPUT_DIR}/companies_${DATE}.json"

# Verify export
if [ -f "${OUTPUT_DIR}/companies_${DATE}.json" ]; then
  count=$(jq '.total_companies' "${OUTPUT_DIR}/companies_${DATE}.json")
  echo "✓ Exported $count companies to ${OUTPUT_DIR}/companies_${DATE}.json"
else
  echo "✗ Export failed"
  exit 1
fi
```

### Testing with curl

```bash
# Test response time
curl -o /dev/null -s -w 'Total: %{time_total}s\n' http://localhost:8000/health

# Test with timing breakdown
curl -o /dev/null -s -w '
  DNS: %{time_namelookup}s
  Connect: %{time_connect}s
  TLS: %{time_appconnect}s
  TTFB: %{time_starttransfer}s
  Total: %{time_total}s
' http://localhost:8000/health

# Load test (10 requests)
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code} " http://localhost:8000/health
done
echo
```

## Common Patterns

### Filter and Process Results

```bash
# Get only Phoenix companies
curl -s http://localhost:8000/companies | \
  jq '[.[] | select(.classification == "Phoenix")]'

# Get company names only
curl -s http://localhost:8000/companies | \
  jq -r '.[].name'

# Get high-growth companies
curl -s http://localhost:8000/companies | \
  jq '[.[] | select(.growth_score > 7.0)] | sort_by(.growth_score) | reverse'

# Count by classification
curl -s http://localhost:8000/companies | \
  jq -r '.[].classification' | sort | uniq -c
```

### Combining API Calls

```bash
# Score company and immediately get details
curl -s -X POST http://localhost:8000/scoring/company/acme-energy-bv/score > /dev/null && \
curl -s http://localhost:8000/companies/acme-energy-bv | jq .

# Parallel requests (using xargs)
echo "company-1 company-2 company-3" | \
  xargs -P 3 -I {} curl -s http://localhost:8000/companies/{}
```

---

**Tip:** Install `jq` for JSON parsing:
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# Windows (with Chocolatey)
choco install jq
```

**Next:** See [Python Examples](../python/python-client.md) for programmatic access
