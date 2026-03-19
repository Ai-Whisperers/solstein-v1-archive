# MASTER AUDIT — Solstein — 2026-03-18

**Scope:** Full source-code audit of the ENEVE pipeline and supporting infrastructure.
**Method:** Direct source code reading with file:line citations. No assumptions — all findings are corroborated from code. Items not fully verified carry explicit `⚠️ DISCLAIMER` markers.
**Prior context:** `ENEVE_PIPELINE_CRITICAL_ANALYSIS.md` (2026-03-10) documented 10 pipeline issues. Several have since been addressed. This audit establishes current ground truth.

---

## AUDIT COVERAGE TRACKER

> Updated after each pass. All counts based on direct file reads — not grep or glob inference.

| Metric | Value |
|---|---|
| **Total `.py` files in `src/solstein/`** | 555 |
| **Files directly read** | ~107 |
| **Coverage** | ~19% |
| **Total issues found** | 50 (1 false positive closed) |
| **Open 🔴 HIGH** | 20 |
| **Open 🟡 MED** | 25 |
| **Open 🟢 LOW** | 5 |
| **Closed (false positive)** | 1 (ISSUE-43) |
| **Confirmed fixes** | 3 |
| **Last pass** | Seventh-pass — Schema mismatch root cause + adapter blast radius (2026-03-18) |
| **Last commit** | `9566e52` — pushed to `origin/master` 2026-03-18 |

### Directories with meaningful coverage
| Directory | Files read / est. total | Notes |
|---|---|---|
| `domain/` | 2 / ~5 | models.py, unified/company.py |
| `analytics/` | 7 / ~35 | scoring, completeness, workflows, activities, 3 scorers |
| `worker/` | 2 / ~5 | enrichment_tasks, base |
| `data/` | 9 / ~30 | unified/enrichment, report_release_gate, report_readiness, gap_analyzer, metric_contract, patent_client, eneve_enrichment_integration, provenance, repositories |
| `api/` | 7 / ~25 | main, routers/enrichment_batch, routers/enrichment_single, routers/async_jobs, middleware/logging, middleware/rate_limit, middleware/security |
| `adapters/` | 7 / ~20 | instrumented, enrichment/patents_unified, enrichment/funding, enrichment/website_unified, enrichment/news_unified, enrichment/funding_unified, enrichment/web_search_unified, enrichment/yahoo_finance |
| `agents/` | 7 / ~15 | web_search, companies_house, coordinator, base, resilience, github/client, github/search |
| `research/` | 4 / ~15 | pipeline, ai_research_orchestrator, gather, pipeline_stages (partial) |
| `core/` | 1 / ~5 | production_hardening |
| `infrastructure/` | 2 / ~20 | conflict_resolution (partial), cache_warming |
| `application/` | 1 / ~10 | enrichment_pipeline |
| `llm/` | 5 / ~17 | enhanced_client, structured_client, query/ollama, query/cloud, provider_strategies |

### Directories with zero coverage (priority for next passes)
| Directory | Est. files | Risk |
|---|---|---|
| `application/` | ~10 | Unknown — likely orchestration layer |
| `llm/` | ~10 | LLM client bugs could affect all AI features |
| `exporters/` | ~5 | Excel/PDF export correctness |
| `extractors/` | ~5 | Markdown extraction |
| `monitoring/` | ~10 | Profiling dashboard imported at app startup |
| `analytics/signals/` | ~10 | Signal definitions and extractors |
| `analytics/simulation/`, `valuation/` | ~5 | Financial modeling |
| `api/middleware/` | ~6 | Security, rate limiting, tenant isolation |
| `api/routers/` (remaining) | ~10 | Most API endpoints unread |
| `adapters/` (remaining) | ~17 | Discovery, aggregation, most enrichment adapters |
| `research/` (remaining) | ~11 | discovery, aggregate, signals, reconcile, evidence |
| `infrastructure/` (remaining) | ~18 | DB, cache, refresh, repositories |

---

## 1. CONFIRMED FIXES (Previously Reported, Now Verified Resolved)

### FIX-01 — Converter consolidation (EPIC-058) ✅

**File:** `scripts/run_eneve_199.py:7-8, 21`
**Evidence:** File docstring states *"EPIC-058: Uses unified convert_to_domain_company() from loaders module. No duplicate custom conversion logic."* Line 21 imports `convert_to_domain_company` from `solstein.data.loaders`. There is no inline custom converter in this file.

**File:** `src/solstein/data/converters/company_extractors.py:35-56`
**Evidence:** `extract_revenue_data()` auto-detects JSON format. Lines 35-46 handle nested `{"revenue": {"timeline": [...]}}` and lines 48-52 handle flat `{"revenue": 33219.99}`. Both formats are extracted without field loss. The ENEVE analysis's original Issue #1 (70% field loss from format mismatch) is resolved in the current code.

---

### FIX-02 — Export/gate decoupling (EPIC-060 partial) ✅

**File:** `scripts/run_eneve_199.py:28-37, 113-163`
**Evidence:** `_parse_args()` exposes `--skip-gate`, `--warn-mode`, and `--min-completeness` CLI flags. `ReportReleaseGate` is constructed with these parameters (lines 113-119). Gate evaluation result is checked (lines 120-126) but export proceeds unconditionally regardless — the `ExcelExporter.create_dashboard()` call at line 153 is NOT gated behind `gate_result.passed`. Export happens whether gate passes or fails.

**File:** `src/solstein/data/report_release_gate.py:119-295`
**Evidence:** `ReportReleaseGate.evaluate()` returns `ReportGateResult(passed=..., reasons=...)` — it does NOT raise. The old throw pattern only exists in `ensure_release_ready()` (lines 297-315).

---

### FIX-03 — Instrumented adapters DO re-raise exceptions ✅

**File:** `src/solstein/adapters/instrumented.py:81-94, 134-145`
**Evidence:** Both `InstrumentedEnrichmentSource.enrich()` and `InstrumentedDiscoverySource.discover()` catch exceptions, record them to `self._records`, then call bare `raise` (line 94, line 145). Exceptions propagate to callers unchanged. The previous analysis that called these "silent failures" was **incorrect** — these wrappers are transparent and do re-raise.

---

## 2. ACTIVE ISSUES (Source-Corroborated)

### ISSUE-01 — FinancialMetric has two conflicting model validators; allow_empty_primary bypass is broken

**Severity:** 🔴 HIGH
**File:** `src/solstein/domain/models.py:107-113, 130-134`

Two `@model_validator(mode="after")` decorators are defined on `FinancialMetric` with different method names:

```python
# Validator 1 — lines 107-113
@model_validator(mode="after")
def require_primary_metric(self) -> "FinancialMetric":
    if self.allow_empty_primary:
        return self          # ← Early exit respects the flag
    if self.revenue is None and self.employees is None:
        raise ValueError("At least revenue OR employees required")
    return self

# Validator 2 — lines 130-134
@model_validator(mode="after")
def at_least_one_primary_metric(self) -> "FinancialMetric":
    if self.revenue is None and self.employees is None:
        raise ValueError("At least one of revenue or employees must be provided")
    return self              # ← Does NOT check allow_empty_primary
```

In Pydantic v2, both validators run independently. If `allow_empty_primary=True` and both `revenue=None` and `employees=None`: the first validator exits early (correct), but the second raises unconditionally.

`Company.financials` defaults to `FinancialMetric(allow_empty_primary=True)` at `models.py:213`. If a Company is constructed with no financial data, this default FinancialMetric construction would fail on `at_least_one_primary_metric`.

**Practical consequence:** Creating a bare Company from the Celery enrichment task (`enrichment_tasks.py:58`: `UnifiedCompany(id=company_id, name=...)`) would fail if `UnifiedCompany` inherits from `Company` and doesn't supply revenue or employees.

**VERIFIED (2026-03-18):** `src/solstein/data/unified/company.py:13` confirms `class UnifiedCompany(Company):` — it inherits directly from `Company`. However, the actual crash path is blocked by two factors:

1. `Company.financials` defaults to `FinancialMetric(allow_empty_primary=True)` at `models.py:213`. The `FinancialMetric.__init__` runs both validators. `require_primary_metric` exits early due to `allow_empty_primary=True`, but `at_least_one_primary_metric` does NOT check this flag and raises `ValueError`.
2. BUT: `Company.sync_financial_fields` (model_validator at `models.py:282-316`) runs AFTER `FinancialMetric` construction. If `FinancialMetric` construction fails, this validator never runs.

**Net effect:** The conflict is real. Constructing `UnifiedCompany(id="test-co", name="Test")` with no revenue/employees WILL raise `ValueError("At least one of revenue or employees must be provided")` from the second validator. The `allow_empty_primary=True` flag is bypassed. This is a **confirmed runtime bug** on any code path that constructs a Company without financial data — including `enrich_company_async` in the Celery worker.

---

### ISSUE-02 — FinancialMetric has duplicate Pydantic field declarations

**Severity:** 🟡 MEDIUM (structural defect; no confirmed runtime impact)
**File:** `src/solstein/domain/models.py:97-103`

```python
margin_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN   # line 97
ebitda_margin: float | None = None                             # line 98
recurring_revenue_pct: float | None = None                     # line 99
funding_raised: float | None = None                            # line 100
margin_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN   # line 101 ← DUPLICATE
funding_raised: float | None = None                            # line 102 ← DUPLICATE
funding_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN  # line 103
```

In Python, the second declaration of a name in a class body overwrites the first. Pydantic sees only the final definition. The first `margin_confidence` (line 97) and first `funding_raised` (line 100) are effectively dead. This is a copy-paste error during model construction and produces an inconsistent model definition.

---

### ISSUE-03 — Company model has duplicate field declarations across two blocks

**Severity:** 🟡 MEDIUM (structural defect)
**File:** `src/solstein/domain/models.py:143-153, 195-201`

Fields `name`, `company_name`, `industry`, `description`, `website`, `headquarters`, `founded_year` are declared in the first block (lines 143-153 after the `id` field) and then re-declared verbatim in a second block (lines 195-201). Additionally, `last_updated` is declared at line 152 and again at line 231. The second declarations override the first. The class model is structurally duplicated, likely from a copy-paste merge accident.

---

### ISSUE-04 — Scoring silently degrades to base_score=0.0 on sub-scorer exceptions

**Severity:** 🔴 HIGH
**File:** `src/solstein/analytics/scoring.py:161-180`

`GrowthScorer.calculate_scores()` wraps each of the three sub-scorers in try/except:

```python
try:
    growth_score, growth_expl = self.growth_momentum_scorer.score(profile.financials)
except Exception as exc:
    logger.warning(f"[EPIC-059] Growth scoring degraded for {profile.name}: {exc}")
    growth_score = growth_base      # ← growth_base = self.config.growth.base_score or 0.0
    growth_expl = ScoringExplanation(base_score=growth_base, final_score=growth_base)
```

If any sub-scorer raises, the degraded score is `config.growth.base_score or 0.0`. A warning is logged at `WARNING` level (not `ERROR`), and the composite score calculation proceeds normally with the degraded value.

**File:** `src/solstein/cli.py:176-178`
**Evidence:**
```python
growth = scored_company.growth_score or 0.0       # None → 0.0
health = scored_company.financial_health_score or 0.0
pos = scored_company.competitive_position_score or 0.0
```

Any `None` score (which can happen if scoring returns None — though the current scorer returns `float`) is converted to `0.0` without warning. A company that failed scoring is presented as scoring `0.0/10` rather than as an error.

**VERIFIED (2026-03-18):** Direct source reading of all three scorers confirms:

- **`growth_momentum.py:75-77`** — `_score_growth_rate`: If `financials.growth_rate is None`, logs `"[EPIC-059] Skipping growth component: growth_rate is None"` at WARNING and returns score unchanged (no penalty applied). The other sub-methods (`_score_employee_efficiency`, `_score_funding_momentum`, `_score_profitability`) silently return `score` unchanged when their inputs are `None`/falsy — no log, no penalty.
- **`financial_health.py:74-84, 114-124`** — `_score_revenue_scale`: If `financials.revenue is None`, applies `_UNKNOWN_DATA_PENALTY = -2.0` and logs "No revenue data." `_score_profitability`: If `financials.profit_margin is None`, applies the same `-2.0` penalty. `_score_operating_efficiency` and `_score_funding_cushion` silently return when inputs are missing (no penalty, no log).
- **`competitive_position.py:13-92`** — Takes `profile: Company` (not `FinancialMetric`). Uses `profile.tier` (default `TIER_3`), `profile.ai_maturity` (default `NONE`), `profile.saas_maturity` (default `1`). These always have defaults, so this scorer never encounters `None` — but the defaults produce low scores.

**Net behavior with incomplete data:** A company with all-None financials gets: growth=`base_score` (typically 5.0, no adjustments), financial_health=`base_score - 4.0` (two `-2.0` penalties for missing revenue and margin), competitive=low defaults. The composite is not zero but is systematically depressed. The ENEVE analysis's claim of "silently skips the component" is **partially correct** — growth momentum silently skips, but financial health actively penalizes. The result is a score that looks like a real assessment but is actually a default-value artifact.

---

