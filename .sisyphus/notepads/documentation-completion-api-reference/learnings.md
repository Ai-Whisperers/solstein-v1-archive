# Documentation Completion - Learnings

## Task 2: Core Endpoints (Companies, Scoring, Market)

### Key Findings from Code Verification

1. **Classification threshold is 3.9, not 4.0**
   - `scoring.py` line 63: `elif growth_score <= 3.9:` → Lead
   - This means growth_score = 4.0 is "Salt", not "Lead"
   - The existing docs had this wrong in the threshold table

2. **Companies router has NO prefix** in main.py (line 135)
   - Paths are `/companies`, `/companies/{company_id}` directly
   - Scoring has `/scoring` prefix, Market has `/market` prefix

3. **Market overlap has no `top_n` query parameter**
   - Hard-coded to return top 10 results (market.py line 98: `overlaps[:10]`)
   - The existing docs incorrectly listed `top_n` as a query parameter

4. **Scoring batch has dual response format**
   - Temporal workflow path returns: status, workflow_id, message, filters
   - Synchronous fallback returns: processed_count, status, message, filters
   - Both need documenting

5. **`founder_names` field does NOT exist in Company model**
   - The spec curl example included it, but Pydantic silently ignores extra fields
   - Removed from curl example in documentation

6. **Company model default values from code**
   - industry defaults to "Energy Software" (not null)
   - tier defaults to "Tier 3"
   - saas_maturity defaults to 1

## Task 6: Getting Started Guide (2026-02-26)

### Patterns
- Getting-started guides work best with persona-based reading paths (API user, developer, operator, business)
- Estimated reading times help readers prioritize which docs to read
- A "Common Tasks" section with quick copy-paste commands provides immediate value
- Using relative links (`../PITCH/...`) keeps docs portable across hosting environments

### Conventions Found
- All guides in docs/guides/ use emoji prefixes in titles (🚀, 📜, ⚡, 🏥, 🚨, 🔄, 🔌, 🔧)
- Guides include Phase/Status/Last Updated metadata headers
- Guides use horizontal rules (---) as section dividers
- The project has 4 personas: API users, developers, operators, business stakeholders

### Key Files
- 20 unique documentation files linked from getting-started.md
- docs/guides/ contains 16 guide files (including new getting-started.md)
- docs/ has 4 subdirectories: api/, architecture/, guides/, PITCH/, LORE/
