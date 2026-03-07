# STORY-172: Add Structured Input Validation with Actionable Error Messages to All CLI Commands

| Field | Value |
|-------|-------|
| **Status** | 🟡 Open |
| **Priority** | P2 — Medium |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-045 CLI Runtime Correctness |
| **Created** | 2026-03-01 |
| **Risk** | Low — additive change, no existing logic modified |
| **Assigned** | — |

---

## Audit Verdict

**DESIGN GAP** — no input validation layer exists. All errors surface as raw Python tracebacks.

Observed failure modes from live run:
1. `score` with wrong JSON format → `TypeError: argument after ** must be a mapping, not str`
2. `generate-llm-report` → `ModuleNotFoundError`
3. `compare "CompanyA" "CompanyB"` with unknown company name → `StopIteration` (no match found)
4. `generate-report "Nonexistent Co"` → silent empty output directory

---

## Problem Statement

None of the CLI commands validate their inputs before attempting to run. When something goes wrong, users see raw Python tracebacks instead of actionable error messages. For a PE/VC analyst using this tool, a raw `TypeError` traceback is unusable. The CLI should:
1. Validate file paths exist before reading
2. Validate JSON structure before parsing
3. Validate company names exist in the data before processing
4. Report errors as `click.UsageError` or `click.ClickException` — not Python exceptions

---

## Impact

| Dimension | Severity |
|-----------|----------|
| User Experience | 🟠 High — analysts cannot self-diagnose issues |
| Reliability | 🟡 Medium — errors still occur, just presented better |
| Maintainability | 🟡 Medium — validation layer makes testing easier |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Change Type |
|------|-------------|
| `src/solstein/cli.py` | Add validation helpers |
| `src/solstein/cli_validators.py` | New — validation helper module |
| `tests/unit/test_cli_validation.py` | New — test all validation paths |

---

## Dependencies

- **Hard**: STORY-169 (JSON fix must land first so validation tests test the right thing)
- **Soft**: STORY-171 (loader migration)
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: Create `src/solstein/cli_validators.py` with the following validators:

```python
def validate_input_file(path: Path) -> dict | list:
    """Validate file exists, is readable, is valid JSON, has known structure."""

def validate_company_exists(companies: list[Company], name: str) -> Company:
    """Find company by name (case-insensitive substring match). Raise UsageError with suggestions on miss."""

def validate_output_dir(path: Path) -> Path:
    """Create output dir if not exists, check write permission."""
```

**REQ-2**: Error messages must include what was provided, what was expected, and (where possible) suggestions:
```
Error: Company 'Eneve Ltd' not found. 
Available companies: Eneve, Test Company 2, Test Company 3
Did you mean: Eneve?
```

**REQ-3**: File validation must check: path exists, is a file (not dir), size > 0, is valid JSON, has recognizable structure (list or `{"competitors": [...]}`).

**REQ-4**: All existing `try/except Exception as e: click.echo(f"Failed: {e}")` patterns must be replaced with specific exception handlers.

---

## Acceptance Criteria

- [ ] Running any command with a nonexistent input file shows: `Error: Input file 'foo.json' not found.`
- [ ] Running any command with malformed JSON shows: `Error: Invalid JSON in 'foo.json': <parse error location>`
- [ ] `compare "Unknown Co" "Eneve"` shows: `Error: Company 'Unknown Co' not found. Available: [list]`
- [ ] `generate-report "Eneve"` with empty output dir path shows: `Error: Cannot create output directory '/path': <reason>`
- [ ] All error messages exit with non-zero code (for CI/script use)
- [ ] Unit tests cover: missing file, empty file, malformed JSON, unknown company name, unwritable output

---

## Definition of Done

- [ ] `cli_validators.py` created and used by all 8 commands
- [ ] Zero raw Python tracebacks visible to end users for any foreseeable input error
- [ ] Unit tests for all validation paths
- [ ] Manual test: run each command with deliberately bad input, verify messages

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Observed raw tracebacks on all failure modes during live run |
