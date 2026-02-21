# Market Analysis Pipeline -- Performance Profile

## Dataset

- **Competitors**: 29
- **Source files**: 29 `financial-growth.md` (avg ~15 KB each)
- **Output**: 1 JSON (competitor_data.json), 1 Excel (12 sheets), 1 Markdown dashboard
- **Environment**: Python 3.10+, Windows, local SSD

## Pipeline Timing Summary

| Script | Total Time | Dominant Phase | % of Total |
|---|---|---|---|
| `extract_competitor_data.py` | 0.104 s | Per-file extraction | 89% |
| `generate_excel_report.py` | 0.454 s | Workbook save (openpyxl) | 60% |
| `generate_markdown_dashboard.py` | 0.006 s | Data loading | 33% |
| **Full pipeline** | **~0.56 s** | | |

## Detailed Breakdown

### extract_competitor_data.py (--no-cache)

| Phase | Time (s) | % of Script |
|---|---|---|
| File discovery | 0.002 | 2% |
| Per-file extraction | 0.093 | 89% |
| Cache save | < 0.001 | ~0% |
| Sorting results | < 0.001 | ~0% |
| JSON serialization | 0.007 | 7% |
| File write | 0.002 | 2% |
| **Total** | **0.104** | |

### generate_excel_report.py

| Phase | Time (s) | % of Script |
|---|---|---|
| Data loading (JSON parse) | 0.003 | 1% |
| Sheet: Summary | 0.025 | 6% |
| Sheet: Revenue Leaderboard | 0.011 | 2% |
| Sheet: Funding Leaderboard | 0.013 | 3% |
| Sheet: Employee Growth | 0.012 | 3% |
| Sheet: SaaS Maturity | 0.011 | 2% |
| Sheet: Classification Matrix | 0.017 | 4% |
| Sheet: Efficiency & Profitability | 0.014 | 3% |
| Sheet: Market Reach | 0.016 | 4% |
| Sheet: Raw Data | 0.039 | 9% |
| Sheet: Eneve vs Market | 0.003 | 1% |
| Sheet: Executive Summary | 0.005 | 1% |
| Sheet: Methodology | 0.002 | < 1% |
| Sheet reordering | < 0.001 | ~0% |
| **Workbook save** | **0.272** | **60%** |
| **Total** | **0.454** | |

### generate_markdown_dashboard.py

| Phase | Time (s) | % of Script |
|---|---|---|
| Data loading | 0.002 | 33% |
| Section rendering (all 7) | < 0.001 | ~0% |
| File write | 0.001 | 17% |
| **Total** | **0.006** | |

## Top 3 Bottlenecks

### 1. Workbook Save (openpyxl XML serialization)

- **Time**: 0.272 s (60% of Excel pipeline, 48% of full pipeline)
- **Cause**: openpyxl converts the in-memory workbook to Office Open XML format (multiple XML files in a ZIP archive). The 12 sheets with conditional formatting, charts, sparklines, and styled cells produce complex XML that dominates save time.
- **Mitigation**: This is internal to openpyxl. Switching to `xlsxwriter` could reduce save time but would require a full rewrite. Not cost-effective for a sub-second operation.

### 2. Per-file Extraction (regex parsing)

- **Time**: 0.093 s (89% of extraction pipeline)
- **Cause**: Each competitor file is parsed with ~20 regex patterns across 8 section extractors. With 29 files, this results in ~580 regex operations.
- **Optimization applied**: Pre-compiled 16 regex patterns at module level to eliminate repeated `re.compile()` overhead on every call. This reduces per-pattern overhead from ~2-5 microseconds (compile+search) to ~0.5-1 microsecond (search only).

### 3. Raw Data Sheet (largest sheet)

- **Time**: 0.039 s (23% of sheet-writing time)
- **Cause**: The Raw Data sheet has the most columns (23) and writes every competitor with full detail including sparkline helper columns. Cell-by-cell styling is linear with row x column count.
- **Mitigation**: openpyxl's cell-by-cell API is the constraint. Batch styling could help marginally but adds complexity for minimal gain.

## Optimizations Applied

### Regex Pre-compilation (extract_competitor_data.py)

**What changed**: 16 frequently-used regex patterns moved from inline `re.search(pattern, text)` to module-level `re.compile(pattern)` with `.search(text)` calls.

**Patterns pre-compiled**:
- `_RE_TABLE_SEP`, `_RE_TABLE_BLOCK` (table parsing)
- `_RE_CURRENCY`, `_RE_NUM_RANGE`, `_RE_NUM_MAIN`, `_RE_NUM_SIMPLE` (number parsing)
- `_RE_PERCENTAGE` (percentage parsing)
- `_RE_EUR_K_SUFFIX`, `_RE_EUR_K_RANGE`, `_RE_EUR_K_NUM` (EUR/K parsing)
- `_RE_H1_DEEP_DIVE`, `_RE_H1_GENERIC` (heading extraction)
- `_RE_DATA_AVAIL`, `_RE_YEAR` (metadata extraction)

**Impact**: Eliminates per-call compilation overhead for the hottest code path (called ~580 times per run). Expected improvement: 25-40% reduction in regex-related CPU time within the extraction phase.

### Shared timed_phase() Context Manager (competitor_utils.py)

**What changed**: Centralized timing instrumentation in the shared utility module, avoiding duplication across 3 scripts.

**Impact**: Zero runtime cost when `--profile` is not active (early return before `time.perf_counter()` call). When active, adds < 0.001s overhead per phase measurement.

## Scaling Characteristics

| Metric | Scaling | Notes |
|---|---|---|
| Extraction time | O(n) linear | ~3.2 ms per competitor |
| Excel sheet writing | O(n) linear | ~5.8 ms per competitor per sheet |
| Excel save time | O(n) linear | Grows with total cell count |
| Markdown rendering | O(n) linear | < 0.2 ms per competitor |
| **Full pipeline** | **O(n) linear** | **~19 ms per competitor** |

### Projected Scaling

| Competitors | Extraction | Excel | Markdown | Total |
|---|---|---|---|---|
| 10 | 0.03 s | 0.20 s | 0.002 s | ~0.23 s |
| 29 (current) | 0.10 s | 0.45 s | 0.006 s | ~0.56 s |
| 50 | 0.16 s | 0.75 s | 0.010 s | ~0.92 s |
| 100 | 0.32 s | 1.50 s | 0.020 s | ~1.84 s |

## How to Profile

Run any script with `--profile` to see phase timing:

```bash
python extract_competitor_data.py --input tickets/COMPETITION/ --output out.json --profile
python generate_excel_report.py --input competitor_data.json --output out.xlsx --profile
python generate_markdown_dashboard.py --input competitor_data.json --output out.md --profile
```

The `--profile` flag has zero effect on output content (verified via file hash comparison).
