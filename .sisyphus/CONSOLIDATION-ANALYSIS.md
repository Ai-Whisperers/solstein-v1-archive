# Code Consolidation Analysis

## Areas with Multiple Implementations

### 1. Data Loaders 🔴 HIGH PRIORITY
**Files:**
- `src/solstein/data/loaders.py` (760 lines) - CompetitorDataLoader
- `src/solstein/data/unified_loader.py` (1142 lines) - UnifiedCompanyLoader
- `src/solstein/analytics/company_loader.py` (66 lines) - Wrapper

**Issue:** 3 loaders doing similar things
**Solution:** Deprecate CompetitorDataLoader, use UnifiedCompanyLoader

### 2. Error Handling 🟡 MEDIUM PRIORITY
**Stats:** 158 error handling occurrences in data/

**Issue:** Error formatting functions scattered across files:
- format_enrichment_error()
- categorize_error()
- add_error_severity()
- build_error_context()
- track_error_with_timestamp()

**Solution:** Create single `error_utils.py` module

### 3. Async Patterns 🟡 MEDIUM PRIORITY
**Stats:** 0 async patterns in connectors

**Issue:** All connectors are synchronous but should be async for I/O
**Solution:** Convert connectors to async

### 4. Database Management ✅ KEEP SEPARATE
**Files:**
- `database.py` - Connection management
- `database_service.py` - Operations layer

**Status:** Properly separated concerns - no changes needed

## Recommendations

1. **Deprecate CompetitorDataLoader** - Add deprecation warning, redirect to UnifiedCompanyLoader
2. **Create error_utils.py** - Consolidate all error handling utilities
3. **Async connector conversion** - Convert sync connectors to async
4. **Keep database files separate** - They serve different architectural layers

## Effort Estimate

- Data loader consolidation: 2 hours
- Error handling consolidation: 3 hours
- Async conversion: 8 hours (all connectors)
- Total: ~13 hours
