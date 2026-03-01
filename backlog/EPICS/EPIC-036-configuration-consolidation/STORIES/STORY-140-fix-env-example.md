# STORY-140: Fix .env.example with All Required Variables

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-036: Configuration Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-137 (Centralize All Environment Variables in config.py) |

---

## The Audit Verdict

> `.env.example` missing `GITHUB_TOKEN` (required for startup!), `COMPANIES_HOUSE_API_KEY`, `GOOGLE_API_KEY`, `EXA_API_KEY`, all LLM provider keys (`GROQ`, `FIREWORKS`, `MISTRAL`, `DEEPINFRA`, `GEMINI`, `NVIDIA`, `CEREBRAS`, `KIMI`), `OLLAMA_URL`, `OLLAMA_MODEL`.

---

## Problem Statement

The `.env.example` file is the canonical onboarding document for a new developer. It is the answer to the question: "What do I need to configure to run this system?" The current `.env.example` answers that question incorrectly. It is missing `GITHUB_TOKEN`, which is required for startup and whose absence causes an immediate failure. It is missing every LLM provider key. It is missing the Ollama configuration. A new developer who follows the documented setup process — copy `.env.example` to `.env`, fill in the values, start the system — will have a non-functional system.

This is not a documentation problem. It is a trust problem. When the setup documentation is wrong, developers stop trusting the documentation. They start reading the source code to understand what the system actually needs. They find the scattered `os.environ.get()` calls that STORY-137 is fixing. They spend hours on setup instead of minutes. The first impression of the codebase is that it is poorly maintained.

The fix is a complete, accurate `.env.example` that reflects every variable defined in `config.py`, grouped by purpose, with comments explaining each variable and instructions for obtaining API keys. The file should be generated from or validated against `config.py` in CI, so it cannot fall out of sync again.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Developer Experience** | Incomplete setup instructions; new developers cannot start the system by following documented process |
| **Onboarding** | Hours of debugging to discover missing variables; erodes confidence in the codebase before any business logic is touched |
| **Operational** | Missing configuration discovered at runtime, not at setup time; production incidents from misconfiguration |
| **Trust** | Inaccurate documentation signals poor maintenance discipline; affects team confidence in other documentation |

---

## Affected Files

| File | Issue |
|------|-------|
| `.env.example` | Missing 15+ required variables; not grouped; no comments; no instructions for obtaining API keys |

---

## Architectural Requirements

- All environment variables defined in `config.py` (after STORY-137 is complete) must appear in `.env.example`
- Variables grouped by purpose with section headers:
  - `# === REQUIRED ===` — variables with no default that must be set
  - `# === Database ===` — PostgreSQL connection strings
  - `# === External APIs ===` — GitHub, Companies House, SEC EDGAR, NewsAPI, Exa, Google
  - `# === LLM Providers ===` — Groq, Fireworks, Mistral, DeepInfra, Gemini, NVIDIA, Cerebras, Kimi, Ollama
  - `# === Celery & Workers ===` — Redis URL, task limits
  - `# === Feature Flags ===` — optional feature toggles
  - `# === Optional / Defaults ===` — variables with sensible defaults that rarely need changing
- Each variable accompanied by a comment explaining: what it controls, where to obtain the value (URL to API key page where applicable)
- Required variables marked with `# REQUIRED: <explanation>` comment
- Example values provided for all variables — realistic but not real secrets (e.g., `your-github-token-here`, `sk-...`)
- Validation script (`scripts/validate_env_example.py`) that:
  - Parses all variable names from `.env.example`
  - Parses all field names from the Pydantic Settings class in `config.py`
  - Fails with a clear error message if any `config.py` field is absent from `.env.example`
  - Runs as a CI step on every pull request
- Developer setup guide updated to reference `.env.example` as the authoritative configuration reference

---

## Acceptance Criteria

- [ ] Every field in the Pydantic Settings class in `config.py` has a corresponding entry in `.env.example`
- [ ] `GITHUB_TOKEN` is present and marked as `# REQUIRED`
- [ ] All LLM provider keys present: `GROQ_API_KEY`, `FIREWORKS_API_KEY`, `MISTRAL_API_KEY`, `DEEPINFRA_API_KEY`, `GEMINI_API_KEY`, `NVIDIA_API_KEY`, `CEREBRAS_API_KEY`, `KIMI_API_KEY`
- [ ] `OLLAMA_URL` and `OLLAMA_MODEL` present with example values
- [ ] Variables grouped by purpose with section headers
- [ ] Every variable has a comment explaining its purpose
- [ ] Required variables marked with `# REQUIRED:` comment
- [ ] Validation script (`scripts/validate_env_example.py`) exists and passes
- [ ] Validation script runs in CI and fails the build if `.env.example` is out of sync with `config.py`
- [ ] Developer setup guide references `.env.example` as the authoritative configuration reference

---

## Definition of Done

- **Tests Required**: The validation script itself is the primary test artifact. It must parse both `config.py` and `.env.example` and produce a clear diff of any missing variables. The script must exit with a non-zero code on mismatch. CI must run the script and fail the build on non-zero exit.
- **Documentation Required**: `.env.example` is itself the documentation artifact. Developer setup guide updated with instruction: "Copy `.env.example` to `.env` and fill in the required values. See comments in `.env.example` for instructions on obtaining each API key."
- **Code Review Gate**: Reviewer performs the new developer simulation: copy `.env.example` to `.env`, fill in placeholder values, attempt to start the system. Reviewer confirms the system starts (or fails with a clear, actionable error message for any missing required variable — not a silent failure). Reviewer runs the validation script and confirms it passes.

---

## Notes

This story has a hard dependency on STORY-137. The `.env.example` cannot be complete until `config.py` is complete. Attempting to write `.env.example` before STORY-137 is done will result in an incomplete file that needs to be rewritten. Do not start this story until STORY-137 is merged.

The validation script should be simple and robust. It does not need to understand Pydantic internals — it can parse the `config.py` file as text, extract field names from the Settings class, and compare them against the variable names in `.env.example`. A false positive (flagging a field that doesn't need to be in `.env.example`) is acceptable and can be handled with an explicit exclusion list. A false negative (missing a required variable) is not acceptable.

The `.env.example` file should never contain real secrets, even for development. Example values should be clearly fake: `your-github-token-here`, `sk-groq-your-key-here`, `postgresql://user:password@localhost:5432/solstein`. Real secrets committed to the repository are a security incident, not a convenience.
