# EPIC-044: Quick Wins — High Impact, Low Effort

> Morale-boosting, high-impact stories that can be completed in a day. The antidote to epic fatigue.

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — High |
| **Stories** | 10 |
| **Target** | 1-2 per sprint |
| **Created** | 2026-03-01 |

---

## Philosophy

Long-running epics (EPIC-007, EPIC-021) can be demoralizing. Quick wins provide:
- **Immediate gratification** — Ship something today
- **Momentum** — Keep the team energized
- **Learning** — Try new approaches with low risk
- **User delight** — Small improvements that users notice

**Rule:** Every sprint must include at least one quick win.

---

## Quick Win Criteria

| Criterion | Definition |
|-----------|------------|
| **Size** | S (1-2 days max) |
| **Risk** | Low |
| **Impact** | High user or developer value |
| **Scope** | Single file or module |
| **Dependencies** | None (can start immediately) |

---

## Stories

| Story | Title | Impact | Owner |
|-------|-------|--------|-------|
| [STORY-403](STORIES/STORY-403-api-response-times.md) | Add API Response Time Headers | Users see performance | Backend |
| [STORY-404](STORIES/STORY-404-health-check-real.md) | Replace Fake Health Check with Real DB Probe | Ops can trust health | Backend |
| [STORY-405](STORIES/STORY-405.md) | Improve Error Message Clarity | Users understand failures | Backend |
| [STORY-406](STORIES/STORY-406.md) | Add Request IDs to All Logs | Debugging is easier | Backend |
| [STORY-407](STORIES/STORY-407.md) | Create Seed Data Script for Local Dev | New devs productive in 30 min | Backend |
| [STORY-408](STORIES/STORY-408.md) | Add Request/Response Examples to API Docs | API easier to use | Backend |
| [STORY-409](STORIES/STORY-409.md) | Speed Up Slowest Test by 50% | Faster feedback | Backend |
| [STORY-410](STORIES/STORY-410.md) | Add Startup Validation for Critical Env Vars | Fail fast on misconfig | Backend |
| [STORY-411](STORIES/STORY-411.md) | Standardize Log Format Across All Modules | Logs are parseable | Backend |
| [STORY-412](STORIES/STORY-412.md) | Add Common Commands to Makefile | Fewer commands to remember | DevEx |

---

## Impact Areas

### User Experience (4 stories)
- [STORY-403](STORIES/STORY-403-api-response-times.md): API Response Time Headers
- [STORY-405](STORIES/STORY-405.md): Error Message Clarity
- [STORY-408](STORIES/STORY-408.md): API Docs Examples

### Developer Experience (4 stories)
- [STORY-407](STORIES/STORY-407.md): Seed Data Script
- [STORY-409](STORIES/STORY-409.md): Test Speed Optimization
- [STORY-411](STORIES/STORY-411.md): Logging Consistency
- [STORY-412](STORIES/STORY-412.md): Makefile Improvements

### Operations (2 stories)
- [STORY-404](STORIES/STORY-404-health-check-real.md): Real Health Checks
- [STORY-410](STORIES/STORY-410.md): Env Validation

---

## Selection Process

### Weekly (Sprint Planning)

1. Review open quick wins
2. Consider team mood and energy
3. Balance with epic work
4. Assign one quick win per engineer

### Selection Questions

- "What would make users smile this week?"
- "What annoying thing can we fix today?"
- "What would make onboarding easier?"
- "What would reduce support tickets?"

---

## Definition of Done (Quick Wins)

**Relaxed criteria for quick wins:**

- [ ] Code works
- [ ] Basic test coverage
- [ ] No breaking changes
- [ ] Deployed to staging

**Skip for quick wins:**
- Extensive documentation
- Load testing
- Architecture review
- Formal ADR

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Quick wins per sprint | ≥1 |
| Average completion time | ≤1.5 days |
| User feedback | Positive |
| Team satisfaction | "That felt good" |

---

## Anti-Patterns

### ❌ Don't Do This

- **Scope creep:** "While I'm here, I'll also refactor..."
- **Quick win chains:** "I'll just do one more quick win..."
- **Deferring epics:** "Quick wins are more fun, let's do those instead"

### ✅ Do This Instead

- **Timebox:** 2 days max, then ship or cut scope
- **Balance:** 1 quick win per 3 epic stories
- **Celebrate:** Acknowledge the win, then return to epics

---

## Related

- [Estimation Framework](../../GUIDELINES/ESTIMATION.md) — S-size definition
- [Epic Registry](../../README.md#epic-registry) — Full epic list
- [Milestones](../../MILESTONES/) — Where quick wins fit
