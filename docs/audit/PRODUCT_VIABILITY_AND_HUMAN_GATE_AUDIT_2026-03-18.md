# Solstein Product Viability & Human-Gated Quality Audit — 2026-03-18

## Scope

Assess whether Solstein can become a sellable/marketable market intelligence product, and identify the critical quality surfaces that **must** remain under human expert oversight — even when built or extended with AI — to avoid business and reputational harm.

Evidence drawn from: pipeline architecture (`src/solstein/research/pipeline.py`), scoring engine (`src/solstein/analytics/scoring.py`), classification logic (`src/solstein/analytics/classification.py`), contradiction detection (`src/solstein/research/reconcile.py`), report release gate (`src/solstein/data/report_release_gate.py`), adjudication system (`src/solstein/data/adjudication.py`), AI report generation (`src/solstein/intelligence/ai_report_generator.py`), and historical audit trail (`docs/archive/audits/GESTALT_IMPROVEMENTS_2026-02-26.md`).

---

## Part 1: Product Viability Assessment

### Can It Become Sellable?

**Yes — but only with specific conditions met.**

Solstein has genuine product-market fit potential in the PE/VC/family-office segment. It is not a science project and not a generic dashboard. The end-to-end capability — from market seed company to scored, classified, contradiction-detected, human-reviewed company profiles exported to Excel/JSON — is a coherent workflow that buyers in this segment pay real money for (PitchBook: $15K–$25K+/seat/year; CB Insights: comparable; Bloomberg: enterprise).

### Top 5 Value Propositions

| # | Value Prop | Evidence |
|---|-----------|----------|
| 1 | **Multi-source convergence with provenance** — data from 8+ enrichment sources (SEC EDGAR, Companies House, GitHub, Patents, News, Funding, Web, LinkedIn) with per-field source attribution tracked at the boundary. File: `src/solstein/data/report_release_gate.py` (lines 17, 180–201). |
| 2 | **Contradiction detection on critical claims** — automatic flagging when revenue, employee_count, funding_total, or valuation diverge >20% across sources without human adjudication. File: `src/solstein/research/reconcile.py` (lines 24–69). Critical claim list: `src/solstein/data/report_release_gate.py` (line 17). |
| 3 | **Structured adjudication workflow** — unresolved contradictions block scoring and export; approved/override decisions are persisted with actor, timestamp, reason, and decision ID. Files: `src/solstein/data/adjudication.py`, `src/solstein/api/routers/scoring.py` (lines 79–124). |
| 4 | **Composite scoring with confidence-weighted signal attribution** — growth, financial health, and competitive position scores weighted and re-weighted by signal-level confidence. File: `src/solstein/analytics/scoring.py` (lines 61–96, 142–215). |
| 5 | **AI-native assessment engine** — structured scoring of company AI maturity across 8 capability domains with evidence-based confidence. File: `src/solstein/intelligence/ai_report_generator.py` (full module). |

### Top 5 Product Risks

| # | Risk | Severity | Evidence |
|---|------|----------|----------|
| 1 | **Unstable core quality surface** — 122 test failures at last full run (86% pass rate). Critical path tests for enrichment, scoring, and classification are among failures. File: `docs/archive/audits/TEST_FAILURE_ANALYSIS_2026-02-26.md`. | HIGH | A product with failing tests on its core logic cannot be sold as reliable. |
| 2 | **MarketAnalyzer generates templated, not derived, recommendations** — SWOT analysis, trends, and recommendations are hardcoded strings with minimal data derivation. File: `src/solstein/analytics/scoring.py` (lines 269–416). Buyer discovery: this is the first thing a VP reads. | HIGH | Misleading narrative recommendations are the fastest path to destroying buyer trust. |
| 3 | **Classification boundary zones have no mandatory human review** — scores near 5.5 (Salt/Lead) and 7.0–7.5 (Salt/Phoenix) are explicitly lower-confidence zones (classification confidence drops to 0.7 near boundaries), yet no mandatory human gate is enforced at these transitions. File: `src/solstein/analytics/classification.py` (lines 69–78). | HIGH | Wrong classification at boundary = wrong investment thesis for buyer. |
| 4 | **Scoring degrades silently to base scores** — `GrowthScorer.calculate_scores` wraps all three sub-scorers in bare `except` blocks that fall back to base scores with only a `logger.warning`. File: `src/solstein/analytics/scoring.py` (lines 161–180). A company can be fully mis-scored with no observable failure signal. | HIGH | Silent degradation means a buyer could act on confidently-wrong data. |
| 5 | **Release gate has a bypass flag** — `skip_gate=True` on `ReportReleaseGate` returns `passed=True` while collecting all failure reasons. Used in `src/solstein/data/report_release_gate.py` (lines 286–288). If this flag is ever set in production config, bad data reaches the export. | HIGH | A hardcoded bypass in the last line of defense is a business risk, not just a code risk. |

