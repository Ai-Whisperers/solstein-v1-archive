# STORY-170: Restore `generate-llm-report` — Fix Missing Module Import

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 — Critical |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-045 CLI Runtime Correctness |
| **Created** | 2026-03-01 |
| **Risk** | Medium — module was moved; full wiring to new location needed |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED BUG** — verified by live execution on 2026-03-01.

```python
# src/solstein/cli.py — generate_llm_report command
from .exporters.report_generator import LLMEnhancedReportGenerator
```

Raises at runtime:
```
ModuleNotFoundError: No module named 'solstein.exporters.report_generator'
```

**Root cause**: The file `src/solstein/exporters/report_generator.py` does not exist. The LLM-enhanced report generator was refactored into `src/solstein/exporters/markdown/generator.py` (as `ReportGenerator` with a `use_llm` flag) but the CLI import was never updated.

---

## Problem Statement

`generate-llm-report` is the highest-value CLI command — it uses the 13-provider LLM chain to produce enhanced competitive intelligence narratives. It has been completely broken since the exporter module was restructured. Users who run `generate-llm-report` receive a bare Python traceback with no guidance.

The LLM call chain (Ollama → Groq → Fireworks → ... → OpenAI) is fully configured with all 13 API keys, the health checker is implemented, and the `ReportGenerator` class already has `use_llm=True` support — but no code path ever reaches it.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Reliability | 🔴 Critical — command 100% unusable |
| Business Value | 🔴 Critical — LLM enhancement is the platform's core differentiator |
| User Experience | 🔴 Critical — raw Python traceback instead of helpful error |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/cli.py` | ~280–320 | Fix import + wire to `ReportGenerator` |
| `src/solstein/exporters/markdown/generator.py` | Existing | Verify `use_llm=True` path is complete |
| `src/solstein/exporters/markdown/company.py` | Existing | Verify LLM call sites |
| `tests/unit/test_cli_llm_report.py` | New | New test (with `--no-llm` flag) |

---

## Dependencies

- **Hard**: None — `ReportGenerator(use_llm=True)` already exists
- **Soft**: STORY-171 (loader migration), EPIC-021 (LLM client improvements)
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: The `generate-llm-report` command must use `ReportGenerator(use_llm=True)` from `exporters.markdown.generator` — the same class used by `generate-report` but with LLM enabled.

**REQ-2**: The `--no-llm` flag must pass `use_llm=False` to `ReportGenerator`, producing identical output to `generate-report` (useful for testing without API calls).

**REQ-3**: When all LLM providers are unavailable (Ollama down + no API keys), the command must fall back gracefully to template-based output with a clear warning, not crash.

**REQ-4**: LLM calls must go through the existing `EnhancedLLMClient` provider chain — no direct API calls in the report generator.

**REQ-5**: LLM output must be validated: if the LLM returns empty string or malformed content, the template fallback kicks in and logs a warning.

---

## Acceptance Criteria

- [ ] `python -m solstein.cli generate-llm-report "Eneve" --no-llm` produces complete report without LLM calls
- [ ] `python -m solstein.cli generate-llm-report "Eneve"` attempts LLM calls through the provider chain and produces enhanced report (or template fallback if all providers fail)
- [ ] On LLM failure, command exits with code 0 (graceful) and prints which provider was used or that template fallback was used
- [ ] On import, no `ModuleNotFoundError` is raised
- [ ] `ReportGenerator(use_llm=True)` path in `generator.py` is tested with a mock LLM client
- [ ] `generate-llm-report` output files are in the same path structure as `generate-report` (after STORY-181 fixes nesting)

---

## Implementation Note

```python
# cli.py — replace broken import with:
from .exporters.markdown.generator import ReportGenerator

# In generate_llm_report command:
@cli.command("generate-llm-report")
@click.argument("company_name")
@click.option("-o", "--output", default="output", type=click.Path())
@click.option("--no-llm", is_flag=True, help="Disable LLM, use template fallback")
def generate_llm_report(company_name, output, no_llm):
    loader = UnifiedCompanyLoader()          # After STORY-171
    companies = loader.load_companies()
    scorer = GrowthScorer()
    scored = [scorer.calculate_scores(c) for c in companies]
    target = find_company(scored, company_name)  # helper for name matching

    generator = ReportGenerator(
        output_dir=Path(output),
        use_llm=not no_llm
    )
    reports = generator.generate_company_reports(target)
    click.echo(f"Generated {len(reports)} reports in {output}/")
```

---

## Definition of Done

- [ ] `generate-llm-report` runs end-to-end without crash
- [ ] `--no-llm` flag tested and produces output
- [ ] LLM fallback tested (mock LLM client returning empty string triggers template)
- [ ] Unit tests in `tests/unit/test_cli_llm_report.py`
- [ ] Manual run log showing LLM provider selected (or graceful fallback)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `ReportGenerator(use_llm=True)` path is incomplete | Medium | High | Read generator.py thoroughly before implementing |
| LLM API call fails during test | High | Low | Always test with `--no-llm` first |
| LLM produces garbled narrative | Medium | Medium | Add output length + structure validation |

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Discovered via live execution of `generate-llm-report "Eneve"` |

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
