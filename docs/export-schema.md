# Excel Export Schema

**STORY-125**: Restored 20 dropped fields to Excel export.
**Last Updated**: 2026-03-27

## Sheet Overview

| Sheet | Purpose | Columns |
|-------|---------|---------|
| Executive Summary | High-level company overview and scoring | 11 |
| Market Rankings | Competitive position rankings | 6 |
| Financial Intelligence | Revenue, funding, and efficiency metrics | 12 |
| Revenue History | Time-series revenue data (one row per company-year) | 4 |
| Advanced Data | Corporate structure, provenance, and notes | 8 |
| Export Metadata | (optional) Export run metadata | 2 |

## Executive Summary Sheet

| Column | Header | Source Field | Data Type | Notes |
|--------|--------|-------------|-----------|-------|
| A | Company | `name` | string | Company name |
| B | Industry | `industry` | string | Industry classification |
| C | Revenue (€M) | `financials.revenue_eur_m` | number | Revenue in EUR millions |
| D | Growth | `financials.growth_rate_pct` | percentage | Revenue growth rate |
| E | AI Score | `ai_score` | number | AI maturity score (0-10) |
| F | Tier | `tier` | string | Company tier classification |
| G | Threat Level | `threat_level` | string | Competitive threat level |
| H | Tech Stack | `tech_stack` | comma-separated list | Technologies used |
| I | Key Customers | `key_customers` | comma-separated list | Major customer names |
| J | Open Positions | `open_positions` | integer | Currently open job positions |
| K | Data Availability | `data_availability` | string | Data quality/availability status |

## Market Rankings Sheet

| Column | Header | Source Field | Data Type | Notes |
|--------|--------|-------------|-----------|-------|
| A | Rank | (computed) | integer | Rank by competitive score |
| B | Company | `name` | string | Company name |
| C | Market Share | `market_share_pct` | percentage | Estimated market share |
| D | Competitive Score | `competitive_position_score` | number | Composite competitive score |
| E | Growth Rate | `financials.growth_rate_pct` | percentage | Revenue growth rate |
| F | Employees | `employee_count` | integer | Total employee count |

## Financial Intelligence Sheet

| Column | Header | Source Field | Data Type | Notes |
|--------|--------|-------------|-----------|-------|
| A | Company | `name` | string | Company name |
| B | Revenue (€M) | `financials.revenue_eur_m` | number | Revenue in EUR millions |
| C | Growth Rate | `financials.growth_rate_pct` | percentage | Revenue growth rate |
| D | Profit Margin | `financials.profit_margin_pct` | percentage | Profit margin (canonical via FinancialMetric) |
| E | Total Funding | `financials.total_funding_raised_eur` | number | Total funding raised in EUR |
| F | Latest Valuation | `financials.latest_valuation_eur` | number | Latest valuation in EUR |
| G | Investors | `lead_investors` | comma-separated list | Lead investor names |
| H | Funding Rounds | `funding_rounds` | structured text | Funding round summaries (stage: amount) |
| I | Funding War Chest | `funding_war_chest` | string | Funding availability/runway status |
| J | Revenue CAGR 5yr | `revenue_cagr_5yr` | percentage | 5-year revenue CAGR |
| K | Revenue/Employee (€K) | `revenue_per_employee_eur_k` | number | Revenue per employee in EUR thousands |
| L | Employee CAGR 3yr | `employee_cagr_3yr` | percentage | 3-year employee count CAGR |

## Revenue History Sheet

| Column | Header | Source Field | Data Type | Notes |
|--------|--------|-------------|-----------|-------|
| A | Company | `name` | string | Company name (repeated per year) |
| B | Year | `revenue_timeline[].year` | integer | Fiscal year |
| C | Revenue (EUR M) | `revenue_timeline[].eur_millions` | number | Revenue in EUR millions |
| D | Source | `revenue_timeline[].source` | string | Data source for this data point |

One row per company-year combination. Companies with no revenue timeline get a single row with N/A values.

## Advanced Data Sheet

| Column | Header | Source Field | Data Type | Notes |
|--------|--------|-------------|-----------|-------|
| A | Company | `name` | string | Company name |
| B | Parent Company | `parent_company` | string | Parent company name (if subsidiary) |
| C | Subsidiaries | `subsidiaries` | comma-separated list | Subsidiary company names |
| D | Acquisitions | `acquisitions` | structured text | Acquisition history (key: value pairs) |
| E | Notes | `notes` | string | Analyst notes and qualitative observations |
| F | Source Links | `source_links` | URLs (newline-separated) | First valid URL is rendered as hyperlink |
| G | Data Sources Per Field | `metric_sources` | structured text | Per-field data source mapping |
| H | Merge Conflicts | `enrichment_quality_metrics.merge_conflicts` | JSON/string | Data quality flags for conflicting sources |

## Field Mapping Summary (20 Restored Fields)

| # | Domain Field | Export Sheet | Export Column |
|---|-------------|-------------|---------------|
| 1 | `tech_stack` | Executive Summary | H |
| 2 | `key_customers` | Executive Summary | I |
| 3 | `open_positions` | Executive Summary | J |
| 4 | `data_availability` | Executive Summary | K |
| 5 | `funding_rounds` | Financial Intelligence | H |
| 6 | `funding_war_chest` | Financial Intelligence | I |
| 7 | `lead_investors` | Financial Intelligence | G |
| 8 | `revenue_cagr_5yr` | Financial Intelligence | J |
| 9 | `revenue_per_employee_eur_k` | Financial Intelligence | K |
| 10 | `employee_cagr_3yr` | Financial Intelligence | L |
| 11 | `revenue_timeline` | Revenue History | B-D |
| 12 | `parent_company` | Advanced Data | B |
| 13 | `subsidiaries` | Advanced Data | C |
| 14 | `acquisitions` | Advanced Data | D |
| 15 | `notes` | Advanced Data | E |
| 16 | `source_links` | Advanced Data | F |
| 17 | `data_source_per_field` | Advanced Data | G |
| 18 | `merge_conflicts` | Advanced Data | H |
| 19 | `profit_margin` | Financial Intelligence | D |
| 20 | `employee_count` | Market Rankings | F |

Notes on fields 17 and 18: `data_source_per_field` is mapped from `Company.metric_sources` (dict of field name to source list). `merge_conflicts` is mapped from `Company.enrichment_quality_metrics["merge_conflicts"]`. Neither exists as a dedicated field on the Company model; they are derived from existing data structures.
