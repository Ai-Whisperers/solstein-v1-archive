# STORY-309: Add GitHub-based AI signals (ML repos, ML frameworks in dependencies)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-077 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-290 (GitHub adapter) |

## Description

Add GitHub-based AI maturity signals: detect ML/AI repositories, detect ML framework dependencies (tensorflow, pytorch, sklearn, transformers, langchain, etc.) in requirements files.

## Acceptance Criteria

- [ ] GitHub signal detects tensorflow, pytorch, sklearn, transformers, langchain
- [ ] AI repo detection uses repo topics and descriptions
- [ ] Signal weight: 0.3 boost to AI maturity score per ML framework detected
- [ ] Caps at 1.0 boost regardless of number of frameworks
