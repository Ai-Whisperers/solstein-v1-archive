# Epic Management Rules

## Epic Lifecycle

### Epic States
- **📋 Proposed** - Idea documented, not yet approved
- **🔄 Ready** - Approved and prioritized, ready to start
- **⚡ In Progress** - Actively being worked on
- **⏳ Blocked** - Waiting on dependencies
- **✅ Complete** - All stories done, verified
- **📦 Archived** - Done and documented

### Epic Dependencies
```
EPIC-019 (Quality Guardrails) 
    ↓ (depends on)
EPIC-020 (God Functions) 
    ↓ (depends on)
EPIC-021 (File Splitting) 
    ↓ (depends on)
EPIC-022 (God Classes)
```

**Rule**: Never start an epic until all dependencies are ✅ Complete.

## Epic Structure

### Required Epic Documentation
Every epic must have:
1. **Clear objective** - What problem are we solving?
2. **Success criteria** - How do we know it's done?
3. **Story breakdown** - Atomic, estimable stories
4. **Dependencies** - What must be done first?
5. **Risks** - What could go wrong?
6. **Definition of Done** - Checklist for completion

### Story Writing
Stories must be:
- **Independent** - Can be done in any order
- **Negotiable** - Details can be discussed
- **Valuable** - Delivers business value
- **Estimable** - Can estimate effort
- **Small** - Can complete in 1-3 days
- **Testable** - Has clear acceptance criteria

### Story Template
```markdown
## Story X: [Title]

**As a** [role]
**I want** [feature]
**So that** [benefit]

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### Technical Notes
- Implementation details
- File paths
- Dependencies

### Definition of Done
- [ ] Code implemented
- [ ] Tests written
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Merged to main
```

## Epic Execution

### Starting an Epic
1. Read the epic documentation completely
2. Verify all dependencies are complete
3. Run baseline metrics (file sizes, test coverage, etc.)
4. Create todo list for all stories
5. Start with Story 0 (assessment/investigation)

### During Epic Execution
1. **Update todos obsessively** - Mark complete immediately
2. **One story at a time** - Finish before starting next
3. **Run quality checks** - After every significant change
4. **Document as you go** - Update MODULE_INDEX, AGENTS.md
5. **Small commits** - Atomic, focused commits

### Epic Completion Checklist
- [ ] All stories complete
- [ ] All quality checks pass
- [ ] No regressions (test suite passes)
- [ ] Documentation updated
- [ ] MODULE_INDEX updated
- [ ] AGENTS.md updated with new patterns
- [ ] Metrics improved (file sizes, complexity, etc.)
- [ ] Handoff notes for next epic

## Epic Handoff

### Handoff Document Template
```markdown
# EPIC-XXX Handoff

## Status: ✅ COMPLETE

## What Was Done
- Summary of changes
- Files modified/created
- Patterns established

## Current State
- Metrics (file sizes, class sizes, etc.)
- Quality gates status
- Known issues

## Next Epic Ready
- EPIC-YYY is ready to start
- Dependencies satisfied
- Foundation laid

## Lessons Learned
- What worked well
- What to do differently
- Patterns to reuse
```

## Parallel Epic Execution

### When to Parallelize
- Epics have **no shared files**
- Epics have **no dependencies**
- Team has **2+ developers**
- Epics are **different domains**

### Safe Parallel Combinations
```
✅ EPIC-023 (Performance) + EPIC-024 (API Docs)
   - Different domains
   - No file overlap
   
✅ EPIC-027 (Security) + EPIC-028 (DevEx)
   - Different concerns
   - No dependencies

❌ EPIC-021 (File Splitting) + EPIC-022 (God Classes)
   - EPIC-022 depends on EPIC-021
   - Would cause conflicts
```

## Epic Metrics

### Track These Metrics
- **Lines of code** - Before/after
- **File count** - Before/after
- **Average file size** - Target: <300 lines
- **Average class size** - Target: <200 lines
- **Average function size** - Target: <50 lines
- **Test coverage** - Should not decrease
- **Code smells** - Should decrease
- **Circular imports** - Target: 0

### Baseline Command
```bash
# Run before starting epic
python scripts/ci/check_file_sizes.py
python scripts/ci/check_class_sizes.py
python scripts/ci/check_function_sizes.py
python scripts/ci/code_smell_detector.py
python scripts/ci/detect_import_cycles.py
```

## Epic Anti-Patterns

### ❌ Don't Do These
- **Skip Story 0** - Always assess first
- **Big bang changes** - Incremental refactoring only
- **Refactor without tests** - Never
- **Ignore quality gates** - Fix issues immediately
- **Batch complete todos** - Mark done immediately
- **Leave broken state** - Always leave working code

### ✅ Do These Instead
- **Start with assessment** - Understand before changing
- **Small, focused changes** - One thing at a time
- **Test-driven refactoring** - Tests first
- **Fix issues immediately** - Don't accumulate debt
- **Real-time todo updates** - Mark complete as you go
- **Always working code** - Commit working state
