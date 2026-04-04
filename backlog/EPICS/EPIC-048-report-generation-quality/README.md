# EPIC-048: Report Generation Quality

> **Discovered**: 2026-03-01 via live end-to-end run analysis  
> **Priority**: P1 — High (primary user-facing output is low quality)  
> **Stories**: 5 ([STORY-181](STORIES/STORY-181.md) through [STORY-185](STORIES/STORY-185.md))  > **Effort**: M–L (4–6 days total)

---

## Problem

The `generate-report` command produces 5 report files per company, but 3 of them are written to the wrong nested path (`eneve/eneve/` instead of `eneve/`), and the content quality is poor: scores are unrounded (`7.138888...`), market counters are always zero, and deep analysis sections contain boilerplate like "No critical weaknesses identified" regardless of actual data.

### Report Output Issues for Eneve

| Report | Path | Size | Issues |
|--------|------|------|--------|
| `competitive-analysis.md` | `eneve/` | 2,230 bytes | ✅ Correct path, good content |
| `market_overview.md` | `eneve/` | 1,162 bytes | ❌ Phoenix/Salt/Lead counters all 0 |
| `financial-growth.md` | `eneve/eneve/` (wrong) | 333 bytes | ❌ "No funding data", unrounded scores |
| `deep-analysis.md` | `eneve/eneve/` (wrong) | 701 bytes | ❌ "No critical weaknesses", boilerplate |
| `corporate-history.md` | `eneve/eneve/` (wrong) | 823 bytes | ❌ Generic content |

---

## Stories

| Story | Title | Priority | Size |
|-------|-------|----------|------|
| [STORY-181](STORIES/STORY-181.md) | Fix report output path nesting bug | P1 | S |
| [STORY-182](STORIES/STORY-182.md) | Round all score outputs to 2 decimal places | P1 | S |
| [STORY-183](STORIES/STORY-183.md) | Fix market overview classification counters | P1 | S |
| [STORY-184](STORIES/STORY-184.md) | Replace boilerplate deep analysis with actual signal-based weaknesses | P1 | M |
| [STORY-185](STORIES/STORY-185.md) | Add report content quality assertions to tests | P2 | M |

---

## Definition of Done

- [ ] All 5 report types written to correct path (`output/{company}/` not `output/{company}/{company}/`)
- [ ] All scores rounded to 2 decimal places in all reports
- [ ] Market overview shows correct Phoenix/Salt/Lead counts
- [ ] Deep analysis derives actual weaknesses from company signals, not boilerplate
- [ ] Tests verify report content quality (not just file existence)
