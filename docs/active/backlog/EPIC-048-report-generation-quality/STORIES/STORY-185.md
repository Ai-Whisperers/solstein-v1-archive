# STORY-185: Add Report Content Quality Assertions to Tests

| Field | Value |
|-------|-------|
| **Status** | 🟡 Open |
| **Priority** | P2 — Medium |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-048 Report Generation Quality |
| **Created** | 2026-03-01 |
| **Risk** | Low — additive tests |
| **Assigned** | — |

---

## Audit Verdict

**TEST GAP** — no existing tests verify report content quality.

Current tests (if any) likely check:
- File exists: `assert report_path.exists()`
- Non-empty: `assert report_path.stat().st_size > 0`

They do NOT check:
- Scores are rounded (not `7.138888...`)
- Market counters are correct (not all zeros)
- No boilerplate text (not "No critical weaknesses identified")
- All expected sections are present
- Content is derived from actual company data

---

## Problem Statement

The bugs in STORY-181 (path nesting), STORY-182 (unrounded scores), STORY-183 (zero counters), and STORY-184 (boilerplate) all passed through CI because tests only check file existence, not content quality. A test that asserts `"7.14" in report_content` would have caught the unrounded score bug. A test that asserts `"Phoenix Tier: 1" in report_content` would have caught the counter bug.

Content quality tests are essential to prevent regression of these issues.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Test Coverage | 🟠 High — critical user-facing output not validated |
| Regression Prevention | 🟠 High — bugs will reoccur without content assertions |
| Code Quality | 🟡 Medium — forces maintainable report structure |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `tests/unit/test_report_content.py` | New (~200 lines) | Content quality tests |
| `tests/unit/test_report_paths.py` | New | Path/nesting tests |
| `.github/workflows/ci.yml` | Optional | Ensure tests run in CI |

---

## Dependencies

- **Hard**: STORY-181, 182, 183, 184 (fixes must land first so tests pass)
- **Soft**: None
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: Create `tests/unit/test_report_content.py` with tests for each report type:

```python
class TestCompetitiveAnalysisReport:
    def test_scores_are_rounded(self, generated_report):
        content = generated_report.read_text()
        # No 7.138888... patterns
        assert not re.search(r"\d+\.\d{3,}", content)
        # Scores present with 2 decimals
        assert "7.14" in content or "7.13" in content  # rounded competitive_position
    
    def test_no_boilerplate_weaknesses(self, generated_report):
        content = generated_report.read_text()
        assert "No critical weaknesses identified" not in content
    
    def test_actual_weaknesses_present(self, generated_report):
        content = generated_report.read_text()
        assert "Tier 4" in content or "Undercapitalized" in content

class TestMarketOverviewReport:
    def test_classification_counters_correct(self, generated_report, companies):
        phoenix_count = sum(1 for c in companies if c.classification == "Phoenix")
        content = generated_report.read_text()
        assert f"Phoenix Tier: {phoenix_count}" in content
```

**REQ-2**: Create `tests/unit/test_report_paths.py`:
```python
def test_reports_not_nested(output_dir, company_name):
    # Should be output/eneve/*.md not output/eneve/eneve/*.md
    nested_path = output_dir / company_name / company_name
    assert not nested_path.exists() or len(list(nested_path.glob("*.md"))) == 0
```

**REQ-3**: Use pytest fixtures to generate reports once and test content across multiple assertions (performance).

**REQ-4**: Tests must fail with clear messages showing expected vs actual content snippets.

---

## Acceptance Criteria

- [ ] `test_report_content.py` exists and passes after STORY-181/182/183/184 fixes
- [ ] `test_report_paths.py` exists and passes
- [ ] Tests verify: rounded scores, correct counters, no boilerplate, actual weaknesses present
- [ ] CI runs these tests on every PR
- [ ] A deliberate regression (e.g., unrounded score) causes test failure with clear diff

---

## Definition of Done

- [ ] Content quality test module created
- [ ] Path test module created
- [ ] Tests run in CI
- [ ] Documentation in test file explains how to add new content assertions

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Identified gap: no content validation in existing tests |