### Verdict

**Advisor-grade, not investor-grade — yet.**  
Solstein produces structured intelligence that a human analyst can act on with appropriate skepticism. It is not ready to be the sole input to an investment decision without human expert review of: boundary classifications, contradiction-adjudicated claims, and any auto-generated narrative sections. This is acceptable as a positioning statement ("AI-assisted research platform") but NOT acceptable as "AI-driven investment intelligence" without the human gates described in Part 2.

---

## Part 2: Critical Quality Surfaces — Non-Negotiable Human Gates

These surfaces MUST have human expert oversight before AI-generated output reaches the buyer. Failure at any of these causes direct business or reputational harm.

### Gate 1: Classification at Boundary Zones (HIGHEST PRIORITY)

- **File**: `src/solstein/analytics/classification.py` (lines 69–78)
- **Risk**: Scores between 5.4–5.6 (Salt/Lead) and 6.9–7.1 (Salt/Phoenix) receive explicit lower confidence (0.7). Scores in these bands are silently labeled with the same classification as stable scores.
- **Why human gate is non-negotiable**: A Phoenix classification triggers different buyer actions than Salt. Boundary misclassification at 0.7 confidence means the system is saying "I'm not sure" but treating the output as certain.
- **Required action**: Add a mandatory `boundary_review_required` flag on any company where `5.4 <= composite_score <= 5.6 or 6.9 <= composite_score <= 7.1`. Block export of those profiles unless a human adjudicator explicitly approves the classification with a reason.

### Gate 2: Critical Claim Contradiction Resolution (HIGHEST PRIORITY)

- **Files**: `src/solstein/research/reconcile.py` (lines 24–69), `src/solstein/data/report_release_gate.py` (lines 203–251)
- **Risk**: A 20%+ divergence on revenue, employee_count, funding_total, or valuation across sources triggers `critical_claim_contradiction` code. The gate blocks export — but only if `allow_synthetic=False` (which it is by default). The gate is bypassable.
- **Why human gate is non-negotiable**: If a buyer acts on a $50M revenue figure that contradicts a $200M figure from another source, and that contradiction was never adjudicated, the buyer has been misled by the platform's authority.
- **Required action**: Every `critical_claim_contradiction` event must produce an explicit adjudication record with: actor, timestamp, decision reason, and the specific evidence each decision was based on. No `critical_claim_contradiction` may be in a final export without this record.

### Gate 3: Scoring Degradation Silently Defaults to Base Scores

- **File**: `src/solstein/analytics/scoring.py` (lines 161–180)
- **Risk**: Three bare `except` blocks each catch scoring failures and silently return base scores with only a `loguru` warning. No alerting, no gate emission, no fail-fast.
- **Why human gate is non-negotiable**: A company whose growth score fails silently returns a default score. The composite score is computed and looks legitimate. The classification is derived. The buyer sees a complete-looking profile with no indication that the core scoring failed.
- **Required action**: Replace silent fallback with an explicit `scoring_degraded` flag on the company profile, add this to the gate reason taxonomy, and surface it prominently in export metadata. The `ReportReleaseGate` already has a `warn_mode` — wire this signal into it.

### Gate 4: Adjudication Decision Integrity

- **Files**: `src/solstein/data/adjudication.py` (lines 40–85), `src/solstein/api/routers/scoring.py` (lines 79–124)
- **Risk**: Adjudication decisions are encoded as `key=value;key=value` strings in `metric_justifications` with no schema validation. Any actor string is accepted. No cryptographic or audit-log integrity on the decision record.
- **Why human gate is non-negotiable**: An adjudicated decision overrides the gate and allows bad data into the export. If that decision is made without expert review, or if the record is later tampered with, the buyer has no recourse.
- **Required action**: Add schema validation on `AdjudicationDecision` fields (actor must be a known user ID; reason must be ≥20 characters; value must match the metric type). Add an append-only adjudication audit log with hash chain integrity.

### Gate 5: AI Narrative Report Generation

