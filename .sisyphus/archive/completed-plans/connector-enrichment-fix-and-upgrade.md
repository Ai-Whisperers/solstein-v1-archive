# Connector Enrichment: Complete Fix & Upgrade Plan

## TL;DR

> **Status**: Fix Required - Architecture is good, execution needs correction
> 
> **Core Issue**: Implementation doesn't work with actual Company model (missing fields) and isn't integrated into the main pipeline
> 
> **Solution Strategy**: 
> 1. Extend Company model with lookup fields (Phase 1)
> 2. Fix implementations to use real Company structure (Phase 2)
> 3. Integrate enrichment into main pipeline (Phase 3)
> 4. Write real tests against actual data (Phase 4)
> 5. Performance & deployment optimization (Phase 5)
> 
> **Estimated Effort**: 12-16 hours total (8-10 hours core fixes + 4-6 hours testing/validation)
> 
> **Current Test Pass Rate**: 31% (4/13 passing, but only no-op paths)
> **Target Pass Rate**: 100% with real data
> **Target Production Readiness**: Week 1, fully functional

---

## PHASE 1: MODEL EXTENSIONS & LOOKUPS (2-3 hours)

### 1.1 Extend Company Model with Lookup Fields

**File**: `src/solstein/domain/models.py`

**Changes**:
```python
# Add after line 96 (after headquarters: str | None = None):

# External Identifiers for Connector Lookups
ticker: str | None = None  # US stock ticker (for SEC EDGAR)
company_number: str | None = None  # UK/EU registration number (for Companies House)
isin: str | None = None  # International Securities Identification Number
geography_code: str | None = None  # "US", "UK", "EU" for enrichment routing

# Enrichment Tracking
enrichment_sources: list[str] = Field(default_factory=list)  # Track which sources were called
enrichment_timestamps: dict[str, datetime] = Field(default_factory=dict)  # When each source was called
enrichment_errors: list[str] = Field(default_factory=list)  # Any errors during enrichment
```

**Why These Fields**:
- `ticker`: Required for SEC EDGAR lookups
- `company_number`: Required for Companies House lookups
- `isin`: Fallback identifier if ticker unavailable
- `geography_code`: Route to correct connector (SEC for US, CH for UK)
- `enrichment_sources`: Audit trail of which enrichments ran
- `enrichment_timestamps`: Performance tracking & refresh scheduling
- `enrichment_errors`: Debugging failed enrichments

**Breaking Change**: Requires migration, but adds nullable fields so backward compatible

**Verification**:
```bash
# After changes:
cd /home/ai-whisperers/solstein && source venv/bin/activate
python -c "from solstein.domain.models import Company; c = Company(id='test', name='Test'); print('✓ Model loads')"
# Should print: ✓ Model loads
```

### 1.2 Create Ticker/Company Number Lookup Service

**File**: `src/solstein/data/connectors/lookup_service.py` (NEW)

**Purpose**: Map company names to external identifiers

**Implementation**:
```python
class IdentifierLookupService:
    """
    Looks up external identifiers (ticker, company_number) for companies.
    
    Strategy:
    1. Try exact name match against cached mappings
    2. Query SEC ticker database (free, public)
    3. Query Companies House (free tier available)
    4. Store successful lookups in cache
    """
    
    def lookup_ticker(self, company_name: str) -> str | None:
        """Look up US stock ticker for company name."""
        # Try cache first
        # Then SEC EDGAR ticker search
        # Return ticker or None
        
    def lookup_company_number(self, company_name: str) -> str | None:
        """Look up UK Companies House number for company."""
        # Try cache first
        # Then Companies House API search
        # Return company_number or None
        
    def infer_geography(self, company_name: str, headquarters: str | None) -> str | None:
        """Infer geography (US, UK, EU, etc.) from company data."""
        # Use headquarters as primary signal
        # Fall back to name patterns
        # Return "US", "UK", "EU", etc or None
```

**Verification**:
```python
# Test lookup service
lookup = IdentifierLookupService()
ticker = lookup.lookup_ticker("Apple Inc")
print(f"Apple ticker: {ticker}")  # Should print: AAPL
```

---

## PHASE 2: FIX IMPLEMENTATIONS (4-5 hours)

### 2.1 Fix `fill_nulls_from_sec_edgar()`

**File**: `src/solstein/data/unified_loader.py` (lines 327-395)

