# EPIC-077: AI Maturity Scoring Enhancement

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P2: Scoring Accuracy |
| **Phase** | P2 — Make Scores Meaningful |
| **Created** | 2026-04-01 |

## Context

AI maturity detection relies on a narrow keyword list that misses modern terminology (LLM, GPT, neural, computer vision, NLP). The signal detection in `research/signals.py` and `analytics/ai_readiness.py` underscores companies that are clearly AI-driven but use different terminology. GitHub repos and patents are not used as AI signals.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-307](STORIES/STORY-307.md) | Expand AI signal detection: add ML/DL/neural/GPT/LLM/automation/predictive/NLP/computer vision keywords | 🔴 READY | File: research/signals.py, analytics/ai_readiness.py |
| [STORY-308](STORIES/STORY-308.md) | Use LLM to assess AI maturity from company descriptions and recent news | 🔴 READY | Deps: LLM provider |
| [STORY-309](STORIES/STORY-309.md) | Add GitHub-based AI signals (ML repos, tensorflow/pytorch/sklearn in dependencies) | 🔴 READY | Deps: STORY-290 |
| [STORY-310](STORIES/STORY-310.md) | Add patent-based AI signals (AI/ML patent filings from USPTO) | 🔴 READY | Deps: STORY-291 |

## Success Criteria

- AI maturity score correctly identifies known AI-native energy companies
- GitHub dependency scanning detects ML frameworks in at least 5 test repos
- Patent signals contribute to AI maturity for companies with USPTO filings

## Dependencies

- STORY-290 (GitHub adapter) for [STORY-309](STORIES/STORY-309.md)
- STORY-291 (arXiv/patent adapter) for [STORY-310](STORIES/STORY-310.md)
- STORY-321 (LLM provider) for [STORY-308](STORIES/STORY-308.md)
