# STORY-303: Expand capability keyword lists with 20+ synonyms per capability

| Field | Value |
|-------|-------|
| **Epic** | EPIC-076 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Expand capability keyword lists in `intelligence/capability_overlap.py` to include 20+ synonyms per Eneve capability. Examples: smart meter→AMI, meter data management, MDM; balancing→imbalance settlement, TSO allocation, ancillary services.

## Acceptance Criteria

- [ ] Each of 8 capabilities has ≥ 20 keyword synonyms
- [ ] Keywords include industry abbreviations and full forms
- [ ] Existing tests still pass
- [ ] New test: known competitor correctly matches ≥ 3 capabilities
