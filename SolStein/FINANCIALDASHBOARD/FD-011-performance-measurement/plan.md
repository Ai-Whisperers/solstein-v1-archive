# FD-011: Performance Measurement and Optimization

## Objective

Measure, document, and optimize the performance of the market analysis pipeline. Identify bottlenecks, apply targeted optimizations, and document baseline vs optimized performance -- the final criterion for Advanced quality level.

## Requirements

1. Add `--profile` flag to all three scripts that enables timing instrumentation
2. Measure wall-clock time for each major phase:
   - `extract_competitor_data.py`: file discovery, per-file parsing, JSON serialization
   - `generate_excel_report.py`: data loading, per-sheet writing, chart creation, file save
   - `generate_markdown_dashboard.py`: data loading, per-section rendering, file write
3. Log timing breakdown at INFO level when `--profile` is active
4. Identify the top 3 bottlenecks from profiling results
5. Apply optimizations where impact is significant (>20% improvement)
6. Document performance characteristics in script docstrings:
   - Baseline time for current dataset (25 competitors)
   - Optimized time after changes
   - Scaling characteristics (e.g., "linear with competitor count")
7. Add a `PERFORMANCE.md` file in the scripts directory summarizing findings

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Profiling requires instrumentation across 3 scripts, analysis of bottlenecks, and potentially refactoring hot paths. The optimization phase is data-driven and may involve algorithm changes.

**Criteria Met**:
- Root Cause: N/A (quality enhancement)
- Files Affected: 4 (`extract_competitor_data.py`, `generate_excel_report.py`, `generate_markdown_dashboard.py`, new `PERFORMANCE.md`)
- Lines Changed: ~100-200 (instrumentation + optimizations)
- Risk Level: Low (profiling is read-only; optimizations can be toggled)
- Solution Pattern: Familiar (Python `time.perf_counter()`, standard profiling)

**Decision Principle Applied**: When in doubt, prefer Complex track

## Status

**Current**: Complete

## Acceptance Criteria

- [x] `--profile` flag added to all 3 scripts
- [x] Timing breakdown logged for each major phase when `--profile` is active
- [x] Top 3 bottlenecks identified and documented
- [x] At least 1 measurable optimization applied (>20% improvement in bottleneck area)
- [x] Performance documented in script docstrings (baseline, optimized, scaling)
- [x] `PERFORMANCE.md` created with:
  - Baseline measurements (dataset size, time per script, total pipeline time)
  - Bottleneck analysis (what's slow, why)
  - Optimizations applied (what changed, impact)
  - Scaling characteristics (how time grows with competitor count)
- [x] Scripts compile clean and `--help` shows `--profile` option
- [x] Existing tests (FD-009) still pass

## Implementation Strategy

### 1. Timing Helper

```python
import time
from contextlib import contextmanager

@contextmanager
def timed_phase(name: str, profile: bool = False):
    """Context manager that logs phase duration when profiling is enabled."""
    if profile:
        start = time.perf_counter()
    yield
    if profile:
        elapsed = time.perf_counter() - start
        log.info("PROFILE: %s took %.3f seconds", name, elapsed)
```

### 2. Instrumentation Points

**extract_competitor_data.py**:
```
[Profile] File discovery: scanning glob pattern
[Profile] Parsing competitor N/25: folder_name
[Profile] Total extraction: N competitors in X.XXs
[Profile] JSON serialization: X.XXs
```

**generate_excel_report.py**:
```
[Profile] Data loading: X.XXs
[Profile] Writing sheet "Executive Summary": X.XXs
[Profile] Writing sheet "Revenue Leaderboard": X.XXs
...
[Profile] Chart creation: X.XXs
[Profile] File save: X.XXs
[Profile] Total generation: X.XXs
```

### 3. Known Likely Bottlenecks

Based on code review, expected bottleneck ranking:
1. **Excel file save** -- openpyxl serialization with charts is typically the slowest step
2. **Chart creation** -- openpyxl chart objects are expensive to build
3. **Markdown parsing regex** -- multiple regex passes per file

### 4. Optimization Candidates

- Batch chart data references instead of cell-by-cell
- Pre-compile regex patterns (already partially done)
- Reduce redundant dictionary lookups in hot loops

## Testing Strategy

1. Run full pipeline with `--profile` and capture timing output
2. Compare baseline vs optimized times for same dataset
3. Run with 1, 10, 25 competitors to verify scaling characteristics
4. Verify `--profile` has no effect on output (same Excel/Markdown generated)

## Dependencies

- FD-009 complete (tests verify optimizations don't break output)
- FD-010 complete (caching provides baseline for "second run" timing)