### ISSUE-05 — Celery EnrichmentTask hooks are empty stubs

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/worker/enrichment_tasks.py:23-29`

```python
class EnrichmentTask(Task):
    def on_success(self, result, task_id, args, kwargs):
        """Called on task success - update result tracking."""
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure - update result tracking."""
        pass
```

Both Celery lifecycle hooks are `pass`. Despite the docstrings indicating they should update result tracking, neither does anything. Celery calls these after task completion/failure, but no metrics, alerts, or state updates occur. This is the correct hook location for monitoring; the implementation is simply absent.

---

### ISSUE-06 — Celery DLQ records string-only error, no monitoring, traceback lost

**Severity:** 🔴 HIGH
**File:** `src/solstein/worker/enrichment_tasks.py:89-109`

On `MaxRetriesExceededError`:
```python
dead_letter_queue.record_failure(
    "enrich_company_async", self.request.id, str(exc), self.request.retries + 1
)
return {
    "status": "FAILED",
    "error": str(exc),    # ← only string, no type, no traceback
    ...
}
```

The full exception (type, traceback) is lost — only `str(exc)` is stored. The returned dict with `status: "FAILED"` is returned by the Celery task, but Celery tasks return values to the result backend; callers using `task.get()` may or may not check `result["status"]`. There is no alerting, no Prometheus counter increment, and `on_failure` (per ISSUE-05) is a no-op.

**VERIFIED (2026-03-18):** `src/solstein/worker/base.py:67-88` confirms the DLQ is an in-memory list with zero monitoring:

```python
class DeadLetterQueue:
    def __init__(self):
        self.failed_jobs = []          # ← in-memory list, lost on process restart

    def record_failure(self, task_name, task_id, error, attempt):
        logger.info(f"[RETRY-FAILED] {task_name} (task_id={task_id}): {error} after {attempt} attempts")
        self.failed_jobs.append({...})  # ← only appends to in-memory list
```

- No Prometheus counter, no Sentry capture, no database persistence.
- `logger.info` at INFO level (not ERROR/CRITICAL) — easily missed in noisy logs.
- The `failed_jobs` list is on a module-global `dead_letter_queue` instance. On Celery worker restart, this list is lost entirely.
- No external caller ever reads `dead_letter_queue.failed_jobs` — the list accumulates but is never consumed.

**This is worse than the audit originally stated.** The DLQ is not just "losing traceback" — it's a write-only in-memory list that vanishes on restart with no alerting whatsoever.

---

### ISSUE-07 — Enrichment loop catches exceptions and breaks without re-raising

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/data/unified/enrichment.py:72-85`

```python
for source in sources:
    try:
        if source == EnrichmentSource.SEC_EDGAR:
            enriched = fill_nulls_from_sec_edgar(loader, enriched)
        elif source == EnrichmentSource.COMPANIES_HOUSE:
            enriched = fill_nulls_from_companies_house(loader, enriched)
        elif source == EnrichmentSource.NEWS_SIGNALS:
            enriched = attach_news_signals(loader, enriched)
    except (ValueError, RuntimeError, TypeError, AttributeError) as e:
        logger.error(f"Enrichment from {source} failed for {enriched.name}: {e}")
        enriched = orchestrator.rollback_on_error(company, enriched, str(e))
        break   # ← Breaks the loop, does not re-raise
```

When a source fails, the error is logged at `ERROR`, the company is rolled back, and the loop breaks. The function returns a partially-enriched `UnifiedCompany` with no exception signal. Callers (`enrich_company_async`) receive what appears to be a successful enrichment result — they must explicitly inspect `enriched.enrichment_errors` to detect the failure.

**Note:** This pattern catches only `ValueError, RuntimeError, TypeError, AttributeError`. An unexpected exception type (e.g., `ConnectionError`, `TimeoutError`, `httpx.ReadTimeout`) would NOT be caught here and would propagate up normally. Whether that is the desired behavior is unclear.

---

### ISSUE-08 — ensure_release_ready() throwing path still exists alongside non-throwing evaluate()

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/data/report_release_gate.py:297-315`

```python
def ensure_release_ready(self, companies, ...) -> None:
    result = self.evaluate(...)
    if not result.passed:
        raise ValueError("Report release gate failed: " + "; ".join(...))
```

The fix (EPIC-060) decoupled `evaluate()` from raising. But `ensure_release_ready()` still exists and still raises. Any caller using `ensure_release_ready()` instead of `evaluate()` gets the old blocking behavior.

**File:** `src/solstein/cli.py:311, 366`
`assert_client_report_ready()` is called in `generate_report` and `generate_llm_report`. This function is imported from `data.report_readiness`, not `report_release_gate` directly — but it delegates to the gate.

**VERIFIED (2026-03-18):** `src/solstein/data/report_readiness.py:85-112` confirms `assert_client_report_ready()` calls `gate.evaluate()` (the non-throwing path) on each company individually, but then **raises `ValueError` itself** if the gate result fails:

```python
def assert_client_report_ready(target, competitors, min_ready_peers=3, ...):
    gate = ReportReleaseGate(min_confidence=0.6, allow_synthetic=False)
    target_result = gate.evaluate([target])
    if not target_result.passed:
        raise ValueError(f"Client report blocked: target company is not PE-ready ({reason_codes})")
    # ... also raises if insufficient ready peers
```

Additionally, `assert_report_ready()` at line 74-76 directly calls `gate.ensure_release_ready(companies)` — the throwing path.

**CLI impact confirmed:** `cli.py:17` imports both `assert_client_report_ready` and `assert_report_ready`. These are called at:
- `cli.py:311` — `generate_report` command calls `assert_client_report_ready` → raises on gate failure
- `cli.py:366` — `generate_llm_report` command calls `assert_client_report_ready` → raises on gate failure
- `cli.py:407` — `export_market_data` command calls `assert_report_ready` → calls `ensure_release_ready` → raises on gate failure

**All three CLI report commands hard-block on gate failure.** The EPIC-060 fix (decoupling evaluate from raising) is real, but the CLI entry points re-introduce the blocking behavior through these wrapper functions. The throwing path is fully active in production CLI usage.

---

### ISSUE-09 — Enrichment errors appended to company list; no caller contract enforces checking

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/data/unified/enrichment.py:129, 137, 143`

Multiple error paths append to `company.enrichment_errors`:
```python
company.enrichment_errors.append(error_msg)
```

This is a list on the `Company` domain model (`models.py:261`). The pattern is used consistently throughout enrichment — errors are recorded but silently carried in the object. No exception is raised. No Pydantic validator checks the list. Callers can construct a company, run enrichment, and proceed to scoring without ever inspecting `enrichment_errors`.

The `Company.enrichment_error_count` field at `models.py:266` exists but is not automatically incremented — it would need to be manually maintained in sync with the list.

---

## 3. PARTIAL / AMBIGUOUS STATUS

### PARTIAL-01 — FinancialMetric validation is partially enforceable

**Status:** Partially fixed, partially broken (see ISSUE-01 and ISSUE-02).

The intent to require at least `revenue` OR `employees` is correct and the validators exist. However, the duplicate validator (`at_least_one_primary_metric`) undercuts the `allow_empty_primary` bypass mechanism. The model simultaneously has validators that check this requirement twice, with inconsistent bypass logic. The net behavior is ambiguous and depends on Pydantic v2 validator execution order.

---

### PARTIAL-02 — Classification thresholds produce degenerate results with degraded scoring

**Status:** Logic confirmed; scorer behavior now fully verified (see ISSUE-04 VERIFIED section).

**File:** `src/solstein/analytics/scoring.py:99-107`
```python
def classify_company(score: float | None) -> CompanyClassification:
    if score is None:
        return CompanyClassification.SALT
    if score >= PHOENIX_SCORE_THRESHOLD:
        return CompanyClassification.PHOENIX
    if score <= LEAD_SCORE_THRESHOLD:
        return CompanyClassification.LEAD
    return CompanyClassification.SALT
```

If scoring degrades (ISSUE-04), composite scores near 0.0 would classify all companies as `LEAD`. This matches the ENEVE analysis's observation that all 5 test companies scored `1.2–3.9` and were classified `Lead`. The classification logic itself is correct — the degenerate output is a downstream symptom of ISSUE-04.

---

## 4. ARCHITECTURAL OBSERVATIONS

### OBS-01 — Company model is significantly over-specified with unclear ownership

**File:** `src/solstein/domain/models.py`
The `Company` model has 60+ fields across financial, scoring, enrichment, tech, geographic, and AI dimensions. Several fields appear to be duplicated at multiple levels (e.g., `revenue` on `Company` directly AND inside `Company.financials`, `employees` same). The `sync_financial_fields` model_validator at lines 282-316 exists specifically to synchronize these duplicates on every construction. This is a design smell — two representations of the same data synced via validator creates latent consistency issues.

### OBS-02 — Scoring breakdown stores ScoringExplanation objects, not serializable dicts

**File:** `src/solstein/analytics/scoring.py:209-213`
```python
profile.scoring_breakdown = {
    "growth": growth_expl,        # ScoringExplanation object
    "financial": fin_expl,
    "competitive": comp_expl,
}
```

`Company.scoring_breakdown` is typed as `dict[str, Any]`. Storing `ScoringExplanation` instances works for in-memory use but would fail on JSON serialization without explicit `model_dump()`. The CLI at `cli.py:186` calls `c.model_dump(mode="json")` which may handle this — but whether `ScoringExplanation` is correctly serialized depends on Pydantic's behavior with nested model instances stored in `dict[str, Any]` fields.

**PARTIALLY VERIFIED (2026-03-18):** `ScoringExplanation` is a Pydantic `BaseModel` (confirmed in `domain/models.py`). Pydantic v2's `model_dump(mode="json")` recursively serializes nested BaseModel instances stored in `dict[str, Any]` fields. So `scoring_breakdown` containing `ScoringExplanation` objects WILL serialize correctly via `model_dump(mode="json")`.

However, any code path that calls `json.dumps(company.scoring_breakdown)` directly (without going through `model_dump`) would fail with `TypeError: Object of type ScoringExplanation is not JSON serializable`. The pipeline export at `pipeline_stages.py:202,436` uses `company.model_dump(mode="json")` — this path is safe. Risk exists only if any ad-hoc serialization bypasses `model_dump`.

---

## 5. SUMMARY TABLE

| ID | Description | File | Severity | Status |
|---|---|---|---|---|
| FIX-01 | Converter consolidation (EPIC-058) | `scripts/run_eneve_199.py:21` | — | ✅ Fixed |
| FIX-02 | Export/gate decoupling (EPIC-060) | `scripts/run_eneve_199.py:113-163` | — | ✅ Fixed |
| FIX-03 | Instrumented adapters re-raise | `adapters/instrumented.py:94,145` | — | ✅ Fixed |
| ISSUE-01 | Duplicate FinancialMetric validators break `allow_empty_primary` | `domain/models.py:107-134` | 🔴 HIGH | Open |
| ISSUE-02 | FinancialMetric duplicate field declarations | `domain/models.py:97-103` | 🟡 MED | Open |
| ISSUE-03 | Company duplicate field blocks | `domain/models.py:143-153 vs 195-201` | 🟡 MED | Open |
| ISSUE-04 | Scoring degrades silently to 0.0 | `analytics/scoring.py:161-180` | 🔴 HIGH | Open |
| ISSUE-05 | Celery hooks are empty stubs | `worker/enrichment_tasks.py:23-29` | 🟡 MED | Open |
| ISSUE-06 | DLQ loses traceback, no alerting | `worker/enrichment_tasks.py:99-109` | 🔴 HIGH | Open |
| ISSUE-07 | Enrichment loop breaks without re-raising | `data/unified/enrichment.py:72-85` | 🟡 MED | Open |
| ISSUE-08 | `ensure_release_ready()` throwing path still exists | `data/report_release_gate.py:297-315` | 🟡 MED | Open |
| ISSUE-09 | Enrichment errors silently accumulate in list | `data/unified/enrichment.py:129+` | 🟡 MED | Open |

---

## 6. RESOLVED INVESTIGATION ITEMS

All five original investigation priorities have been resolved via direct source reading:

| # | Investigation | Result | Details |
|---|---|---|---|
| 1 | `UnifiedCompany` inherits `Company`? | **YES — confirmed bug** | `unified/company.py:13`: `class UnifiedCompany(Company)`. The duplicate validator conflict in ISSUE-01 is a confirmed runtime bug. |
| 2 | How do scorers handle `None` inputs? | **Mixed behavior verified** | Growth: silently skips (no penalty). Financial health: applies `-2.0` penalty per missing field. Competitive: uses defaults (never sees None). See ISSUE-04 detail. |
| 3 | DLQ has monitoring? | **NO — write-only in-memory list** | `worker/base.py:67-88`: No metrics, no persistence, no alerting. Lost on restart. Worse than originally reported. |
| 4 | CLI commands hard-block on gate? | **YES — all three** | `report_readiness.py:74-112`: Both `assert_report_ready` and `assert_client_report_ready` raise on failure. CLI lines 311, 366, 407 all call these. |
| 5 | `scoring_breakdown` serializes? | **YES via model_dump** | `ScoringExplanation` is a Pydantic BaseModel; `model_dump(mode="json")` handles it. Direct `json.dumps` would fail. |

## 7. PIPELINE CORRUPTION FLOW (Added 2026-03-18)

Cross-referencing the exception handling audit with the pipeline execution flow reveals the full corruption chain. This supplements ISSUE-04 and ISSUE-09 with pipeline-level context.

### Data Flow and Silent Failure Points

```
pipeline.py::run_market_intelligence()
  └─ pipeline_stages.py
       ├─ DiscoveryStage    →  discovery.py::discover_companies()
       │                        └─ Source failures: logged at WARNING, continues with remaining  [ACCEPTABLE]
       ├─ GatherStage       →  gather.py::enrich_company()
       │                        └─ Source failures: logged at DEBUG level (near invisible)       [P0 - CORRUPTION SOURCE]
       │                        └─ All sources fail → stub company enters pipeline silently      [P0 - CORRUPTION SOURCE]
       │                        └─ aggregate.py: fact extraction failures continue silently      [P1 - DATA LOSS]
       │                        └─ signals.py: signal extractors fail with continue              [P1 - PHANTOM SCORES]
       ├─ PerCompanySourceGate → defaults to None (disabled) — no filtering occurs              [CONFIG GAP]
       ├─ ScoringStage      →  scoring.py: sub-scorer exceptions degrade to base_score          [ISSUE-04]
       └─ ExportStage       →  hollow scores reach final output
```

### Key Finding: `gather.py:158` is the primary corruption source

Enrichment source failures are logged at `logger.debug()` — the lowest severity level. In production log configurations, these are typically filtered out entirely. A company with 0 enrichment sources gets tagged `data_quality_tier="stub"` but still proceeds through every downstream stage.

The `PerCompanySourceGate` at `pipeline_stages.py:245-290` COULD catch this, but its `min_sources` parameter defaults to `None` (disabled). No pipeline configuration currently enables it.

---

---

## 8. ADDITIONAL ISSUES (Second-Pass Deep Dive — 2026-03-18)

The following issues were found by reading files not covered in the initial audit pass. All are source-corroborated with exact file:line references.

---

### ISSUE-10 — Batch API response hardcodes all failure metrics to zero / 100%

**Severity:** 🔴 HIGH
**File:** `src/solstein/api/routers/enrichment_batch.py:50-70`

```python
results.append(
    BatchEnrichmentResult(
        company_id=enriched.id,
        status="success",          # ← always "success", regardless of enrichment outcome
        ...
    )
)
return BatchEnrichmentResponse(
    ...
    failed_count=0,               # ← HARDCODED
    results=results,
    metrics={
        ...
        "cache_hits": 0,           # ← HARDCODED
        "cache_misses": len(request_data.company_ids),  # ← HARDCODED
        "success_rate": 100.0,     # ← HARDCODED
    },
)
```

Every company in a batch response is reported as `status="success"`, `failed_count=0`, and `success_rate=100.0`, regardless of what actually happened during enrichment. If `enrich_batch()` internally failed on 10 of 20 companies (substituting originals — see ISSUE-11), the caller receives a response claiming full success. This makes the batch API response metrics completely unreliable.

---

### ISSUE-11 — `enrich_batch()` silently substitutes unenriched original on per-company failure

**Severity:** 🔴 HIGH
**File:** `src/solstein/data/unified/enrichment.py:189-191`

```python
except (ValueError, RuntimeError, TypeError, AttributeError) as e:
    logger.warning(f"Batch enrichment failed for {company.name}: {e}")
    enriched_companies.append(company)  # ← original, unenriched company appended
    loader.metrics.record_enrichment(0, False)
```

When per-company enrichment fails, the original (unenriched) company object is appended to the result list. The returned list has the same length as the input. There is no flag on the returned company to distinguish "successfully enriched" from "original substituted due to failure." Callers (including the batch API handler) receive a uniform list, cannot detect which entries failed, and — as noted in ISSUE-10 — report them all as successes.

---

### ISSUE-12 — `store_facts()` is an unimplemented stub; the DB write never happens

**Severity:** 🔴 HIGH
**File:** `src/solstein/worker/base.py:34-59`

```python
async def store_facts(db_manager, facts: list[dict], source: str) -> int:
    stored_count = 0
    async with db_manager.get_session() as session:
        for fact in facts:
            try:
                company_id = fact.get("company_id")
                if not company_id:
                    continue
                # Get existing company or create new record logic
                # For now, we just count successful facts
                stored_count += 1          # ← no actual DB write
            except Exception as e:
                logger.warning(f"Failed to store fact from {source}: {e}")
                continue
        await session.commit()             # ← commits nothing
    return stored_count
```

The function docstring states "Store fetched facts in database." The implementation counts facts and calls `session.commit()` but performs zero writes. The comment `# For now, we just count successful facts` confirms this is an incomplete implementation. Any call path that uses `store_facts()` to persist gathered intelligence to the database silently discards all data.

---

### ISSUE-13 — Gap analyzer treats `revenue=0.0` as missing, blocking pre-revenue companies

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/data/gap_analyzer.py:80-85`

```python
def _is_missing_value(field_name: str, value: float | int | None) -> bool:
    if value is None:
        return True
    if value == 0 and field_name not in ZERO_ALLOWED_FIELDS:
        return True
    return False
```

`ZERO_ALLOWED_FIELDS = {"growth_rate", "profit_margin"}` — `revenue` is NOT in this set. A company with `revenue=0.0` (e.g., a pre-revenue startup) is treated as having missing revenue data. This triggers a `GapStatus.MISSING` in the gap analysis, which causes the release gate to report `gap_analysis` failure for that company, blocking its export.

This is a semantic decision baked into the gap analyzer without a configurable flag. Any pre-revenue company will permanently fail the gap check on `revenue`.

---

### ISSUE-14 — Gap analyzer provenance check requires HTTP/HTTPS/URN; JSON-loaded companies always fail

**Severity:** 🔴 HIGH
**File:** `src/solstein/data/gap_analyzer.py:36-46`

```python
def _has_valid_provenance(company: Any, field_name: str) -> bool:
    metric_sources = getattr(company, "metric_sources", {}) or {}
    sources = metric_sources.get(field_name, [])
    if not sources:
        return False
    for source in sources:
        if isinstance(source, str) and (
            source.startswith("http://") or source.startswith("https://") or source.startswith("urn:")
        ):
            return True
    return False
```

A field has valid provenance only if its source list contains at least one `http://`, `https://`, or `urn:` URI. Companies loaded from local JSON files have no URL-based sources — their `metric_sources` either contains local identifiers (like `"competitor_json"`, `"static_catalog"`) or is empty. All four required fields (`revenue`, `employees`, `growth_rate`, `profit_margin`) fail this provenance check, producing `GapStatus.PROVENANCE_INVALID` for each.

**Consequence:** The release gate's `gap_analysis` check ALWAYS fails for any company loaded directly from JSON without prior web enrichment. This means the gate, as currently configured, categorically blocks all non-enriched data — including valid real-world data in the input files.

---

### ISSUE-15 — Completeness calculator counts enum defaults and empty lists as "filled"

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/analytics/completeness.py:98-104`

```python
def calculate_completeness_score(self, company: Company) -> float:
    non_null_count = 0
    for field in self.TRACKED_FIELDS:
        value = self._get_field_value(company, field)
        if value is not None:          # ← only checks non-None
            non_null_count += 1
```

Three of the 19 tracked fields have model-level defaults that are never `None`:
- `tier` → default `CompanyTier.TIER_3` (StrEnum)
- `threat_level` → default `ThreatLevel.MEDIUM` (StrEnum)
- `ai_maturity` → default `AIMaturity.NONE` (StrEnum)

One list-type tracked field defaults to an empty list:
- `geographic_presence` → `Field(default_factory=list)` → `[]` — and `[] is not None` is `True`

A freshly-loaded company with only `name`, `id`, and `revenue`/`employees` gets credit for 4 fields it never actually had data for. On 19 total fields this inflates completeness by ~21 percentage points (4/19 × 100). A company with only `revenue` and `employees` data would score 6/19 = 31.6% (MINIMAL) instead of the actual 2/19 = 10.5% (INSUFFICIENT), potentially escaping the gate's threshold check.

---

### ISSUE-16 — `normalize_percent()` heuristic is ambiguous for values near the [-1, 1] boundary

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/data/metric_contract.py:34-37`

```python
def normalize_percent(value: Any) -> MetricNormalizationResult:
    ...
    numeric_value = float(value)
    if -1 <= numeric_value <= 1:
        return MetricNormalizationResult(value=numeric_value * 100, assumed_unit="ratio")
    return MetricNormalizationResult(value=numeric_value, assumed_unit="percent")
```

The function assumes values in `[-1, 1]` are ratios (e.g., `0.054` meaning 5.4%) and multiplies by 100. Values outside this range are assumed to already be percentages (e.g., `5.4` meaning 5.4%). The boundary values are ambiguous:

- `0.5` → treated as ratio → `50%` (but could legitimately be `0.5%` growth)
- `1.0` → treated as ratio → `100%` (but could be `1%`)
- `1.1` → NOT treated as ratio → `1.1%` (but `0.99` → `99%`)

A growth rate stored as `0.05` (5%) is correctly identified as a ratio. But `0.9` (0.9% growth, a plausible European market figure) becomes `90%`. There is no validation or warning when the heuristic fires. The `assumed_unit` field in the result is returned but not stored anywhere in the pipeline — callers only receive the `value`.

---

### ISSUE-17 — Scorers have inconsistent None-handling: missing data is penalized in one, silently skipped in another

**Severity:** 🟡 MEDIUM
**Files:**
- `src/solstein/analytics/scorers/growth_momentum.py:75-77`
- `src/solstein/analytics/scorers/financial_health.py:74-84, 114-124`

`GrowthMomentumScorer` silently skips all components when inputs are `None`:
```python
# growth_momentum.py:75-77
if financials.growth_rate is None:
    logger.warning("[EPIC-059] Skipping growth component: growth_rate is None")
    return score   # ← score unchanged, no penalty
```
Same pattern for `employees`/`revenue` (line 150-151) and `funding_raised` (line 183-184). Missing growth data produces the same score as 0% growth data — no differentiation.

`FinancialHealthScorer` actively penalizes missing data:
```python
# financial_health.py:74-84
if financials.revenue is None:
    score += self._UNKNOWN_DATA_PENALTY   # ← -2.0
    ...
    return score
# financial_health.py:114-124
if financials.profit_margin is None:
    score += self._UNKNOWN_DATA_PENALTY   # ← -2.0
```

**Result:** A company with `growth_rate=None` and `revenue=None` would lose 2.0 points on financial health but no points on growth momentum. The composite score partially penalizes missing data and partially ignores it, depending on which scorer processes it. Classification can shift between tiers based solely on which fields are populated, even when no actual business performance data exists.

---

### ISSUE-18 — DLQ is in-memory only and logs failures at INFO severity (extends ISSUE-06)

**Severity:** 🔴 HIGH
**File:** `src/solstein/worker/base.py:67-88`

```python
class DeadLetterQueue:
    def __init__(self):
        self.failed_jobs = []          # ← in-memory list, not persisted

    def record_failure(self, task_name, task_id, error, attempt):
        logger.info(                   # ← INFO level, not WARNING or ERROR
            f"[RETRY-FAILED] {task_name} (task_id={task_id}): {error} after {attempt} attempts"
        )
        self.failed_jobs.append(...)   # ← appends to in-memory list
```

Two confirmed facts beyond what ISSUE-06 documented:
1. **No persistence**: `failed_jobs` is a plain Python list on an instance object. On worker process restart (Celery restart, container redeploy), all DLQ history is silently lost.
2. **Wrong severity**: `logger.info` at `[RETRY-FAILED]` means permanently failed jobs appear in INFO-level log output alongside routine operational messages. Any log filter that shows only WARNING+ silently discards the failure record entirely.

---

### ISSUE-19 — Three of seven CLI report commands still hard-block on gate failure (resolves ISSUE-08 disclaimer)

**Severity:** 🔴 HIGH
**File:** `src/solstein/data/report_readiness.py:74-112`

Two functions confirmed to raise unconditionally on gate failure:

```python
# Lines 74-76 — used by cli.py:407 generate_all_reports
def assert_report_ready(companies):
    gate = ReportReleaseGate(min_confidence=0.6, allow_synthetic=False)
    gate.ensure_release_ready(companies)   # ← raises ValueError if gate fails

# Lines 85-112 — used by cli.py:311,366 generate_report and generate_llm_report
def assert_client_report_ready(target, competitors, min_ready_peers=3, min_confidence=0.6):
    gate = ReportReleaseGate(...)
    target_result = gate.evaluate([target])
    if not target_result.passed:
        raise ValueError("Client report blocked: ...")   # ← raises
    if ready_peers < min_ready_peers:
        raise ValueError("Client report blocked: insufficient PE-ready peer coverage...")  # ← raises
```

CLI commands `generate_report`, `generate_llm_report`, and `generate_all_reports` all call one of these two functions before generating output. All three commands are entirely blocked if the gate fails. The EPIC-060 decoupling work only applies to `scripts/run_eneve_199.py` — the CLI report generation path was not updated.

---

### ISSUE-20 — `saas_maturity` None fallback in CompetitivePositionScorer is unreachable dead code

**Severity:** 🟢 LOW
**File:** `src/solstein/analytics/scorers/competitive_position.py:41`

```python
saas_maturity = profile.saas_maturity if profile.saas_maturity is not None else 5.0
```

`Company.saas_maturity` is typed as `int` with default value `1` at `domain/models.py:209`. Pydantic validates it as a non-nullable integer. `profile.saas_maturity` can never be `None` at runtime — the `else 5.0` branch is unreachable. If the intent was to treat missing SaaS data as "medium maturity" (5/10), the logic as written does not achieve this: companies with the default `saas_maturity=1` score `(1-1)/9 * 2.0 = 0.0`, the lowest possible SaaS adjustment.

---

### ISSUE-21 — Two `ConfidenceLevel` enums with the same name exist in different modules

**Severity:** 🟡 MEDIUM
**Files:**
- `src/solstein/domain/models.py:30-36` — `ConfidenceLevel(StrEnum)`: values `CONFIRMED, ESTIMATED, UNKNOWN, SYNTHETIC`
- `src/solstein/data/provenance.py:27-38` — `ConfidenceLevel(Enum)`: values `CERTAIN, HIGH, MEDIUM, LOW, UNCERTAIN`

These are two entirely different enumerations with the same class name. The `FinancialMetric` confidence fields (`revenue_confidence`, `growth_confidence`, etc.) use `domain.models.ConfidenceLevel`. The provenance module uses its own `ConfidenceLevel`.

The gap analyzer's `_extract_confidence()` at `gap_analyzer.py:64-76` relies on string matching (`"confirmed"`, `"estimated"`, `"unknown"`) which maps correctly to `domain.models.ConfidenceLevel` values. However:
- Any code that accidentally imports from the wrong module gets a silently different set of valid values
- IDE type checkers may not detect the collision since both are named `ConfidenceLevel`
- `data.provenance.ConfidenceLevel.CERTAIN` would serialize to the string `"CERTAIN"`, which the gap analyzer's string match would not recognize — returning `None` (unknown confidence), triggering `GapStatus.LOW_CONFIDENCE`

---

### ISSUE-22 — Deprecated Pydantic v2 `.dict()` method used in API cache path

**Severity:** 🟢 LOW
**File:** `src/solstein/api/routers/enrichment_single.py:108`

```python
enriched_data=enriched.dict(),   # ← Pydantic v2 deprecated
```

In Pydantic v2, `.dict()` is deprecated and emits `PydanticDeprecatedSince20` warnings. The correct method is `.model_dump()`. While `.dict()` still functions, it will generate deprecation noise in logs and will be removed in a future Pydantic major version. This is the only confirmed location of this pattern in the files read; a wider codebase search may reveal more occurrences.

---

## 9. UPDATED SUMMARY TABLE (Full)

| ID | Description | File | Severity | Status |
|---|---|---|---|---|
| FIX-01 | Converter consolidation (EPIC-058) | `scripts/run_eneve_199.py:21` | — | ✅ Fixed |
| FIX-02 | Export/gate decoupling in ENEVE script (EPIC-060) | `scripts/run_eneve_199.py:113-163` | — | ✅ Fixed |
| FIX-03 | Instrumented adapters re-raise exceptions | `adapters/instrumented.py:94,145` | — | ✅ Fixed |
| ISSUE-01 | Duplicate FinancialMetric validators break `allow_empty_primary`; crashes UnifiedCompany construction | `domain/models.py:107-134` | 🔴 HIGH | Open |
| ISSUE-02 | FinancialMetric duplicate field declarations | `domain/models.py:97-103` | 🟡 MED | Open |
| ISSUE-03 | Company duplicate field blocks (defined twice) | `domain/models.py:143-153 vs 195-201` | 🟡 MED | Open |
| ISSUE-04 | Scoring degrades silently to base_score on exception | `analytics/scoring.py:161-180` | 🔴 HIGH | Open |
| ISSUE-05 | Celery EnrichmentTask hooks are empty stubs | `worker/enrichment_tasks.py:23-29` | 🟡 MED | Open |
| ISSUE-06 | DLQ loses traceback, no alerting (see also ISSUE-18) | `worker/enrichment_tasks.py:99-109` | 🔴 HIGH | Open |
| ISSUE-07 | Enrichment loop breaks without re-raising | `data/unified/enrichment.py:72-85` | 🟡 MED | Open |
| ISSUE-08 | `ensure_release_ready()` throwing path still used in CLI (see also ISSUE-19) | `data/report_release_gate.py:297-315` | 🟡 MED | Open |
| ISSUE-09 | Enrichment errors silently accumulate in list | `data/unified/enrichment.py:129+` | 🟡 MED | Open |
| ISSUE-10 | Batch API hardcodes `failed_count=0`, `success_rate=100.0` | `api/routers/enrichment_batch.py:50-70` | 🔴 HIGH | Open |
| ISSUE-11 | `enrich_batch()` silently substitutes original on failure | `data/unified/enrichment.py:189-191` | 🔴 HIGH | Open |
| ISSUE-12 | `store_facts()` is an unimplemented stub; DB never written | `worker/base.py:34-59` | 🔴 HIGH | Open |
| ISSUE-13 | Gap analyzer treats `revenue=0.0` as missing; blocks pre-revenue companies | `data/gap_analyzer.py:80-85` | 🟡 MED | Open |
| ISSUE-14 | Provenance check requires HTTP/HTTPS/URN; JSON-loaded data always fails | `data/gap_analyzer.py:36-46` | 🔴 HIGH | Open |
| ISSUE-15 | Completeness calculator counts enum defaults and empty lists as filled | `analytics/completeness.py:98-104` | 🟡 MED | Open |
| ISSUE-16 | `normalize_percent()` heuristic silently misclassifies values near ±1 | `data/metric_contract.py:34-37` | 🟡 MED | Open |
| ISSUE-17 | Scorers have inconsistent None-handling: GrowthMomentum skips, FinancialHealth penalizes | `analytics/scorers/growth_momentum.py:75-77` vs `financial_health.py:74-84` | 🟡 MED | Open |
| ISSUE-18 | DLQ in-memory only (lost on restart), logs at INFO not ERROR | `worker/base.py:67-88` | 🔴 HIGH | Open |
| ISSUE-19 | 3 of 7 CLI report commands hard-block via `assert_client_report_ready` | `data/report_readiness.py:74-112` | 🔴 HIGH | Open |
| ISSUE-20 | `saas_maturity` None fallback in CompetitivePositionScorer is dead code | `analytics/scorers/competitive_position.py:41` | 🟢 LOW | Open |
| ISSUE-21 | Two `ConfidenceLevel` enums with same name in different modules | `domain/models.py:30` vs `data/provenance.py:27` | 🟡 MED | Open |
| ISSUE-22 | Deprecated Pydantic v2 `.dict()` in API cache path | `api/routers/enrichment_single.py:108` | 🟢 LOW | Open |

**Critical path summary (🔴 HIGH):** ISSUE-01, 04, 06, 10, 11, 12, 14, 18, 19 — 9 high-severity issues. Of these, ISSUE-01, 10, 11, 12, 14, 18, 19 were not in the original audit.

---

*Audit performed 2026-03-18. Second-pass deep dive completed 2026-03-18. All file:line references correspond to the state of the repository at this date.*

---

## 10. ADDITIONAL ISSUES (Third-Pass — Modified-File Coverage — 2026-03-18)

The following issues were found by reading the five files modified since the last commit (`agents/github/search.py`, `analytics/workflows.py`, `data/eneve_enrichment_integration.py`, `data/patent_client.py`, `research/ai_research_orchestrator.py`, `research/pipeline.py`) plus directly-dependent modules (`adapters/enrichment/patents_unified.py`, `agents/github/client.py`, `analytics/activities.py`). All findings are source-corroborated with exact file:line references.

---

### ISSUE-23 — `search_company_patents()` calls async sub-functions without `await`; always raises `AttributeError`

**Severity:** 🔴 HIGH
**File:** `src/solstein/data/patent_client.py:33-54, 57, 135, 189`

`_search_uspto_peds`, `_search_google_patents`, and `_search_duckduckgo` are all declared `async def`:

```python
async def _search_uspto_peds(company_name: str) -> PatentResult: ...   # line 57
async def _search_google_patents(company_name: str) -> PatentResult: ...  # line 135
async def _search_duckduckgo(company_name: str) -> PatentResult: ...    # line 189
```

`search_company_patents` is a synchronous `def` (line 33) and calls them without `await`:

```python
def search_company_patents(company_name: str) -> PatentResult:
    result = _search_uspto_peds(company_name)   # ← returns coroutine, not PatentResult
    if result.total_patents > 0:                # ← AttributeError: coroutine has no .total_patents
```

In Python, calling an `async def` function without `await` returns a coroutine object. Accessing `.total_patents` on a coroutine raises `AttributeError` on every call. The coroutine is also never awaited, generating `RuntimeWarning: coroutine '_search_uspto_peds' was never awaited`. This function is fully broken — no code path through it can succeed.

**Root cause:** The three private functions were converted from `def` to `async def` (or written as async from the start) but `search_company_patents` was not updated to either be `async` itself or use `asyncio.run()` to invoke them.

---

### ISSUE-24 — `PatentsUnifiedAdapter` is entirely non-functional due to ISSUE-23

**Severity:** 🔴 HIGH
**File:** `src/solstein/adapters/enrichment/patents_unified.py:66, 97, 134`

All three public methods of `PatentsUnifiedAdapter` call `search_company_patents()`:

```python
def discover(...):    result = search_company_patents(query)       # line 66
def enrich(...):      result = search_company_patents(company_name) # line 97
async def fetch_facts(...):  result = search_company_patents(company_name)  # line 134
```

Since `search_company_patents` always raises `AttributeError` (ISSUE-23), all three methods propagate that exception. The adapter is entirely non-functional. Any pipeline using `PatentsUnifiedAdapter` for discovery or enrichment will crash. The exception is not caught inside the adapter — callers receive the raw `AttributeError`.

**Root cause:** Transitively depends on ISSUE-23. The adapter was written (or adapted) without being aware that the underlying function is broken.

---

### ISSUE-25 — `_search_duckduckgo()` in `patent_client.py` does not check HTTP status before parsing

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/data/patent_client.py:202-203`

```python
response = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(response.text, "html.parser")   # ← no status check
```

A rate-limited 429, a redirect to a CAPTCHA page, or any non-200 response is parsed without detection. `_search_uspto_peds` (lines 76-78) and `_search_google_patents` (lines 150-151) both check `response.status_code` before parsing. This inconsistency would be moot while ISSUE-23 is active, but becomes a latent defect once the async/await fix is applied.

**Root cause:** Copy-paste omission — the status check present in the other two backends was not included.

---

### ISSUE-26 — `BatchScoreMarketWorkflow` is missing Temporal `@workflow.defn` and `@workflow.run` decorators

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/analytics/workflows.py:30-41`

```python
class BatchScoreMarketWorkflow:
    async def run(self, filters: dict[str, Any]) -> dict[str, Any]:
        company_ids = await workflow.execute_activity(fetch_market_company_ids, filters)
        ...
```

The Temporal Python SDK requires workflow classes to be decorated with `@workflow.defn` and their run method with `@workflow.run`. Neither decorator is present. When Temporal is available, `workflow` is the `temporalio.workflow` module — `workflow.execute_activity` is a module-level function valid only inside a properly decorated workflow run context. Without `@workflow.defn`, Temporal cannot register this class as a workflow type. Attempting to execute it via a Temporal worker would raise a registration error. The stub path (when Temporal is unavailable) would raise `RuntimeError("Temporal workflow is unavailable")` on any `execute_activity` call.

**Root cause:** Workflow class was written to use Temporal's module-level API functions without the required decorator scaffolding that makes Temporal aware of the class as a workflow.

---

### ISSUE-27 — `ContentExtractorAgent.http` (httpx.AsyncClient) is created in `__init__` and never closed

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/research/ai_research_orchestrator.py:371`

```python
class ContentExtractorAgent:
    def __init__(self, ...):
        self.http = httpx.AsyncClient(timeout=30.0, follow_redirects=True)  # ← never closed
```

`httpx.AsyncClient` holds a connection pool of open sockets. The class has no `close()` method, no `__del__`, and is not used as an async context manager. The client is used directly across many `_fetch_page` calls. On every instantiation of `ContentExtractorAgent` (which happens inside `AIResearchOrchestrator.__init__`), a new client is created and the connection pool is never released. Under repeated use or in long-running processes, this leaks file descriptors and connection resources.

**Root cause:** `httpx.AsyncClient` should be either closed in a `finally` block, used as an `async with` context manager per-request, or given a proper lifecycle with `await self.http.aclose()`.

---

### ISSUE-28 — `WebSearchAgent.cache` is an unbounded in-memory dict with no eviction policy

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/research/ai_research_orchestrator.py:183, 216`

```python
self.cache: dict[str, list[SearchResult]] = {}

# ... later, every search result is cached:
self.cache[cache_key] = ranked   # line 216, cache_key = f"{query}_{intent}"
```

There is no TTL, no max-size, no LRU eviction, and no invalidation mechanism. Every distinct `(query, intent)` pair adds an entry to the dict. Each `SearchResult` contains multiple string fields. A batch research run over 100+ companies with 6-8 queries each produces 600-800+ cache entries. The cache lives for the lifetime of the `WebSearchAgent` instance. For long-running processes or repeated calls to `AIResearchOrchestrator`, memory grows without bound.

**Root cause:** In-memory cache was implemented without a size or time bound. Likely intended for short-lived single-company research calls where growth is bounded; the design breaks under batch usage.

---

### ISSUE-29 — `DataValidatorAgent` validation bounds are unit-agnostic; revenue-per-employee check implicitly assumes millions

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/research/ai_research_orchestrator.py:553-616`

```python
VALIDATION_RULES = {
    "revenue": {"min": 0, "max": 1_000_000},        # unit unclear
    "funding_raised": {"min": 0, "max": 100_000},    # unit unclear
    "valuation": {"min": 0, "max": 1_000_000},       # unit unclear
}
...
# line 611:
if revenue_per_employee > 10:
    issues.append(f"Revenue per employee unusually high: {revenue_per_employee:.2f}M")
```

The LLM extractor (`_llm_extract`) receives raw web page text and returns numeric values. LLMs commonly return revenue as raw dollars (e.g., `500000000`), as thousands (`500000`), or as millions (`500`) depending on the source text. `VALIDATION_RULES` does not specify units or perform normalization before comparison. The per-employee check at line 611 labels its threshold as "M" (millions), confirming the implicit assumption. A company with $500M revenue returned by the LLM as raw dollars (`500000000`) would: (a) fail the `max: 1_000_000` bounds check flagging it as invalid, (b) produce a massively inflated per-employee ratio if not caught. There is no normalization step between LLM extraction and validation.

**Root cause:** No unit normalization contract exists between `_llm_extract` and `DataValidatorAgent.validate`. The validator assumes a fixed unit (millions) that the extractor does not guarantee.

---

### ISSUE-30 — `GitHubClient.fetch_file()` silently swallows all exceptions with no logging

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/agents/github/client.py:80-81`

```python
    except Exception:
        return None    # ← no logging, no context, all errors discarded
```

The bare `except Exception: return None` catches network timeouts, authentication failures, malformed JSON, base64 decode errors, and encoding errors identically — all become `None`. Callers cannot distinguish "file does not exist" (legitimate 404) from "API authentication failed" or "network timed out." No log message is emitted. This pattern is explicitly prohibited by the project's error-handling rules (`error-handling.md`: "NEVER silently swallow errors").

**Root cause:** Silent failure was used as a convenience fallback. The correct behavior is at minimum `logger.debug(f"[GitHubClient] fetch_file failed for {org}/{repo}/{path}: {e}")` before returning `None`.

---

### ISSUE-31 — `GitHubOrgSearcher.fetch_repos()` silently truncates at 100 regardless of `max_repos` parameter

**Severity:** 🟢 LOW
**File:** `src/solstein/agents/github/search.py:56`

```python
params = {
    "per_page": min(max_repos, 100),    # ← only sets page size, no pagination
    "sort": "stars",
    "direction": "desc",
}
```

The GitHub API returns at most 100 results per page. When `max_repos > 100`, `min(max_repos, 100)` evaluates to `100` and no further pages are fetched. The function returns at most 100 repos regardless of the `max_repos` argument. No pagination loop exists. The parameter name implies the caller can request up to `max_repos` results, which is silently unmet for any value > 100.

**Root cause:** Pagination was not implemented. The `per_page` parameter controls page size, not total results.

---

### ISSUE-32 — `EneveEnricher._merge_enrichment()` mutates the caller's input dict in-place

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/data/eneve_enrichment_integration.py:299-328`

```python
def _merge_enrichment(self, company_data: dict[str, Any], raw_sources: ...) -> dict[str, Any]:
    company_data["enrichment_source_count"] = len(raw_sources)     # line 309
    company_data["data_quality_score"] = min(0.95, ...)            # line 310
    company_data["enrichment_quality_metrics"] = quality_metrics   # line 314
    company_data["source_links"] = [...]                           # line 317
    ...
    return company_data    # ← same reference that was passed in
```

`company_data` is a dict reference from the caller's `companies` list (derived from `data.get("competitors", [])` in `enrich_eneve_data`). All four assignments directly mutate the caller's dict before returning it. If `_merge_enrichment` raises partway through (e.g., in `_calculate_quality_metrics`), the dict is left in a partially-mutated state. The `except` block at line 191 would then append this partially-modified dict as the fallback "original" company.

**Root cause:** The function was written to mutate and return the same object, which is an implicit side-effect on the caller's data structure. A defensive copy (`company_data = dict(company_data)`) at the function entry would isolate mutations.

---

### ISSUE-33 — `EneveEnricher.data_quality_score` is a fabricated metric based solely on source count

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/data/eneve_enrichment_integration.py:310`

```python
company_data["data_quality_score"] = min(0.95, 0.5 + (len(raw_sources) * 0.15))
```

With 1 source → 0.65 ("decent quality"). With 3 sources → 0.95 ("excellent"). The formula does not consider: source reliability, actual field coverage in the extracted data, confidence levels, contradictions between sources, or whether the fallback "minimal source" (`source_name="Input Data"`) was used. A company enriched only with the fallback synthetic source (ISSUE-11 pattern: the original dict re-wrapped as a `RawDataSource`) receives `data_quality_score = 0.65`, indistinguishable from a company enriched with a real external source. This metric is stored in `company_data` and likely surfaced in downstream reports or quality gates, where it will mislead consumers.

**Root cause:** The score was implemented as a count-based heuristic without a semantic quality model. The correct implementation would incorporate field coverage and source reliability.

---

## 11. UPDATED SUMMARY TABLE (Full — Third Pass)

| ID | Description | File | Severity | Status |
|---|---|---|---|---|
| FIX-01 | Converter consolidation (EPIC-058) | `scripts/run_eneve_199.py:21` | — | ✅ Fixed |
| FIX-02 | Export/gate decoupling in ENEVE script (EPIC-060) | `scripts/run_eneve_199.py:113-163` | — | ✅ Fixed |
| FIX-03 | Instrumented adapters re-raise exceptions | `adapters/instrumented.py:94,145` | — | ✅ Fixed |
| ISSUE-01 | Duplicate FinancialMetric validators break `allow_empty_primary` | `domain/models.py:107-134` | 🔴 HIGH | Open |
| ISSUE-02 | FinancialMetric duplicate field declarations | `domain/models.py:97-103` | 🟡 MED | Open |
| ISSUE-03 | Company duplicate field blocks (defined twice) | `domain/models.py:143-153 vs 195-201` | 🟡 MED | Open |
| ISSUE-04 | Scoring degrades silently to base_score on exception | `analytics/scoring.py:161-180` | 🔴 HIGH | Open |
| ISSUE-05 | Celery EnrichmentTask hooks are empty stubs | `worker/enrichment_tasks.py:23-29` | 🟡 MED | Open |
| ISSUE-06 | DLQ loses traceback, no alerting (see also ISSUE-18) | `worker/enrichment_tasks.py:99-109` | 🔴 HIGH | Open |
| ISSUE-07 | Enrichment loop breaks without re-raising | `data/unified/enrichment.py:72-85` | 🟡 MED | Open |
| ISSUE-08 | `ensure_release_ready()` throwing path still used in CLI (see also ISSUE-19) | `data/report_release_gate.py:297-315` | 🟡 MED | Open |
| ISSUE-09 | Enrichment errors silently accumulate in list | `data/unified/enrichment.py:129+` | 🟡 MED | Open |
| ISSUE-10 | Batch API hardcodes `failed_count=0`, `success_rate=100.0` | `api/routers/enrichment_batch.py:50-70` | 🔴 HIGH | Open |
| ISSUE-11 | `enrich_batch()` silently substitutes original on failure | `data/unified/enrichment.py:189-191` | 🔴 HIGH | Open |
| ISSUE-12 | `store_facts()` is an unimplemented stub; DB never written | `worker/base.py:34-59` | 🔴 HIGH | Open |
| ISSUE-13 | Gap analyzer treats `revenue=0.0` as missing; blocks pre-revenue companies | `data/gap_analyzer.py:80-85` | 🟡 MED | Open |
| ISSUE-14 | Provenance check requires HTTP/HTTPS/URN; JSON-loaded data always fails | `data/gap_analyzer.py:36-46` | 🔴 HIGH | Open |
| ISSUE-15 | Completeness calculator counts enum defaults and empty lists as filled | `analytics/completeness.py:98-104` | 🟡 MED | Open |
| ISSUE-16 | `normalize_percent()` heuristic silently misclassifies values near ±1 | `data/metric_contract.py:34-37` | 🟡 MED | Open |
| ISSUE-17 | Scorers inconsistent None-handling: GrowthMomentum skips, FinancialHealth penalizes | `analytics/scorers/growth_momentum.py:75-77` vs `financial_health.py:74-84` | 🟡 MED | Open |
| ISSUE-18 | DLQ in-memory only (lost on restart), logs at INFO not ERROR | `worker/base.py:67-88` | 🔴 HIGH | Open |
| ISSUE-19 | 3 of 7 CLI report commands hard-block via `assert_client_report_ready` | `data/report_readiness.py:74-112` | 🔴 HIGH | Open |
| ISSUE-20 | `saas_maturity` None fallback in CompetitivePositionScorer is dead code | `analytics/scorers/competitive_position.py:41` | 🟢 LOW | Open |
| ISSUE-21 | Two `ConfidenceLevel` enums with same name in different modules | `domain/models.py:30` vs `data/provenance.py:27` | 🟡 MED | Open |
| ISSUE-22 | Deprecated Pydantic v2 `.dict()` in API cache path | `api/routers/enrichment_single.py:108` | 🟢 LOW | Open |
| ISSUE-23 | `search_company_patents()` calls async sub-functions without `await`; always crashes | `data/patent_client.py:33-54` | 🔴 HIGH | Open |
| ISSUE-24 | `PatentsUnifiedAdapter` entirely non-functional (depends on ISSUE-23) | `adapters/enrichment/patents_unified.py:66,97,134` | 🔴 HIGH | Open |
| ISSUE-25 | `_search_duckduckgo()` does not check HTTP status before parsing | `data/patent_client.py:202-203` | 🟡 MED | Open |
| ISSUE-26 | `BatchScoreMarketWorkflow` missing `@workflow.defn` / `@workflow.run` decorators | `analytics/workflows.py:30-41` | 🟡 MED | Open |
| ISSUE-27 | `ContentExtractorAgent.http` (httpx.AsyncClient) never closed; leaks connections | `research/ai_research_orchestrator.py:371` | 🟡 MED | Open |
| ISSUE-28 | `WebSearchAgent.cache` is unbounded in-memory dict with no eviction | `research/ai_research_orchestrator.py:183,216` | 🟡 MED | Open |
| ISSUE-29 | `DataValidatorAgent` bounds are unit-agnostic; per-employee check assumes millions | `research/ai_research_orchestrator.py:553-616` | 🟡 MED | Open |
| ISSUE-30 | `GitHubClient.fetch_file()` silently swallows all exceptions with no logging | `agents/github/client.py:80-81` | 🟡 MED | Open |
| ISSUE-31 | `fetch_repos()` truncates at 100 regardless of `max_repos`; no pagination | `agents/github/search.py:56` | 🟢 LOW | Open |
| ISSUE-32 | `_merge_enrichment()` mutates caller's input dict in-place | `data/eneve_enrichment_integration.py:299-328` | 🟡 MED | Open |
| ISSUE-33 | `data_quality_score` is fabricated from source count; misleads downstream quality gates | `data/eneve_enrichment_integration.py:310` | 🟡 MED | Open |

**Critical path summary (🔴 HIGH):** ISSUE-01, 04, 06, 10, 11, 12, 14, 18, 19, 23, 24 — 11 high-severity issues. ISSUE-23 and ISSUE-24 are new and represent a completely broken subsystem (patent data pipeline).

---

*Audit performed 2026-03-18. Second-pass deep dive completed 2026-03-18. Third-pass modified-file coverage completed 2026-03-18. All file:line references correspond to the state of the repository at this date.*

---

## 12. ADDITIONAL ISSUES (Fourth-Pass — Agent and Infrastructure Deep Dive — 2026-03-18)

The following issues were found by reading the agents layer (`agents/web_search_agent.py`, `agents/companies_house_agent.py`, `agents/coordinator_agent.py`, `agents/base_agent.py`, `agents/resilience.py`), the API layer (`api/main.py`), and `core/production_hardening.py`. All findings are directly source-corroborated.

---

### ISSUE-34 — `WebSearchAgent._api_search_news()` contains unreachable dead code with undefined `requests` reference

**Severity:** 🟡 MEDIUM (dead code; primary path works correctly)
**File:** `src/solstein/agents/web_search_agent.py:145-167`

```python
    # Working async implementation ends here:
    return []                       # line 145 — early return from the function

    # Lines 146-167 are UNREACHABLE dead code:
    if not self.google_api_key or not self.search_engine_id:
        return []
    try:
        params = { ... }
        resp = requests.get(...)    # line 158 — `requests` is never imported
        ...
    return []
```

Lines 146-167 appear after `return []` at line 145 and are unreachable. The unreachable block references `requests.get()`, but `requests` is not imported anywhere in this file — only `httpx` is imported (line 10). The primary implementation (lines 121-145) is correct and uses `async with httpx.AsyncClient()`. This appears to be copy-paste residue from a sync→async refactor where the old synchronous implementation was not deleted.

**Root cause:** Incomplete refactoring — old synchronous code left in place after the async implementation was written above it.

---

### ISSUE-35 — `CompaniesHouseAgent` uses `requests.get()` in three methods without importing `requests`

**Severity:** 🔴 HIGH
**File:** `src/solstein/agents/companies_house_agent.py:138, 182, 224`

```python
# Line 10 — only httpx is imported:
import httpx

# Line 138 — _api_search_company():
resp = requests.get(url, headers=self.headers, params=params, timeout=10, auth=(...))

# Line 182 — _api_get_company():
resp = requests.get(url, headers=self.headers, timeout=10, auth=(...))

# Line 224 — _api_get_financials():
resp = requests.get(url, headers=self.headers, params=params, timeout=10, auth=(...))
```

`requests` is not imported in this file. Three API call methods — `_api_search_company`, `_api_get_company`, and `_api_get_financials` — all reference `requests.get()`. However, see ISSUE-36 for why the `NameError` is masked.

**Root cause:** The file was originally written with synchronous `requests` and then partially converted to async. The import was removed (or never added for `httpx`-based conversion) but the call sites were not updated.

---

### ISSUE-36 — `CompaniesHouseAgent` async methods called via `asyncio.to_thread` return coroutines instead of results

**Severity:** 🔴 HIGH
**File:** `src/solstein/agents/companies_house_agent.py:114-121, 129, 177, 215`

`_api_search_company`, `_api_get_company`, and `_api_get_financials` are all `async def`:

```python
async def _api_search_company(self, company_name: str) -> str | None: ...  # line 129
async def _api_get_company(self, company_num: str) -> dict | None: ...      # line 177
async def _api_get_financials(self, company_num: str) -> dict | None: ...   # line 215
```

But they are invoked via `asyncio.to_thread`:

```python
company_num = await call_with_retry(
    asyncio.to_thread,             # runs func in thread pool
    self._api_search_company,      # ← async def
    company_name,
    ...
)
```

`asyncio.to_thread` runs the given callable in a `ThreadPoolExecutor`. When the thread calls `self._api_search_company(company_name)`, it calls an `async def` function — which returns a coroutine object without executing its body. The thread returns the coroutine. `asyncio.to_thread` then delivers that coroutine object as its result to the awaiting caller.

**Consequence:** `company_num` receives a coroutine object, not `None` or a string. Coroutines are truthy, so `if company_num:` evaluates `True` — the agent believes it found a company when it has not. The `NameError` from ISSUE-35 is never raised because the body of `_api_search_company` is never executed. The Companies House agent always silently "succeeds" with garbage data while believing it found the company.

**Root cause:** `asyncio.to_thread` is designed for synchronous (blocking) functions. These methods should either be `def` (synchronous, using `requests`) or awaited directly as `async def` (without `asyncio.to_thread`).

---

### ISSUE-37 — `CoordinatorAgent.__init__()` passes only one argument to `BaseDataGatheringAgent.__init__()`, which requires two

**Severity:** 🔴 HIGH
**File:** `src/solstein/agents/coordinator_agent.py:58`

```python
class CoordinatorAgent(BaseDataGatheringAgent):
    def __init__(self, ...):
        super().__init__("Coordinator")   # ← only agent_name, missing source_type
```

`BaseDataGatheringAgent.__init__` signature (base_agent.py:36):

```python
def __init__(self, agent_name: str, source_type: DataSourceType):
```

`source_type` has no default value. Every instantiation of `CoordinatorAgent` raises:
```
TypeError: BaseDataGatheringAgent.__init__() missing 1 required positional argument: 'source_type'
```

**Root cause:** `CoordinatorAgent` was written without passing a `DataSourceType` enum value to the parent. Since `CoordinatorAgent` orchestrates multiple source types, no single `DataSourceType` is obviously correct — but the omission is a crash.

---

### ISSUE-38 — `CoordinatorAgent.analyze_company()` constructs `AgentTaskResult` with wrong fields, causing `ValidationError`

**Severity:** 🔴 HIGH
**File:** `src/solstein/agents/coordinator_agent.py:135-148`

```python
result = AgentTaskResult(
    agent_name="Coordinator",
    company_name=company_name,    # ← NOT a field on AgentTaskResult
    raw_sources=...,
    extracted_facts=...,
    signals=...,                  # ← NOT a field on AgentTaskResult
    errors=...,                   # ← NOT a field on AgentTaskResult
)
# ...
f"{len(result.signals)} signals"  # line 148 ← AttributeError: AgentTaskResult has no 'signals'
```

`AgentTaskResult` (base_agent.py:16-26) requires `source_type: DataSourceType` (no default) and `success: bool` (no default). Neither is passed here. Pydantic v2 raises `ValidationError` for missing required fields. Even if the extra fields were tolerated, `result.signals` at line 148 would raise `AttributeError` since `signals` is not a field.

**Root cause:** The `AgentTaskResult` model was either changed after this code was written, or this code was written without checking the model definition. The two required fields (`source_type`, `success`) were not supplied, and three non-existent fields were passed.

---

### ISSUE-39 — `ResponseCache` uses deprecated `datetime.utcnow()`, will break on Python 3.13

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/core/production_hardening.py:111, 125`

```python
# Line 111 — in get():
if datetime.utcnow() > expiry:

# Line 125 — in set():
expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
```

`datetime.utcnow()` was deprecated in Python 3.12 and removed in Python 3.13. The correct replacement is `datetime.now(timezone.utc)`. As written, both `get()` and `set()` also store a naive datetime (no timezone info). Comparing naive and timezone-aware datetimes raises `TypeError`; the current code stores and compares two naive datetimes consistently, so it works — but it is timezone-unaware and will fail on Python 3.13.

**Root cause:** Deprecated API not updated during Python version migration.

---

## 13. FINAL SUMMARY TABLE (All Issues)

| ID | Description | File | Severity | Status |
|---|---|---|---|---|
| FIX-01 | Converter consolidation (EPIC-058) | `scripts/run_eneve_199.py:21` | — | ✅ Fixed |
| FIX-02 | Export/gate decoupling in ENEVE script (EPIC-060) | `scripts/run_eneve_199.py:113-163` | — | ✅ Fixed |
| FIX-03 | Instrumented adapters re-raise exceptions | `adapters/instrumented.py:94,145` | — | ✅ Fixed |
| ISSUE-01 | Duplicate FinancialMetric validators break `allow_empty_primary` | `domain/models.py:107-134` | 🔴 HIGH | Open |
| ISSUE-02 | FinancialMetric duplicate field declarations | `domain/models.py:97-103` | 🟡 MED | Open |
| ISSUE-03 | Company duplicate field blocks (defined twice) | `domain/models.py:143-153 vs 195-201` | 🟡 MED | Open |
| ISSUE-04 | Scoring degrades silently to base_score on exception | `analytics/scoring.py:161-180` | 🔴 HIGH | Open |
| ISSUE-05 | Celery EnrichmentTask hooks are empty stubs | `worker/enrichment_tasks.py:23-29` | 🟡 MED | Open |
| ISSUE-06 | DLQ loses traceback, no alerting (see also ISSUE-18) | `worker/enrichment_tasks.py:99-109` | 🔴 HIGH | Open |
| ISSUE-07 | Enrichment loop breaks without re-raising | `data/unified/enrichment.py:72-85` | 🟡 MED | Open |
| ISSUE-08 | `ensure_release_ready()` throwing path still used in CLI (see also ISSUE-19) | `data/report_release_gate.py:297-315` | 🟡 MED | Open |
| ISSUE-09 | Enrichment errors silently accumulate in list | `data/unified/enrichment.py:129+` | 🟡 MED | Open |
| ISSUE-10 | Batch API hardcodes `failed_count=0`, `success_rate=100.0` | `api/routers/enrichment_batch.py:50-70` | 🔴 HIGH | Open |
| ISSUE-11 | `enrich_batch()` silently substitutes original on failure | `data/unified/enrichment.py:189-191` | 🔴 HIGH | Open |
| ISSUE-12 | `store_facts()` is an unimplemented stub; DB never written | `worker/base.py:34-59` | 🔴 HIGH | Open |
| ISSUE-13 | Gap analyzer treats `revenue=0.0` as missing; blocks pre-revenue companies | `data/gap_analyzer.py:80-85` | 🟡 MED | Open |
| ISSUE-14 | Provenance check requires HTTP/HTTPS/URN; JSON-loaded data always fails | `data/gap_analyzer.py:36-46` | 🔴 HIGH | Open |
| ISSUE-15 | Completeness calculator counts enum defaults and empty lists as filled | `analytics/completeness.py:98-104` | 🟡 MED | Open |
| ISSUE-16 | `normalize_percent()` heuristic silently misclassifies values near ±1 | `data/metric_contract.py:34-37` | 🟡 MED | Open |
| ISSUE-17 | Scorers inconsistent None-handling: GrowthMomentum skips, FinancialHealth penalizes | `analytics/scorers/growth_momentum.py:75-77` vs `financial_health.py:74-84` | 🟡 MED | Open |
| ISSUE-18 | DLQ in-memory only (lost on restart), logs at INFO not ERROR | `worker/base.py:67-88` | 🔴 HIGH | Open |
| ISSUE-19 | 3 of 7 CLI report commands hard-block via `assert_client_report_ready` | `data/report_readiness.py:74-112` | 🔴 HIGH | Open |
| ISSUE-20 | `saas_maturity` None fallback in CompetitivePositionScorer is dead code | `analytics/scorers/competitive_position.py:41` | 🟢 LOW | Open |
| ISSUE-21 | Two `ConfidenceLevel` enums with same name in different modules | `domain/models.py:30` vs `data/provenance.py:27` | 🟡 MED | Open |
| ISSUE-22 | Deprecated Pydantic v2 `.dict()` in API cache path | `api/routers/enrichment_single.py:108` | 🟢 LOW | Open |
| ISSUE-23 | `search_company_patents()` calls async sub-functions without `await`; always crashes | `data/patent_client.py:33-54` | 🔴 HIGH | Open |
| ISSUE-24 | `PatentsUnifiedAdapter` entirely non-functional (depends on ISSUE-23) | `adapters/enrichment/patents_unified.py:66,97,134` | 🔴 HIGH | Open |
| ISSUE-25 | `_search_duckduckgo()` does not check HTTP status before parsing | `data/patent_client.py:202-203` | 🟡 MED | Open |
| ISSUE-26 | `BatchScoreMarketWorkflow` missing `@workflow.defn` / `@workflow.run` decorators | `analytics/workflows.py:30-41` | 🟡 MED | Open |
| ISSUE-27 | `ContentExtractorAgent.http` (httpx.AsyncClient) never closed; leaks connections | `research/ai_research_orchestrator.py:371` | 🟡 MED | Open |
| ISSUE-28 | `WebSearchAgent.cache` is unbounded in-memory dict with no eviction | `research/ai_research_orchestrator.py:183,216` | 🟡 MED | Open |
| ISSUE-29 | `DataValidatorAgent` bounds are unit-agnostic; per-employee check assumes millions | `research/ai_research_orchestrator.py:553-616` | 🟡 MED | Open |
| ISSUE-30 | `GitHubClient.fetch_file()` silently swallows all exceptions with no logging | `agents/github/client.py:80-81` | 🟡 MED | Open |
| ISSUE-31 | `fetch_repos()` truncates at 100 regardless of `max_repos`; no pagination | `agents/github/search.py:56` | 🟢 LOW | Open |
| ISSUE-32 | `_merge_enrichment()` mutates caller's input dict in-place | `data/eneve_enrichment_integration.py:299-328` | 🟡 MED | Open |
| ISSUE-33 | `data_quality_score` is fabricated from source count; misleads downstream quality gates | `data/eneve_enrichment_integration.py:310` | 🟡 MED | Open |
| ISSUE-34 | `WebSearchAgent._api_search_news()` contains unreachable dead code with undefined `requests` | `agents/web_search_agent.py:145-167` | 🟡 MED | Open |
| ISSUE-35 | `CompaniesHouseAgent` uses `requests.get()` in 3 methods without importing `requests` | `agents/companies_house_agent.py:138,182,224` | 🔴 HIGH | Open |
| ISSUE-36 | `CompaniesHouseAgent` async methods called via `asyncio.to_thread` return coroutines instead of results | `agents/companies_house_agent.py:114-121` | 🔴 HIGH | Open |
| ISSUE-37 | `CoordinatorAgent.__init__()` missing required `source_type` arg to parent; always crashes at instantiation | `agents/coordinator_agent.py:58` | 🔴 HIGH | Open |
| ISSUE-38 | `CoordinatorAgent.analyze_company()` constructs `AgentTaskResult` with missing required fields and non-existent fields | `agents/coordinator_agent.py:135-148` | 🔴 HIGH | Open |
| ISSUE-39 | `ResponseCache` uses deprecated `datetime.utcnow()`; breaks on Python 3.13 | `core/production_hardening.py:111,125` | 🟡 MED | Open |

**Final critical path (🔴 HIGH):** ISSUE-01, 04, 06, 10, 11, 12, 14, 18, 19, 23, 24, 35, 36, 37, 38 — **15 high-severity open issues.**

New confirmed broken subsystems: Companies House agent (ISSUE-35, 36), Coordinator agent (ISSUE-37, 38), Patent pipeline (ISSUE-23, 24).

---

*Audit performed 2026-03-18. All passes completed 2026-03-18. All file:line references correspond to the state of the repository at this date.*

---

## 14. ADDITIONAL ISSUES (Fifth-Pass — LLM Layer, API Middleware, Application, Async Jobs — 2026-03-18)

Files read this pass: `api/middleware/logging.py`, `api/middleware/rate_limit.py`, `api/middleware/security.py`, `api/routers/async_jobs.py`, `application/enrichment_pipeline.py`, `llm/enhanced_client.py`, `llm/structured_client.py`, `llm/query/ollama.py`, `llm/provider_strategies.py`. All findings are source-corroborated with exact file:line references.

---

### ISSUE-40 — `ErrorLoggingMiddleware` consumes `response.body_iterator` without restoring it; all 4xx/5xx API error responses deliver empty bodies to clients

**Severity:** 🔴 HIGH
**File:** `src/solstein/api/middleware/logging.py:168-176, 185-186`

The `dispatch` method calls `_log_error_response` for all responses with `status_code >= 400`, then returns the response to the client:

```python
# lines 168-176
async def dispatch(self, request: Request, call_next: Callable) -> Response:
    response = await call_next(request)
    if response.status_code >= 400:
        await self._log_error_response(request, response)
    return response   # ← same response object returned, body already exhausted

# lines 185-186 — inside _log_error_response:
body = b""
async for chunk in response.body_iterator:   # ← consumes the async generator
    body += chunk
```

In Starlette, `response.body_iterator` is a single-use async generator. Once iterated, it is exhausted and cannot be re-iterated. The method reads the full body for logging purposes but never replaces `response.body_iterator` with the read bytes. The `dispatch` method then returns the response with an exhausted iterator. The ASGI transport layer iterates `body_iterator` to build the HTTP response body — finding it exhausted, it sends a zero-byte body.

**Consequence:** Every API response with `status_code >= 400` (all errors, all validation failures, all 404s) delivers an empty HTTP body to clients. API consumers receive status 4xx/5xx with no JSON error payload — making the error completely opaque to callers. This affects every path through the API that errors.

**Root cause:** The correct pattern is to reassign `response.body_iterator` after reading:
```python
async for chunk in response.body_iterator:
    body += chunk
response.body_iterator = iter([body])  # restore for downstream
```
This step is missing.

---

### ISSUE-41 — `get_rate_limit_for_path()` operator precedence bug neutralizes trailing-slash guard; exact-path routes match as prefixes

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/api/middleware/rate_limit.py:50`

```python
for route_pattern, limit in ROUTE_LIMITS.items():
    if route_pattern.endswith("/") and path.startswith(route_pattern) or path.startswith(route_pattern):
        return limit
```

Python's operator precedence evaluates `and` before `or`. This expression parses as:
```
(route_pattern.endswith("/") and path.startswith(route_pattern)) or path.startswith(route_pattern)
```

Since the right side of `or` is `path.startswith(route_pattern)` — the same as the second operand of `and` — the entire condition reduces to just `path.startswith(route_pattern)`. The `endswith("/")` guard is completely neutralized.

**Practical consequence:** `ROUTE_LIMITS` contains non-trailing-slash patterns like `"/market/analysis"` and `"/api/v1/companies/analyze"`. These are intended as exact-match patterns (already caught by the `if path in ROUTE_LIMITS` exact check at line 45). However, once the exact check fails (i.e., a sub-path like `/api/v1/companies/analyze/bulk`), the prefix loop fires. The `endswith("/")` guard was meant to prevent this — it should have ensured only trailing-slash patterns (like `/api/v1/research/`) match sub-paths. With the bug, non-trailing-slash exact patterns also match any prefix, applying their 10 req/min limit to unexpected paths.

The intended logic was: `if route_pattern.endswith("/") and path.startswith(route_pattern):`.

---

### ISSUE-42 — `AuthenticationMiddleware` bypasses auth for any URL starting with `/companies` or `/enrichment`; no path separator check

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/api/middleware/security.py:61-62`

```python
if request.url.path.startswith(("/companies", "/enrichment")):
    return await call_next(request)
```

`startswith` matches any URL that begins with these strings. A path like `/enrichment_admin`, `/enrichment-bypass`, `/companies-backdoor`, or `/enrichment/../../admin` all bypass authentication. FastAPI would 404 for unknown routes — but if any route is registered with such a pattern (e.g., `/enrichment_jobs`), it silently skips auth. The check also fails to validate that the match is a complete path segment (i.e., that the character after `/enrichment` is `/` or end-of-string). The correct check is:

```python
if request.url.path.startswith(("/companies/", "/enrichment/")) or request.url.path in ("/companies", "/enrichment"):
```

**Root cause:** `startswith` used without a trailing-slash anchor for prefix matching.

---

### ISSUE-43 — `EnrichmentPipeline.enrich()` uses `asyncio.gather(..., return_exceptions=False)`, contradicting documented isolation guarantee; one failing adapter kills the entire enrichment

**Severity:** 🔴 HIGH
**File:** `src/solstein/application/enrichment_pipeline.py:1-19, 99`

The module docstring explicitly states: *"Errors in individual adapters are isolated so one failing source never blocks the rest."*

The implementation at line 99:
```python
raw_sources: list[RawDataSource | None] = await asyncio.gather(*tasks, return_exceptions=False)
```

`return_exceptions=False` (the default) causes `asyncio.gather` to immediately propagate the first exception raised by any task and cancel all remaining tasks. If any single adapter raises — whether from a network timeout, API key failure, or invalid response — the entire `enrich()` call raises that exception. No partial results are returned. The docstring promise of isolation is completely false.

**Consequence:** Under realistic conditions (e.g., one external data source is temporarily down), enrichment for that company fails entirely rather than proceeding with the remaining working sources. This turns transient single-source failures into total enrichment failures.

**Fix:** Change to `return_exceptions=True` and filter `isinstance(result, Exception)` from the results list:
```python
raw_sources = await asyncio.gather(*tasks, return_exceptions=True)
successful = [r for r in raw_sources if not isinstance(r, Exception) and r is not None]
```

---

### ISSUE-44 — `StructuredLLMClient.extract()` passes `temperature` kwarg to `EnhancedLLMClient.generate()` which has no such parameter; `TypeError` on every call

**Severity:** 🔴 HIGH
**File:** `src/solstein/llm/structured_client.py:110-113` and `src/solstein/llm/enhanced_client.py:97-103`

`StructuredLLMClient.extract()` signature accepts `temperature: float = 0.1` and forwards it:

```python
# structured_client.py:110-113
raw = await self._inner.generate(
    prompt=prompt,
    system_prompt=system_prompt,
    temperature=temperature,   # ← forwarded as kwarg
)
```

`EnhancedLLMClient.generate()` signature:
```python
# enhanced_client.py:97-103
async def generate(
    self,
    prompt: str,
    system_prompt: str | None = None,
    max_retries: int = 2,
    preferred_provider: str | None = None,
) -> str | None:
```

There is no `temperature` parameter. Python raises `TypeError: generate() got an unexpected keyword argument 'temperature'` on every call to `StructuredLLMClient.extract()`. The `StructuredLLMClient` is entirely non-functional. Any code path that uses structured LLM extraction (e.g., the `DataValidatorAgent` noted in ISSUE-29, any LLM-based company data extraction) will crash at the first call.

**Root cause:** The `temperature` parameter was added to `StructuredLLMClient.extract()` but the corresponding forwarding was not added to `EnhancedLLMClient.generate()`.

---

### ISSUE-45 — `EnhancedLLMClient.generate()` returns `None` silently after all providers fail; callers receive no exception signal

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/llm/enhanced_client.py:114-115`

```python
logger.error(f"All LLM providers failed after {len(attempts)} attempts")
return None
```

When every provider in `PROVIDER_PRIORITY` fails their retries, `generate()` logs at ERROR and returns `None`. No exception is raised. Callers that do not explicitly check for `None` will pass it downstream where it causes `AttributeError` or `TypeError` on the first string operation. The `StructuredLLMClient` at `structured_client.py:115` calls `self._parse_and_validate(raw, schema)` — with `raw = None` (from a `None` return), `_parse_and_validate` would immediately fail on any string operation on `None`.

**Note:** ISSUE-44 would raise `TypeError` before this line is reached in practice. But once ISSUE-44 is fixed (by adding `temperature` to `generate()`), ISSUE-45 becomes the next failure mode.

**Root cause:** `generate()` treats total-failure as a graceful `None` return rather than raising an exception. The module defines `LLMGenerationError` (line 26) but never uses it.

---

### ISSUE-46 — `OllamaQuerier.query()` uses bare `except Exception: raise` without any diagnostic logging

**Severity:** 🟢 LOW
**File:** `src/solstein/llm/query/ollama.py:67-68`

```python
except TimeoutError as e:
    raise Exception("Ollama request timeout") from e
except Exception:
    raise           # ← re-raises without any logging or context
```

The bare `except Exception: raise` catches all non-`TimeoutError` exceptions (including `aiohttp.ClientError`, `ConnectionRefusedError`, `json.JSONDecodeError`) and re-raises them without logging. The caller receives the raw exception with no enriched context about which URL was requested, what payload was sent, or what status code was returned. This violates the project's error-handling rules (`error-handling.md`: "Always include context"). Callers can distinguish the failure from `TimeoutError` but cannot diagnose it without a log line.

**Additionally:** `EnhancedLLMClient._query_provider()` at line 166-168 contains:
```python
if provider == "ollama":
    raise Exception("Ollama is not available (removed from VPS)")
```
Since `"ollama"` is absent from `PROVIDER_PRIORITY` (line 39-53), this check is unreachable dead code. The `OllamaQuerier` at `enhanced_client.py:62` is also initialized but never used. This represents zombie code from an incomplete removal of the Ollama provider.

---

### ISSUE-47 — `async_jobs.py` calls `celery_app.send_task()` synchronously in async handlers; blocks the event loop under broker latency

**Severity:** 🟡 MEDIUM
**File:** `src/solstein/api/routers/async_jobs.py:130, 173`

```python
# Line 130 — enrich_company_async handler:
task = celery_app.send_task(
    "solstein.worker_tasks.enrich_company_async",
    args=[...],
    task_id=str(uuid.uuid4()),
)

# Line 173 — enrich_batch_async handler:
task = celery_app.send_task(
    "solstein.worker_tasks.enrich_companies_batch_async",
    args=[...],
    task_id=str(uuid.uuid4()),
)
```

Both handlers are `async def` FastAPI route functions. `celery_app.send_task()` is a synchronous blocking call — it establishes a connection to the Celery broker (Redis or RabbitMQ) and writes the task message over the network. Under normal conditions this is fast (~1-5ms), but under broker latency, connection pool exhaustion, or TLS negotiation, this call can block for hundreds of milliseconds to seconds. In an `async def` handler, this blocks the event loop thread, stalling all other concurrent requests for the duration of the call.

**Correct pattern:** Wrap in `asyncio.to_thread`:
```python
task = await asyncio.to_thread(
    celery_app.send_task,
    "solstein.worker_tasks.enrich_company_async",
    args=[...],
    task_id=str(uuid.uuid4()),
)
```

**Root cause:** Synchronous Celery API used directly in async context without thread offloading.

---

## 15. FINAL SUMMARY TABLE (All Issues — Fifth Pass)

| ID | Description | File | Severity | Status |
|---|---|---|---|---|
| FIX-01 | Converter consolidation (EPIC-058) | `scripts/run_eneve_199.py:21` | — | ✅ Fixed |
| FIX-02 | Export/gate decoupling in ENEVE script (EPIC-060) | `scripts/run_eneve_199.py:113-163` | — | ✅ Fixed |
| FIX-03 | Instrumented adapters re-raise exceptions | `adapters/instrumented.py:94,145` | — | ✅ Fixed |
| ISSUE-01 | Duplicate FinancialMetric validators break `allow_empty_primary` | `domain/models.py:107-134` | 🔴 HIGH | Open |
| ISSUE-02 | FinancialMetric duplicate field declarations | `domain/models.py:97-103` | 🟡 MED | Open |
| ISSUE-03 | Company duplicate field blocks (defined twice) | `domain/models.py:143-153 vs 195-201` | 🟡 MED | Open |
| ISSUE-04 | Scoring degrades silently to base_score on exception | `analytics/scoring.py:161-180` | 🔴 HIGH | Open |
| ISSUE-05 | Celery EnrichmentTask hooks are empty stubs | `worker/enrichment_tasks.py:23-29` | 🟡 MED | Open |
| ISSUE-06 | DLQ loses traceback, no alerting (see also ISSUE-18) | `worker/enrichment_tasks.py:99-109` | 🔴 HIGH | Open |
| ISSUE-07 | Enrichment loop breaks without re-raising | `data/unified/enrichment.py:72-85` | 🟡 MED | Open |
| ISSUE-08 | `ensure_release_ready()` throwing path still used in CLI (see also ISSUE-19) | `data/report_release_gate.py:297-315` | 🟡 MED | Open |
| ISSUE-09 | Enrichment errors silently accumulate in list | `data/unified/enrichment.py:129+` | 🟡 MED | Open |
| ISSUE-10 | Batch API hardcodes `failed_count=0`, `success_rate=100.0` | `api/routers/enrichment_batch.py:50-70` | 🔴 HIGH | Open |
| ISSUE-11 | `enrich_batch()` silently substitutes original on failure | `data/unified/enrichment.py:189-191` | 🔴 HIGH | Open |
| ISSUE-12 | `store_facts()` is an unimplemented stub; DB never written | `worker/base.py:34-59` | 🔴 HIGH | Open |
| ISSUE-13 | Gap analyzer treats `revenue=0.0` as missing; blocks pre-revenue companies | `data/gap_analyzer.py:80-85` | 🟡 MED | Open |
| ISSUE-14 | Provenance check requires HTTP/HTTPS/URN; JSON-loaded data always fails | `data/gap_analyzer.py:36-46` | 🔴 HIGH | Open |
| ISSUE-15 | Completeness calculator counts enum defaults and empty lists as filled | `analytics/completeness.py:98-104` | 🟡 MED | Open |
| ISSUE-16 | `normalize_percent()` heuristic silently misclassifies values near ±1 | `data/metric_contract.py:34-37` | 🟡 MED | Open |
| ISSUE-17 | Scorers inconsistent None-handling: GrowthMomentum skips, FinancialHealth penalizes | `analytics/scorers/growth_momentum.py:75-77` vs `financial_health.py:74-84` | 🟡 MED | Open |
| ISSUE-18 | DLQ in-memory only (lost on restart), logs at INFO not ERROR | `worker/base.py:67-88` | 🔴 HIGH | Open |
| ISSUE-19 | 3 of 7 CLI report commands hard-block via `assert_client_report_ready` | `data/report_readiness.py:74-112` | 🔴 HIGH | Open |
| ISSUE-20 | `saas_maturity` None fallback in CompetitivePositionScorer is dead code | `analytics/scorers/competitive_position.py:41` | 🟢 LOW | Open |
| ISSUE-21 | Two `ConfidenceLevel` enums with same name in different modules | `domain/models.py:30` vs `data/provenance.py:27` | 🟡 MED | Open |
| ISSUE-22 | Deprecated Pydantic v2 `.dict()` in API cache path | `api/routers/enrichment_single.py:108` | 🟢 LOW | Open |
| ISSUE-23 | `search_company_patents()` calls async sub-functions without `await`; always crashes | `data/patent_client.py:33-54` | 🔴 HIGH | Open |
| ISSUE-24 | `PatentsUnifiedAdapter` entirely non-functional (depends on ISSUE-23) | `adapters/enrichment/patents_unified.py:66,97,134` | 🔴 HIGH | Open |
| ISSUE-25 | `_search_duckduckgo()` does not check HTTP status before parsing | `data/patent_client.py:202-203` | 🟡 MED | Open |
| ISSUE-26 | `BatchScoreMarketWorkflow` missing `@workflow.defn` / `@workflow.run` decorators | `analytics/workflows.py:30-41` | 🟡 MED | Open |
| ISSUE-27 | `ContentExtractorAgent.http` (httpx.AsyncClient) never closed; leaks connections | `research/ai_research_orchestrator.py:371` | 🟡 MED | Open |
| ISSUE-28 | `WebSearchAgent.cache` is unbounded in-memory dict with no eviction | `research/ai_research_orchestrator.py:183,216` | 🟡 MED | Open |
| ISSUE-29 | `DataValidatorAgent` bounds are unit-agnostic; per-employee check assumes millions | `research/ai_research_orchestrator.py:553-616` | 🟡 MED | Open |
| ISSUE-30 | `GitHubClient.fetch_file()` silently swallows all exceptions with no logging | `agents/github/client.py:80-81` | 🟡 MED | Open |
| ISSUE-31 | `fetch_repos()` truncates at 100 regardless of `max_repos`; no pagination | `agents/github/search.py:56` | 🟢 LOW | Open |
| ISSUE-32 | `_merge_enrichment()` mutates caller's input dict in-place | `data/eneve_enrichment_integration.py:299-328` | 🟡 MED | Open |
| ISSUE-33 | `data_quality_score` is fabricated from source count; misleads downstream quality gates | `data/eneve_enrichment_integration.py:310` | 🟡 MED | Open |
| ISSUE-34 | `WebSearchAgent._api_search_news()` contains unreachable dead code with undefined `requests` | `agents/web_search_agent.py:145-167` | 🟡 MED | Open |
| ISSUE-35 | `CompaniesHouseAgent` uses `requests.get()` in 3 methods without importing `requests` | `agents/companies_house_agent.py:138,182,224` | 🔴 HIGH | Open |
| ISSUE-36 | `CompaniesHouseAgent` async methods called via `asyncio.to_thread` return coroutines instead of results | `agents/companies_house_agent.py:114-121` | 🔴 HIGH | Open |
| ISSUE-37 | `CoordinatorAgent.__init__()` missing required `source_type` arg to parent; always crashes at instantiation | `agents/coordinator_agent.py:58` | 🔴 HIGH | Open |
| ISSUE-38 | `CoordinatorAgent.analyze_company()` constructs `AgentTaskResult` with missing required fields | `agents/coordinator_agent.py:135-148` | 🔴 HIGH | Open |
| ISSUE-39 | `ResponseCache` uses deprecated `datetime.utcnow()`; breaks on Python 3.13 | `core/production_hardening.py:111,125` | 🟡 MED | Open |
| ISSUE-40 | `ErrorLoggingMiddleware` exhausts `response.body_iterator`; all 4xx/5xx responses deliver empty body to clients | `api/middleware/logging.py:168-186` | 🔴 HIGH | Open |
| ISSUE-41 | `get_rate_limit_for_path()` operator precedence bug neutralizes trailing-slash guard | `api/middleware/rate_limit.py:50` | 🟡 MED | Open |
| ISSUE-42 | `AuthenticationMiddleware` bypasses auth for any URL starting with `/companies` or `/enrichment` | `api/middleware/security.py:61-62` | 🟡 MED | Open |
| ISSUE-43 | `EnrichmentPipeline.enrich()` uses `return_exceptions=False`; one adapter failure kills entire enrichment | `application/enrichment_pipeline.py:99` | 🔴 HIGH | Open |
| ISSUE-44 | `StructuredLLMClient.extract()` passes `temperature` kwarg not in `generate()` signature; `TypeError` every call | `llm/structured_client.py:113` | 🔴 HIGH | Open |
| ISSUE-45 | `EnhancedLLMClient.generate()` returns `None` silently after all providers fail; callers crash downstream | `llm/enhanced_client.py:114-115` | 🟡 MED | Open |
| ISSUE-46 | `OllamaQuerier.query()` bare `except Exception: raise` with no logging; plus `OllamaQuerier` is zombie code never invoked | `llm/query/ollama.py:67-68` | 🟢 LOW | Open |
| ISSUE-47 | `async_jobs.py` calls `celery_app.send_task()` synchronously in async handlers; blocks event loop under broker latency | `api/routers/async_jobs.py:130,173` | 🟡 MED | Open |

**Critical path summary (🔴 HIGH — 18 issues):** ISSUE-01, 04, 06, 10, 11, 12, 14, 18, 19, 23, 24, 35, 36, 37, 38, 40, 43, 44.

Newly confirmed broken subsystems this pass: `StructuredLLMClient` (ISSUE-44 — TypeError on every call), `ErrorLoggingMiddleware` (ISSUE-40 — empty bodies for all API errors), `EnrichmentPipeline` (ISSUE-43 — false isolation guarantee).

---

*Audit performed 2026-03-18. Fifth pass (LLM layer, API middleware, application, async jobs) completed 2026-03-18. All file:line references correspond to the state of the repository at this date.*

---

## 16. DEEP-DIVE ROOT CAUSE ANALYSIS (Sixth Pass — 2026-03-18)

This pass re-reads source files for previously documented issues to verify root causes, correct false positives, and trace full crash chains. Files newly read: `agents/__init__.py`, `agents/base_agent.py` (full), `agents/companies_house_agent.py` (lines 1-30, 109-175), `agents/coordinator_agent.py` (full), `application/enrichment_pipeline.py` (lines 161-183), `application/agents/__init__.py`, `data/unified/company.py`, `domain/models.py` (lines 84-135, 194-328), `monitoring/continuous_monitor.py`, `worker/enrichment_tasks.py` (lines 50-109).

---

### ISSUE-01 DEEP REVISION — `FinancialMetric(allow_empty_primary=True)` ALWAYS raises; `Company.financials` default value is permanently broken; Celery enrichment task always crashes

**Severity:** 🔴 HIGH — upgraded from "bypass broken" to "entire Company construction pipeline broken"
**Files:** `domain/models.py:84-134`, `domain/models.py:213`, `worker/enrichment_tasks.py:58`

**Original finding:** The `allow_empty_primary` flag is bypassed by the second validator.

**Actual root cause — confirmed by full source trace:**

`FinancialMetric` has two `@model_validator(mode="after")` validators:

```python
@model_validator(mode="after")
def require_primary_metric(self) -> "FinancialMetric":
    if self.allow_empty_primary:
        return self          # ← exits, but does NOT stop the chain
    ...

@model_validator(mode="after")
def at_least_one_primary_metric(self) -> "FinancialMetric":
    if self.revenue is None and self.employees is None:
        raise ValueError(...)   # ← ALWAYS runs, regardless of allow_empty_primary
```

In Pydantic v2, `return self` from a model validator does not stop subsequent validators. ALL validators in sequence. So `FinancialMetric(allow_empty_primary=True)` with `revenue=None` and `employees=None` ALWAYS raises `ValueError` from `at_least_one_primary_metric`. The `allow_empty_primary` flag is permanently broken.

**Chain reaction — the default value for `Company.financials` is broken:**

```python
# domain/models.py:213
financials: FinancialMetric | None = Field(
    default_factory=lambda: FinancialMetric(allow_empty_primary=True)
)
```

This `default_factory` runs every time a `Company` is constructed without providing `financials`. It calls `FinancialMetric(allow_empty_primary=True)` which ALWAYS raises. Pydantic v2 captures this as a `ValidationError` on the `financials` field.

**Consequence: `Company(id=..., name=...)` ALWAYS raises `ValidationError`** when `financials` is not explicitly provided with non-None revenue or employees.

**Chain reaction — Celery enrichment task ALWAYS fails at line 58:**

```python
# worker/enrichment_tasks.py:58
company = UnifiedCompany(id=company_id, name=company_name or company_id)
```

`UnifiedCompany` inherits `Company`. No `financials`, no `revenue`, no `employees` passed. The `default_factory` runs → `FinancialMetric(allow_empty_primary=True)` raises → `ValidationError` raised inside `enrich_company_async`.

The `except Exception as exc` at line 89 catches this. Celery retries until `MaxRetriesExceededError`, then records to the in-memory DLQ (ISSUE-06/18). **Every enrichment job submitted via the async API immediately fails, retries three times, and silently lands in an in-memory DLQ that is never read and is lost on worker restart.**

**The full silent failure chain:**
```
POST /api/v1/enrich/company
  → celery_app.send_task(...)         [ISSUE-47: blocks event loop]
  → job "SUBMITTED" returned to caller
  → worker runs enrich_company_async
  → UnifiedCompany(id=..., name=...) RAISES ValidationError  [ISSUE-01]
  → except Exception: retry scheduled  [ISSUE-06: logged at INFO]
  → MaxRetriesExceededError
  → dead_letter_queue.record_failure()  [ISSUE-18: in-memory, lost on restart]
  → task returns {"status": "FAILED"}   [caller likely never checks this]
  → GET /api/v1/jobs/{id} → "FAILED" (if checked)
```

The API returns 200 "SUBMITTED" but enrichment NEVER occurs.

**Note:** `Company.sync_financial_fields` at line 288 also calls `FinancialMetric(allow_empty_primary=True)` as a fallback when `self.financials is None`. This is equally broken.

---

### ISSUE-37 DEEP REVISION — `coordinator_agent.py` imports non-existent `workflow_nodes` module; entire `solstein.agents` package fails to import

**Severity:** 🔴 HIGH — upgraded from "TypeError at instantiation" to "ModuleNotFoundError at package load; blast radius includes application/agents/ and monitoring/"
**Files:** `agents/coordinator_agent.py:23-28`, `agents/__init__.py:9`

**Original finding:** `CoordinatorAgent.__init__()` misses `source_type` arg — `TypeError` at instantiation.

**Actual root cause — confirmed by directory listing and import trace:**

`coordinator_agent.py:23-28` imports:
```python
from .workflow_nodes import (
    ExtractSignalsNode,
    GatherSourcesNode,
    LogicFusionNode,
    ProcessRawNode,
)
```

`workflow_nodes.py` does NOT exist in `src/solstein/agents/`. Confirmed by `Glob("src/solstein/agents/workflow_nodes*")` returning no results and `Glob("src/solstein/agents/*.py")` showing no such file. This is a `ModuleNotFoundError` at module LOAD time — before any class is instantiated.

**Blast radius — `agents/__init__.py` exports `CoordinatorAgent`:**

```python
# agents/__init__.py:9
from .coordinator_agent import CoordinatorAgent   # ← triggers ModuleNotFoundError
```

When Python imports any member of the `solstein.agents` package (including sub-modules like `solstein.agents.base_agent`), it runs `agents/__init__.py`. The import at line 9 fails. **ALL imports from `solstein.agents.*` fail with `ModuleNotFoundError`**, including:

- `from solstein.agents.base_agent import ...` — fails
- `from solstein.agents.companies_house_agent import ...` — fails
- `from solstein.agents.resilience import ...` — fails

**Confirmed affected files (all fail to import):**
- `application/agents/__init__.py` — imports from `solstein.agents.base_agent`, `.companies_house_agent`, `.github_agent`, `.resilience`, `.web_search_agent`
- `application/agents/base_agent.py` — imports from `solstein.agents.base_agent`
- `application/agents/companies_house_agent.py`, `github_agent.py`, `web_search_agent.py`, `resilience.py` — same
- `monitoring/continuous_monitor.py:13` — `from ..agents import GitHubAgent, WebSearchAgent`

**Blast radius assessment:** `application/agents/` is a redundant agents layer that mirrors `agents/`. Grep confirms nothing outside `application/agents/` and `monitoring/continuous_monitor.py` imports from `application.agents` or `solstein.agents`. `ContinuousMonitor` is not imported anywhere else. The main API and research pipeline do NOT import from `solstein.agents.*` — confirmed by grep returning 0 results for `from.*agents import` in `api/` and `research/`. The blast radius is **contained to `application/agents/` (6 files) and `monitoring/continuous_monitor.py`**, but these are completely non-functional.

**The `source_type` TypeError (original ISSUE-37)** would only manifest if `workflow_nodes.py` existed and `CoordinatorAgent` could be instantiated. It is masked by the `ModuleNotFoundError`.

---

### ISSUE-43 — CLOSED (False Positive)

**Status:** ❌ **Closed — finding was incorrect.**
**File:** `application/enrichment_pipeline.py:99`

**Original claim:** `asyncio.gather(*tasks, return_exceptions=False)` violates the isolation guarantee.

**Actual behavior:** The tasks are calls to `_call_adapter()`, which at lines 154-159 wraps ALL exceptions with:
```python
except TimeoutError:
    logger.warning("Adapter timed out", ...)
    return None
except Exception as exc:
    logger.error("Adapter failed", ...)
    return None
```

`_call_adapter` NEVER raises — it always returns `RawDataSource | None`. Therefore `asyncio.gather(return_exceptions=False)` never propagates an exception. The `return_exceptions=False` is functionally equivalent to `return_exceptions=True` here. The docstring's isolation guarantee is accurate.

---

### ISSUE-49 — `EnrichmentPipeline._merge()` has unimplemented `pass` stub; `RawDataSource` with `.data` attribute silently discards all data

**Severity:** 🔴 HIGH
**File:** `src/solstein/application/enrichment_pipeline.py:172-174`

```python
def _merge(self, company_id, company_name, sources):
    all_records: list[RawDataRecord] = []
    for src in sources:
        if hasattr(src, "records") and src.records:
            all_records.extend(src.records)
        elif hasattr(src, "data") and src.data:
            # Adapt raw dict data into a minimal RawDataRecord if needed
            pass                   # ← UNIMPLEMENTED STUB
```

Any `RawDataSource` that stores enrichment data in `.data` (a `dict`) rather than `.records` (a `list[RawDataRecord]`) is silently ignored. The `pass` leaves `all_records` unmodified. The source's data is never added to the aggregate.

`RawDataSource` is defined in `domain/models.py` and has both `raw_content: str | dict` and potentially adapter-specific fields. Adapters that return dict-based data (rather than `RawDataRecord` lists) produce results that `_merge` sees, considers, and then drops completely with no log. The `AggregatedDataRecord` returned has `facts=[]` for all such sources. The `record.update_quality_metrics()` call then reports 0 records — which would calculate artificially low confidence scores.

**Root cause:** The branch was added as a placeholder noting the need to adapt dict data, but the implementation was deferred indefinitely without a TODO marker that would surface it in CI.

---

### ISSUE-36 ROOT CAUSE — Full trace of coroutine-as-result propagation through CompaniesHouseAgent

**Severity:** 🔴 HIGH — existing finding, root cause fully traced
**File:** `agents/companies_house_agent.py:109-175`

The previously documented ISSUE-36 was correct but the full trace was incomplete. Here is the complete execution path:

**Step 1** — `_search_company_by_name` calls `call_with_retry(asyncio.to_thread, self._api_search_company, company_name, ...)` at line 114-121.

**Step 2** — `asyncio.to_thread` submits `self._api_search_company(company_name)` to a thread. Since `_api_search_company` is `async def`, calling it returns a coroutine object immediately. The coroutine body (including `requests.get(...)`) never executes. The thread returns the coroutine object.

**Step 3** — `asyncio.to_thread` delivers the coroutine as its result. `company_num = await call_with_retry(...)` receives the coroutine object.

**Step 4** — Line 122: `if company_num:` — a coroutine object is always truthy (`bool(coroutine)` = `True`). The agent believes it found a valid company number.

**Step 5** — Line 123: `self.log_info(f"Found company number: {company_num}")` — logs something like `"Found company number: <coroutine object _api_search_company at 0x7f3a2b1c4d80>"`. This is the only observable symptom in logs.

**Step 6** — The coroutine object is returned as `company_num`. It is passed to `_fetch_company_details(company_num)` at line 164-172. This calls `asyncio.to_thread(self._api_get_company, company_num, ...)`. Again `_api_get_company` is `async def` — another coroutine returned. Same cycle.

**Step 7** — The agent returns a result claiming to have found companies, with all data fields populated by coroutine objects used as string identifiers.

**Step 8** — Python generates `RuntimeWarning: coroutine '_api_search_company' was never awaited` and `RuntimeWarning: coroutine '_api_get_company' was never awaited` at GC time. These appear in stderr, not in the structured logger. They may be filtered or missed entirely.

**Root cause confirmed:** `asyncio.to_thread` is designed for synchronous (blocking) callables. Passing an `async def` function causes the callable to return a coroutine rather than executing the function body. The fix requires either: (a) making `_api_search_company` a `def` using `requests`, or (b) calling the async methods directly with `await` instead of via `asyncio.to_thread`.

---

## 17. UPDATED SUMMARY TABLE (Full — Including Revisions)

| ID | Description | File | Severity | Status |
|---|---|---|---|---|
| FIX-01 | Converter consolidation (EPIC-058) | `scripts/run_eneve_199.py:21` | — | ✅ Fixed |
| FIX-02 | Export/gate decoupling in ENEVE script (EPIC-060) | `scripts/run_eneve_199.py:113-163` | — | ✅ Fixed |
| FIX-03 | Instrumented adapters re-raise exceptions | `adapters/instrumented.py:94,145` | — | ✅ Fixed |
| ISSUE-01 | `FinancialMetric(allow_empty_primary=True)` always raises; `Company` default construction always fails; Celery enrichment always crashes silently | `domain/models.py:107-134, 213` + `worker/enrichment_tasks.py:58` | 🔴 HIGH | Open — **DEEPENED** |
| ISSUE-02 | FinancialMetric duplicate field declarations | `domain/models.py:97-103` | 🟡 MED | Open |
| ISSUE-03 | Company duplicate field blocks (defined twice) | `domain/models.py:143-153 vs 195-201` | 🟡 MED | Open |
| ISSUE-04 | Scoring degrades silently to base_score on exception | `analytics/scoring.py:161-180` | 🔴 HIGH | Open |
| ISSUE-05 | Celery EnrichmentTask hooks are empty stubs | `worker/enrichment_tasks.py:23-29` | 🟡 MED | Open |
| ISSUE-06 | DLQ loses traceback, no alerting (see also ISSUE-18) | `worker/enrichment_tasks.py:99-109` | 🔴 HIGH | Open |
| ISSUE-07 | Enrichment loop breaks without re-raising | `data/unified/enrichment.py:72-85` | 🟡 MED | Open |
| ISSUE-08 | `ensure_release_ready()` throwing path still used in CLI | `data/report_release_gate.py:297-315` | 🟡 MED | Open |
| ISSUE-09 | Enrichment errors silently accumulate in list | `data/unified/enrichment.py:129+` | 🟡 MED | Open |
| ISSUE-10 | Batch API hardcodes `failed_count=0`, `success_rate=100.0` | `api/routers/enrichment_batch.py:50-70` | 🔴 HIGH | Open |
| ISSUE-11 | `enrich_batch()` silently substitutes original on failure | `data/unified/enrichment.py:189-191` | 🔴 HIGH | Open |
| ISSUE-12 | `store_facts()` is an unimplemented stub; DB never written | `worker/base.py:34-59` | 🔴 HIGH | Open |
| ISSUE-13 | Gap analyzer treats `revenue=0.0` as missing; blocks pre-revenue companies | `data/gap_analyzer.py:80-85` | 🟡 MED | Open |
| ISSUE-14 | Provenance check requires HTTP/HTTPS/URN; JSON-loaded data always fails | `data/gap_analyzer.py:36-46` | 🔴 HIGH | Open |
| ISSUE-15 | Completeness calculator counts enum defaults and empty lists as filled | `analytics/completeness.py:98-104` | 🟡 MED | Open |
| ISSUE-16 | `normalize_percent()` heuristic silently misclassifies values near ±1 | `data/metric_contract.py:34-37` | 🟡 MED | Open |
| ISSUE-17 | Scorers inconsistent None-handling: GrowthMomentum skips, FinancialHealth penalizes | `analytics/scorers/growth_momentum.py:75-77` | 🟡 MED | Open |
| ISSUE-18 | DLQ in-memory only (lost on restart), logs at INFO not ERROR | `worker/base.py:67-88` | 🔴 HIGH | Open |
| ISSUE-19 | 3 of 7 CLI report commands hard-block via `assert_client_report_ready` | `data/report_readiness.py:74-112` | 🔴 HIGH | Open |
| ISSUE-20 | `saas_maturity` None fallback in CompetitivePositionScorer is dead code | `analytics/scorers/competitive_position.py:41` | 🟢 LOW | Open |
| ISSUE-21 | Two `ConfidenceLevel` enums with same name in different modules | `domain/models.py:30` vs `data/provenance.py:27` | 🟡 MED | Open |
| ISSUE-22 | Deprecated Pydantic v2 `.dict()` in API cache path | `api/routers/enrichment_single.py:108` | 🟢 LOW | Open |
| ISSUE-23 | `search_company_patents()` calls async sub-functions without `await`; always crashes | `data/patent_client.py:33-54` | 🔴 HIGH | Open |
| ISSUE-24 | `PatentsUnifiedAdapter` entirely non-functional (depends on ISSUE-23) | `adapters/enrichment/patents_unified.py:66,97,134` | 🔴 HIGH | Open |
| ISSUE-25 | `_search_duckduckgo()` does not check HTTP status before parsing | `data/patent_client.py:202-203` | 🟡 MED | Open |
| ISSUE-26 | `BatchScoreMarketWorkflow` missing `@workflow.defn` / `@workflow.run` decorators | `analytics/workflows.py:30-41` | 🟡 MED | Open |
| ISSUE-27 | `ContentExtractorAgent.http` (httpx.AsyncClient) never closed; leaks connections | `research/ai_research_orchestrator.py:371` | 🟡 MED | Open |
| ISSUE-28 | `WebSearchAgent.cache` is unbounded in-memory dict with no eviction | `research/ai_research_orchestrator.py:183,216` | 🟡 MED | Open |
| ISSUE-29 | `DataValidatorAgent` bounds are unit-agnostic; per-employee check assumes millions | `research/ai_research_orchestrator.py:553-616` | 🟡 MED | Open |
| ISSUE-30 | `GitHubClient.fetch_file()` silently swallows all exceptions with no logging | `agents/github/client.py:80-81` | 🟡 MED | Open |
| ISSUE-31 | `fetch_repos()` truncates at 100 regardless of `max_repos`; no pagination | `agents/github/search.py:56` | 🟢 LOW | Open |
| ISSUE-32 | `_merge_enrichment()` mutates caller's input dict in-place | `data/eneve_enrichment_integration.py:299-328` | 🟡 MED | Open |
| ISSUE-33 | `data_quality_score` is fabricated from source count | `data/eneve_enrichment_integration.py:310` | 🟡 MED | Open |
| ISSUE-34 | `WebSearchAgent._api_search_news()` contains unreachable dead code | `agents/web_search_agent.py:145-167` | 🟡 MED | Open |
| ISSUE-35 | `CompaniesHouseAgent` uses `requests.get()` without importing `requests` | `agents/companies_house_agent.py:138,182,224` | 🔴 HIGH | Open |
| ISSUE-36 | `CompaniesHouseAgent` async methods via `asyncio.to_thread` return coroutines; full trace in §16 | `agents/companies_house_agent.py:114-121` | 🔴 HIGH | Open — **DEEPENED** |
| ISSUE-37 | `coordinator_agent.py` imports non-existent `workflow_nodes`; `ModuleNotFoundError` at package load; blast radius includes `application/agents/` and `monitoring/continuous_monitor.py` | `agents/coordinator_agent.py:23-28`, `agents/__init__.py:9` | 🔴 HIGH | Open — **DEEPENED** |
| ISSUE-38 | `CoordinatorAgent.analyze_company()` constructs `AgentTaskResult` with missing required fields | `agents/coordinator_agent.py:135-148` | 🔴 HIGH | Open — *masked by ISSUE-37* |
| ISSUE-39 | `ResponseCache` uses deprecated `datetime.utcnow()`; breaks on Python 3.13 | `core/production_hardening.py:111,125` | 🟡 MED | Open |
| ISSUE-40 | `ErrorLoggingMiddleware` exhausts `response.body_iterator`; all 4xx/5xx responses deliver empty body | `api/middleware/logging.py:168-186` | 🔴 HIGH | Open |
| ISSUE-41 | `get_rate_limit_for_path()` operator precedence bug neutralizes trailing-slash guard | `api/middleware/rate_limit.py:50` | 🟡 MED | Open |
| ISSUE-42 | `AuthenticationMiddleware` bypasses auth for any URL starting with `/companies` or `/enrichment` | `api/middleware/security.py:61-62` | 🟡 MED | Open |
| ISSUE-43 | ~~`EnrichmentPipeline` isolation guarantee violated~~ | `application/enrichment_pipeline.py:99` | — | ❌ CLOSED — false positive; `_call_adapter` handles all exceptions |
| ISSUE-44 | `StructuredLLMClient.extract()` passes `temperature` kwarg not in `generate()` signature; TypeError every call | `llm/structured_client.py:113` | 🔴 HIGH | Open |
| ISSUE-45 | `EnhancedLLMClient.generate()` returns `None` silently after all providers fail | `llm/enhanced_client.py:114-115` | 🟡 MED | Open |
| ISSUE-46 | `OllamaQuerier` bare `except Exception: raise` with no logging; zombie code | `llm/query/ollama.py:67-68` | 🟢 LOW | Open |
| ISSUE-47 | `celery_app.send_task()` called synchronously in async handlers | `api/routers/async_jobs.py:130,173` | 🟡 MED | Open |
| ISSUE-48 | `EnrichmentPipeline._merge()` unimplemented stub silently drops `RawDataSource.data` | `application/enrichment_pipeline.py:172-174` | 🔴 HIGH | Open |

**Critical path (🔴 HIGH — 19 issues):** ISSUE-01, 04, 06, 10, 11, 12, 14, 18, 19, 23, 24, 35, 36, 37, 38, 40, 44, 48, and the revised ISSUE-01 chain confirms the Celery enrichment pipeline is end-to-end broken.

**Most consequential finding this pass:** ISSUE-01 revision reveals that `UnifiedCompany(id=..., name=...)` at `enrichment_tasks.py:58` ALWAYS raises `ValidationError`. The async enrichment API appears to accept jobs but every job silently crashes before any enrichment occurs, retries three times, lands in an in-memory DLQ, and is permanently lost.

---

*Audit performed 2026-03-18. Sixth pass (deep-dive root cause) completed 2026-03-18. All file:line references correspond to the state of the repository at this date.*

---

## 18. ADDITIONAL ISSUES (Seventh Pass — Schema Mismatch Root Cause + Adapter Blast Radius — 2026-03-18)

Files newly read this pass: `domain/models.py:651-730` (canonical `RawDataSource` and `DataSourceType` definitions), `adapters/enrichment/funding_unified.py`, `adapters/enrichment/web_search_unified.py`, `adapters/enrichment/yahoo_finance.py`, `application/enrichment_pipeline.py:150-183` (full `_merge()` implementation). All findings are source-corroborated.

---

### ISSUE-49 — All `BaseRefreshConnector` unified adapters construct `RawDataSource` with wrong field names; `raw_content` (required, no default) never provided; every `enrich()` call raises `ValidationError`

**Severity:** 🔴 HIGH
**Files:**
- `src/solstein/adapters/enrichment/website_unified.py:151-161`
- `src/solstein/adapters/enrichment/news_unified.py:191-212`
- `src/solstein/adapters/enrichment/funding_unified.py:153-163`
- `src/solstein/adapters/enrichment/web_search_unified.py:146-165`
- `src/solstein/domain/models.py:672-687` (canonical `RawDataSource` definition)

**Canonical `RawDataSource` as defined in `domain/models.py:672-687`:**

```python
class RawDataSource(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    source_type: DataSourceType
    source_name: str
    raw_content: str | dict[str, Any]   # ← REQUIRED, no default
    url: str | None = None
    retrieval_timestamp: datetime = Field(default_factory=...)
    confidence: float = Field(default=0.5, ge=0, le=1)
    relevance_score: float = Field(default=0.5, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    extraction_method: str | None = None
    notes: str | None = None
    # ← NO `data` field, NO `company_id` field, NO `fetch_timestamp` field
```

**What all unified adapters pass instead (example from `website_unified.py:151-161`):**

```python
return RawDataSource(
    source_name=self.source_name,
    source_type=self.source_type,
    company_id=company_id,          # ← NOT a field on RawDataSource → extra, ignored by Pydantic
    fetch_timestamp=datetime.now(), # ← NOT a field on RawDataSource → extra, ignored by Pydantic
    data=data,                      # ← NOT a field on RawDataSource → extra, ignored by Pydantic
    metadata={...},
    # raw_content NOT PROVIDED       ← required field, no default → ValidationError
)
```

Same pattern in `news_unified.py:191-212` (`data={...}`), `funding_unified.py:153-163` (`data=data`), `web_search_unified.py:146-165` (`data={...}`).

Pydantic v2 uses `extra="ignore"` by default — the `company_id`, `fetch_timestamp`, and `data` extra fields are silently ignored. But `raw_content` is a required field with no default. Pydantic v2 raises `ValidationError: 1 validation error for RawDataSource — raw_content: Field required` on every `RawDataSource(...)` construction call that omits it.

**Execution chain:**
1. `_call_adapter(adapter, ...)` calls `adapter.enrich(...)`
2. `enrich()` calls `RawDataSource(source_name=..., data=..., ...)` without `raw_content`
3. Pydantic raises `ValidationError` inside `enrich()`
4. `_call_adapter` at line 157-159 catches `Exception as exc` → `logger.error("Adapter failed", ...)` → `return None`
5. `_merge()` receives `None` in the sources list — skipped silently

**Root cause:** The unified adapters were written against an older `RawDataSource` schema that had `data: dict`, `company_id: str`, and `fetch_timestamp: datetime` as fields. The canonical `RawDataSource` was subsequently refactored to use `raw_content`, `retrieval_timestamp`, and removed `company_id`. The unified adapters were NOT updated to match the new schema. The discrepancy is invisible at static analysis time if `extra` is not set to `"forbid"`.

**The only adapter that uses correct field names:** `adapters/enrichment/yahoo_finance.py:43-53` — constructs `RawDataSource(raw_content=profile.model_dump(mode="json"), retrieval_timestamp=datetime.now(timezone.utc), confidence=0.8, relevance_score=0.9, ...)`. This adapter succeeds at construction. However, it is still silently dropped by `_merge()` — see ISSUE-48 deepening below.

**⚠️ DISCLAIMER:** `adapters/enrichment/linkedin_unified.py` has not been directly read for this finding. Based on the same import pattern and structural consistency with other unified adapters (all written against the same old schema), it is very likely to share this defect. Requires a direct read of `linkedin_unified.py:enrich()` to confirm.

---

### ISSUE-48 — DEEPENED: `_merge()` checks for `.records` and `.data` — attributes from old `RawDataSource` schema; both branches unreachable for all current `RawDataSource` objects; `_merge()` ALWAYS returns empty `AggregatedDataRecord`

**Severity:** 🔴 HIGH — **deepened from "stub drops .data sources" to "both branches structurally unreachable; zero enrichment data ever aggregated"**
**File:** `src/solstein/application/enrichment_pipeline.py:161-182`

**Original finding:** The `elif hasattr(src, "data") and src.data: pass` branch is an unimplemented stub that silently drops dict-based sources.

**Actual root cause — confirmed by reading canonical `RawDataSource` at `domain/models.py:672-687`:**

```python
def _merge(self, company_id, company_name, sources):
    all_records: list[RawDataRecord] = []
    for src in sources:
        if hasattr(src, "records") and src.records:      # ← Branch A
            all_records.extend(src.records)
        elif hasattr(src, "data") and src.data:           # ← Branch B
            pass                                          # ← stub
```

**Branch A — `hasattr(src, "records")`:** The canonical `RawDataSource` has NO `.records` field. Its fields are `raw_content`, `url`, `retrieval_timestamp`, `confidence`, `relevance_score`, `metadata`, `extraction_method`, `notes`. `hasattr(RawDataSource_instance, "records")` evaluates to `False`. Branch A never executes for any correctly-constructed `RawDataSource`.

**Branch B — `hasattr(src, "data")`:** The canonical `RawDataSource` has NO `.data` field either — the old `data` field was removed and replaced by `raw_content`. `hasattr(RawDataSource_instance, "data")` evaluates to `False`. Branch B never executes for any correctly-constructed `RawDataSource`.

**Combined result:** For every `RawDataSource` object that reaches `_merge()`, both `if` and `elif` evaluate to `False`. The source is silently skipped. `all_records` remains `[]`. The returned `AggregatedDataRecord` always has `facts=[]`.

**Interaction with ISSUE-49:** Unified adapters crash with `ValidationError` before reaching `_merge()` (ISSUE-49), so they never contribute even a skippable `RawDataSource` object. `YahooFinanceEnrichment` correctly constructs `RawDataSource(raw_content=...)`, but even this object is silently dropped by `_merge()` because neither branch matches.

**The correct field is `raw_content`.** Branch A should check `hasattr(src, "raw_content") and src.raw_content` and convert it into an `AggregatedFact`. Branch B is dead code from the old schema.

**Net effect:** `EnrichmentPipeline.enrich()` always returns an `AggregatedDataRecord` with `facts=[]` and artificially low quality metrics. No data from any adapter is ever incorporated into the aggregated result, regardless of whether the adapter succeeds or not.

---

### ISSUE-40 — ADDENDUM: Middleware ordering confirmed; `ErrorLoggingMiddleware` is outermost wrapper affecting 100% of 4xx/5xx responses

**Severity:** 🔴 HIGH (existing) — addendum with exact ordering evidence
**File:** `src/solstein/api/main.py:140-154`

Previously documented: `ErrorLoggingMiddleware` consumes `response.body_iterator` without restoring it, delivering empty bodies to clients on all error responses.

**Now confirmed from `main.py:140-154`:** Middleware registration order:

```python
# main.py:140-154 — order of registration = outermost to innermost in Starlette
setup_exception_handlers(app)        # line 140 — not middleware, exception handlers
setup_logging_middleware(app)        # line 141 — registers ErrorLoggingMiddleware FIRST → OUTERMOST
setup_rate_limiting(app)             # line 142
setup_security_middleware(app)       # line 143
setup_performance_middleware(app)    # line 146
app.add_middleware(TenantMiddleware) # line 154 — INNERMOST
```

In Starlette/FastAPI, middleware added first wraps all subsequent middleware and the application. `ErrorLoggingMiddleware` (added via `setup_logging_middleware` at line 141, immediately after exception handlers) is the outermost layer. It processes every single response before it reaches the ASGI transport. **All 4xx/5xx responses from any route, any middleware, and any exception handler get their body exhausted here before reaching the client.**

---

## 19. UPDATED SUMMARY TABLE (Full — Including ISSUE-49 and Revisions)

| ID | Description | File | Severity | Status |
|---|---|---|---|---|
| FIX-01 | Converter consolidation (EPIC-058) | `scripts/run_eneve_199.py:21` | — | ✅ Fixed |
| FIX-02 | Export/gate decoupling in ENEVE script (EPIC-060) | `scripts/run_eneve_199.py:113-163` | — | ✅ Fixed |
| FIX-03 | Instrumented adapters re-raise exceptions | `adapters/instrumented.py:94,145` | — | ✅ Fixed |
| ISSUE-01 | `FinancialMetric(allow_empty_primary=True)` always raises; `Company` default construction always fails; Celery enrichment always crashes | `domain/models.py:107-134, 213` + `worker/enrichment_tasks.py:58` | 🔴 HIGH | Open — DEEPENED |
| ISSUE-02 | FinancialMetric duplicate field declarations | `domain/models.py:97-103` | 🟡 MED | Open |
| ISSUE-03 | Company duplicate field blocks (defined twice) | `domain/models.py:143-153 vs 195-201` | 🟡 MED | Open |
| ISSUE-04 | Scoring degrades silently to base_score on exception | `analytics/scoring.py:161-180` | 🔴 HIGH | Open |
| ISSUE-05 | Celery EnrichmentTask hooks are empty stubs | `worker/enrichment_tasks.py:23-29` | 🟡 MED | Open |
| ISSUE-06 | DLQ loses traceback, no alerting | `worker/enrichment_tasks.py:99-109` | 🔴 HIGH | Open |
| ISSUE-07 | Enrichment loop breaks without re-raising | `data/unified/enrichment.py:72-85` | 🟡 MED | Open |
| ISSUE-08 | `ensure_release_ready()` throwing path still used in CLI | `data/report_release_gate.py:297-315` | 🟡 MED | Open |
| ISSUE-09 | Enrichment errors silently accumulate in list | `data/unified/enrichment.py:129+` | 🟡 MED | Open |
| ISSUE-10 | Batch API hardcodes `failed_count=0`, `success_rate=100.0` | `api/routers/enrichment_batch.py:50-70` | 🔴 HIGH | Open |
| ISSUE-11 | `enrich_batch()` silently substitutes original on failure | `data/unified/enrichment.py:189-191` | 🔴 HIGH | Open |
| ISSUE-12 | `store_facts()` is an unimplemented stub; DB never written | `worker/base.py:34-59` | 🔴 HIGH | Open |
| ISSUE-13 | Gap analyzer treats `revenue=0.0` as missing; blocks pre-revenue companies | `data/gap_analyzer.py:80-85` | 🟡 MED | Open |
| ISSUE-14 | Provenance check requires HTTP/HTTPS/URN; JSON-loaded data always fails | `data/gap_analyzer.py:36-46` | 🔴 HIGH | Open |
| ISSUE-15 | Completeness calculator counts enum defaults and empty lists as filled | `analytics/completeness.py:98-104` | 🟡 MED | Open |
| ISSUE-16 | `normalize_percent()` heuristic silently misclassifies values near ±1 | `data/metric_contract.py:34-37` | 🟡 MED | Open |
| ISSUE-17 | Scorers inconsistent None-handling: GrowthMomentum skips, FinancialHealth penalizes | `analytics/scorers/growth_momentum.py:75-77` | 🟡 MED | Open |
| ISSUE-18 | DLQ in-memory only (lost on restart), logs at INFO not ERROR | `worker/base.py:67-88` | 🔴 HIGH | Open |
| ISSUE-19 | 3 of 7 CLI report commands hard-block via `assert_client_report_ready` | `data/report_readiness.py:74-112` | 🔴 HIGH | Open |
| ISSUE-20 | `saas_maturity` None fallback in CompetitivePositionScorer is dead code | `analytics/scorers/competitive_position.py:41` | 🟢 LOW | Open |
| ISSUE-21 | Two `ConfidenceLevel` enums with same name in different modules | `domain/models.py:30` vs `data/provenance.py:27` | 🟡 MED | Open |
| ISSUE-22 | Deprecated Pydantic v2 `.dict()` in API cache path | `api/routers/enrichment_single.py:108` | 🟢 LOW | Open |
| ISSUE-23 | `search_company_patents()` calls async sub-functions without `await`; always crashes | `data/patent_client.py:33-54` | 🔴 HIGH | Open |
| ISSUE-24 | `PatentsUnifiedAdapter` entirely non-functional (depends on ISSUE-23) | `adapters/enrichment/patents_unified.py:66,97,134` | 🔴 HIGH | Open |
| ISSUE-25 | `_search_duckduckgo()` does not check HTTP status before parsing | `data/patent_client.py:202-203` | 🟡 MED | Open |
| ISSUE-26 | `BatchScoreMarketWorkflow` missing `@workflow.defn` / `@workflow.run` decorators | `analytics/workflows.py:30-41` | 🟡 MED | Open |
| ISSUE-27 | `ContentExtractorAgent.http` (httpx.AsyncClient) never closed; leaks connections | `research/ai_research_orchestrator.py:371` | 🟡 MED | Open |
| ISSUE-28 | `WebSearchAgent.cache` is unbounded in-memory dict with no eviction | `research/ai_research_orchestrator.py:183,216` | 🟡 MED | Open |
| ISSUE-29 | `DataValidatorAgent` bounds are unit-agnostic; per-employee check assumes millions | `research/ai_research_orchestrator.py:553-616` | 🟡 MED | Open |
| ISSUE-30 | `GitHubClient.fetch_file()` silently swallows all exceptions with no logging | `agents/github/client.py:80-81` | 🟡 MED | Open |
| ISSUE-31 | `fetch_repos()` truncates at 100 regardless of `max_repos`; no pagination | `agents/github/search.py:56` | 🟢 LOW | Open |
| ISSUE-32 | `_merge_enrichment()` mutates caller's input dict in-place | `data/eneve_enrichment_integration.py:299-328` | 🟡 MED | Open |
| ISSUE-33 | `data_quality_score` is fabricated from source count | `data/eneve_enrichment_integration.py:310` | 🟡 MED | Open |
| ISSUE-34 | `WebSearchAgent._api_search_news()` contains unreachable dead code | `agents/web_search_agent.py:145-167` | 🟡 MED | Open |
| ISSUE-35 | `CompaniesHouseAgent` uses `requests.get()` without importing `requests` | `agents/companies_house_agent.py:138,182,224` | 🔴 HIGH | Open |
| ISSUE-36 | `CompaniesHouseAgent` async methods via `asyncio.to_thread` return coroutines; full trace in §16 | `agents/companies_house_agent.py:114-121` | 🔴 HIGH | Open — DEEPENED |
| ISSUE-37 | `coordinator_agent.py` imports non-existent `workflow_nodes`; `ModuleNotFoundError` at package load | `agents/coordinator_agent.py:23-28`, `agents/__init__.py:9` | 🔴 HIGH | Open — DEEPENED |
| ISSUE-38 | `CoordinatorAgent.analyze_company()` constructs `AgentTaskResult` with missing required fields | `agents/coordinator_agent.py:135-148` | 🔴 HIGH | Open — masked by ISSUE-37 |
| ISSUE-39 | `ResponseCache` uses deprecated `datetime.utcnow()`; breaks on Python 3.13 | `core/production_hardening.py:111,125` | 🟡 MED | Open |
| ISSUE-40 | `ErrorLoggingMiddleware` exhausts `response.body_iterator`; all 4xx/5xx responses deliver empty body; outermost middleware (main.py:141) | `api/middleware/logging.py:168-186` | 🔴 HIGH | Open — ADDENDUM |
| ISSUE-41 | `get_rate_limit_for_path()` operator precedence bug neutralizes trailing-slash guard | `api/middleware/rate_limit.py:50` | 🟡 MED | Open |
| ISSUE-42 | `AuthenticationMiddleware` bypasses auth for any URL starting with `/companies` or `/enrichment` | `api/middleware/security.py:61-62` | 🟡 MED | Open |
| ISSUE-43 | ~~`EnrichmentPipeline` isolation guarantee violated~~ | `application/enrichment_pipeline.py:99` | — | ❌ CLOSED — false positive |
| ISSUE-44 | `StructuredLLMClient.extract()` passes `temperature` kwarg not in `generate()` signature; TypeError every call | `llm/structured_client.py:113` | 🔴 HIGH | Open |
| ISSUE-45 | `EnhancedLLMClient.generate()` returns `None` silently after all providers fail | `llm/enhanced_client.py:114-115` | 🟡 MED | Open |
| ISSUE-46 | `OllamaQuerier` bare `except Exception: raise` with no logging; zombie code | `llm/query/ollama.py:67-68` | 🟢 LOW | Open |
| ISSUE-47 | `celery_app.send_task()` called synchronously in async handlers | `api/routers/async_jobs.py:130,173` | 🟡 MED | Open |
| ISSUE-48 | `EnrichmentPipeline._merge()` checks for `.records` and `.data` — old schema attributes; neither exists on current `RawDataSource`; both branches unreachable; always returns empty aggregate | `application/enrichment_pipeline.py:170-174` | 🔴 HIGH | Open — DEEPENED |
| ISSUE-49 | All `BaseRefreshConnector` unified adapters construct `RawDataSource` with wrong field names; `raw_content` (required) never provided; `ValidationError` on every `enrich()` call | `adapters/enrichment/website_unified.py:151`, `news_unified.py:191`, `funding_unified.py:153`, `web_search_unified.py:146` | 🔴 HIGH | Open — NEW |

**Critical path (🔴 HIGH — 20 issues):** ISSUE-01, 04, 06, 10, 11, 12, 14, 18, 19, 23, 24, 35, 36, 37, 38, 40, 44, 48, 49.

**Most consequential finding this pass (ISSUE-48+49 interaction):** The unified adapter layer and `EnrichmentPipeline._merge()` are broken at the schema level due to an uncoordinated refactoring of `RawDataSource` (old fields: `data`, `company_id`, `fetch_timestamp` → new fields: `raw_content`, `retrieval_timestamp`). No unified adapter enrichment data is ever aggregated. Every `EnrichmentPipeline.enrich()` call returns an empty `AggregatedDataRecord` regardless of adapter success. The single correctly-implemented adapter (`yahoo_finance.py`) is also silently dropped by `_merge()` because it checks for `.records`/`.data` instead of `.raw_content`. **The `EnrichmentPipeline` is structurally non-functional end-to-end.**

---

*Audit performed 2026-03-18. Seventh pass (schema mismatch root cause, adapter blast radius) completed 2026-03-18. All file:line references correspond to the state of the repository at this date.*