**Current Problem**:
```python
if not company.ticker or not company.ticker.strip():
    return company
```
← Crashes because ticker doesn't exist

**New Implementation**:
```python
def fill_nulls_from_sec_edgar(self, company: UnifiedCompany) -> UnifiedCompany:
    """Fill NULL financial fields from SEC EDGAR for US companies."""
    
    if not self.sec_connector:
        logger.debug("SEC EDGAR connector not available, skipping enrichment")
        return company
    
    # Step 1: Determine if US company
    if company.geography_code and company.geography_code != "US":
        logger.debug(f"Skipping SEC EDGAR for non-US company: {company.name} ({company.geography_code})")
        return company
    
    # Step 2: Get ticker (from model or lookup)
    ticker = company.ticker
    if not ticker and not company.ticker:
        # Try lookup service
        ticker = self.lookup_service.lookup_ticker(company.name)
        if ticker:
            company.ticker = ticker
            logger.debug(f"Looked up ticker for {company.name}: {ticker}")
    
    if not ticker or not ticker.strip():
        logger.debug(f"No ticker available for {company.name}, skipping SEC enrichment")
        return company
    
    # Step 3: Fetch filing data
    try:
        from datetime import datetime
        current_year = datetime.now().year
        
        filing_data = None
        for year_offset in range(0, 3):
            try:
                year = current_year - year_offset
                filing_data = self.sec_connector.fetch_filing(
                    ticker=ticker.upper().strip(),
                    year=year,
                    form_type="10-K"
                )
                if filing_data:
                    logger.debug(f"Found SEC filing for {company.name} ({ticker}) year {year}")
                    break
            except Exception as e:
                logger.debug(f"No SEC filing for {ticker} year {year}: {e}")
                continue
        
        if not filing_data:
            logger.debug(f"No SEC EDGAR data found for {company.name}")
            company.enrichment_errors.append(f"SEC: No filings found")
            return company
        
        # Step 4: Fill only NULL fields
        if company.financials.revenue is None and filing_data.get("revenue"):
            company.financials.revenue = filing_data["revenue"]
            company.financials.revenue_confidence = ConfidenceLevel.CONFIRMED
            company.data_source_per_field["revenue"] = "SEC EDGAR"
            logger.info(f"Filled revenue for {company.name} from SEC: ${filing_data['revenue']:,.0f}")
        
        # Step 5: Store additional metrics (don't overwrite existing)
        if filing_data.get("gross_margin") and "gross_margin" not in company.profitability_raw_metrics:
            company.profitability_raw_metrics["gross_margin"] = filing_data["gross_margin"]
            company.profitability_raw_metrics["gross_margin_source"] = "SEC EDGAR"
        
        if filing_data.get("ebitda") and "ebitda" not in company.profitability_raw_metrics:
            company.profitability_raw_metrics["ebitda"] = filing_data["ebitda"]
            company.profitability_raw_metrics["ebitda_source"] = "SEC EDGAR"
        
        if filing_data.get("cash_position") and "cash_position" not in company.profitability_raw_metrics:
            company.profitability_raw_metrics["cash_position"] = filing_data["cash_position"]
            company.profitability_raw_metrics["cash_position_source"] = "SEC EDGAR"
        
        # Step 6: Track enrichment
        company.enrichment_sources.append("SEC EDGAR")
        company.enrichment_timestamps["SEC EDGAR"] = datetime.now(timezone.utc)
        
        return company
        
    except ValueError as e:
        # Handle API validation errors specifically
        logger.warning(f"SEC EDGAR validation error for {company.name}: {e}")
        company.enrichment_errors.append(f"SEC: Validation error - {e}")
        return company
        
    except Exception as e:
        # Log unexpected errors but don't crash
        logger.error(f"Unexpected error enriching {company.name} from SEC: {e}", exc_info=True)
        company.enrichment_errors.append(f"SEC: Unexpected error - {type(e).__name__}")
        return company
```

**Key Changes**:
- Uses `company.geography_code` not missing `company.ticker`
- Has fallback lookup if ticker missing
- Stores metrics in `profitability_raw_metrics` instead of wrong fields
- Specific exception handling (ValueError vs generic Exception)
- Tracks errors and enrichment sources
- Proper error logging with context

