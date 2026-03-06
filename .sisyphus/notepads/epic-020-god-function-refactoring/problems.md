# EPIC-020 Problems

> Unresolved blockers and problems

---

## Current Blockers

*None yet - will be populated if blockers arise*

---

## Potential Risks

### RISK-001: Test Coverage Gap
Current test coverage is ~28%. Refactoring without adequate tests risks introducing regressions.

**Mitigation:**
- Add tests for god functions BEFORE refactoring
- Use golden dataset for regression testing
- Incremental refactoring with verification at each step

---

### RISK-002: Performance Degradation
Breaking functions into smaller units may add overhead from function calls and object creation.

**Mitigation:**
- Benchmark before/after each refactoring
- Profile hot paths
- Consider inlining for truly hot code paths

---

### RISK-003: Merge Conflicts
With 108 functions to refactor, multiple developers working in parallel may create conflicts.

**Mitigation:**
- Clear file ownership
- Small, focused PRs
- Rebase frequently
- Communicate file changes in standups

---

*Last updated: 2026-03-06*
