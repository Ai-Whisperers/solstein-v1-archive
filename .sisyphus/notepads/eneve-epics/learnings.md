# Learnings - ENEVE Epics

## 2026-03-01 Session Start

### Key Architecture Facts
- `classify_company()` in scoring.py already uses PHOENIX_SCORE_THRESHOLD/LEAD_SCORE_THRESHOLD constants (NOT a bug)
- `run_eneve_199.py` lines 287-289 use HARDCODED thresholds (7.0, 4.0) — NEEDS FIX
- Constants: Phoenix >= 7.5, Salt 4.5–7.49, Lead < 4.49
- Scoring: composite = growth*0.4 + financial*0.3 + competitive*0.3
- All scoring starts from cfg.base_score, adds bonuses — no strong negative paths = score inflation

### File Locations
- Scoring: `src/solstein/analytics/scoring.py`
- Constants: `src/solstein/analytics/constants.py`
- Main pipeline: `scripts/run_eneve_199.py`
- Synthetic generator: `scripts/generate_synthetic_companies.py`
- Excel exporter: `src/solstein/exporters/excel_improved.py`
- Company model: `src/solstein/domain/models.py`
- Validation: `src/solstein/validation/company_validator.py`

### Coding Conventions
- Type hints required everywhere
- Google-style docstrings
- Line length: 120 chars (black)
- loguru for logging: `from loguru import logger`
- PYTHONPATH must include src/: `export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"`
- Run scripts via: `python scripts/run_eneve_199.py`

### Critical Bug Pattern
- Do NOT use bare `except:` — always `except SpecificError as e:`
- Do NOT silently swallow errors

### Git Convention
- Commit with `--no-verify` (pre-commit hooks broken)
- Push to `origin master`
- Conventional commits: `fix:`, `feat:`, `refactor:`, `test:`, `docs:`