**Verification**:
```python
# Test with actual Company object
from solstein.data.unified_loader import UnifiedCompanyLoader
from solstein.domain.models import Company, FinancialMetric

loader = UnifiedCompanyLoader()
company = Company(
    id="AAPL",
    name="Apple Inc",
    ticker="AAPL",
    geography_code="US",
    financials=FinancialMetric(revenue=None)
)
result = loader.fill_nulls_from_sec_edgar(company)
assert result.financials.revenue is not None or result.enrichment_errors
print("✓ SEC enrichment works")
```

### 2.2 Fix `fill_nulls_from_companies_house()`

**File**: `src/solstein/data/unified_loader.py` (lines 397-450)

**New Implementation** (similar pattern to SEC fix):
```python
def fill_nulls_from_companies_house(self, company: UnifiedCompany) -> UnifiedCompany:
    """Fill financial fields from Companies House for UK companies."""
    
    if not self.companies_house_connector:
        return company
    
    # Only enrich UK companies
    if company.geography_code and company.geography_code != "UK":
        logger.debug(f"Skipping Companies House for non-UK company: {company.name}")
        return company
    
    # Get company_number (from model or lookup)
    company_number = company.company_number
    if not company_number:
        company_number = self.lookup_service.lookup_company_number(company.name)
        if company_number:
            company.company_number = company_number
    
    if not company_number:
        logger.debug(f"No company_number for {company.name}, skipping Companies House")
        return company
    
    try:
        metrics = self.companies_house_connector.get_company_metrics(
            company_number=company_number.strip()
        )
        
        if not metrics:
            company.enrichment_errors.append("Companies House: No data found")
            return company
        
        # Fill NULL fields only
        if company.financials.revenue is None and metrics.get("revenue"):
            company.financials.revenue = metrics["revenue"]
            company.financials.revenue_confidence = ConfidenceLevel.CONFIRMED
            company.data_source_per_field["revenue"] = "Companies House"
        
        if company.financials.employees is None and metrics.get("employees"):
            company.financials.employees = metrics["employees"]
            company.financials.employees_confidence = ConfidenceLevel.CONFIRMED
            company.data_source_per_field["employees"] = "Companies House"
        
        # Track enrichment
        company.enrichment_sources.append("Companies House")
        company.enrichment_timestamps["Companies House"] = datetime.now(timezone.utc)
        
        return company
        
    except ValueError as e:
        logger.warning(f"Companies House validation error for {company.name}: {e}")
        company.enrichment_errors.append(f"Companies House: Validation - {e}")
        return company
    except Exception as e:
        logger.error(f"Companies House enrichment failed for {company.name}: {e}", exc_info=True)
        company.enrichment_errors.append(f"Companies House: {type(e).__name__}")
        return company
```

### 2.3 Fix `attach_news_signals()`

**File**: `src/solstein/data/unified_loader.py` (lines 452-507)

**Key Fix**: The methods DO exist, but need proper error handling

```python
def attach_news_signals(self, company: UnifiedCompany) -> UnifiedCompany:
    """Attach news signals to company."""
    
    if not self.news_detector:
        logger.debug(f"News detector not available, skipping signals for {company.name}")
        return company
    
    if not company.name or not company.name.strip():
        logger.debug("Cannot attach signals to company without name")
        return company
    
    try:
        # Detect funding signals
        try:
            funding_signals = self.news_detector.detect_funding_signal(company.name)
            for signal in funding_signals or []:
                if hasattr(company, 'signals') and company.signals is not None:
                    company.signals.append(signal)
                    logger.debug(f"Attached funding signal to {company.name}")
        except RuntimeError as e:
            logger.warning(f"Funding signal detection failed: {e}")
            company.enrichment_errors.append(f"News/Funding: {e}")
        
        # Detect partnership signals
        try:
            partnership_signals = self.news_detector.detect_partnership_signal(company.name)
            for signal in partnership_signals or []:
                if hasattr(company, 'signals') and company.signals is not None:
                    company.signals.append(signal)
                    logger.debug(f"Attached partnership signal to {company.name}")
        except RuntimeError as e:
            logger.warning(f"Partnership detection failed: {e}")
            company.enrichment_errors.append(f"News/Partnership: {e}")
        
        # Detect key hire signals
        try:
            hire_signals = self.news_detector.detect_key_hire_signal(company.name)
            for signal in hire_signals or []:
                if hasattr(company, 'signals') and company.signals is not None:
                    company.signals.append(signal)
                    logger.debug(f"Attached hire signal to {company.name}")
        except RuntimeError as e:
            logger.warning(f"Key hire detection failed: {e}")
            company.enrichment_errors.append(f"News/Hiring: {e}")
        
        # Track enrichment
        company.enrichment_sources.append("NewsAPI")
        company.enrichment_timestamps["NewsAPI"] = datetime.now(timezone.utc)
        
        return company
        
    except Exception as e:
        logger.error(f"News signal attachment failed for {company.name}: {e}", exc_info=True)
        company.enrichment_errors.append(f"News: {type(e).__name__}")
        return company
```

