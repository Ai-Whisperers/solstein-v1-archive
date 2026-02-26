# Connector Enrichment Guide

## Overview

The Connector Enrichment system automatically fills NULL financial data in company profiles using three external data sources:

1. **SEC EDGAR** - US public company financial filings (10-K forms)
2. **Companies House** - UK company registration and financial data
3. **News Signal Detector** - Real-time news signals (funding, partnerships, key hires)

This guide explains how to use, configure, and extend the enrichment system.

## Quick Start

### Basic Usage

The enrichment system is automatically integrated into the data loading pipeline:

```python
from solstein.data.unified_loader import unified_loader

# Load companies - enrichment happens automatically
companies = unified_loader.load_unified_companies()

# Each company now has:
# - enrichment_sources: list of connectors that enriched it
# - enrichment_timestamps: when each enrichment occurred
# - enrichment_errors: any errors encountered during enrichment
```

### Manual Enrichment

You can also enrich individual companies:

```python
from solstein.data.unified_loader import UnifiedCompanyLoader
from solstein.domain.models import UnifiedCompany

loader = UnifiedCompanyLoader()
company = UnifiedCompany(id="AAPL", name="Apple Inc", ticker="AAPL")

# Enrich from all available connectors
enriched = loader.enrich_from_connectors(company)

# Or enrich from specific connectors
enriched = loader.fill_nulls_from_sec_edgar(company)
enriched = loader.fill_nulls_from_companies_house(enriched)
enriched = loader.attach_news_signals(enriched)
```

## Data Model

### New Company Fields

The `Company` model now includes fields for connector enrichment:

```python
# External Identifiers (required for lookups)
ticker: str | None = None                          # US stock ticker (e.g., "AAPL")
company_number: str | None = None                  # UK Companies House number
isin: str | None = None                            # International Securities ID
geography_code: str | None = None                  # "US", "UK", "EU", etc

# Enrichment Tracking
enrichment_sources: list[str] = []                 # Which connectors enriched this company
enrichment_timestamps: dict[str, datetime] = {}    # When each enrichment occurred
enrichment_errors: list[str] = []                  # Errors encountered during enrichment
```

### Enrichment Behavior

**Key Principle: Never Replace Existing Data**

The enrichment system ONLY fills NULL fields. If a field already has a value, it is never replaced:

```python
company = UnifiedCompany(
    id="AAPL",
    name="Apple Inc",
    ticker="AAPL",
    financials=FinancialMetric(
        revenue=400000000000,  # EXISTING - will NOT be replaced
        growth_rate=None,      # NULL - will be filled if available
    )
)

enriched = loader.fill_nulls_from_sec_edgar(company)
# Result: revenue stays 400B, growth_rate is filled from SEC if available
```

## Connector Details

### SEC EDGAR (US Companies)

**Scope**: US public companies with valid stock tickers

**Data Filled**:
- `revenue` - Annual revenue from 10-K filing
- `growth_rate` - Year-over-year revenue growth
- `employees` - Employee count
- `profit_margin` - Gross profit margin

**Configuration**:
```bash
# Set SEC API key (optional - uses free tier if not set)
export SEC_API_KEY="your-api-key"
```

**Example**:
```python
loader = UnifiedCompanyLoader()
company = UnifiedCompany(
    id="AAPL",
    name="Apple Inc",
    ticker="AAPL",  # Required for SEC lookup
    financials=FinancialMetric(revenue=None)
)
enriched = loader.fill_nulls_from_sec_edgar(company)
# Fetches latest 10-K filing and fills revenue, growth_rate, employees, profit_margin
```

**Retry Logic**:
- Tries current year, then previous 2 years
- Handles API rate limits gracefully
- Logs errors but continues with other enrichment

### Companies House (UK Companies)

**Scope**: UK registered companies with valid company numbers

**Data Filled**:
- `revenue` - Annual turnover from Companies House filing
- `employees` - Employee count
- `profit_margin` - Profit margin

**Configuration**:
```bash
# Set Companies House API key (required)
export COMPANIES_HOUSE_API_KEY="your-api-key"
```

**Example**:
```python
company = UnifiedCompany(
    id="ACME-UK",
    name="ACME Ltd",
    company_number="01234567",  # Required for Companies House lookup
    financials=FinancialMetric(revenue=None)
)
enriched = loader.fill_nulls_from_companies_house(company)
# Fetches latest filing and fills revenue, employees, profit_margin
```

