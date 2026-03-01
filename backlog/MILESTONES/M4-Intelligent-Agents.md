# M4: Intelligent Agents

> Modern LLM stack with Anthropic SDK, structured outputs, and LangGraph orchestration.

| Field | Value |
|-------|-------|
| **Target Date** | 2026-04-30 |
| **Duration** | 2 weeks |
| **Epics** | 2 |
| **Stories** | 9 |
| **Status** | 🔴 Not Started |
| **Depends On** | [M3: Modern Data Layer](M3-Modern-Data-Layer.md) |

---

## Goal

Replace the 661-line custom LLM client with modern tools: Anthropic SDK for API calls, Instructor for structured outputs, Langfuse for observability, and LangGraph for agent orchestration. This transforms the research pipeline from a collection of stub agents into an intelligent, observable system.

---

## Included Epics

| Epic | Title | Stories | Priority |
|------|-------|---------|----------|
| [EPIC-021](../EPICS/EPIC-021-modern-llm-stack/README.md) | Modern LLM Stack | 5 | P1 |
| [EPIC-022](../EPICS/EPIC-022-langraph-agent-orchestration/README.md) | LangGraph Agent Orchestration | 4 | P2 |

---

## Story Breakdown

### EPIC-021: Modern LLM Stack

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-071 | Replace Custom LLM Client with Anthropic SDK | L | High |
| STORY-072 | Implement Structured LLM Outputs with Instructor | M | Medium |
| STORY-073 | Integrate Langfuse for Cost Tracking and Prompt Management | M | Medium |
| STORY-074 | Migrate LLM Evaluation to Langfuse | M | Low |
| STORY-075 | Implement Multi-Provider Fallback via SDK | M | Medium |

### EPIC-022: LangGraph Agent Orchestration

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-076 | Define LangGraph State and Research Graph Architecture | M | Medium |
| STORY-077 | Migrate Coordinator Agent to LangGraph State Machine | L | High |
| STORY-078 | Implement Real Agent Nodes as LangGraph Graph Nodes | L | High |
| STORY-079 | Add Checkpointing and Human-in-the-Loop | M | Medium |

---

## Dependencies

**Hard:**
- [M3: Modern Data Layer](M3-Modern-Data-Layer.md) — Data layer must be stable

**Soft:**
- EPIC-021 should complete before EPIC-022 (SDK before orchestration)

---

## Exit Criteria

- [ ] Custom LLM client fully replaced
- [ ] All LLM outputs structured and validated
- [ ] Cost tracking and prompt management in Langfuse
- [ ] Agent coordinator migrated to LangGraph
- [ ] 7 stub agents replaced with real implementations
- [ ] Human-in-the-loop for critical decisions
- [ ] Multi-provider fallback tested

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| LLM client lines of code | 661 | <100 (SDK wrapper) |
| Stub agents | 7 | 0 |
| LLM response time | ~5s | <2s |
| Agent success rate | ~60% | >90% |
| Cost per research | Unknown | <$0.50 |
| Structured output rate | ~40% | >95% |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Anthropic SDK breaking changes | Medium | Medium | Pin versions, read changelogs |
| LangGraph learning curve | High | Medium | Spike story, team training |
| Prompt migration issues | Medium | High | A/B test prompts, gradual rollout |
| Cost escalation | Medium | Medium | Set budgets, alerts in Langfuse |
| Agent reliability | Medium | High | Comprehensive testing, fallback modes |

---

## Definition of Done

- [ ] All stories in Done status
- [ ] Agent performance benchmarks met
- [ ] Cost tracking accurate
- [ ] Demo to stakeholders
- [ ] M5 planning ready

---

## Related

- [M3: Modern Data Layer](M3-Modern-Data-Layer.md) — Previous milestone
- [M5: Production Ready](M5-Production-Ready.md) — Next milestone
