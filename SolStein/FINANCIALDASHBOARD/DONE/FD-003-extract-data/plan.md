# FD-003: Extract Additional Data from Source Markdown

## Objective

Extract rich data fields from the competitor `financial-growth.md` files that are currently ignored by the extraction pipeline. These new fields enable the Efficiency & Profitability sheet (FD-004), enrich existing sheets, and provide deeper board-level insights.

**In Scope**: Extracting profitability metrics (EBITDA margin, revenue/employee), funding details (lead investors, war chest signals), geographic indicators (international revenue %, countries count), and SaaS metrics (cloud revenue %, deployment model) from existing markdown source files. Adding corresponding accessor functions in `competitor_utils.py`.

**Out of Scope**: Modifying the Excel report generator (`generate_excel_report.py`), adding new sheets, changing existing JSON schema structure, or updating downstream consumers of the extracted data. Those are handled by FD-004 and FD-005.

## Requirements

1. **Profitability Extraction Enhancement**: Parse structured EBITDA margin (float/null) and revenue per employee (float/null) from the profitability metrics table in `financial-growth.md` files.
2. **Funding Extraction Enhancement**: Extract lead investor names (list of strings) from funding rounds table and war chest signals text (string/null) from the corresponding subsection.
3. **Geographic Extraction (New)**: Extract international revenue percentage (float/null) and count of unique countries (int/null) from the Geographic & Market Expansion section.
4. **SaaS Metrics Extraction (New)**: Extract cloud revenue percentage (float/null) and deployment model classification (string/null: "SaaS"/"Hybrid"/"On-Premise") from the SaaS Transition Metrics section.
5. **Accessor Functions**: Provide convenience accessor functions in `competitor_utils.py` for all newly extracted fields.
6. **Backward Compatibility**: All existing extraction output must remain unchanged -- new fields are additive only.
7. **Graceful Handling of Missing Data**: All new fields must default to `None`/`null` when the source section or data point is absent. No exceptions on missing data.

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Multiple new extraction functions plus enhancements to two existing functions across 2 files. Regex-based markdown parsing introduces edge-case risk, and the variety of data formats (percentages, currency, lists) requires careful handling. Estimated >10 lines of new code.

**Criteria Met**:
- Root Cause: Multiple (4 distinct data categories to extract: profitability, funding, geographic, SaaS)
- Files Affected: 2 (`extract_competitor_data.py`, `competitor_utils.py`)
- Lines Changed: >50 (new functions + enhancements + accessors)
- Risk Level: Medium (regex parsing of varied markdown formats, edge cases in data representation)
- Solution Pattern: Known (extends existing extraction pattern, familiar regex approach)

**Effort**: 2-3 hours

## Acceptance Criteria

- [ ] **Profitability (structured)**:
  - `ebitda_margin_pct` extracted (float or null) -- from profitability table "EBITDA Margin" row
  - `revenue_per_employee_eur_k` extracted (float or null) -- from profitability table "Revenue per Employee" row
- [ ] **Funding (structured)**:
  - `lead_investors` extracted (list of strings) -- from funding rounds table "Lead Investor(s)" column
  - `war_chest_signals` extracted (string or null) -- from "War Chest Signals" subsection text
- [ ] **Geographic**:
  - `international_revenue_pct` extracted (float or null) -- from Geographic section
  - `countries_count` extracted (int or null) -- count of unique countries from expansion events
- [ ] **SaaS (structured)**:
  - `cloud_revenue_pct` extracted (float or null) -- from SaaS Transition Metrics section
  - `deployment_model` extracted (string or null) -- "SaaS" / "Hybrid" / "On-Premise"
- [ ] New accessor functions added to `competitor_utils.py`
- [ ] All existing extraction still works (no regressions)
- [ ] JSON output includes new fields
- [ ] Script compiles clean

## Implementation Approach

### 1. New Extraction Functions in `extract_competitor_data.py`

#### Profitability Enhancement

Current: `extract_profitability()` stores `raw_metrics` dict and `recurring_revenue_pct`.

Add parsing of specific metrics from `raw_metrics`:

```python
def extract_profitability(text: str) -> dict:
    # ... existing code ...
    
    # Parse structured metrics from raw_metrics
    ebitda_margin = None
    revenue_per_employee = None
    for key, val in result["raw_metrics"].items():
        key_lower = key.lower()
        if "ebitda margin" in key_lower:
            ebitda_margin = parse_number(val)
        elif "revenue per employee" in key_lower:
            revenue_per_employee = parse_number(val)
    
    result["ebitda_margin_pct"] = ebitda_margin
    result["revenue_per_employee_eur_k"] = revenue_per_employee
    return result
```

