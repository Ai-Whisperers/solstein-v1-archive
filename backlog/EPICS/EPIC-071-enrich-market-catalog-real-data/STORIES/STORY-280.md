# STORY-280: Add GitHub org names where applicable

| Field | Value |
|-------|-------|
| **Epic** | EPIC-071 |
| **Priority** | P1 |
| **Size** | XS |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Add GitHub organization names to catalog companies that have a public GitHub presence. This enables the GitHub enrichment adapter (STORY-290) to detect tech stack and open source activity.

## Acceptance Criteria

- [ ] All catalog companies with a GitHub presence have a `github_org` field
- [ ] Org names resolve to valid github.com/org-name pages
- [ ] Companies without GitHub have `github_org = None`

## Technical Notes

- File: `src/solstein/data/market_catalogs.py`
- Pure data entry — no logic changes
