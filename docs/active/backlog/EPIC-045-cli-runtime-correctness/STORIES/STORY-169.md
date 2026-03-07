# STORY-169: Fix JSON Parsing in `score`, `analyze-market`, `compare`, `export-excel` CLI Commands

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 — Critical |
| **Size** | S (< 1 day) |
| **Epic** | EPIC-045 CLI Runtime Correctness |
| **Created** | 2026-03-01 |
| **Risk** | Low — surgical 3-line fix with no logic change |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED BUG** — verified by live execution on 2026-03-01.

```python
# src/solstein/cli.py — lines 126–127 (score command)
data = json.loads(input_file.read_text())
domain_companies = [Company(**item) for item in data]  # BUG
```

When `data = {"competitors": [...]}` (a dict), `for item in data` iterates over dict keys (`"competitors"`, etc.) — strings, not dicts. `Company(**"competitors")` raises:

```
TypeError: solstein.domain.models.Company() argument after ** must be a mapping, not str
```

The identical pattern appears in 4 commands:
- `score` — `cli.py:126`
- `analyze-market` — `cli.py:~200`
- `compare` — `cli.py:~250`
- `export-excel` — `cli.py:~180`

---

## Problem Statement

The primary input file `data/input/competitor_data.json` uses a wrapper object format `{"competitors": [...]}`. All JSON-consuming CLI commands use `[Company(**item) for item in data]` which works only if `data` is a flat list. Every JSON file in the project uses the wrapper format — the flat-list assumption is incorrect and was never valid against real data.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Reliability | 🔴 Critical — 4 commands 100% unusable |
| User Experience | 🔴 Critical — no useful error message, raw Python traceback shown |
| Security | ⬜ None |
| Performance | ⬜ None |
| Maintainability | 🟡 Medium — pattern repeated in 4 places |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/cli.py` | ~126, ~180, ~200, ~250 | Bug fix |
| `tests/unit/test_cli.py` | New | New test |

---

## Dependencies

- **Hard**: None
- **Soft**: STORY-171 (loader migration — once migrated, this pattern is replaced entirely)
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: JSON loading must support both `[...]` (flat list) and `{"competitors": [...]}` (wrapped object) formats — the same file format used by every other part of the codebase.

**REQ-2**: The fix must be applied consistently in all 4 affected commands — no partial fixes.

**REQ-3**: If the JSON structure is unrecognized (neither a list nor a dict with a known key), raise a `click.UsageError` with a clear message showing the expected format.

---

## Acceptance Criteria

- [ ] `python -m solstein.cli score data/input/competitor_data.json` completes without error and writes scored output
- [ ] `python -m solstein.cli analyze-market data/input/competitor_data.json` completes without error
- [ ] `python -m solstein.cli compare "Eneve" "Test Company 2" --input data/input/competitor_data.json` completes without error
- [ ] `python -m solstein.cli export-excel data/input/competitor_data.json` completes without error
- [ ] All 4 commands also work correctly with a flat-list JSON `[{"name": ...}, ...]`
- [ ] Unrecognized JSON format shows `UsageError: Expected a JSON list or {"competitors": [...]} object`
- [ ] Unit tests added covering both JSON formats for at least the `score` command

---

## Implementation Note

```python
# Fix pattern — apply to all 4 commands:
raw = json.loads(input_file.read_text())
if isinstance(raw, dict):
    # Support {"competitors": [...]} and {"companies": [...]} wrappers
    items = raw.get("competitors") or raw.get("companies") or raw.get("data")
    if items is None:
        raise click.UsageError(
            f"JSON file must be a list [...] or a dict with 'competitors' key. "
            f"Got dict with keys: {list(raw.keys())}"
        )
elif isinstance(raw, list):
    items = raw
else:
    raise click.UsageError("Expected a JSON array or wrapped object")

domain_companies = [Company(**item) for item in items]
```

---

## Definition of Done

- [ ] All 4 commands fixed and manually tested against `data/input/competitor_data.json`
- [ ] Unit tests: `tests/unit/test_cli_json_parsing.py` covering both formats + invalid input
- [ ] No new `DeprecationWarning` introduced
- [ ] Code review: fix reviewer checks all 4 command sites are updated

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Fix misses one of 4 occurrences | Low | High | Grep for pattern before marking done |
| Flat-list format needed elsewhere | Low | Low | Test both formats in unit test |

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Discovered via live execution of `score` command |
