# EPIC-005: Fix Excel Export System

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 5 story points
## Sprint: Must be completed before production use

---

## Problem Statement

The Excel export system has **multiple critical bugs** that prevent correct data display and make the output difficult to use.

### Current Broken State
```python
# Line 266-267 in excel.py - WRONG FIELD ACCESS
f"{p.profit_margin:.1f}%"      # p.profit_margin = None (always)
f"{p.ebitda_margin:.1f}%"      # p.ebitda_margin = None (always)
# Should be: p.financials.profit_margin

# Result: Margin columns always show "N/A"
```

### Additional Issues
- **Headers on row 3** instead of row 0 - breaks standard parsing
- **Inconsistent header rows** across sheets (row 4 vs row 5)
- **Magic numbers** throughout (40, 50, etc.)
- **Division by zero risk** in lines 269-270
- **Only 5 sheets** instead of expected 7

### Impact
- **Margin columns always "N/A"** - critical financial data missing
- **Cannot parse with pandas** without skiprows=3
- **Inconsistent formatting** across sheets
- **Potential runtime errors** from division by zero

---

## Success Criteria

- [ ] profit_margin and ebitda_margin display correctly in Excel
- [ ] Headers on row 0 for standard parsing compatibility
- [ ] Consistent header placement across all sheets
- [ ] No division by zero errors
- [ ] Magic numbers replaced with named constants
- [ ] All 7 expected sheets present (if applicable)
- [ ] Excel file passes data validation

---

## Technical Analysis

### Root Causes
1. **Wrong field access pattern** - using company.field instead of company.financials.field
2. **Header row placement** - title rows push headers to row 3
3. **Inconsistent formatting** - different sheets use different row offsets
4. **Missing null checks** - no validation before division

### Affected Files
- `src/solstein/exporters/excel.py` (main issue)
- `src/solstein/exporters/markdown/` (related exporters)

---

## Stories

### Story 5.1: Fix Field Access in Excel Export
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix profit_margin and ebitda_margin field access to use correct nested path.

**Acceptance Criteria:**
- [ ] Change `p.profit_margin` to `p.financials.profit_margin`
- [ ] Change `p.ebitda_margin` to `p.financials.ebitda_margin`
- [ ] Verify margins display correctly in Excel
- [ ] Test with companies that have/don't have margin data
- [ ] Handle None values gracefully (show "N/A")

**Implementation:**
```python
# OLD (broken):
ws.cell(row=row, column=6, value=f"{p.profit_margin:.1f}%" if p.profit_margin else "N/A")
ws.cell(row=row, column=7, value=f"{p.ebitda_margin:.1f}%" if p.ebitda_margin else "N/A")

# NEW (fixed):
profit_margin = p.financials.profit_margin if p.financials else None
ebitda_margin = p.financials.ebitda_margin if p.financials else None
ws.cell(row=row, column=6, value=f"{profit_margin:.1f}%" if profit_margin else "N/A")
ws.cell(row=row, column=7, value=f"{ebitda_margin:.1f}%" if ebitda_margin else "N/A")
```

---

### Story 5.2: Fix Header Row Placement
**Priority:** P0 | **Effort:** 2 points

**Description:**
Move headers to row 0 for standard parsing compatibility, or document the offset.

**Acceptance Criteria:**
- [ ] Headers start on row 0 (or row 1 if title needed)
- [ ] Consistent across all sheets
- [ ] Update any code that reads the Excel file
- [ ] Document header row location in README
- [ ] Provide pandas read example

**Options:**

**Option A: Move headers to row 0**
```python
# Remove title rows, start with headers immediately
headers = ["Company", "Score", ...]
for col, header in enumerate(headers, 1):
    ws.cell(row=1, column=col, value=header)  # Row 1 (0-indexed: row 0)
```

**Option B: Keep headers on row 3, document clearly**
```python
# Add prominent documentation
"""
NOTE: This Excel file has headers on row 4 (index 3).
To read with pandas:
    df = pd.read_excel('file.xlsx', sheet_name='Market Rankings', skiprows=3)
"""
```

