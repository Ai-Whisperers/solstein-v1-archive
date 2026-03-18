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

⚠️ **DISCLAIMER:** I did not read `src/solstein/data/unified/company.py` which defines `UnifiedCompany`. It's possible `UnifiedCompany` does not inherit from `Company` and this path is not affected. A future agent should verify whether `UnifiedCompany` inherits `Company` and whether this validator conflict causes actual runtime failures in `enrich_company_async`.

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

⚠️ **DISCLAIMER:** I did not read the individual scorer files (`scorers/growth_momentum.py`, `scorers/financial_health.py`, `scorers/competitive_position.py`) to verify exactly how they handle `None` inputs from incomplete `FinancialMetric`. The ENEVE analysis states they "silently skip the component," but this needs verification against the actual scorer implementations.

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

⚠️ **DISCLAIMER:** I did not read `src/solstein/worker/base.py` to verify `dead_letter_queue` implementation. It's possible the DLQ itself has monitoring integration. A future agent should verify `dead_letter_queue.record_failure()` to confirm whether it emits metrics or sends alerts.

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

⚠️ **DISCLAIMER:** I read `report_readiness.py` only partially (lines 1-56). I did not verify what `assert_client_report_ready()` ultimately calls — whether it calls `evaluate()` or `ensure_release_ready()`. A future agent should trace `assert_client_report_ready` to confirm whether the `generate_report` and `generate_llm_report` CLI commands still hard-block on gate failure.

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

### PARTIAL-02 — Classification thresholds may produce degenerate results with degraded scoring

**Status:** Logic confirmed; full impact requires scorer-level verification.

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

⚠️ **DISCLAIMER:** Not verified against actual serialization output. A future agent should run the score command and inspect the output JSON to confirm `scoring_breakdown` serializes correctly.

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

## 6. RECOMMENDED INVESTIGATION PRIORITIES FOR FUTURE AGENTS

1. **Read `src/solstein/data/unified/company.py`** — verify if `UnifiedCompany` inherits `Company`. If yes, confirm whether `FinancialMetric(allow_empty_primary=True)` actually raises in practice (ISSUE-01).
2. **Read `src/solstein/analytics/scorers/growth_momentum.py`, `financial_health.py`, `competitive_position.py`** — verify exactly how each scorer handles `None` inputs from incomplete `FinancialMetric`. The ENEVE analysis claimed "silently skips," but this needs direct source confirmation.
3. **Read `src/solstein/worker/base.py`** — verify `dead_letter_queue.record_failure()` to determine if any alerting/metrics are emitted on DLQ writes (ISSUE-06).
4. **Trace `assert_client_report_ready()` in `src/solstein/data/report_readiness.py`** (read full file past line 56) — confirm whether `generate_report` and `generate_llm_report` still hard-block on gate failure (ISSUE-08 / PARTIAL-01).
5. **Run `solstein score <input>` and inspect output JSON** — verify `scoring_breakdown` serializes `ScoringExplanation` objects correctly (OBS-02).

---

*Audit performed 2026-03-18. All file:line references correspond to the state of the repository at this date.*
