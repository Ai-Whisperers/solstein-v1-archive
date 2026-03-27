# Field Lineage: Ingestion to Export

**Last Updated**: 2026-03-27
**Schema Version**: 1.0
**Reflects**: Post-STORY-125/126/127 architecture

This document traces every domain model field from its source adapter through to its export destination. See `docs/diagrams/field-data-flow.md` for the visual data flow.

---

## Field Lineage Table

### Identity & Metadata

| Field | Domain Model | Source Adapter | Analytics Consumer | Export Sheet | Export Header | Notes |
|-------|-------------|----------------|-------------------|-------------|---------------|-------|
| `id` | Company | All adapters | All | Not exported | — | Internal identifier |
| `tenant_id` | Company | System (EPIC-019) | Tenant isolation | Not exported | — | Multi-tenancy scoping |
| `name` | Company | All adapters | All | Executive Summary, Market Rankings, Financial Intelligence, Revenue History, Advanced Data | Company | Primary display name |
| `company_name` | Company | Legacy adapters | None | Not exported | — | Deprecated alias for name |
| `industry` | Company | Web Research, Manual | Classification | Executive Summary | Industry | Industry classification |
| `description` | Company | Web Research, Crunchbase | None | Not exported | — | Free-text company description |
| `website` | Company | Web Research | None | Not exported | — | Company website URL |
| `headquarters` | Company | Web Research, CH | None | Not exported | — | HQ location |
| `founded_year` | Company | Web Research, CB | None | Not exported | — | Year founded |
| `last_updated` | Company | System | None | Not exported | — | Last data refresh timestamp |
| `data_source` | Company | System | None | Not exported | — | Primary data source identifier |
| `notes` | Company | Manual | None | Advanced Data | Notes | Analyst notes |
| `source_links` | Company | All adapters | None | Advanced Data | Source Links | URLs rendered as hyperlinks |

### Financial Metrics (FinancialMetric — canonical source, STORY-127)

| Field | Domain Model | Source Adapter | Analytics Consumer | Export Sheet | Export Header | Notes |
|-------|-------------|----------------|-------------------|-------------|---------------|-------|
| `financials.revenue` | FinancialMetric | SEC EDGAR, CH, Web | Scoring, Growth | Financial Intelligence | Revenue (€M) | Via `revenue_eur_m` accessor |
| `financials.profit_margin` | FinancialMetric | SEC EDGAR, CH | Scoring | Financial Intelligence | Profit Margin | Canonical source (STORY-127) |
| `financials.employees` | FinancialMetric | Web Research, LinkedIn | Scoring | Market Rankings | Employees | Canonical source (STORY-127) |
| `financials.growth_rate` | FinancialMetric | Computed | Scoring, Growth | Executive Summary, Market Rankings, Financial Intelligence | Growth / Growth Rate | Revenue growth rate |
| `financials.ebitda_margin` | FinancialMetric | SEC EDGAR | Scoring | Not exported | — | Internal financial metric |
| `financials.recurring_revenue_pct` | FinancialMetric | SEC EDGAR, Manual | Scoring | Not exported | — | SaaS metric |
| `financials.funding_raised` | FinancialMetric | Crunchbase | None | Not exported | — | Raw funding, use total_funding_raised_eur |
| `financials.valuation` | FinancialMetric | Crunchbase | None | Not exported | — | Raw valuation, use latest_valuation_eur |
| `financials.revenue_confidence` | FinancialMetric | All adapters | None | Not exported | — | ConfidenceLevel enum for revenue |
| `financials.growth_confidence` | FinancialMetric | All adapters | None | Not exported | — | ConfidenceLevel enum for growth_rate |
| `financials.employees_confidence` | FinancialMetric | All adapters | None | Not exported | — | ConfidenceLevel enum for employees |
| `financials.margin_confidence` | FinancialMetric | All adapters | None | Not exported | — | ConfidenceLevel enum for profit_margin |
| `financials.funding_confidence` | FinancialMetric | All adapters | None | Not exported | — | ConfidenceLevel enum for funding_raised |
| `financials.valuation_confidence` | FinancialMetric | All adapters | None | Not exported | — | ConfidenceLevel enum for valuation |

### Company-Level Financial Fields

