# STORY-031: Decompose the GitHub Agent God File

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | MEDIUM |
| Epic | [EPIC-008: God File Decomposition](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `agents/github_agent.py` is 771 lines. It handles API authentication, repository listing, commit analysis, contributor profiling, technology detection, activity scoring, and result aggregation — all in one file.

## Problem Statement

A 771-line agent file conflates multiple distinct analysis concerns. Technology detection (identifying programming languages and frameworks from repository metadata) has nothing to do with API authentication (managing tokens and rate limits). Contributor profiling (analysing commit authors and patterns) is logically separate from commit frequency analysis (measuring activity velocity).

The `GitHubAgent` class has become a monolith because each new analysis capability was added to the existing file rather than to a focused sub-module. The result is a single class that does seven things, only some of which are related.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Maintainability** | Changing technology detection logic requires navigating past authentication and commit analysis code |
| **Testability** | Testing contributor profiling requires instantiating the entire GitHub agent with all its dependencies |
| **Single Responsibility** | Seven responsibilities in one class — the class has at least six too many |
| **Code Review** | Diffs in a 771-line file make it hard to isolate the scope of a change |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/agents/github_agent.py` | Split | 771 lines → focused analysis modules |
| New: `src/solstein/agents/github/auth.py` | Add | API authentication and rate limit management |
| New: `src/solstein/agents/github/repo_analyzer.py` | Add | Repository listing and metadata analysis |
| New: `src/solstein/agents/github/commit_analyzer.py` | Add | Commit frequency and pattern analysis |
| New: `src/solstein/agents/github/contributor_profiler.py` | Add | Contributor identification and profiling |
| New: `src/solstein/agents/github/tech_detector.py` | Add | Technology stack detection from repository data |
| New: `src/solstein/agents/github/activity_scorer.py` | Add | Activity scoring and aggregation |
| `src/solstein/agents/github/__init__.py` | Add | Re-export `GitHubAgent` as the public interface |

## Architectural Requirements

- **REQ-1**: `github_agent.py` must be split by analysis responsibility into focused modules
- **REQ-2**: No resulting module may exceed 300 lines
- **REQ-3**: The main `GitHubAgent` class may remain as an orchestrator, but must delegate all analysis work to focused sub-modules — the orchestrator should contain only coordination logic, not analysis logic
- **REQ-4**: All existing GitHub agent tests must pass after decomposition
- **REQ-5**: Each sub-module must be independently testable — testing technology detection should not require API authentication setup

## Acceptance Criteria

- [ ] No resulting module exceeds 300 lines
- [ ] Each module has a named single responsibility describable in one sentence
- [ ] All existing GitHub agent tests pass without modification
- [ ] The `GitHubAgent` orchestrator delegates to sub-modules — it does not contain analysis logic itself
- [ ] Each sub-module has its own test file

## Definition of Done

**Tests Required:**
- [ ] All pre-existing GitHub agent tests pass after decomposition
- [ ] New unit tests for each extracted module (auth, repo analysis, commit analysis, contributor profiling, tech detection, activity scoring)
- [ ] Test: each sub-module can be imported and tested independently without the orchestrator

**Documentation Required:**
- [ ] Comment at the top of each module explaining its analysis responsibility
- [ ] `__init__.py` documents the public API of the `agents.github` package

**Code Review Gate:**
- [ ] Reviewer confirms each module has one clear responsibility
- [ ] Reviewer confirms the orchestrator contains only coordination logic
- [ ] Reviewer confirms no module exceeds 300 lines

## Notes

This story has no dependencies and can start immediately. It pairs well with STORY-028 (markdown generator decomposition) for parallel execution — neither has dependencies and they affect completely different parts of the codebase.

The `GitHubAgent` class should become a thin orchestrator: it calls sub-modules in sequence, collects their results, and returns the aggregated output. The orchestrator should be under 100 lines. If it is longer, it is doing analysis work that should be delegated.

The suggested module boundaries follow the seven responsibilities identified in the audit. Adjust them based on the actual code structure — some responsibilities may be small enough to combine, and others may need further splitting.
