# MASTER AUDIT — Solstein — 2026-03-18

**Scope:** Full source-code audit of the ENEVE pipeline and supporting infrastructure.
**Method:** Direct source code reading with file:line citations. No assumptions — all findings are corroborated from code. Items not fully verified carry explicit `⚠️ DISCLAIMER` markers.
**Prior context:** `ENEVE_PIPELINE_CRITICAL_ANALYSIS.md` (2026-03-10) documented 10 pipeline issues. Several have since been addressed. This audit establishes current ground truth.

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
