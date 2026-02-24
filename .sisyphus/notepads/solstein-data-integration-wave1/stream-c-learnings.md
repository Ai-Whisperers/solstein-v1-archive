# Stream C: News Signal Detector — Implementation Learnings

**Date**: February 24, 2026  
**Status**: ✅ COMPLETE  
**Tests**: 25/25 PASSING  

## What Was Built

### Core Implementation
- **File**: `src/solstein/data/connectors/news_signal_detector.py`
- **Class**: `NewsSignalDetector`
- **Lines of Code**: 385 (including docstrings)
- **Coverage**: 91% (11 lines uncovered - edge cases in date parsing)

### Key Features Implemented

1. **Funding Signal Detection**
   - Pattern: "Series [A-Z]", "raised $X million", "funding round", "investment round"
   - Confidence: 0.75
   - Handles multiple funding announcements per company

2. **Partnership Signal Detection**
   - Pattern: "partnership", "collaboration", "integrates with", "strategic alliance"
   - Confidence: 0.72
   - Detects various partnership keywords

3. **Key Hire Signal Detection**
   - Pattern: "appoints CEO", "joins as CTO", "new CFO", "executive appointment"
   - Confidence: 0.70
   - Covers C-suite and executive positions

4. **Rate Limit Tracking**
   - Daily limit: 100 queries/day (NewsAPI free tier)
   - Automatic counter reset at midnight
   - Warning at 90 queries (10% remaining)
   - Error raised at 100 queries

5. **Deduplication Logic**
   - Key: (company_name.lower(), signal_type, signal_date)
   - Case-insensitive company name matching
   - Prevents duplicate signals from same date
   - In-memory cache with `clear_seen_signals()` method

6. **Error Handling**
   - 429 Rate Limit: Raises RuntimeError with clear message
   - 500+ Server Errors: Raises RuntimeError with status code
   - Network Errors: Catches RequestException, re-raises as RuntimeError
   - Invalid API Key: Detects "status": "error" in response

## Test Coverage

### Test File
- **File**: `tests/unit/data/test_news_signal_detector.py`
- **Total Tests**: 25
- **Pass Rate**: 100% (25/25)
- **Coverage**: 91% of detector code

### Test Categories

1. **Initialization Tests** (3 tests)
   - API key from parameter
   - API key from environment variable
   - Missing API key raises ValueError

2. **Funding Signal Tests** (3 tests)
   - Successful detection
   - No matches (negative case)
   - Multiple patterns in same article

3. **Partnership Signal Tests** (2 tests)
   - Successful detection
   - Collaboration keyword pattern

4. **Key Hire Signal Tests** (2 tests)
   - Successful detection
   - Executive keyword pattern

5. **Deduplication Tests** (3 tests)
   - Same signal twice returns empty on second call
   - Case-insensitive deduplication
   - Clear cache functionality

6. **Rate Limit Tests** (5 tests)
   - Initial status (0/100)
   - Query counter increments
   - Exceeding limit raises error
   - Warning at 90 queries
   - Daily counter resets

7. **Confidence Scoring Tests** (3 tests)
   - Funding: 0.75
   - Partnership: 0.72
   - Key hire: 0.70

8. **Error Handling Tests** (4 tests)
   - 429 rate limit response
   - 500+ server errors
   - Non-ok status in response
   - Network request exceptions

## Design Decisions

### 1. Confidence Scoring Strategy
- **Funding**: 0.75 (news can be speculative, but usually accurate)
- **Partnership**: 0.72 (requires confirmation, may not materialize)
- **Key hire**: 0.70 (often announced but may not happen)

**Rationale**: News signals are less reliable than SEC filings (0.95), so confidence reflects uncertainty.

### 2. Deduplication Key
Used `(company_name.lower(), signal_type, signal_date)` instead of article URL because:
- Same news can be reported by multiple outlets
- URL-based dedup would miss duplicates
- Date-based dedup prevents same-day duplicates
- Case-insensitive matching handles "TechCorp" vs "techcorp"

### 3. Rate Limit Tracking
- Automatic daily reset at midnight (not 24h from first query)
- Warning at 90/100 (10% buffer)
- Error at 100/100 (hard stop)

**Rationale**: Aligns with NewsAPI's daily reset schedule.

### 4. Pattern Matching
- Case-insensitive regex matching
- Combined title + description + content for matching
- Regex patterns use word boundaries where needed

**Rationale**: News articles vary in capitalization and structure.

### 5. Error Handling Philosophy
- All errors logged with context (company, attempt, error details)
- Specific exception types (CompanyNotFoundError not used, RuntimeError instead)
- No silent failures (all errors raised)

## Patterns & Conventions

