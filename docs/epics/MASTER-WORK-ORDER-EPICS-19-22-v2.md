# Master Work Order: EPICs 19-22 Implementation Roadmap

## Document Information
- **Version:** 2.0
- **Created:** 2026-03-06
- **Status:** Active
- **Owner:** Engineering Team
- **Review Cycle:** Weekly

---

## Executive Summary

This work order provides a comprehensive implementation roadmap for EPICs 19-22, incorporating all improvements and lessons learned from EPIC-020 (God Function Breakdown) completion.

### Key Changes from Original Plan:
1. ✅ **EPIC-020 COMPLETE** - 28 functions refactored, 10 helper modules created
2. 🔄 **EPIC-019 ENHANCED** - Added import cycle detection, dead code detection, EPIC-020 pattern validation
3. 🔄 **EPIC-021 UPDATED** - Accounted for EPIC-020 partial completion, added consolidation stories
4. 🔄 **EPIC-022 RE-ASSESSED** - Must re-measure classes after EPIC-020 before starting

### Total Effort:
- **Original:** 211 points (EPICs 19-22)
- **Updated:** ~240 points (including new stories and EPIC-020 completion)
- **Duration:** ~30 weeks with 1 developer
- **Recommended:** 2 developers parallel (15 weeks)

---

## Phase Overview

### Phase 0: Foundation ✅ COMPLETE
| Epic | Status | Points | Duration |
|------|--------|--------|----------|
| EPIC-020 | ✅ COMPLETE | 194 | 4 weeks |

**Deliverables:**
- 28 god functions refactored
- 10 helper modules created
- Established patterns: Extract Method, Strategy, Pipeline Stage, Builder
- Fixed circular import in domain/models

---

### Phase 1: Quality Infrastructure (Weeks 1-6)
| Epic | Status | Points | Duration |
|------|--------|--------|----------|
| EPIC-019 v2 | 🔄 Ready | 49 | 6 weeks |

**Stories:**
1. Story 1: AST-Based Code Smell Detection (5 pts)
2. Story 2: PR Size and Complexity Limits (3 pts)
3. Story 3: Code Quality Score Dashboard (5 pts)
4. Story 4: Agent-Specific Guidelines (3 pts)
5. Story 5: Bare Except Detection (2 pts) - ✅ Already done
6. Story 6: Function and Class Size Monitoring (3 pts)
7. Story 7: Architecture Compliance Checks (5 pts)
8. Story 8: Code Duplication Detection (3 pts)
9. Story 9: Automated Refactoring Bot (8 pts)
10. Story 10: Code Quality Gates (3 pts)
11. **NEW** Story 11: Import Cycle Detection (3 pts)
12. **NEW** Story 12: Dead Code Detection (3 pts)
13. **NEW** Story 13: EPIC-020 Pattern Validation (5 pts)
14. **NEW** Story 14: Module Boundary Enforcement (3 pts)

**Deliverables:**
- CI/CD guardrails operational
- Import cycle detection active
- Dead code monitoring
- EPIC-020 pattern validation
- Quality gates blocking deployment

**Dependencies:**
- ✅ EPIC-020 complete

**Success Criteria:**
- [ ] Zero new code smells in main for 2 weeks
- [ ] Zero import cycles
- [ ] Helper module utilization >80%
- [ ] All PRs pass quality gates

---

### Phase 2: File Modularization (Weeks 7-18)
| Epic | Status | Points | Duration |
|------|--------|--------|----------|
| EPIC-021 v2 | 🔄 Ready | 108 | 12 weeks |

**Phase 2A: Complete Partial Work (Weeks 7-8)**
- Story 6: Complete domain/models migration (2 pts)
- Story 10: Complete health_checker migration (2 pts)
- **NEW** Story 26: Consolidate helper modules (5 pts)
- **NEW** Story 27: Create module index (3 pts)
- **NEW** Story 28: Circular import prevention (5 pts)

**Phase 2B: Split P0 Files (Weeks 9-12)**
- Story 1: Split exporters/markdown/generator.py (13 pts)
- Story 2: Split data/unified_loader.py (8 pts)
- Story 3: Split data/loaders.py (8 pts)
- Story 4: Split worker_tasks.py (5 pts)
- Story 5: Split infrastructure/database_models.py (5 pts)

**Phase 2C: Split P1-P2 Files (Weeks 13-16)**
- Story 7: Split api/routers/enrichment.py (5 pts)
- Story 8: Split agents/github_agent.py (5 pts)
- Story 9: Split data/additional_sources.py (5 pts)
- Stories 11-15: Split remaining large files (15 pts)

**Phase 2D: Split P3 Files (Weeks 17-18)**
- Stories 16-25: Split files approaching limit (20 pts)

