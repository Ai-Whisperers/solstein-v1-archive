## 2026-02-24 Baseline test issue: CLI/markdown extractor circular import
- `pytest tests/unit/test_cli_coverage.py` fails during collection with circular import:
  `solstein.cli -> markdown_extractor -> solstein.research -> pipeline -> markdown_extractor`.
- This appears pre-existing (fails even when stashing pipeline changes).
- Track as blocker for final verification wave; may need to make `solstein.research` package lazy-import safe (e.g., remove `from .pipeline import run_market_intelligence` in `src/solstein/research/__init__.py`).

## 2026-02-24 Resolved: CLI/markdown extractor circular import
- Fixed by making `src/solstein/research/__init__.py` lazy via `__getattr__` (no eager `.pipeline` import).
- Verified: `python -m pytest tests/unit/test_cli_coverage.py -q` and `python -m pytest tests/unit/test_markdown_extractor_coverage.py -q` both pass.
