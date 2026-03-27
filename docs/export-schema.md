# Excel Export Schema

**Schema Version**: 1.0
**Auto-generated from**: `src/solstein/exporters/export_schema.py`

---

## Executive Summary

| Column | Header | Domain Field | Type | Required |
|--------|--------|-------------|------|----------|
| A | Company | `name` | string | Yes |
| B | Industry | `industry` | string | Yes |
| C | Revenue (€M) | `revenue_eur_m` | number | Yes |
| D | Growth | `growth_rate_pct` | percentage | Yes |
| E | AI Score | `ai_score` | number | Yes |
| F | Tier | `tier` | string | Yes |
| G | Threat Level | `threat_level` | string | Yes |
| H | Tech Stack | `tech_stack` | list | Yes |
| I | Key Customers | `key_customers` | list | Yes |
| J | Open Positions | `open_positions` | integer | Yes |
| K | Data Availability | `data_availability` | string | Yes |

## Market Rankings

| Column | Header | Domain Field | Type | Required |
|--------|--------|-------------|------|----------|
| A | Rank | `rank` | integer | Yes |
| B | Company | `name_rankings` | string | Yes |
| C | Market Share | `market_share_pct` | percentage | Yes |
| D | Competitive Score | `competitive_position_score` | number | Yes |
| E | Growth Rate | `growth_rate_rankings` | percentage | Yes |
| F | Employees | `employee_count` | integer | Yes |

## Financial Intelligence

| Column | Header | Domain Field | Type | Required |
|--------|--------|-------------|------|----------|
| A | Company | `name_financial` | string | Yes |
| B | Revenue (€M) | `revenue_financial` | number | Yes |
| C | Growth Rate | `growth_rate_financial` | percentage | Yes |
| D | Profit Margin | `profit_margin` | percentage | Yes |
| E | Total Funding | `total_funding` | number | Yes |
| F | Latest Valuation | `latest_valuation` | number | Yes |
| G | Investors | `lead_investors` | list | Yes |
| H | Funding Rounds | `funding_rounds` | structured | Yes |
| I | Funding War Chest | `funding_war_chest` | string | Yes |
| J | Revenue CAGR 5yr | `revenue_cagr_5yr` | percentage | Yes |
| K | Revenue/Employee (€K) | `revenue_per_employee` | number | Yes |
| L | Employee CAGR 3yr | `employee_cagr_3yr` | percentage | Yes |

## Revenue History

| Column | Header | Domain Field | Type | Required |
|--------|--------|-------------|------|----------|
| A | Company | `name_revenue` | string | Yes |
| B | Year | `year` | integer | Yes |
| C | Revenue (EUR M) | `revenue_eur_m_history` | number | Yes |
| D | Source | `source` | string | Yes |

## Advanced Data

| Column | Header | Domain Field | Type | Required |
|--------|--------|-------------|------|----------|
| A | Company | `name_advanced` | string | Yes |
| B | Parent Company | `parent_company` | string | Yes |
| C | Subsidiaries | `subsidiaries` | list | Yes |
| D | Acquisitions | `acquisitions` | structured | Yes |
| E | Notes | `notes` | string | Yes |
| F | Source Links | `source_links` | list | Yes |
| G | Data Sources Per Field | `data_source_per_field` | structured | Yes |
| H | Merge Conflicts | `merge_conflicts` | structured | Yes |

---

## Schema Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-27 | Initial schema: 5 sheets, all 20 STORY-125 fields + original fields |