**Deliverables:**
- All files <500 lines
- Clean module boundaries
- No circular imports
- Public API documented
- Helper modules consolidated

**Dependencies:**
- ✅ EPIC-020 complete
- 🔄 EPIC-019 (for import cycle detection)

**Success Criteria:**
- [ ] No files >500 lines
- [ ] All imports clean
- [ ] Tests passing
- [ ] Documentation complete

---

### Phase 3: Class Refactoring (Weeks 19-30)
| Epic | Status | Points | Duration |
|------|--------|--------|----------|
| EPIC-022 v2 | 🔄 Ready | ~80 | 12 weeks |

**Phase 3A: Assessment (Week 19)**
- **NEW** Story 0: Re-assess class sizes (3 pts)

**Phase 3B: Major Classes (Weeks 20-23)**
- Story 1: Break Down UnifiedCompanyLoader (8 pts)
- Story 2: Break Down ReportGenerator (8 pts)
- Story 3: Break Down CompetitorDataLoader (5 pts)
- Story 4: Break Down GitHubAgent (5 pts)

**Phase 3C: Medium Classes (Weeks 24-27)**
- Story 5: Break Down ProviderHealthChecker (3 pts) - reduced
- Story 6: Break Down AdditionalDataSources (5 pts)
- Story 7: Break Down EnhancedLLMClient (3 pts) - reduced
- Stories 8-14: Break Down medium classes (21 pts)

**Phase 3D: Smaller Classes + Documentation (Weeks 28-30)**
- Stories 15-19: Break Down smaller classes (10 pts) - may reduce to 0
- **NEW** Story 20: Create Class Extraction Patterns Guide (3 pts)
- **NEW** Story 21: Extract Reusable Components Library (5 pts)
- **NEW** Story 22: Coordinate with EPIC-021 (3 pts)

**Deliverables:**
- All classes <300 lines
- Base component library
- Patterns documented
- Coordination with EPIC-021 complete

**Dependencies:**
- ✅ EPIC-020 complete
- 🔄 EPIC-021 (coordinate on file splits)

**Success Criteria:**
- [ ] No classes >300 lines
- [ ] No classes with >15 methods
- [ ] Test coverage >80%
- [ ] Patterns documented

---

## Cross-Cutting Concerns

### 1. Testing Infrastructure
**Gap Identified:** Missing `bcrypt` dependency blocked test execution

**Action Required:**
- Fix test dependencies before Phase 1
- Add to EPIC-029 (Testing Infrastructure)
- Ensure all refactored code has tests

**Owner:** DevOps Team  
**Deadline:** End of Week 1

### 2. Documentation
**Requirements:**
- Update AGENTS.md with EPIC-020 patterns
- Document EPIC-019 guardrails
- Create module index for EPIC-021
- Document class extraction patterns for EPIC-022

**Owner:** Tech Lead  
**Deadline:** Ongoing

### 3. Coordination
**EPIC-021 ↔ EPIC-022 Coordination:**
- Weekly sync meetings
- Shared module boundary document
- Avoid duplicate work
- Consistent naming conventions

**Owner:** Engineering Manager  
**Cadence:** Weekly

---

## Risk Management

### High Risks:

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| Test infrastructure not fixed | Blocks all verification | Priority fix in Week 1 | DevOps |
| Circular imports reappear | Breaks codebase | EPIC-019 detection | Engineering |
| EPIC-021/022 duplicate work | Wasted effort | Coordination story | EM |
| Class size re-assessment shows little work | Effort overestimate | Re-assess first | Tech Lead |

### Medium Risks:

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| Helper module dead code | Unused code bloat | EPIC-019 detection | Engineering |
| Import path confusion | Developer confusion | Module index | Tech Lead |
| Performance regression | Slower execution | Benchmarks | Engineering |

---

## Resource Allocation

### Option A: Sequential (1 Developer)
- **Total Duration:** 30 weeks
- **Cost:** 1 FTE
- **Risk:** Lower (focused)
- **Benefit:** Deep knowledge

### Option B: Parallel (2 Developers)
- **Total Duration:** 15 weeks
- **Cost:** 2 FTE
- **Risk:** Medium (coordination needed)
- **Benefit:** Faster delivery

**Recommended:** Option B with strong coordination

### Developer 1: Quality & Infrastructure
- EPIC-019 (all stories)
- EPIC-021 Phase 2A (consolidation)
- EPIC-022 Phase 3A (assessment)

### Developer 2: Modularization
- EPIC-021 Phases 2B-2D (file splitting)
- EPIC-022 Phases 3B-3D (class refactoring)

---

## Weekly Cadence

### Monday: Planning
- Review previous week
- Plan current week
- Identify blockers
- Update estimates