| Field | Domain Model | Source Adapter | Analytics Consumer | Export Sheet | Export Header | Notes |
|-------|-------------|----------------|-------------------|-------------|---------------|-------|
| `financials` | Company | All adapters | Scoring, Growth | — | — | Reference to FinancialMetric sub-model (STORY-127) |
| `revenue` | Company | Legacy | None | Not exported | — | Use financials.revenue |
| `employees` | Company (computed) | Delegates to FinancialMetric | — | — | — | Read-only computed property (STORY-127) |
| `growth_rate` | Company | Legacy | None | Not exported | — | Use financials.growth_rate |
| `profit_margin` | Company (computed) | Delegates to FinancialMetric | — | — | — | Read-only computed property (STORY-127) |
| `employee_count` | Company (computed) | Delegates to FinancialMetric | — | — | — | Read-only computed property (STORY-127) |
| `funding` | Company | Legacy | None | Not exported | — | Use total_funding_raised_eur |
| `valuation` | Company | Legacy | None | Not exported | — | Use latest_valuation_eur |
| `ebitda_margin` | Company | SEC EDGAR | Scoring | Not exported | — | Duplicates financials field |
| `recurring_revenue_pct` | Company | SEC EDGAR, Manual | Scoring | Not exported | — | Duplicates financials field |
| `revenue_per_employee_eur_k` | Company | Computed | None | Financial Intelligence | Revenue/Employee (€K) | Derived metric |
| `revenue_timeline` | Company | SEC EDGAR, Web | None | Revenue History | Year, Revenue (EUR M), Source | Time-series, one row per entry |
| `revenue_cagr_3yr` | Company | Computed | Scoring | Not exported | — | 3-year revenue CAGR |
| `revenue_cagr_5yr` | Company | Computed | None | Financial Intelligence | Revenue CAGR 5yr | 5-year revenue CAGR |
| `total_funding_raised_eur` | Company | Crunchbase, Manual | None | Financial Intelligence | Total Funding | Total funding in EUR |
| `latest_valuation_eur` | Company | Crunchbase, Manual | None | Financial Intelligence | Latest Valuation | Latest known valuation |
| `lead_investors` | Company | Crunchbase | None | Financial Intelligence | Investors | Comma-separated list |
| `funding_rounds` | Company | Crunchbase | None | Financial Intelligence | Funding Rounds | Structured text (round: amount) |
| `funding_war_chest` | Company | Computed/Manual | None | Financial Intelligence | Funding War Chest | Runway/availability status |
| `employee_cagr_3yr` | Company | Computed | Scoring | Financial Intelligence | Employee CAGR 3yr | 3-year employee CAGR |
| `open_positions` | Company | LinkedIn, Web | Signal Detection | Executive Summary | Open Positions | Current open job count |
| `profitability_raw_metrics` | Company | SEC EDGAR | Scoring | Not exported | — | Raw profitability data dict |

### Technology & Market

| Field | Domain Model | Source Adapter | Analytics Consumer | Export Sheet | Export Header | Notes |
|-------|-------------|----------------|-------------------|-------------|---------------|-------|
| `ai_maturity` | Company | Computed | AI Scoring | Not exported | — | Enum: NONE/EXPLORING/ADOPTING/ADVANCED/LEADING |
| `saas_maturity` | Company | Manual/Computed | Scoring | Not exported | — | Integer 1-5 scale |
| `tech_stack` | Company | Web Research, GitHub | Signal Detection | Executive Summary | Tech Stack | Comma-separated list |
| `geographic_presence` | Company | Web Research | None | Not exported | — | List of countries/regions |
| `key_customers` | Company | Web Research, Manual | None | Executive Summary | Key Customers | Comma-separated list |

### Corporate Structure

| Field | Domain Model | Source Adapter | Analytics Consumer | Export Sheet | Export Header | Notes |
|-------|-------------|----------------|-------------------|-------------|---------------|-------|
| `parent_company` | Company | Crunchbase, Manual | None | Advanced Data | Parent Company | Parent company name |
| `subsidiaries` | Company | Crunchbase, Manual | None | Advanced Data | Subsidiaries | Comma-separated list |
| `acquisitions` | Company | Crunchbase, News | None | Advanced Data | Acquisitions | Structured text |

### Scoring & Classification (Analytics Outputs)

| Field | Domain Model | Source Adapter | Analytics Consumer | Export Sheet | Export Header | Notes |
|-------|-------------|----------------|-------------------|-------------|---------------|-------|
| `ai_score` | Company | AI Scoring Engine | Classification | Executive Summary | AI Score | 0-10 scale |
| `ai_signal_level` | Company | Signal Detection | None | Not exported | — | Internal signal level |
| `ai_key_capabilities` | Company | AI Scoring Engine | None | Not exported | — | Free-text AI capabilities |
| `ai_in_production` | Company | Signal Detection | AI Scoring | Not exported | — | Boolean: AI in production use |
| `composite_score` | Company | Scoring Engine | Classification | Not exported | — | Aggregate composite score |
| `competitive_position_score` | Company | Scoring Engine | Classification | Market Rankings | Competitive Score | Position score |
| `financial_health_score` | Company | Scoring Engine | None | Not exported | — | Financial health metric |
| `growth_score` | Company | Scoring Engine | None | Not exported | — | Growth metric |
| `classification` | Company | Classification Engine | Export (row coloring) | Not exported (drives row colors) | — | phoenix/salt/lead |
| `threat_level` | Company | Derived from classification | None | Executive Summary | Threat Level | Competitive threat |
| `tier` | Company | Classification Engine | None | Executive Summary | Tier | Company tier |
| `scoring_breakdown` | Company | Scoring Engine | None | Not exported | — | Detailed scoring breakdown dict |
| `market_share_pct` | Company | Computed | None | Market Rankings | Market Share | Estimated market share |

