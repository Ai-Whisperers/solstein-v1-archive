# FD-010: Progress Reporting and Smart Caching

## Objective

Add two Advanced features to the market analysis pipeline: **progress reporting** (visual feedback during processing) and **smart caching** (skip re-extraction of unchanged source files). These are the 2nd and 3rd advanced features required for Advanced quality level (structured logging already counts as the 1st).

**Out of Scope**: Cache expiry policies (time-based TTL), distributed/shared caching, progress reporting for scripts other than the two listed above, and parallelised extraction.

## Requirements

### Progress Reporting

1. Add Rich progress bars to `extract_competitor_data.py` for the competitor-scanning loop (25+ files)
2. Add Rich progress bars to `generate_excel_report.py` for the sheet-writing loop (12 sheets)
3. Graceful fallback to simple `print()` progress if Rich is not installed
4. Progress output goes to stderr so stdout remains clean for piped JSON output

### Smart Caching

5. In `extract_competitor_data.py`, compute MD5 hash of each `financial-growth.md` file
6. Store hashes in a `.cache/market_hashes.json` sidecar file alongside the output
7. On subsequent runs, skip parsing files whose hash hasn't changed
8. Provide `--no-cache` flag to force full re-extraction
9. Cache invalidation: delete cache file or use `--no-cache`
10. Log cache hits/misses at DEBUG level

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Two distinct features touching multiple modules, with fallback logic, file I/O for cache, and hashing. Estimated 150-250 lines across 2 scripts plus requirements change.

**Criteria Met**:
- Root Cause: N/A (feature enhancement)
- Files Affected: 3 (`extract_competitor_data.py`, `generate_excel_report.py`, `requirements.txt`)
- Lines Changed: ~150-250
- Risk Level: Low-Medium (cache bugs could cause stale data, mitigated by `--no-cache`)
- Solution Pattern: Familiar (Rich progress is well-documented; MD5 caching is standard)

**Decision Principle Applied**: When in doubt, prefer Complex track

## Status

**Current**: Implementation Complete

## Acceptance Criteria

- [ ] `extract_competitor_data.py` shows progress bar when processing 25+ competitors
- [ ] `generate_excel_report.py` shows progress bar when writing 12 sheets
- [ ] Progress bars render correctly in terminal (stderr)
- [ ] Progress falls back gracefully if `rich` is not installed (no crash)
- [ ] `--no-cache` flag forces full re-extraction
- [ ] Second run with unchanged source files skips parsing for all cached files (verified via DEBUG log showing 100% cache hits)
- [ ] Cache file stored at `.cache/market_hashes.json` relative to output
- [ ] Cache hits/misses logged at DEBUG level
- [ ] `rich>=13.0` added to `requirements.txt` (optional dependency)
- [ ] All existing tests (FD-009) still pass
- [ ] Corrupted or invalid cache file is handled gracefully (treated as empty cache, no crash)
- [ ] Scripts compile clean and `--help` includes `--no-cache` option

## Implementation Strategy

### 1. Progress Reporting

```python
try:
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

def iter_with_progress(items, description="Processing"):
    if HAS_RICH:
        with Progress(SpinnerColumn(), TextColumn("{task.description}"),
                       BarColumn(), TextColumn("{task.completed}/{task.total}")) as progress:
            task = progress.add_task(description, total=len(items))
            for item in items:
                yield item
                progress.advance(task)
    else:
        for i, item in enumerate(items, 1):
            print(f"\r{description}: {i}/{len(items)}", end="", file=sys.stderr)
            yield item
        print(file=sys.stderr)
```

### 2. Smart Caching

```python
import hashlib

def compute_file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()

def load_cache(cache_path: Path) -> dict:
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except (json.JSONDecodeError, ValueError):
            logger.warning("Corrupted cache file %s, starting fresh", cache_path)
            return {}
    return {}

def save_cache(cache_path: Path, hashes: dict) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(hashes, indent=2))
```

### 3. Integration into extraction loop

The main loop in `extract_competitor_data.py` wraps the glob results with `iter_with_progress()` and checks hashes before parsing.

## Testing Strategy

1. Run `extract_competitor_data.py` twice -- second run should be faster
2. Modify one source file, re-run -- only that file re-parsed
3. Run with `--no-cache` -- all files re-parsed
4. Delete `rich` from environment -- fallback progress works
5. New unit tests in FD-009 test suite for cache helpers: `compute_file_hash`, `load_cache` (valid, corrupted, missing), `save_cache`, and cache hit/miss logic in the extraction loop

## Dependencies

- FD-001 through FD-008 complete (production code finalized)
- rich >= 13.0 (optional, graceful fallback)
