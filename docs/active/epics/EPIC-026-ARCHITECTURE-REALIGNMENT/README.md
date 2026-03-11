# EPIC-026: Architecture Realignment (Simplify vs Implement)

> **Status**: 🔴 NOT STARTED
> **Priority**: P1 - High
> **Effort**: 21 story points
> **Sprint**: Architecture Decision
> **Related**: EPIC-022, ROOT_CAUSE_ANALYSIS
> **Blocked By**: Decision on Option A vs Option B

---

## 🚨 Problem Statement

**Massive architecture-implementation gap**: The documentation describes a sophisticated 6-agent LangGraph system with cross-validation, conflict resolution, and source authority weighting. The actual implementation is a single sequential function with none of these features.

### Documented Architecture (Not Implemented)

```
AI_RESEARCH_ARCHITECTURE.md describes:
┌─────────────────────────────────────────────────────────┐
│  LangGraph 6-Agent Orchestration                         │
├─────────────────────────────────────────────────────────┤
│  Planner → Searcher → Extractor → Validator → Cross-Ref → Synthesizer │
└─────────────────────────────────────────────────────────┘

Features Promised:
- Multi-agent LangGraph workflow
- Cross-reference agent for conflict resolution
- LLM-based cross-field validation
- Source authority weighting
- Confidence scoring based on source diversity
```

### Actual Implementation (Reality)

```python
# ai_research_orchestrator.py - Reality
def _execute_research_workflow(self, company_id, company_name):
    # 1. Search (basic web search)
    search_results = await self._search_company(company_name)

    # 2. Extract (LLM extraction)
    extracted_data = await self._extract_with_llm(search_results)

    # 3. Validate (naive range checks only)
    validated_data = self._validate_ranges(extracted_data)

    # MISSING: Cross-reference agent
    # MISSING: Conflict resolution
    # MISSING: Source authority weighting
    # MISSING: LLM cross-field validation
```

### The Decision

**Option A: Implement the Documented Architecture**
- Build full 6-agent LangGraph system
- Implement cross-reference agent
- Add conflict resolution
- **Effort**: 6-8 weeks
- **Risk**: Over-engineered, complex

**Option B: Simplify Architecture to Match Reality**
- Update docs to reflect simpler flow
- Add validation to existing workflow
- Focus on data quality over sophistication
- **Effort**: 2-3 weeks
- **Risk**: May need rework if scaling

**RECOMMENDATION: Option B**

### Impact

| Impact Area | Current State | Risk Level |
|-------------|---------------|------------|
| **Documentation Trust** | Docs promise what doesn't exist | 🔴 Critical |
| **System Complexity** | Simpler than documented | 🟡 Medium |
| **Maintenance** | Easier to maintain simple system | 🟢 Low |
| **Future Scaling** | May need rework | 🟡 Medium |
| **Investor/Demo Risk** | Pitching sophisticated AI that doesn't exist | 🔴 Critical |

### Root Cause Analysis Reference

See `docs/active/programs/root-cause/ROOT_CAUSE_ANALYSIS.md` - Section "Root Cause 2: Architecture-Implementation Gap"

---

## 🎯 Success Criteria

- [ ] Architecture decision made (Option A or B)
- [ ] Documentation updated to match actual implementation
- [ ] If Option B: Validation added to existing flow
- [ ] If Option A: Cross-reference agent implemented
- [ ] Architecture Decision Record (ADR) created
- [ ] Team aligned on chosen path
- [ ] No more architecture-documentation drift

---

## 📊 Current vs Target State

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Architecture Docs** | 6-agent LangGraph | Match reality | Doc review |
| **Cross-Validation** | Missing | Implemented | Feature check |
| **Conflict Resolution** | Missing | Implemented | Feature check |
| **Source Weighting** | Missing | Implemented | Feature check |
| **Doc-Code Alignment** | 20% | 100% | Review |

---

## 📚 Technical Analysis

### Option A: Full Implementation

```python
# LangGraph 6-agent system
from langgraph import Graph

class ResearchWorkflow:
    def build_graph(self):
        graph = Graph()

        # Add nodes
        graph.add_node("planner", PlannerAgent())
        graph.add_node("searcher", SearcherAgent())
        graph.add_node("extractor", ExtractorAgent())
        graph.add_node("validator", ValidatorAgent())
        graph.add_node("cross_ref", CrossReferenceAgent())  # NEW
        graph.add_node("synthesizer", SynthesizerAgent())

        # Add edges
        graph.add_edge("planner", "searcher")
        graph.add_edge("searcher", "extractor")
        graph.add_edge("extractor", "validator")
        graph.add_edge("validator", "cross_ref")  # NEW
        graph.add_edge("cross_ref", "synthesizer")

        return graph
```

**Pros:**
- Matches documented architecture
- Sophisticated cross-validation
- Future-proof for complex needs
- Impressive for demos

**Cons:**
- 6-8 weeks effort
- Complex to debug
- Overkill for current needs
- May not solve core data quality issues

### Option B: Simplify

```python
# Update documentation to match reality
"""
Research Pipeline (Sequential):
1. Search - Gather sources
2. Extract - LLM extraction
3. Validate - Range and format checks
4. Cross-Check - Simple conflict detection  [NEW]
5. Finalize - Prepare output
"""

def _execute_research_workflow(self, company_id, company_name):
    # 1. Search
    search_results = await self._search_company(company_name)

    # 2. Extract
    extracted_data = await self._extract_with_llm(search_results)

    # 3. Validate (enhanced)
    validated_data = self._validate_data(extracted_data)  # ENHANCED

    # 4. Cross-Check (NEW)
    cross_checked = self._detect_conflicts(validated_data)  # NEW

    # 5. Finalize
    return cross_checked
```