### News Signal Detector

**Scope**: All companies (uses company name for search)

**Signals Detected**:
- Funding announcements (Series A, B, C, etc)
- Partnership announcements
- Key hire announcements

**Configuration**:
```bash
# Set NewsAPI key (required)
export NEWSAPI_KEY="your-api-key"
```

**Example**:
```python
company = UnifiedCompany(
    id="STARTUP",
    name="TechStartup Inc"
)
enriched = loader.attach_news_signals(company)
# Detects recent funding, partnership, and key hire signals
# Appends to company.signals list
```

## Enrichment Tracking

### Audit Trail

Every enrichment operation is tracked:

```python
enriched = loader.enrich_from_connectors(company)

# See which connectors enriched this company
print(enriched.enrichment_sources)
# Output: ['SEC EDGAR', 'News Signals (Funding)']

# See when each enrichment occurred
print(enriched.enrichment_timestamps)
# Output: {
#   'SEC EDGAR': datetime(2026, 2, 25, 19:30:00),
#   'News Signals': datetime(2026, 2, 25, 19:30:05)
# }

# See any errors that occurred
print(enriched.enrichment_errors)
# Output: ['SEC EDGAR API: Rate limit exceeded']
```

### Data Source Tracking

The `data_source_per_field` dictionary tracks where each field came from:

```python
print(enriched.data_source_per_field)
# Output: {
#   'revenue': 'SEC EDGAR',
#   'growth_rate': 'SEC EDGAR',
#   'employees': 'Companies House',
#   'profit_margin': 'JSON'  # Original source
# }
```

## Error Handling

The enrichment system is designed to be resilient:

1. **Graceful Degradation**: If a connector fails, enrichment continues with other connectors
2. **Error Tracking**: All errors are logged and tracked in `enrichment_errors`
3. **No Data Loss**: If enrichment fails, the original company data is preserved
4. **Specific Exception Handling**: Uses `ValueError` and `RuntimeError` for specific error types

```python
# Example: SEC fails, but Companies House succeeds
company = UnifiedCompany(
    id="MIXED",
    name="Mixed Company",
    ticker="INVALID",  # Will fail SEC lookup
    company_number="01234567",  # Will succeed CH lookup
    financials=FinancialMetric(revenue=None)
)

enriched = loader.enrich_from_connectors(company)
# Result:
# - SEC EDGAR fails (invalid ticker)
# - Companies House succeeds (fills revenue, employees)
# - enrichment_errors contains SEC error
# - enrichment_sources contains 'Companies House'
```

## Configuration

### Environment Variables

```bash
# SEC EDGAR (optional - uses free tier if not set)
export SEC_API_KEY="your-sec-api-key"

# Companies House (required for UK enrichment)
export COMPANIES_HOUSE_API_KEY="your-ch-api-key"

# News Signal Detector (required for news signals)
export NEWSAPI_KEY="your-newsapi-key"
```

### Programmatic Configuration

```python
from solstein.data.connectors.sec_edgar_connector import SECEdgarConnector
from solstein.data.connectors.companies_house_connector import CompaniesHouseConnector
from solstein.data.connectors.news_signal_detector import NewsSignalDetector
from solstein.data.unified_loader import UnifiedCompanyLoader

# Create connectors with custom configuration
sec = SECEdgarConnector(api_key="custom-key")
ch = CompaniesHouseConnector(api_key="custom-key")
news = NewsSignalDetector(api_key="custom-key")

# Create loader with custom connectors
loader = UnifiedCompanyLoader(
    sec_connector=sec,
    companies_house_connector=ch,
    news_detector=news
)

# Load companies with custom enrichment
companies = loader.load_unified_companies()
```

### Disabling Enrichment

To load companies without enrichment:

```python
# Create loader with no connectors
loader = UnifiedCompanyLoader(
    sec_connector=None,
    companies_house_connector=None,
    news_detector=None
)

# Load companies - no enrichment will occur
companies = loader.load_unified_companies()
```

## Testing

### Unit Tests

Test individual enrichment methods:

