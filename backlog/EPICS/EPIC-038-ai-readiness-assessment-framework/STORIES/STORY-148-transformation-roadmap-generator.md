# STORY-148: Transformation Roadmap Generator

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-038: AI-Readiness Assessment Framework |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-146 |

## The Strategic Context

> "Domain expertise is the moat. AI sharks cannot compete with domain-experienced teams augmented by AI."

## Problem Statement

After assessing AI-readiness and calculating transformation investment, PE firms need a concrete roadmap: what to do in months 1-6, 6-12, 12-24. Generic roadmaps don't work — they need to be customized to the company's specific situation, industry, and starting point. Solstein should generate these roadmaps using LLMs trained on successful transformations, combined with company-specific signals.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Portfolio Value Creation** | Clear transformation path post-investment |
| **LP Confidence** | Demonstrable value creation plan |
| **Execution Success** | Roadmap based on proven patterns |

## Affected Files

| File | Issue |
|------|-------|
| New: `application/roadmap_generator.py` | Does not exist |
| `llm/` | No roadmap generation prompts |

## Architectural Requirements

- Roadmap generator: input company profile + AI-readiness assessment, output phased transformation plan
- Phases: Foundation (data infra, team training), Quick Wins (high-impact, low-effort automations), Transformation (core process AI), Optimization (advanced AI, predictive)
- Each phase: specific initiatives, timelines, resource requirements, success metrics
- Industry-specific patterns: energy sector roadmaps differ from fintech roadmaps
- Customization: PE team can adjust priorities based on investment thesis
- Progress tracking: integrate with project management tools (Asana, Jira)
- Update mechanism: roadmap evolves as transformation progresses
- Export: presentation-ready roadmap for board meetings

## Acceptance Criteria

- [ ] Roadmap generated with 4 phases (Foundation, Quick Wins, Transformation, Optimization)
- [ ] Each phase has specific initiatives with timelines
- [ ] Industry-specific patterns applied (energy vs. fintech vs. healthcare)
- [ ] Roadmap customizable by PE team
- [ ] Export generates board-ready presentation

## Definition of Done

- **Tests Required**: Validation against Energy 21 transformation pattern
- **Documentation Required**: Roadmap generation methodology
- **Code Review Gate**: Reviewer verifies roadmaps are actionable (not generic fluff)

## Notes

The roadmap turns assessment into action.
