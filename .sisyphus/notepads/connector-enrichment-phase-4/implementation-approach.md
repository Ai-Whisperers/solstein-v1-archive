# Phase 4: Implementation Approach Decision

## Date
February 25, 2026

## Decision
**Direct Orchestrator Implementation** (not delegation)

## Rationale

### Delegation Attempts
1. **First attempt**: Sisyphus-Junior delegation timed out after 600s
2. **Second attempt**: Sisyphus-Junior delegation timed out after 600s

### Why Delegation Failed
- The codebase is complex (1036 lines in unified_loader.py alone)
- Integration requires understanding existing enrichment flow
- Multiple interdependencies between methods
- Subagent context window insufficient for full codebase analysis

### Why Direct Implementation is Viable
- Orchestrator module already created and complete (enrichment_orchestrator.py)
- Integration points are well-defined (4 methods in unified_loader.py)
- Changes are surgical and localized
- Can verify immediately with existing test suite (10/10 tests)
- Direct implementation avoids context loss and timeout issues

## Implementation Plan

### Phase 4 Tasks (15 items)
All 15 Phase 4 items are implemented in enrichment_orchestrator.py:

1. ✅ Skip enrichment if data already complete → `should_skip_enrichment()`
2. ✅ Implement enrichment prioritization → `get_enrichment_order()`
3. ✅ Make enrichment order configurable → `EnrichmentConfig.source_order`
4. ✅ Add enrichment dependency resolution → `get_enrichment_order()` with identifier checks
5. ✅ Allow selective enrichment → `EnrichmentConfig.fields_to_enrich`
6. ✅ Add enrichment cost tracking → `EnrichmentCost` class + `track_cost()`
7. ✅ Implement enrichment result comparison → `compare_results()`
8. ✅ Check existing confidence before overwriting → `should_overwrite_field()`
9. ✅ Implement enrichment rollback → `rollback_on_error()`
10. ✅ Return new object, don't mutate input → `create_enrichment_copy()`
11. ✅ Make enrichment idempotent → Guaranteed by immutable copy + same logic
12. ✅ Implement batch enrichment → `enrich_batch()`
13. ✅ Add enrichment progress tracking → `register_progress_callback()`
14. ✅ Add enrichment cancellation support → `request_cancellation()`
15. ✅ Add enrichment dry-run mode → `EnrichmentConfig.dry_run`

### Integration Tasks (Remaining)
1. Import EnrichmentOrchestrator into unified_loader.py
2. Modify enrich_from_connectors() to use orchestrator
3. Verify all 10 tests still pass
4. Document integration in notepad

## Constraints Preserved
- ✅ Don't replace existing data, only fill NULLs
- ✅ Graceful failure: if connector fails, log and continue
- ✅ Don't call connectors for companies that already have complete data
- ✅ Don't replace working data with API data if there's a conflict
- ✅ Preserve backward compatibility
- ✅ Don't break existing tests

## Next Steps
1. Integrate orchestrator into unified_loader.py (direct edit)
2. Run pytest to verify all 10 tests pass
3. Document completion in Phase 4 notepad
4. Proceed to Phase 5 (Testing & Verification)