```bash
pytest tests/integration/test_connector_enrichment_real.py::TestSECEdgarEnrichment -v
pytest tests/integration/test_connector_enrichment_real.py::TestCompaniesHouseEnrichment -v
pytest tests/integration/test_connector_enrichment_real.py::TestNewsSignalEnrichment -v
```

### Integration Tests

Test the complete enrichment pipeline:

```bash
pytest tests/integration/test_connector_enrichment_real.py::TestEnrichmentPipeline -v
```

### Test Coverage

- ✅ Filling NULL fields from each connector
- ✅ Never replacing existing data
- ✅ Skipping enrichment when identifiers missing
- ✅ Handling API errors gracefully
- ✅ Tracking enrichment sources and timestamps
- ✅ Continuing enrichment when one connector fails

## Migration Guide

### From Old System

If you were using the old fake enrichment system:

**Before**:
```python
# Old system used fake Company objects with non-existent fields
company = Company(
    id="test",
    name="Test",
    ticker="TEST",  # This field didn't exist
    gross_margin=0.25  # This field didn't exist
)
```

**After**:
```python
# New system uses real Company model with proper fields
company = UnifiedCompany(
    id="test",
    name="Test",
    ticker="TEST",  # Now properly defined
    financials=FinancialMetric(
        profit_margin=0.25  # Use profit_margin, not gross_margin
    )
)
```

### Key Changes

1. **Model Fields**: Use `ticker`, `company_number`, `geography_code`, `isin` for lookups
2. **Financial Fields**: Use `financials.revenue`, `financials.profit_margin`, etc
3. **Enrichment Tracking**: Check `enrichment_sources`, `enrichment_timestamps`, `enrichment_errors`
4. **Error Handling**: Specific exception types (`ValueError`, `RuntimeError`) instead of broad `Exception`

## Troubleshooting

### No Data Filled

**Problem**: Enrichment runs but no data is filled

**Solutions**:
1. Check that identifiers are set: `ticker` for SEC, `company_number` for Companies House
2. Verify API keys are configured: `SEC_API_KEY`, `COMPANIES_HOUSE_API_KEY`, `NEWSAPI_KEY`
3. Check `enrichment_errors` for specific error messages
4. Verify the company exists in the external data source

### API Rate Limits

**Problem**: "Rate limit exceeded" errors

**Solutions**:
1. SEC EDGAR: Implements automatic retry with backoff (tries 3 years)
2. Companies House: Implement request caching (see Performance section)
3. News API: Implement request batching

### Missing Identifiers

**Problem**: "No ticker found" or "No company number found"

**Solutions**:
1. Manually set `ticker` or `company_number` on the company
2. Use `IdentifierLookupService` to look up identifiers (stub implementation in Phase 5)
3. Provide identifiers in the data source (JSON/Markdown)

## Performance Considerations

### Caching

For production use, implement caching to avoid repeated API calls:

```python
from functools import lru_cache

class CachedSECConnector:
    def __init__(self, connector):
        self.connector = connector
    
    @lru_cache(maxsize=1000)
    def fetch_filing(self, ticker, year, form_type):
        return self.connector.fetch_filing(ticker, year, form_type)
```

### Batch Processing

For large datasets, process companies in batches:

```python
from itertools import islice

companies = loader.load_unified_companies()

# Process in batches of 100
batch_size = 100
for i in range(0, len(companies), batch_size):
    batch = companies[i:i+batch_size]
    # Process batch...
```

### Rate Limiting

Implement rate limiting to respect API quotas:

```python
import time
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=60)  # 10 calls per minute
def fetch_with_rate_limit(ticker):
    return loader.sec_connector.fetch_filing(ticker, 2026, "10-K")
```

## Future Enhancements

### Phase 5 (Planned)

- [ ] Implement `IdentifierLookupService` with real ticker/company number lookups
- [ ] Add request caching for repeated queries
- [ ] Implement rate limit awareness
- [ ] Add configuration options to `UnifiedCompanyLoaderConfig`
- [ ] Add monitoring and metrics

### Phase 6 (Planned)

- [ ] Comprehensive developer documentation
- [ ] Migration guide for existing code
- [ ] Configuration reference
- [ ] Troubleshooting guide

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review test cases in `tests/integration/test_connector_enrichment_real.py`
3. Check enrichment logs: `enrichment_errors` and `enrichment_timestamps`
4. Review connector-specific documentation in connector modules