**Recommendation:** Option A - move headers to row 0 for standard compatibility.

---

### Story 5.3: Add Null Checks and Error Handling
**Priority:** P0 | **Effort:** 1 point

**Description:**
Add validation to prevent division by zero and handle missing data gracefully.

**Acceptance Criteria:**
- [ ] Check for zero before division in lines 269-270
- [ ] Handle None values in all numeric formatting
- [ ] Add try/except around risky operations
- [ ] Log errors for debugging
- [ ] Show "N/A" for invalid/missing data

**Implementation:**
```python
# OLD (risky):
f"{(p.recurring_revenue_pct or 0):.0f}%"
f"{(p.revenue_per_employee_eur_k or 0):.0f}K"

# NEW (safe):
recurring = p.financials.recurring_revenue_pct if p.financials else None
rev_per_emp = p.financials.revenue_per_employee if p.financials else None

recurring_str = f"{recurring:.0f}%" if recurring is not None else "N/A"
rev_per_emp_str = f"{rev_per_emp:.0f}K" if rev_per_emp is not None else "N/A"
```

---

### Story 5.4: Replace Magic Numbers with Constants
**Priority:** P1 | **Effort:** 1 point

**Description:**
Replace hardcoded numbers with named constants for maintainability.

**Acceptance Criteria:**
- [ ] Define constants for row heights, column widths
- [ ] Replace all magic numbers in excel.py
- [ ] Document what each constant controls
- [ ] Make constants configurable if appropriate

**Implementation:**
```python
# In excel.py or constants.py
EXCEL_CONSTANTS = {
    "TITLE_ROW_HEIGHT": 40,
    "HEADER_ROW_HEIGHT": 30,
    "DATA_ROW_HEIGHT": 25,
    "MAX_COLUMN_WIDTH": 50,
    "MIN_COLUMN_WIDTH": 10,
    "DEFAULT_COLUMN_WIDTH": 20,
    "HEADER_ROW": 1,  # 1-indexed for openpyxl
    "DATA_START_ROW": 2,
}

# Usage
ws.row_dimensions[1].height = EXCEL_CONSTANTS["TITLE_ROW_HEIGHT"]
ws.column_dimensions["A"].width = min(
    max_length + 2, 
    EXCEL_CONSTANTS["MAX_COLUMN_WIDTH"]
)
```

---

### Story 5.5: Standardize Sheet Structure
**Priority:** P1 | **Effort:** 1 point

**Description:**
Ensure all sheets have consistent structure and formatting.

**Acceptance Criteria:**
- [ ] All sheets use same header row placement
- [ ] All sheets use same title format
- [ ] Column widths consistent across sheets
- [ ] Cell formatting consistent (fonts, colors, alignment)
- [ ] Create helper function for consistent sheet setup

**Implementation:**
```python
def setup_sheet_header(ws, title, headers):
    """Standardized sheet header setup."""
    # Title row
    ws.cell(row=1, column=1, value=f"SOLSTEIN | {title}")
    ws.row_dimensions[1].height = EXCEL_CONSTANTS["TITLE_ROW_HEIGHT"]
    
    # Headers row
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")
    
    ws.row_dimensions[2].height = EXCEL_CONSTANTS["HEADER_ROW_HEIGHT"]
    
    return 3  # Return data start row
```

---

## Dependencies

- Story 5.1 is critical - must be done first
- Stories 5.2 and 5.3 can be done in parallel
- Stories 5.4 and 5.5 are improvements (P1)

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Changing headers breaks existing parsers | High | Version the export format, document changes |
| Field access fixes affect other exporters | Medium | Test all exporters after changes |
| Excel formatting changes affect readability | Low | User acceptance testing |

## Definition of Done

- [ ] profit_margin and ebitda_margin display correctly
- [ ] Headers on consistent row across all sheets
- [ ] No division by zero errors in testing
- [ ] Magic numbers replaced with constants
- [ ] Excel file passes data validation
- [ ] Pandas can read file without skiprows parameter
- [ ] Documentation updated with Excel format spec