### Wednesday: Mid-week Sync
- Progress check
- Cross-epic coordination
- Blocker resolution
- Re-prioritization

### Friday: Demo & Retro
- Demo completed work
- Update documentation
- Retro on process
- Plan next week

---

## Definition of Done (All EPICs)

### EPIC-019 (Quality Guardrails):
- [ ] All 14 stories complete
- [ ] CI/CD pipeline operational
- [ ] Zero new code smells in main for 2 weeks
- [ ] Zero import cycles
- [ ] Helper module utilization >80%
- [ ] AGENTS.md updated

### EPIC-020 (God Functions):
- [x] All 24 god functions broken down ✅
- [x] No functions >100 lines ✅
- [x] 10 helper modules created ✅
- [x] Patterns documented ✅

### EPIC-021 (File Splitting):
- [ ] All 25 files split
- [ ] No files >500 lines
- [ ] No circular imports
- [ ] Public API documented
- [ ] Helper modules consolidated

### EPIC-022 (God Classes):
- [ ] Re-assessment complete
- [ ] All god classes broken down
- [ ] No classes >300 lines
- [ ] Base component library
- [ ] Patterns documented

---

## Metrics Dashboard

### Track Weekly:

| Metric | Target | Current | Week 0 | Week 6 | Week 18 | Week 30 |
|--------|--------|---------|--------|--------|---------|---------|
| Functions >100 lines | 0 | 0 | 0 | 0 | 0 | 0 |
| Files >500 lines | 0 | 25 | 25 | 20 | 0 | 0 |
| Classes >300 lines | 0 | 19 | 19 | 19 | 15 | 0 |
| Import cycles | 0 | 1 | 1 | 0 | 0 | 0 |
| Helper utilization | >80% | ? | ? | 80% | 90% | 95% |
| Test coverage | >80% | ? | ? | 75% | 80% | 85% |
| Code smell density | <5 | ? | ? | 5 | 3 | 1 |

---

## Communication Plan

### Stakeholders:
- **Engineering Team:** Daily standups
- **Tech Lead:** Weekly 1:1s
- **Engineering Manager:** Weekly sync
- **Product:** Bi-weekly demo
- **Executive:** Monthly summary

### Artifacts:
- **Weekly:** Progress report
- **Bi-weekly:** Demo recording
- **Monthly:** Executive summary
- **Milestone:** Epic completion report

---

## Appendices

### Appendix A: EPIC-020 Helper Modules Reference

| Module | Lines | Classes/Functions | Used By |
|--------|-------|-------------------|---------|
| pipeline_stages.py | 491 | 10 stages | EPIC-021, EPIC-022 |
| company_extractors.py | 447 | 12 extractors | EPIC-021, EPIC-022 |
| market_catalogs.py | 169 | Data-driven | EPIC-021, EPIC-022 |
| report_sections.py | 299 | 9 generators | EPIC-022 |
| research_persistence.py | 291 | 8 helpers | EPIC-022 |
| reconciliation_helpers.py | 202 | 5 helpers | EPIC-022 |
| provider_strategies.py | 322 | 12 strategies | EPIC-022 |
| enrichment_executors.py | 221 | 3 executors | EPIC-022 |
| company_builder.py | 225 | 8 builders | EPIC-022 |
| sec_edgar_helpers.py | 158 | 7 helpers | EPIC-022 |

### Appendix B: Pattern Quick Reference

**Extract Method:**
- When: Function >100 lines
- Result: 3-5 helper methods
- Example: `growth_momentum.py:score`

**Strategy Pattern:**
- When: Multiple provider implementations
- Result: Strategy classes + Factory
- Example: `provider_strategies.py`

**Pipeline Stage:**
- When: Multi-step process
- Result: Stage classes + Orchestrator
- Example: `pipeline_stages.py`

**Builder Pattern:**
- When: Complex object construction
- Result: Builder classes
- Example: `company_builder.py`

### Appendix C: Naming Conventions

**Helper Modules:**
- `*_helpers.py` - Utility functions
- `*_strategies.py` - Strategy pattern implementations
- `*_stages.py` - Pipeline stage classes
- `*_builders.py` - Builder pattern implementations
- `*_extractors.py` - Data extraction functions
- `*_executors.py` - Execution classes

**Extracted Classes:**
- `*Loader` - Data loading
- `*Generator` - Report/content generation
- `*Analyzer` - Analysis components
- `*Validator` - Validation logic
- `*Orchestrator` - Coordination

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Tech Lead | | | |
| Engineering Manager | | | |
| Product Manager | | | |

---

*Version: 2.0*  
*Last Updated: 2026-03-06*  
*Next Review: Weekly*
