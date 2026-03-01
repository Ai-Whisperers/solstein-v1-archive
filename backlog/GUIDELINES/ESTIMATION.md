# Estimation Framework

> T-shirt sizing for stories. No hours, no points — just realistic buckets that account for uncertainty.

---

## Size Definitions

| Size | Duration | Complexity | Team Size | Definition |
|------|----------|------------|-----------|------------|
| **S** | 1-2 days | Well-understood | 1 engineer | Clear scope, no research needed, familiar domain |
| **M** | 3-5 days | Moderate complexity | 1 engineer | Some uncertainty, may need minor research |
| **L** | 1-2 weeks | High complexity | 1-2 engineers | Cross-module changes, significant research |
| **XL** | 3+ weeks | Architectural | 2+ engineers | System-wide impact, needs spike, high coordination |

---

## Size Indicators

### Small (S)

**Characteristics:**
- Single file or module change
- Well-understood pattern
- No external dependencies
- Existing tests cover similar code
- Can be reviewed in one sitting

**Examples:**
- Fix a specific bug with clear reproduction
- Add a validation rule
- Rename a variable/function for clarity
- Update a configuration value
- Add a missing index to database

**Checklist:**
- [ ] I can describe the complete solution in one sentence
- [ ] I know exactly which files need to change
- [ ] No new dependencies required
- [ ] No architectural decisions needed

---

### Medium (M)

**Characteristics:**
- 2-3 modules affected
- Some uncertainty about approach
- May need minor research or spike
- Requires new tests
- Reviewable in 30-60 minutes

**Examples:**
- Implement a new endpoint with standard patterns
- Refactor a function into a class
- Add integration with a well-documented API
- Migrate from one library to a similar one
- Implement a new validation service

**Checklist:**
- [ ] I have a good idea of the approach but need to verify details
- [ ] May need to read documentation or source code
- [ ] Requires new tests
- [ ] Might affect 2-3 files/modules

---

### Large (L)

**Characteristics:**
- Cross-module changes (5+ files)
- Significant uncertainty
- Requires research spike
- May introduce new patterns
- Needs careful review

**Examples:**
- Migrate to a new database schema
- Implement a new service from scratch
- Refactor a god class into multiple classes
- Add a new authentication mechanism
- Implement complex business logic with many edge cases

**Checklist:**
- [ ] Requires research or proof-of-concept
- [ ] Affects multiple modules
- [ ] Introduces new patterns or abstractions
- [ ] Needs architectural review
- [ ] May require coordination with other work

---

### Extra Large (XL)

**Characteristics:**
- System-wide impact
- High uncertainty
- Requires significant spike
- New architecture or major refactoring
- High coordination overhead

**Examples:**
- Migrate to new framework (e.g., FastAPI to Django)
- Implement multi-tenancy across entire system
- Replace core data layer
- Major version upgrade with breaking changes
- Extract a service from a monolith

**Checklist:**
- [ ] Needs dedicated spike story first
- [ ] Affects most of the codebase
- [ ] Requires team alignment on approach
- [ ] High risk of unknown unknowns
- [ ] Should be broken down if possible

---

## Estimation Process

### For Individual Stories

1. **Read the story completely** — understand the problem and requirements
2. **Identify affected files** — how many modules will change?
3. **Assess uncertainty** — how well do we understand the solution?
4. **Check dependencies** — are there blockers or coordination needs?
5. **Select size** — use the indicators above

### Calibration Questions

If unsure between two sizes, ask:

- "What could make this take twice as long?"
- "What's the worst-case scenario?"
- "Have we done something similar before?"
- "How many review cycles will this need?"

### Team Calibration

**Monthly calibration session:**
1. Pick 3 recently completed stories
2. Re-estimate them with current knowledge
3. Compare to original estimates
4. Adjust future estimates based on learnings

---

## Anti-Patterns

### ❌ Don't Do This

- **Splitting hairs**: Arguing between S and M for more than 2 minutes
- **False precision**: Using hours ("this will take 6.5 hours")
- **Points theater**: Converting to story points for velocity charts
- **Management padding**: Adding "buffer" to every estimate
- **Hero sizing**: Assuming uninterrupted focus time

### ✅ Do This Instead

- **Trust the buckets**: S is 1-2 days, that's the precision we need
- **Record actuals**: Note how long stories actually took
- **Adjust for context**: Same technical work takes longer during on-call week
- **Call out uncertainty**: "This is an M, but could be L if X happens"

---

## Estimation Confidence

Add confidence level to each estimate:

| Confidence | Meaning | Action |
|------------|---------|--------|
| **High** | Done this before, clear scope | Proceed |
| **Medium** | Some uncertainty, but bounded | Add 20% buffer |
| **Low** | Significant unknowns | Consider spike story first |

Example: "Size: M, Confidence: Low" → Consider making it L or adding spike

---

## Velocity Tracking

Don't track velocity by points. Track by **throughput**:

```
Sprint 1: 8 S, 4 M, 2 L = 14 stories
Sprint 2: 6 S, 5 M, 3 L = 14 stories
Sprint 3: 5 S, 6 M, 1 L, 1 XL = 13 stories
```

This gives realistic capacity planning without gamification.

---

## Related

- [Risk Assessment](RISK-ASSESSMENT.md) — Size and risk are correlated
- [Success Metrics](SUCCESS-METRICS.md) — Track estimation accuracy
- [Story Template](../.backlog/templates/story.md) — Include size field