### Data Quality & Provenance

| Field | Domain Model | Source Adapter | Analytics Consumer | Export Sheet | Export Header | Notes |
|-------|-------------|----------------|-------------------|-------------|---------------|-------|
| `data_availability` | Company | System | None | Executive Summary | Data Availability | Data quality status |
| `metric_sources` | Company | All adapters | None | Advanced Data | Data Sources Per Field | Maps field→sources |
| `metric_justifications` | Company | LLM/Manual | None | Not exported | — | Justification text per metric |
| `metric_observations` | Company | All adapters | None | Not exported | — | Raw observations per metric |
| `signal_confidences` | Company | Signal Detection | None | Not exported | — | Confidence per signal |
| `confidence_scores` | Company | All adapters | None | Not exported | — | General confidence scores |
| `enrichment_source_count` | Company | System | None | Not exported | — | Number of enrichment sources |
| `enrichment_quality_metrics` | Company | System | None | Advanced Data (merge_conflicts) | Merge Conflicts | Quality metrics dict |
| `data_quality_tier` | Company | System | None | Not exported | — | unknown/bronze/silver/gold |
| `data_source_type` | Company | System | None | Not exported | — | synthetic/real/mixed/unknown |
| `enrichment_sources` | Company | System | None | Not exported | — | List of enrichment sources |
| `enrichment_timestamps` | Company | System | None | Not exported | — | Timestamps per enrichment |
| `enrichment_errors` | Company | System | None | Not exported | — | Error list |
| `enrichment_error_count` | Company | System | None | Not exported | — | Error count |
| `enrichment_error_categories` | Company | System | None | Not exported | — | Error category breakdown |
| `enrichment_error_timestamps` | Company | System | None | Not exported | — | Error timestamps |
| `enrichment_errors_per_field` | Company | System | None | Not exported | — | Errors per field |

### External Identifiers

| Field | Domain Model | Source Adapter | Analytics Consumer | Export Sheet | Export Header | Notes |
|-------|-------------|----------------|-------------------|-------------|---------------|-------|
| `ticker` | Company | SEC EDGAR, Manual | SEC lookups | Not exported | — | Stock ticker symbol |
| `company_number` | Company | Companies House | CH lookups | Not exported | — | UK company registration number |
| `isin` | Company | Manual | None | Not exported | — | International Securities ID |
| `geography_code` | Company | Computed | None | Not exported | — | ISO country code |

---

## Current Gaps

Fields present in the domain model but intentionally not exported:

| Field | Justification |
|-------|---------------|
| `id`, `tenant_id` | Internal system identifiers, not relevant to analyst deliverable |
| `company_name` | Deprecated alias for `name`, retained for backward compatibility only |
| `description` | Free-text, too long for Excel cells; available in UI |
| `website`, `headquarters`, `founded_year` | Could be exported in future; low priority for PE/VC analysts who source this independently |
| `data_source`, `data_source_type`, `data_quality_tier` | Internal data quality metadata |
| `ai_maturity`, `saas_maturity` | Internal enum/scale; `ai_score` is the exported metric |
| `ai_signal_level`, `ai_key_capabilities`, `ai_in_production` | Internal AI assessment details; `ai_score` summarizes |
| `composite_score`, `financial_health_score`, `growth_score` | Internal scoring components; final scores are exported |
| `scoring_breakdown` | Detailed breakdown dict; too complex for Excel |
| `classification` | Internal enum used for row coloring, not a direct column |
| `geographic_presence` | List of regions; could be exported in future |
| `ebitda_margin`, `recurring_revenue_pct` (Company-level) | Duplicate of FinancialMetric fields; internal use only |
| `revenue`, `growth_rate`, `funding`, `valuation` (Company-level) | Legacy fields, superseded by financials.* and *_eur fields |
| `revenue_cagr_3yr` | Internal metric; 5yr CAGR exported instead |
| `profitability_raw_metrics` | Raw data dict; derived metrics exported |
| `metric_justifications`, `metric_observations`, `signal_confidences`, `confidence_scores` | Internal provenance metadata |
| `enrichment_*` (8 fields) | Internal enrichment tracking metadata |
| `ticker`, `company_number`, `isin`, `geography_code` | External identifiers for connector lookups; not analyst-facing |
| `market_share_pct` | Exported on Market Rankings sheet (not a gap) |

**Potential gaps requiring future decision:**
- `website`, `headquarters`, `founded_year` — commonly requested by analysts but currently not exported
- `geographic_presence` — relevant for international market analysis
- `description` — could be truncated and exported

---

## Changelog

| Date | Change |
|------|--------|
| 2026-03-27 | Initial lineage document created (STORY-128). Covers all 76 Company fields + 3 computed fields + 21 FinancialMetric fields (including 6 confidence-level fields). |
