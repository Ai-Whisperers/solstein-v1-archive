# STORY-140: Fix .env.example with All Required Variables

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-036: Configuration Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-137 |

## The Audit Verdict

> .env.example missing GITHUB_TOKEN (required for startup!), COMPANIES_HOUSE_API_KEY, GOOGLE_API_KEY, EXA_API_KEY, all LLM provider keys (GROQ, FIREWORKS, MISTRAL, DEEPINFRA, GEMINI, NVIDIA, CEREBRAS, KIMI), OLLAMA_URL, OLLAMA_MODEL.

## Problem Statement

The .env.example file is supposed to be the canonical list of environment variables a developer needs. It's incomplete. GITHUB_TOKEN is required for startup but not listed. Most LLM provider keys aren't listed. A new developer following the setup instructions will have a non-functional system because half the required variables are undocumented. The fix is a complete, accurate .env.example with all variables, grouped by purpose, with comments.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Developer Experience** | Incomplete setup instructions |
| **Onboarding** | New developers can't start the system |
| **Operational** | Missing config discovered only at runtime |

## Affected Files

| File | Issue |
|------|-------|
| `.env.example` | Incomplete |

## Architectural Requirements

- All environment variables from config.py listed in .env.example
- Grouped by purpose: Required, Database, External APIs, LLM Providers, Optional/Feature Flags
- Comments explaining each variable
- Example values (not real secrets)
- Placeholder markers for required variables: REQUIRED: set this value
- Validation script: verify .env.example matches config.py (CI check)
- Instructions: how to get API keys for each service

## Acceptance Criteria

- [ ] All config.py settings in .env.example
- [ ] Grouped and commented
- [ ] Required variables marked
- [ ] Validation script passes in CI
- [ ] Setup instructions reference .env.example

## Definition of Done

- **Tests Required**: Validation script
- **Documentation Required**: Complete .env.example with comments
- **Code Review Gate**: New developer can cp .env.example .env, fill in values, and start the system

## Notes

.env.example should be the canonical setup guide.
