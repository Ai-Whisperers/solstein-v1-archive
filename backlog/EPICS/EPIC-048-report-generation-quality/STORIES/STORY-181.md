# STORY-181: Fix Report Output Path Nesting Bug

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | S (< half a day) |
| **Epic** | EPIC-048 Report Generation Quality |
| **Created** | 2026-03-01 |
| **Risk** | Low — path construction fix |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED BUG** — verified by live execution on 2026-03-01.

```
Expected: /tmp/eneve_report/eneve/financial-growth.md
Actual:   /tmp/eneve_report/eneve/eneve/Eneve_financial_growth.md
```

The `generate-report` command creates a double-nested directory:
1. CLI creates `output_dir / company_name` (e.g., `eneve/`)
2. `ReportGenerator` creates `output_dir / company_name` again inside that (e.g., `eneve/eneve/`)
3. Files are written to the nested path

The CLI then reports "Success ✅" but 3 of 5 report types are in the wrong location.

---

## Problem Statement

The `generate-report` CLI and the `ReportGenerator` class each create a company-named subdirectory. This results in `output/Eneve/Eneve/` nesting. The CLI expects files at `output/Eneve/*.md` but they're at `output/Eneve/Eneve/*.md`.

This breaks:
- User expectations (they look in `output/Eneve/` and find only 2 files)
- Downstream automation (CI jobs, file watchers)
- The `generate-all-reports` command which may have similar issues

---

## Impact

| Dimension | Severity |
|-----------|----------|
| User Experience | 🟠 High — 60% of reports in wrong location |
| Automation | 🟠 High — breaks scripted report consumption |
| Reliability | 🟡 Medium — files exist but in wrong place |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/cli.py` | `generate_report` command | Remove redundant directory creation |
| `src/solstein/exporters/markdown/generator.py` | `ReportGenerator.__init__` or `generate_company_reports` | Ensure single directory level |
| `tests/unit/test_report_generator.py` | Existing or new | Verify correct path |

---

## Dependencies

- **Hard**: None
- **Soft**: STORY-170 (generate-llm-report fix) — same path logic applies there
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: The CLI should pass `output_dir` (e.g., `/tmp/eneve_report`) to `ReportGenerator`, not `output_dir / company_name`.

**REQ-2**: `ReportGenerator` should create `output_dir / company_name` internally and write all files there.

**REQ-3**: No nested `company_name/company_name/` directories should be created.

**REQ-4**: The fix must apply to both `generate-report` and `generate-all-reports` commands.

---

## Acceptance Criteria

- [ ] `generate-report "Eneve" -o /tmp/test` creates `/tmp/test/eneve/*.md` (not `/tmp/test/eneve/eneve/*.md`)
- [ ] All 5 report types are in the same directory level
- [ ] `generate-all-reports -o /tmp/all` creates `/tmp/all/{company}/*.md` for each company
- [ ] Unit test: `test_report_paths_not_nested` verifies no double-nesting
- [ ] Manual verification: `ls -R /tmp/test` shows only one level of company-named directory

---

## Implementation Note

```python
# cli.py — BEFORE (bug):
output_path = Path(output) / sanitize_filename(company_name)
output_path.mkdir(parents=True, exist_ok=True)
generator = ReportGenerator(output_dir=output_path)  # ← passes nested path

# cli.py — AFTER (fix):
output_path = Path(output)  # ← just the base output dir
generator = ReportGenerator(output_dir=output_path)  # generator creates company subdir

# generator.py — ensure this creates company subdir:
def generate_company_reports(self, company):
    company_dir = self.output_dir / sanitize_filename(company.name)
    company_dir.mkdir(parents=True, exist_ok=True)
    # ... write files to company_dir
```

---

## Definition of Done

- [ ] Path nesting bug fixed in both `generate-report` and `generate-all-reports`
- [ ] Unit test verifies correct paths
- [ ] Manual run confirms all 5 reports in correct location

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Confirmed via `ls -R` on generated output |

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