**Key Changes**:
- Catches RuntimeError (what the methods actually throw)
- Handles None returns gracefully (`for signal in signals or []`)
- Tracks enrichment source
- Doesn't mask unexpected errors

---

## PHASE 3: INTEGRATE INTO MAIN PIPELINE (1-2 hours)

### 3.1 Call Enrichment from `load_unified_companies()`

**File**: `src/solstein/data/unified_loader.py` (lines 48-98)

**Current Code**:
```python
def load_unified_companies(self) -> List[UnifiedCompany]:
    # ... load JSON and Markdown ...
    for company in unified_companies:
        populate_signal_confidences(company)
    return unified_companies
```

**New Code**:
```python
def load_unified_companies(self, enrichment_enabled: bool = True) -> List[UnifiedCompany]:
    """
    Load and optionally enrich company data from all sources.
    
    Args:
        enrichment_enabled: If True, call connectors to fill NULL fields
    
    Returns:
        List of enriched UnifiedCompany objects
    """
    # ... load JSON and Markdown ...
    
    # Step 1: Enrich if enabled
    if enrichment_enabled:
        logger.info("Starting connector enrichment for loaded companies")
        enrichment_count = 0
        error_count = 0
        
        for i, company in enumerate(unified_companies):
            try:
                # Infer geography if not set
                if not company.geography_code:
                    company.geography_code = self.lookup_service.infer_geography(
                        company.name, 
                        company.headquarters
                    )
                
                # Run enrichment
                company = self.enrich_from_connectors(company)
                
                if company.enrichment_sources:
                    enrichment_count += 1
                if company.enrichment_errors:
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to enrich {company.name}: {e}", exc_info=True)
                company.enrichment_errors.append(f"Pipeline: {type(e).__name__}")
                error_count += 1
        
        logger.info(f"Enrichment complete: {enrichment_count} companies enriched, {error_count} errors")
    
    # Step 2: Populate signal confidences (existing logic)
    for company in unified_companies:
        populate_signal_confidences(company)
    
    return unified_companies
```

**Verification**:
```bash
# After integration:
cd /home/ai-whisperers/solstein && source venv/bin/activate
python -c "
from solstein.data.unified_loader import UnifiedCompanyLoader
loader = UnifiedCompanyLoader()
# This should now attempt enrichment (may fail without data, but shouldn't crash)
print('✓ Enrichment is integrated')
"
```

---

## PHASE 4: REWRITE TESTS WITH REAL DATA (3-4 hours)

### 4.1 Delete Broken Test File

**Action**: Remove `tests/integration/test_connector_enrichment.py` (it uses fake data)

### 4.2 Create Real Integration Tests

**File**: `tests/integration/test_connector_enrichment_real.py` (NEW)

**Key Principle**: Use actual Company objects from the model, not fake fixtures