### Code Structure
```python
class NewsSignalDetector:
    # Class-level pattern definitions
    FUNDING_PATTERNS = [...]
    PARTNERSHIP_PATTERNS = [...]
    KEY_HIRE_PATTERNS = [...]
    
    # Public methods: detect_*_signal()
    # Private methods: _search_news(), _extract_signals(), _match_patterns()
    # Utility methods: get_rate_limit_status(), clear_seen_signals()
```

### Method Naming
- `detect_funding_signal()` - public API
- `_search_news()` - private helper
- `_extract_signals()` - private helper
- `_match_patterns()` - private helper
- `_reset_daily_counter()` - private helper
- `_check_rate_limit()` - private helper

### Return Types
- Signal detection methods return `list[dict[str, Any]]`
- Each signal dict contains: company_name, signal_type, title, description, source, url, published_at, signal_date, confidence, detected_at

## Known Limitations

1. **No Batch Query Optimization**
   - Current: 1 query per company
   - Future: Could batch 10 companies per query using OR logic
   - Impact: Uses 100 queries/day for 100 companies (1 query each)

2. **No Persistent Deduplication**
   - Current: In-memory cache (lost on restart)
   - Future: Store seen signals in PostgreSQL
   - Impact: May see duplicate signals across restarts

3. **No Conflict Resolution**
   - Current: Takes first match
   - Future: Could score multiple matches and pick best
   - Impact: May miss nuanced signals

4. **Limited Pattern Coverage**
   - Current: ~15 patterns total
   - Future: Could expand with ML-based pattern learning
   - Impact: May miss novel signal types

## Integration Points

### Dependencies
- `requests` - HTTP client for NewsAPI
- `loguru` - Logging
- `datetime` - Date/time handling
- `re` - Regex pattern matching
- `os` - Environment variable access

### Environment Variables
- `NEWSAPI_KEY` - Required for API access

### Future Integration
- PostgreSQL: Store signals in `facts` table
- Scoring Engine: Incorporate signals into Growth Score
- Orchestration: Batch company processing

## Performance Characteristics

### Time Complexity
- `detect_funding_signal()`: O(n*m) where n=articles, m=patterns
- `_match_patterns()`: O(m) where m=patterns
- `_extract_signals()`: O(n*m) where n=articles, m=patterns

### Space Complexity
- `seen_signals`: O(k) where k=unique signals detected
- Response: O(n) where n=matching articles

### API Calls
- 1 call per company per signal type
- 100 queries/day limit
- ~5-10 articles per query

## Testing Strategy

### Unit Tests (25 total)
- Mocked API responses (no real API calls)
- Isolated test cases (no dependencies)
- Edge cases covered (no matches, duplicates, errors)

### Integration Tests (Future)
- Real API calls to NewsAPI sandbox
- End-to-end: company → signals → database
- Golden dataset: 5 known companies with expected signals

### Data Quality Tests (Future)
- Signal accuracy: Compare to manual research
- Confidence calibration: Validate 0.70-0.75 range
- Deduplication: Verify no duplicates in database

## Acceptance Criteria Met

✅ `src/solstein/data/connectors/news_signal_detector.py` created  
✅ `tests/unit/data/test_news_signal_detector.py` created  
✅ Detect funding signals (Series A/B/C, raised, investment)  
✅ Detect partnership signals (collaboration, integration, partnership)  
✅ Detect key hire signals (appoints, joins, new CEO, executive)  
✅ All signals confidence-scored 0.70-0.75  
✅ Deduplication working (by company_id, signal_type, date)  
✅ 25/25 unit tests passing (exceeds 7/7 requirement)  
✅ Rate limit tracking implemented (100/day limit)  
✅ Full docstrings on all public methods  
✅ Logging on all API calls  
✅ No LSP errors  

## Next Steps (Stream D-G)

1. **Stream D**: GitHub Enhanced Analysis
   - Extend existing GitHub agent
   - Add velocity trends, language distribution, dependency health

2. **Stream E**: Fact Model + Database Schema
   - Create `facts` table in PostgreSQL
   - Add `gathering_batches` and `fact_sources` tables
   - Implement immutable fact storage

3. **Stream F**: Scoring Integration
   - Integrate financial data into Growth Score
   - Create Financial Health Score dimension
   - Update scoring engine to use new facts

4. **Stream G**: Integration Tests
   - End-to-end pipeline tests
   - Golden dataset regression (5 known companies)
   - 80%+ coverage verification

## Recommendations

1. **Before Stream E**: Add NewsAPI key to .env file
2. **Before Stream F**: Validate signal confidence scores against real data
3. **Before Stream G**: Create golden dataset with 5 known companies
4. **Future Enhancement**: Implement batch query optimization (10 companies per query)
5. **Future Enhancement**: Move deduplication to PostgreSQL for persistence

---

**Implementation Time**: ~2 hours  
**Test Time**: ~1 hour  
**Total**: ~3 hours  
**Status**: ✅ Ready for Stream D
