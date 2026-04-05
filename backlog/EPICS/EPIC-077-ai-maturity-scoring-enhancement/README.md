# EPIC-077: AI Maturity Scoring Enhancement

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Phase** | P2 — Make Scores Meaningful |
| **Effort** | M (3–5 days) |
| **Stories** | 4 ([STORY-307](STORIES/STORY-307.md) through [STORY-310](STORIES/STORY-310.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (added metadata, Verified Codebase State, DoD) |

## Context

AI maturity detection relies on a narrow keyword list that misses modern terminology (LLM, GPT, neural, computer vision, NLP). The signal detection in `research/signals.py` and `analytics/ai_readiness.py` underscores companies that are clearly AI-driven but use different terminology. GitHub repos and patents are not used as AI signals.

## Verified Codebase State (2026-04-05)

- `src/solstein/analytics/ai_readiness.py` confirmed: keyword list does not contain "LLM", "GPT", "neural", "computer vision", "NLP", "transformer"
- `src/solstein/research/signals.py` confirmed: AI signal detection uses narrow keyword matching
- No GitHub repo dependency scanning exists for ML framework detection
- No patent-based AI signal exists
- All AI maturity scoring is keyword-frequency-only

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-307](STORIES/STORY-307.md) | Expand AI signal detection: add ML/DL/neural/GPT/LLM/automation/predictive/NLP/computer vision keywords | 🔴 READY | Files: research/signals.py, analytics/ai_readiness.py |
| [STORY-308](STORIES/STORY-308.md) | Use LLM to assess AI maturity from company descriptions and recent news | 🔴 READY | Deps: LLM provider |
| [STORY-309](STORIES/STORY-309.md) | Add GitHub-based AI signals (ML repos, tensorflow/pytorch/sklearn in dependencies) | 🔴 READY | Deps: STORY-290 |
| [STORY-310](STORIES/STORY-310.md) | Add patent-based AI signals (AI/ML patent filings from USPTO) | 🔴 READY | Deps: STORY-291 |

## Success Criteria

- AI maturity score correctly identifies known AI-native energy companies
- GitHub dependency scanning detects ML frameworks in at least 5 test repos
- Patent signals contribute to AI maturity for companies with USPTO filings

## Definition of Done

- [ ] [STORY-307](STORIES/STORY-307.md): `ai_readiness.py` and `signals.py` keyword lists include LLM/GPT/neural/NLP/computer vision
- [ ] [STORY-308](STORIES/STORY-308.md): LLM-based AI maturity assessment produces scores for companies with descriptions
- [ ] [STORY-309](STORIES/STORY-309.md): GitHub adapter detects tensorflow/pytorch/sklearn in repo dependencies
- [ ] [STORY-310](STORIES/STORY-310.md): patent scraper returns AI/ML patent count for test companies
- [ ] `pytest tests/unit/ -k "ai_maturity or ai_readiness"` passes

## Dependencies

- STORY-290 (GitHub adapter) for [STORY-309](STORIES/STORY-309.md)
- STORY-291 (arXiv/patent adapter) for [STORY-310](STORIES/STORY-310.md)
- STORY-321 (LLM provider) for [STORY-308](STORIES/STORY-308.md)