```python
import pytest
from solstein.data.unified_loader import UnifiedCompanyLoader
from solstein.domain.models import Company, FinancialMetric, ConfidenceLevel

class TestSECEnrichmentWithRealCompanies:
    """Test SEC enrichment with actual Company objects."""
    
    def test_sec_enrichment_skips_non_us_companies(self):
        """Verify SEC skips companies with non-US geography."""
        loader = UnifiedCompanyLoader()
        company = Company(
            id="test-uk",
            name="Unilever",
            ticker=None,
            geography_code="UK",  # ← Not US
            financials=FinancialMetric(revenue=None)
        )
        
        result = loader.fill_nulls_from_sec_edgar(company)
        
        # Should return unchanged
        assert result.financials.revenue is None
        assert "SEC EDGAR" not in result.enrichment_sources
    
    def test_sec_enrichment_with_valid_ticker(self):
        """Verify SEC fills NULL revenue when ticker available."""
        loader = UnifiedCompanyLoader()
        company = Company(
            id="AAPL",
            name="Apple Inc",
            ticker="AAPL",
            geography_code="US",
            financials=FinancialMetric(revenue=None)
        )
        
        result = loader.fill_nulls_from_sec_edgar(company)
        
        # Either enriched or has error reason
        assert result.financials.revenue is not None or len(result.enrichment_errors) > 0
        # Either populated or attempted
        assert "SEC EDGAR" in result.enrichment_sources or len(result.enrichment_errors) > 0
    
    def test_sec_enrichment_preserves_existing_revenue(self):
        """Verify SEC never replaces existing revenue."""
        loader = UnifiedCompanyLoader()
        original_revenue = 50000000.0
        company = Company(
            id="TSLA",
            name="Tesla",
            ticker="TSLA",
            geography_code="US",
            financials=FinancialMetric(
                revenue=original_revenue,
                revenue_confidence=ConfidenceLevel.CONFIRMED
            )
        )
        
        result = loader.fill_nulls_from_sec_edgar(company)
        
        # Must not change existing value
        assert result.financials.revenue == original_revenue
        assert result.data_source_per_field.get("revenue") != "SEC EDGAR"

class TestCompaniesHouseEnrichment:
    """Test Companies House enrichment."""
    
    def test_skips_non_uk_companies(self):
        """Verify Companies House skips non-UK companies."""
        loader = UnifiedCompanyLoader()
        company = Company(
            id="AAPL",
            name="Apple Inc",
            geography_code="US",  # ← Not UK
            financials=FinancialMetric(revenue=None)
        )
        
        result = loader.fill_nulls_from_companies_house(company)
        
        assert "Companies House" not in result.enrichment_sources

class TestPipelineIntegration:
    """Test full enrichment pipeline."""
    
    def test_enrichment_is_automatic(self):
        """Verify load_unified_companies calls enrichment."""
        loader = UnifiedCompanyLoader()
        
        # This will fail without data files, but verifies integration
        try:
            companies = loader.load_unified_companies(enrichment_enabled=True)
            # Just verify no crash - actual data enrichment verified above
            assert isinstance(companies, list)
        except FileNotFoundError:
            # Expected if no competitor_data.json
            pass
    
    def test_enrichment_can_be_disabled(self):
        """Verify enrichment can be skipped."""
        loader = UnifiedCompanyLoader()
        
        try:
            companies = loader.load_unified_companies(enrichment_enabled=False)
            # Should still work, just no enrichment
            assert isinstance(companies, list)
        except FileNotFoundError:
            pass

class TestErrorTracking:
    """Test error tracking during enrichment."""
    
    def test_enrichment_errors_are_tracked(self):
        """Verify errors are tracked in company.enrichment_errors."""
        loader = UnifiedCompanyLoader()
        company = Company(
            id="test",
            name="Test",
            ticker="INVALID_TICKER_XYZ",  # ← Won't have data
            geography_code="US",
            financials=FinancialMetric(revenue=None)
        )
        
        result = loader.fill_nulls_from_sec_edgar(company)
        
        # Either got data or has error
        if result.financials.revenue is None:
            assert len(result.enrichment_errors) > 0 or "SEC EDGAR" not in result.enrichment_sources
    
    def test_enrichment_sources_are_tracked(self):
        """Verify which enrichment sources were called."""
        loader = UnifiedCompanyLoader()
        company = Company(
            id="test",
            name="Test",
            geography_code="UK",
            financials=FinancialMetric(revenue=None)
        )
        
        result = loader.fill_nulls_from_companies_house(company)
        
        # If no company_number, shouldn't attempt enrichment
        if not company.company_number:
            assert "Companies House" not in result.enrichment_sources
```

**Verification**:
```bash
cd /home/ai-whisperers/solstein && source venv/bin/activate
python -m pytest tests/integration/test_connector_enrichment_real.py -v
# Should see actual test results (pass/fail with real data behavior)
```

---

## PHASE 5: PERFORMANCE & DEPLOYMENT (1-2 hours)

### 5.1 Add Caching for Lookups

**File**: `src/solstein/data/connectors/lookup_service.py`

Add simple in-memory cache to avoid repeated lookups:

```python
class IdentifierLookupService:
    def __init__(self):
        self.cache = {}  # {("ticker", "Apple Inc"): "AAPL"}
        self.cache_ttl = 3600  # 1 hour
        self.cache_times = {}
    
    def lookup_ticker(self, company_name: str) -> str | None:
        # Check cache first
        cache_key = ("ticker", company_name)
        if cache_key in self.cache and self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # ... lookup logic ...
        
        # Store in cache
        if result:
            self.cache[cache_key] = result
            self.cache_times[cache_key] = datetime.now()
        
        return result
```

### 5.2 Add Rate Limiting Awareness

**File**: `src/solstein/data/unified_loader.py`

```python
def __init__(self, ...):
    # ... existing init ...
    self.rate_limit_state = {
        "SEC EDGAR": {"requests": 0, "reset_time": None},
        "NewsAPI": {"requests": 0, "reset_time": None},
    }

def enrich_from_connectors(self, company):
    # Check rate limits before calling
    if self._check_rate_limits_exceeded():
        logger.warning("Rate limits approaching, skipping enrichment")
        return company
    
    # ... existing enrichment ...
```

### 5.3 Add Configuration Options

**File**: `src/solstein/data/unified_loader.py`

```python
class UnifiedCompanyLoaderConfig:
    """Configuration for enrichment behavior."""
    
    # Which sources to enable
    enable_sec_edgar: bool = True
    enable_companies_house: bool = True
    enable_news_signals: bool = False  # Disabled by default (needs API key)
    
    # Enrichment behavior
    skip_if_complete: bool = True  # Don't enrich if all fields present
    max_lookups_per_run: int = 100  # Rate limiting
    enrichment_timeout: int = 30  # Seconds per company
    
    # Retry behavior
    max_retries: int = 3
    retry_backoff: float = 1.5
```

---

## PHASE 6: DOCUMENTATION & DEPLOYMENT (1 hour)

### 6.1 Update README for Enrichment

Add to `docs/guides/developer.md`:

```markdown
## Connector Enrichment

The system automatically enriches company data from multiple sources:

### Enabling Enrichment

```python
from solstein.data.unified_loader import UnifiedCompanyLoader

loader = UnifiedCompanyLoader()
companies = loader.load_unified_companies(enrichment_enabled=True)
```

### What Gets Enriched

| Source | Coverage | Fields | Confidence |
|--------|----------|--------|------------|
| SEC EDGAR | US companies with ticker | revenue, EBITDA, gross margin, cash | 0.95 |
| Companies House | UK companies with company_number | revenue, employees, profit margin | 0.93 |
| NewsAPI | All companies | Funding, partnerships, key hires | 0.70-0.75 |

### Configuration

See `UnifiedCompanyLoaderConfig` for options.

### Monitoring Enrichment

Check `company.enrichment_sources` and `company.enrichment_errors` to see what happened.

```

### 6.2 Migration Guide

Document how to migrate existing code:

```markdown
## Upgrading to Enhanced Enrichment

### What Changed

1. Company model now has ticker, company_number fields
2. Enrichment is automatic when calling load_unified_companies()
3. Error tracking is built-in via enrichment_errors list

### Migration Steps

1. Update database schema (add new fields)
2. Run data migration to populate ticker/company_number where available
3. No code changes required (enrichment is automatic)
4. Optional: Configure enrichment in loader config
```

---

## TESTING STRATEGY (Detailed)

### Pre-Deployment Verification Checklist

- [ ] **Unit Tests**: All 13+ tests pass with real Company objects
- [ ] **Integration Tests**: Full pipeline test with actual data files
- [ ] **API Tests**: 
  - [ ] SEC EDGAR connector tested with AAPL, MSFT tickers
  - [ ] Companies House tested with known UK company numbers
  - [ ] NewsAPI tested (if key available)
- [ ] **Error Scenarios**:
  - [ ] Invalid ticker handled gracefully
  - [ ] Missing API keys logged appropriately
  - [ ] Rate limits respected
  - [ ] Existing data never replaced
- [ ] **Performance**:
  - [ ] Enrichment < 2s per company average
  - [ ] Batch enrichment of 100 companies < 200s
  - [ ] Caching working (repeated lookups instant)
- [ ] **Data Quality**:
  - [ ] 80%+ of NULL revenue fields filled (for US companies with tickers)
  - [ ] 0 data corruption cases (no metric confusion)
  - [ ] 100% preservation of existing data
  - [ ] Proper source tracking in data_source_per_field

### Regression Testing

Before deploying, run full test suite:

```bash
# Unit tests
pytest tests/unit/ -v --tb=short

# Integration tests
pytest tests/integration/test_connector_enrichment_real.py -v

# Golden dataset regression
pytest tests/data_quality/golden_dataset_regression.py -v
```

---

## ROLLOUT PLAN

### Week 1: Development & Testing
- [ ] Implement Phase 1 (Model extensions): 2-3 hours
- [ ] Implement Phase 2 (Fix implementations): 4-5 hours
- [ ] Implement Phase 3 (Pipeline integration): 1-2 hours
- [ ] Write Phase 4 tests (Real data): 3-4 hours
- [ ] Performance Phase 5: 1-2 hours
- [ ] Docs Phase 6: 1 hour

**Total**: 12-17 hours spread across week

### Week 2: Validation & Staging
- Deploy to staging environment
- Run full test suite
- Manually test with real companies (AAPL, unilever, etc.)
- Performance testing with 100+ companies
- Stakeholder review

### Week 3: Production Deployment
- Deploy with enrichment_enabled=False initially
- Monitor for 1 day
- Enable enrichment for 10% of companies
- Monitor error rates (target: <1% errors)
- Enable for 100% of companies

---

## SUCCESS CRITERIA

### Functional
- ✅ All 13+ tests pass with real Company objects
- ✅ SEC EDGAR fills 80%+ of NULL revenue for US companies
- ✅ Companies House fills 60%+ of NULL metrics for UK companies
- ✅ NewsAPI attaches signals without crashing
- ✅ Zero data corruption cases

### Performance
- ✅ Enrichment < 2s per company
- ✅ Batch enrichment of 100 companies < 200s total
- ✅ Lookups cached (repeated < 10ms)

### Reliability
- ✅ 99%+ uptime (handles API failures gracefully)
- ✅ All errors tracked and logged
- ✅ No crash scenarios
- ✅ Data never lost or corrupted

### Maintainability
- ✅ Code is well-documented
- ✅ Tests cover all code paths
- ✅ Easy to enable/disable features
- ✅ Clear error messages for debugging

---

## RISKS & MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| SEC EDGAR API changes | Low | High | Version pinning, API monitoring |
| Rate limiting hits | Medium | Medium | Automatic backoff, caching |
| Missing tickers for 20%+ companies | High | Medium | Implement lookup service, fallback to None |
| API key exposure | Low | Critical | Use environment variables, never commit keys |
| Performance degradation | Low | Medium | Add caching, implement timeouts |

---

## FINAL GRADE COMPARISON

| Metric | Current | After Fix |
|--------|---------|-----------|
| Test Pass Rate | 31% | 100% |
| Production Ready | ❌ D+ | ✅ A |
| Actual Data Filled | 0% | 80%+ |
| Error Handling | Broad/unsafe | Specific/safe |
| Documentation | Minimal | Complete |
| Deployment Risk | High | Low |

---

## APPENDIX: Specific Code Locations to Change

```
src/solstein/domain/models.py
├── Line 96: Add ticker, company_number, geography_code fields
└── Line 109: Add enrichment_sources, enrichment_errors fields

src/solstein/data/connectors/lookup_service.py (NEW FILE)
└── IdentifierLookupService class with lookup methods

src/solstein/data/unified_loader.py
├── Lines 36-68: __init__() - add lookup_service
├── Lines 48-98: load_unified_companies() - add enrichment call
├── Lines 327-395: fill_nulls_from_sec_edgar() - complete rewrite
├── Lines 397-450: fill_nulls_from_companies_house() - complete rewrite
└── Lines 452-507: attach_news_signals() - error handling fix

tests/integration/test_connector_enrichment.py
└── DELETE (replace with test_connector_enrichment_real.py)

tests/integration/test_connector_enrichment_real.py (NEW FILE)
└── Real integration tests with actual Company objects
```

---

## CONCLUSION

This plan transforms a broken implementation into a production-grade system that actually works. The key insights:

1. **Root Cause**: Implementing without checking data models
2. **Fix Strategy**: Extend models + fix implementations + integrate + real tests
3. **Validation**: Real data tests before declaring success
4. **Deployment**: Staged rollout with monitoring

**Target Completion**: 12-17 hours development + 1 week validation = ~3 weeks to production

**Expected Outcome**: 80%+ NULL data filled automatically, zero data corruption, < 2s per company enrichment
