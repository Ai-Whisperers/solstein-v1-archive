# STORY-214: Add Gate Evaluation Metadata to Export Output

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-060 Export & Release Gate Decoupling |
| **Created** | 2026-03-01 |
| **Risk** | Low — adds metadata; no logic change |
| **Assigned** | — |
| **Depends On** | STORY-212 (Gate Refactor) |

---

## Audit Verdict

**CONFIRMED MISSING** — Excel export contains no information about gate evaluation or data quality assessment.

Current output: Companies with scores, nothing else.

Missing: Gate evaluation results, data quality indicators, threshold information.

---

## Problem Statement

When an analyst opens the Excel export, they don't know:
- Whether data quality gates passed
- What the completeness score was
- What thresholds were used
- Why scores are lower than expected

Adding gate metadata to export makes the data quality story transparent.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Explainability | 🟡 Medium — Users don't understand data quality |
| Transparency | 🟡 Medium — No visibility into gate evaluation |
| Auditability | 🟡 Medium — No record of what gates were checked |

---

## Affected Files

| File | Lines | Change Type |
|-------|-------|-------------|
| `src/solstein/exporters/excel_exporter.py` | Excel generation | Add gate metadata sheet |
| `scripts/run_eneve_199.py` | Export call | Pass gate result to exporter |

---

## Dependencies

- **Hard**: STORY-212 (Gate Refactor to return detailed result)
- **Blocks**: Nothing

---

## Architectural Requirements

**REQ-1**: Excel export includes new sheet "Data Quality" with:
- Gate evaluation timestamp
- Overall gate status (PASS/FAIL)
- Completeness score (%)
- Data quality score (%)
- Thresholds used
- Warning messages (if any)

**REQ-2**: Main scores sheet includes confidence column (from STORY-208).

**REQ-3**: Export remains backward compatible (existing sheets unchanged).

---

## Acceptance Criteria

- [ ] Excel export has "Data Quality" sheet
- [ ] Gate result metadata stored in sheet
- [ ] Timestamp of gate evaluation included
- [ ] All threshold values documented
- [ ] Warning messages (if any) included
- [ ] Main scores sheet has confidence column
- [ ] Manual test: Open export → data quality information visible
- [ ] Backward compatibility verified (old sheets unchanged)

---

## Definition of Done

- [ ] Gate metadata sheet created
- [ ] All gate results documented
- [ ] Confidence column added to scores
- [ ] Export backward compatible
- [ ] Manual verification complete

---

## Implementation Notes

### Data Quality Sheet Structure

| Field | Value |
|-------|-------|
| **Gate Evaluation** | |
| Timestamp | 2026-03-01 10:30:00 |
| Overall Status | PASS |
| Passed to Export | YES |
| | |
| **Scores** | |
| Completeness | 92% |
| Data Quality | 88% |
| Overall | 90% |
| | |
| **Thresholds** | |
| Completeness Threshold | 50% |
| Data Quality Threshold | 60% |
| | |
| **Issues Found** | |
| 1. | growth_rate missing for 3 companies |
| 2. | profit_margin confidence < 0.65 for 5 companies |

### Code Pattern

```python
def export_with_gate_metadata(
    companies: List[Company],
    scores: List[ScoreResult],
    gate_result: GateResult,
    output_file: str
):
    wb = openpyxl.Workbook()
    
    # Add existing sheets (companies, scores, etc.)
    add_scores_sheet(wb, scores)
    
    # Add gate metadata sheet
    ws_quality = wb.create_sheet("Data Quality", 0)
    ws_quality['A1'] = "Gate Evaluation Metadata"
    ws_quality['A2'] = f"Timestamp: {datetime.now().isoformat()}"
    ws_quality['A3'] = f"Overall Status: {'PASS' if gate_result.passed else 'FAIL'}"
    ws_quality['A4'] = f"Completeness: {gate_result.completeness_score:.1f}%"
    ws_quality['A5'] = f"Data Quality: {gate_result.data_quality_score:.1f}%"
    
    # Add threshold info
    row = 7
    ws_quality[f'A{row}'] = "Thresholds Used:"
    for key, value in gate_result.thresholds.items():
        row += 1
        ws_quality[f'A{row}'] = f"  {key}: {value}"
    
    # Add messages/warnings
    if gate_result.messages:
        row += 2
        ws_quality[f'A{row}'] = "Messages:"
        for msg in gate_result.messages:
            row += 1
            ws_quality[f'A{row}'] = f"  {msg}"
    
    wb.save(output_file)
```

### Files to Create/Modify

- `src/solstein/exporters/excel_exporter.py` - Add gate metadata sheet
- `scripts/run_eneve_199.py` - Pass gate result to exporter

### Risk Mitigation

- Sheet might be confusing → Use clear layout and headers
- Users might not understand thresholds → Add explanatory text
- Export size might increase → Metadata is minimal

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Excel export lacks data quality metadata |

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