**Pros:**
- 2-3 weeks effort
- Easier to understand and debug
- Solves core data quality issues
- Can evolve later if needed

**Cons:**
- Less impressive for demos
- May need rework for complex markets
- Simpler than originally envisioned

---

## 📖 Stories Overview

### If Option B (Simplify) - RECOMMENDED

| Story | Title | Priority | Points | Dependencies |
|-------|-------|----------|--------|--------------|
| 26.1 | Update Architecture Documentation | P1 | 3 | None |
| 26.2 | Add Conflict Detection to Pipeline | P1 | 5 | None |
| 26.3 | Implement Simple Cross-Validation | P1 | 5 | 26.2 |
| 26.4 | Create Architecture Decision Record | P1 | 2 | 26.1 |
| 26.5 | Deprecate/Remove LangGraph References | P1 | 3 | 26.1 |
| 26.6 | Update Research Orchestrator | P1 | 3 | 26.2, 26.3 |

**Total Stories**: 6
**Total Points**: 21

### If Option A (Implement)

| Story | Title | Priority | Points | Dependencies |
|-------|-------|----------|--------|--------------|
| 26.1 | Implement Planner Agent | P1 | 5 | None |
| 26.2 | Implement Searcher Agent | P1 | 5 | 26.1 |
| 26.3 | Implement Extractor Agent | P1 | 5 | 26.2 |
| 26.4 | Implement Validator Agent | P1 | 5 | 26.3 |
| 26.5 | Implement Cross-Reference Agent | P1 | 8 | 26.4 |
| 26.6 | Implement Synthesizer Agent | P1 | 5 | 26.5 |
| 26.7 | Build LangGraph Orchestration | P1 | 8 | All above |
| 26.8 | Integration and Testing | P1 | 8 | 26.7 |

**Total Stories**: 8
**Total Points**: 49 (6-8 weeks)

---

## 🔗 Dependencies

```
# Option B (Simplify)
Story 26.1 (Update Docs)
    └── Story 26.4 (Create ADR)
    └── Story 26.5 (Deprecate LangGraph)

Story 26.2 (Conflict Detection)
    └── Story 26.3 (Cross-Validation)
        └── Story 26.6 (Update Orchestrator)

# Option A (Implement) - Complex dependency chain
Story 26.1 → Story 26.2 → Story 26.3 → Story 26.4 → Story 26.5 → Story 26.6 → Story 26.7 → Story 26.8
```

---

## ⚠️ Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Wrong architectural choice | Medium | High | Document decision rationale |
| Team disagreement on choice | Medium | Medium | Collaborative decision |
| Stakeholder pushback (Option B) | Medium | Medium | Explain data quality priority |
| Option A takes longer than estimated | High | High | Start with Option B |
| Complex system hard to debug | High (Option A) | High | Extensive testing |

---

## ✅ Definition of Done

- [ ] Architecture decision made and documented
- [ ] All stories for chosen option completed
- [ ] ADR created explaining decision
- [ ] Documentation updated to match reality
- [ ] Team aligned on path forward
- [ ] No drift between docs and code

---

## 📁 Epic Structure

```
docs/active/epics/EPIC-026-ARCHITECTURE-REALIGNMENT/
├── README.md                                    # This file
├── OPTION-A-IMPLEMENT/                          # If Option A chosen
│   ├── STORY-26.1-PLANNER.md
│   ├── STORY-26.2-SEARCHER.md
│   └── ...
├── OPTION-B-SIMPLIFY/                           # If Option B chosen (RECOMMENDED)
│   ├── STORY-26.1-UPDATE-DOCS.md
│   ├── STORY-26.2-CONFLICT-DETECTION.md
│   ├── STORY-26.3-CROSS-VALIDATION.md
│   ├── STORY-26.4-CREATE-ADR.md
│   ├── STORY-26.5-DEPRECATE-LANGGRAPH.md
│   └── STORY-26.6-UPDATE-ORCHESTRATOR.md
├── ARCHITECTURE-DECISION.md                     # Decision rationale
└── UPDATED-ARCHITECTURE.md                      # New architecture docs
```

---

## 🔗 Related Documentation

- [ROOT_CAUSE_ANALYSIS.md](../../programs/root-cause/ROOT_CAUSE_ANALYSIS.md) - Root cause context
- [AI_RESEARCH_ARCHITECTURE.md](../../../research/AI_RESEARCH_ARCHITECTURE.md) - Current architecture docs
- `src/solstein/research/ai_research_orchestrator.py` - Current implementation

---

## 📝 Notes

### Decision Criteria

Choose Option A (Full Implementation) if:
- Team has LangGraph expertise
- Budget for 6-8 weeks
- Need sophisticated AI for demos
- Scaling to complex markets

Choose Option B (Simplify) if:
- Need working system in 2-3 weeks
- Data quality is priority over sophistication
- Team familiar with current code
- Can evolve later if needed

### Recommendation Rationale

**Option B is recommended because:**
1. Current simple flow works (produces output)
2. Core problem is data quality, not architecture
3. Easier to validate and debug simple system
4. Can evolve to multi-agent later
5. Business need is reliable data, not sophisticated AI

---

*Created: 2026-03-11*
*Updated: 2026-03-11*
*Status: Decision Required Before Implementation*
*Version: 1.0*
