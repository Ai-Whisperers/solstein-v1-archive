# EPIC-021 Story 1: Split exporters/markdown/generator.py

## Current State
- `generator.py`: 1,402 lines (needs to be ~200 lines)
- Already has: `base.py` (153 lines), `company.py` (328 lines), `market.py` (176 lines)

## Target Structure
```
exporters/markdown/
├── __init__.py              # Public API exports
├── base.py                  # ReportFormatter, ScoreInterpreter, BaseReportGenerator (153 lines) ✓
├── company.py               # CompanyReportGenerator (328 lines) ✓
├── market.py                # MarketReportGenerator (176 lines) ✓
├── client.py                # NEW: ClientReportGenerator (~300 lines)
├── llm_enhanced.py          # NEW: LLMEnhancedReportGenerator (~200 lines)
├── helpers.py               # NEW: Helper functions (_rank_*, _score_*, _interpret_*, _avg, _median) (~150 lines)
└── generator.py             # Orchestration only (~150 lines)
```

## Migration Plan

### Phase 1: Create client.py
Move `ClientReportGenerator` class (lines 874-1265) to `client.py`
- `_generate_competitive_analysis()`
- `_rank_revenue()`, `_rank_growth()`, `_rank_score()`, `_rank_ai()`, `_rank_saas()`
- `_generate_client_strengths()`, `_generate_client_weaknesses()`

### Phase 2: Create llm_enhanced.py
Move `LLMEnhancedReportGenerator` class (lines 1268-1359) to `llm_enhanced.py`
- `generate_llm_enhanced_report()`
- `_save_llm_content()`, `_save_swot_report()`, `_save_recommendations()`

### Phase 3: Create helpers.py
Move helper functions from generator.py:
- `_sanitize_filename()` → use from base.py
- `_classify_trajectory()` → move to helpers.py
- `_interpret_growth()`, `_interpret_health()`, `_interpret_position()` → use from ScoreInterpreter
- `_calculate_3yr_growth()` → move to helpers.py
- `_generate_strengths()`, `_generate_weaknesses()` → move to helpers.py
- `_generate_strategic_assessment()` → move to helpers.py
- `_format_funding_rounds()`, `_format_funding_detail()` → move to helpers.py
- `_score_funding()`, `_score_employee_growth()`, `_score_geographic()`, `_score_ma()` → move to helpers.py
- `_interpret_funding()`, `_interpret_employee_growth()`, `_interpret_geographic()`, `_interpret_ma()`, `_interpret_saas()` → move to helpers.py
- `_avg()`, `_median()` → use from base.py
- `generate_enhanced_report()` → keep in generator.py as public API

### Phase 4: Update generator.py
Keep only:
- Imports from new modules
- `ReportGenerator` class with orchestration methods only
- `generate_enhanced_report()` convenience function
- Backward compatibility exports

## Testing Strategy
1. Import tests for each new module
2. Golden tests comparing output before/after
3. Integration tests for cross-module calls
4. All existing tests must pass