- **File**: `src/solstein/intelligence/ai_report_generator.py` (lines 1–572)
- **Risk**: The report generator produces structured markdown narratives including: strategic priority ratings, capability assessments, competitive positioning, maturity narratives, and recommendations — all from pattern-matched public data.
- **Specific hazards**:
  - Lines 226–240: Use case categories are hardcoded for energy sector regardless of actual company domain.
  - Lines 269–289: Maturity narrative stages are templated, not derived from evidence.
  - Lines 326–380: Recommendations are templated per signal level, not generated from actual assessment data.
  - Methodology section (lines 382–440): explicitly states limitations including "false negatives," "signal ambiguity," and "evidence dependency" — yet these caveats appear only in a buried methodology section, not as first-class warnings on the report itself.
- **Why human gate is non-negotiable**: LLM-generated text about a company's strategic posture, competitive risks, and investment recommendations is the highest-risk output category. One confident-sounding but wrong recommendation can destroy buyer trust faster than any data quality issue.
- **Required action**: Every AI-generated narrative section must carry an explicit confidence qualifier at the section level (not buried in methodology), must be flagged as "AI-assisted" in the export metadata, and must include the raw evidence list that informed the narrative so a human can verify the chain.

### Gate 6: Export Release Gate Bypass Flag

- **File**: `src/solstein/data/report_release_gate.py` (lines 286–288)
- **Risk**: `skip_gate=True` returns `passed=True` with all failure reasons collected but suppressed. Any code path that sets this flag in config silently sends incomplete data to buyers.
- **Why human gate is non-negotiable**: This is a backdoor in the last line of defense. In a sales context, this bypass means a buyer could receive a report marked "passed" that actually failed provenance, contradiction, and completeness checks.
- **Required action**: Remove `skip_gate` from production paths entirely, or require it to emit a separate `gate_bypassed` artifact with full reason dump and a signed human override record.

### Gate 7: Source Authority in Conflict Resolution

- **File**: `src/solstein/infrastructure/conflict_resolution.py`
- **Risk**: When multiple sources disagree on a metric, a `SourceAuthority` hierarchy determines which wins. If that hierarchy is wrong or outdated, bad data wins silently.
- **Why human gate is non-negotiable**: Buyers use Solstein reports to make investment decisions. If SEC EDGAR (authoritative) is accidentally ranked below a web scrape, a mis-scraped figure becomes the authoritative figure.
- **Required action**: Expose the authority resolution trace in export metadata. Every contested metric in the final report must list: winning source, losing sources, and the authority gap (difference between values).

---

## Part 3: What Must Be True Before Go-to-Market

| Condition | Current State | Action Required |
|-----------|--------------|-----------------|
| Core test pass rate ≥95% | ~86% | Fix missing pytest-asyncio, pytest-httpx, fix broken assertions. Priority: immediate. |
| Silent scoring degradation produces observable signal | Silent fallback to base score | Add `scoring_degraded` flag, wire to gate, surface in export. |
| Boundary classifications require human review | No enforcement | Add `boundary_review_required` flag, block export without approval. |
| AI narratives carry first-class confidence qualifiers | Caveats buried in methodology | Move confidence qualifier to section header of each narrative. |
| `skip_gate` removed from production paths | Exists in `ReportReleaseGate` | Remove or require signed override record. |
| Adjudication decisions have integrity | Plain string encoding | Add schema validation and audit log with hash chain. |
| MarketAnalyzer recommendations are data-derived | Hardcoded template strings | Either derive from actual data or clearly label as "analyst template." |

---

## Part 4: Honest Positioning Statement

**Can sell:** "Solstein is an AI-assisted market intelligence platform that automates company discovery, multi-source enrichment, and structured scoring — with built-in contradiction detection and human review workflows for critical claims."

**Cannot sell (yet):** "Solstein provides investment-grade intelligence with AI-generated recommendations."

The current state is a strong foundation with specific, fixable correctness and governance gaps. The product is viable. The path to market requires fixing the gates in Part 3 first, not marketing around them.

---

*Audit by Sisyphus — 2026-03-18. Evidence files: src/solstein/research/pipeline.py, src/solstein/analytics/scoring.py, src/solstein/analytics/classification.py, src/solstein/research/reconcile.py, src/solstein/data/report_release_gate.py, src/solstein/data/adjudication.py, src/solstein/intelligence/ai_report_generator.py, docs/archive/audits/GESTALT_IMPROVEMENTS_2026-02-26.md, docs/archive/audits/TEST_FAILURE_ANALYSIS_2026-02-26.md.*
