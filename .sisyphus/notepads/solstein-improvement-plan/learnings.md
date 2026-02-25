# Learnings from Solstein Improvement Initiative

## Task 1: Data Quality Audit
- **Finding**: 84% NULL values across dataset (168/199 companies missing revenue)
- **Impact**: Data quality tiers: 3% COMPLETE, 13.6% PARTIAL, 83.4% INSUFFICIENT
- **Lesson**: Audit first, then design merge strategy around actual data distribution

## Task 2: Unified Company Loader (COMPLETE)

### Merge Strategy Validation
- **Markdown Priority Rule**: Works perfectly when both sources exist
- **Conflict Tracking**: Essential for transparency (users need to know data provenance)
- **Eneve Case Study**: 
  - JSON: €32.5M, 44% growth, 135 employees, Moderate AI, Tier 2
  - Markdown: €30M, 22% growth, 130 employees, Strong AI, Tier 3
  - Result: Markdown values used (as designed)
  - Conflicts: 5 fields tracked and documented

### Testing Insights
- **Mock-based testing**: Works well for loader logic (no file I/O needed)
- **Factory pattern**: Essential for creating consistent test data
- **Coverage**: 89% file coverage, 100% of merge methods covered
- **Test count**: 33 tests needed to cover all scenarios (JSON-only, Markdown-only, merged, conflicts, errors)

### Code Patterns
- **UnifiedCompany model**: Extends Company with `data_source_per_field` dict and `merge_conflicts` list
- **Merge priority**: Implemented via explicit if/else checks (not elegant but explicit and testable)
- **Timestamp tracking**: `merge_timestamp` records when merge occurred (useful for audit trails)

## Conventions Established

### Data Source Tracking
- Every field in UnifiedCompany has a source: "JSON" or "Markdown"
- Conflicts documented in `merge_conflicts` list
- Confidence levels preserved from source (Markdown confidence used when Markdown value selected)

### Merge Priority
- **Rule**: Markdown > JSON (when both exist and differ)
- **Rationale**: Markdown is manually curated, JSON is automated
- **Implementation**: Check Markdown value first, use if not None and different from JSON

### Testing Pattern
- Use factories for consistent test data
- Mock external dependencies (file I/O, extractors)
- Test both happy path and error cases
- Verify side effects (timestamps, conflict tracking)

## Decisions Made

### Why Markdown Priority?
- Markdown files are manually researched and curated
- JSON is from automated sources (may be stale or incorrect)
- Manual > Automated for conflict resolution

### Why Track Data Sources?
- Users need transparency on where data came from
- Enables confidence scoring (Markdown = higher confidence)
- Supports audit trails and data quality reporting

### Why Document Conflicts?
- Conflicts indicate data quality issues
- Helps identify companies needing manual review
- Supports future reconciliation logic

## Gotchas & Lessons

### Gotcha 1: None Value Handling
- **Issue**: Markdown might have None for a field (missing data)
- **Solution**: Check `is not None` before comparing values
- **Lesson**: Explicit None checks prevent silent failures

### Gotcha 2: Enum Comparison
- **Issue**: Comparing string "Strong" to enum AIMaturity.STRONG fails
- **Solution**: Use proper enum types in factories
- **Lesson**: Type safety matters in merge logic

### Gotcha 3: Confidence Level Preservation
- **Issue**: Merging financials loses confidence metadata
- **Solution**: Copy confidence level from source when value is selected
- **Lesson**: Metadata travels with data

## Next Steps for Task 3+

### Data Completeness Scoring (Task 3)
- Use audit results from Task 1
- Calculate 0-100 score per company
- Assign tiers: COMPLETE (>80%), PARTIAL (50-80%), MINIMAL (20-50%), INSUFFICIENT (<20%)
- **Lesson from Task 2**: Track which fields are complete vs. incomplete

### NULL Handling Strategy (Task 4)
- Use completeness scores to identify interpolation candidates
- Markdown priority means: if Markdown has value, use it (even if NULL in JSON)
- **Lesson from Task 2**: Merge logic must feed into interpolation logic

### Scoring Fixes (Tasks 5-8)
- Revenue per employee bug: use merged revenue (not JSON-only)
- Tier classification: use merged tier (not JSON-only)
- Deterministic scoring: seed RNG with company ID
- Confidence weighting: use data source confidence (Markdown > JSON)
- **Lesson from Task 2**: Unified loader must be called before scoring

## Metrics to Track

### Data Quality
- NULL percentage per field (before/after merge)
- Conflict percentage (fields where JSON ≠ Markdown)
- Completeness score distribution

### Merge Success
- Companies merged: 4/4 Dutch companies
- Conflicts detected: 5 for Eneve
- Data source distribution: % from JSON vs. Markdown

### Test Quality
- Test coverage: 89% (target: >80%)
- Test count: 33 (covers all scenarios)
- Execution time: <1 second (fast feedback)

## Recommendations for Future Tasks

1. **Always test merge logic first** before using merged data in scoring
2. **Track data provenance** at every step (not just at merge)
3. **Use factories** for consistent test data across all tests
4. **Mock external I/O** to keep tests fast and deterministic
5. **Document conflicts** for transparency and debugging
6. **Preserve metadata** (confidence, timestamps) through all transformations
