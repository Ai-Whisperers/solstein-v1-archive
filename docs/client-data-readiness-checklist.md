# Client Data Readiness Checklist

Use this checklist before generating any client-facing report.

## 1) Data source policy

- [ ] Input dataset is real-data only (`data_source_type != "synthetic"` for all companies)
- [ ] Synthetic fixtures are only under `tests/fixtures/**`
- [ ] Report run uses `data/input/competitor_data_real_enriched.json` (or approved real equivalent)

## 2) Required identifiers per company

- [ ] At least one of: `ticker`, `company_number`, `isin`, `lei`
- [ ] `identifier_confidence` recorded
- [ ] Identifier cache present and updated: `data/output/identifier_cache.json`

## 3) Required PE financial fields per company

- [ ] `revenue`
- [ ] `employees`
- [ ] `growth_rate`
- [ ] `profit_margin`
- [ ] `funding_raised`
- [ ] `valuation`

If any field is missing, company must remain in `data/output/research_queue.json` and report generation must stay blocked.

## 4) Evidence quality

- [ ] Each key metric has source and confidence
- [ ] Metric units are normalized (revenue/funding/valuation in millions; growth/margin in percent)
- [ ] No unresolved unit ambiguity flags

## 5) Environment and credentials

- [ ] `OPENFIGI_API_KEY` configured
- [ ] `COMPANIES_HOUSE_API_KEY` configured (if UK coverage needed)
- [ ] `NEWS_API_KEY` configured
- [ ] Optional premium provider key configured (Crunchbase/PitchBook/Orbis/CapIQ) for private-company coverage

## 6) Execution pipeline

- [ ] Run `scripts/auto_enrich_real_data.py`
- [ ] Confirm queue shrinks and missing counts improve
- [ ] Run scoring/export pipeline
- [ ] Confirm client report gate passes

## 7) Final release checks

- [ ] Report generation command succeeds without readiness errors
- [ ] Output artifacts exist and are non-empty
- [ ] Audit trail recorded in session notes/issues