#### Funding Enhancement

Current: `extract_funding()` stores rounds, total_raised_text, latest_valuation_text.

Add lead investor extraction and war chest signals:

```python
def extract_funding(text: str) -> dict:
    # ... existing code ...
    
    # Extract lead investors from rounds
    lead_investors = set()
    for round_data in result["rounds"]:
        investors_text = round_data.get("lead_investors", "")
        if investors_text and investors_text not in ("N/A", "—", "-", ""):
            for inv in investors_text.split(","):
                lead_investors.add(inv.strip())
    result["lead_investors"] = sorted(lead_investors)
    
    # Extract war chest signals
    war_chest_match = re.search(r"(?:War Chest Signals|Investment Capacity)(.*?)(?=\n##|\n\*\*|\Z)", text, re.DOTALL | re.IGNORECASE)
    result["war_chest_signals"] = war_chest_match.group(1).strip() if war_chest_match else None
    
    return result
```

#### New: Geographic Extraction

Currently not extracted at all. Add new function:

```python
def extract_geographic(text: str) -> dict:
    result = {
        "international_revenue_pct": None,
        "countries_count": None,
        "expansion_events": [],
    }
    
    # Find Geographic & Market Expansion section
    geo_section = extract_section(text, "Geographic")
    if not geo_section:
        return result
    
    # Parse international revenue %
    intl_match = re.search(r"International Revenue[^:]*:\s*([\d.]+)\s*%", geo_section, re.IGNORECASE)
    if intl_match:
        result["international_revenue_pct"] = float(intl_match.group(1))
    
    # Count unique countries from expansion events table
    countries = set()
    for row in parse_markdown_table(geo_section):
        event = row.get("Event", row.get("Details", ""))
        # Extract country names from event descriptions
        # This is heuristic -- look for known patterns
    result["countries_count"] = len(countries) if countries else None
    
    return result
```

#### New: SaaS Metrics Extraction

Currently not extracted. Add new function:

```python
def extract_saas_metrics(text: str) -> dict:
    result = {
        "cloud_revenue_pct": None,
        "deployment_model": None,
    }
    
    saas_section = extract_section(text, "SaaS Transition")
    if not saas_section:
        return result
    
    # Deployment model
    deploy_match = re.search(r"Deployment Model[^:]*:\s*(.+)", saas_section, re.IGNORECASE)
    if deploy_match:
        model = deploy_match.group(1).strip().rstrip("|").strip()
        result["deployment_model"] = model
    
    # Cloud revenue %
    cloud_match = re.search(r"Cloud Revenue[^:]*:\s*([\d.]+)\s*%", saas_section, re.IGNORECASE)
    if cloud_match:
        result["cloud_revenue_pct"] = float(cloud_match.group(1))
    
    return result
```

### 2. Wire into Main Extraction

In `extract_competitor()`, add calls to new functions and merge results:

```python
competitor["geographic"] = extract_geographic(text)
competitor["saas"] = extract_saas_metrics(text)
# profitability and funding already extracted, just enhanced
```

### 3. New Accessor Functions in `competitor_utils.py`

```python
def get_ebitda_margin(competitor: dict) -> Optional[float]:
    return competitor.get("profitability", {}).get("ebitda_margin_pct")

def get_revenue_per_employee(competitor: dict) -> Optional[float]:
    return competitor.get("profitability", {}).get("revenue_per_employee_eur_k")

def get_deployment_model(competitor: dict) -> Optional[str]:
    return competitor.get("saas", {}).get("deployment_model")

def get_cloud_revenue_pct(competitor: dict) -> Optional[float]:
    return competitor.get("saas", {}).get("cloud_revenue_pct")

def get_international_revenue_pct(competitor: dict) -> Optional[float]:
    return competitor.get("geographic", {}).get("international_revenue_pct")
```

## Testing Strategy

1. `python -m py_compile extract_competitor_data.py`
2. Run extraction on a few known competitors and verify new fields appear in JSON
3. Spot-check values against source `financial-growth.md` files
4. Verify existing fields are unchanged (no regression)
5. Run `generate_excel_report.py` to ensure it still works with enriched data

## Risks

- **Inconsistent markdown formats**: Different competitors may format the same section differently. Use flexible regex patterns and handle None gracefully.
- **Parse errors on edge cases**: Some fields may have text like "~15%" or "EUR 200K" -- `parse_number()` should handle these.
- **New sections may not exist**: Many competitors may lack Geographic or SaaS sections entirely. Always default to None.

## Dependencies

None (enhances extraction independently). FD-004 depends on this ticket's output.

## Status

**Current**: Implementation Complete
