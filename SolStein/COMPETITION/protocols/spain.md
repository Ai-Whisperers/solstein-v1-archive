# Spain - Energy Market Protocols

**TSO**: REE (Red Electrica de Espana)
**Market Operator**: OMIE (Operador del Mercado Iberico de Electricidad)
**Regulator**: CNMC (Comision Nacional de los Mercados y la Competencia)
**DSO**: Major DSOs include i-DE (Iberdrola), e-distribusion (Endesa), UFD (Naturgy)
**Data Hub**: SIPS (Sistema de Informacion de Puntos de Suministro)

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Day-Ahead Market** | OMIE MGP | Proprietary / XML | OMIE platform | OMIE / CNMC |
| **Intraday Market** | OMIE MI (7 sessions + 15-min from 2025) | Proprietary / XML | OMIE platform | OMIE / CNMC |
| **Balancing** | REE Balancing Mechanism (MSD/MB) | XML | REE / e-sios | REE |
| **Settlement** | OMIE Settlement (marginal price per zone) | Proprietary | OMIE platform | OMIE |
| **Cross-border** | SDAC (Single Day-Ahead Coupling) / SIDC | ENTSO-E XML | PCR / XBID | ENTSO-E / OMIE |
| **Metering** | SIPS (Point of Supply Info System) | XML | SIPS platform | CNMC / DSOs |
| **Switching** | CNMC Switching Protocol | XML | SIPS / bilateral | CNMC |
| **Scheduling** | ENTSO-E ESS / REE scheduling | ESS XML | ECP | ENTSO-E / REE |
| **Transparency** | ESIOS (REE System Information) | REST API, JSON/CSV | HTTPS | REE |
| **Renewables** | REER (Renewable Energy Economic Regime) | Proprietary | OMIE (from Mar 2025) | CNMC / OMIE |
| **Gas** | Enagas protocols | EDIG@S / XML | Enagas platform | Enagas / CNMC |

---

## Key Developments (2025)

### 15-Minute Products
- OMIE launched **quarter-hourly (15-minute) trading** in intraday market (March 2025)
- 15-minute products in SDAC go live June 2025
- SIDC launched 15-minute products in January 2025

### REER Settlement
- OMIE began settlement of Renewable Energy Economic Regime in March 2025
- Supports renewable energy remuneration framework

### New Bid Typology
- New bid types implemented in day-ahead market (2025)

---

## Implementing Companies

### Market Operations & Trading

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Previse Systems** | Coral | Entering Spanish market (expansion from CH) | Yes (Tier 2) |
| **Brady Technologies** | PowerDesk | ETRM, Iberian market presence | Yes (Tier 1) |
| **ION Commodities** | Allegro | ETRM, global presence | Yes (Tier 2) |

### Utility Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **SAP** | IS-U / S4HANA | Used by Iberdrola, Endesa, Naturgy | **NEW** (infrastructure) |
| **Indra** | Onesait Utilities | Spanish utility software (Minsait) | **NEW** |

---

## Newly Discovered Companies (ES)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| **Indra / Minsait** | Onesait Utilities | ES | OMIE, REE, SIPS, metering | **Medium** (major Iberian utility software vendor, part of Indra group) |
| Spain's market is dominated by large vertically integrated utilities (Iberdrola, Endesa, Naturgy) with in-house or SAP-based systems. Less visibility of independent back-office vendors compared to NL/DE. | | | | |

---

## Sources

- OMIE: https://www.omie.es/en
- OMIE Market Information: https://www.omie.es/en/market-information
- OMIE Settlements: https://www.omie.es/en/faq/settlements
- OMIE 2025 updates: https://www.omie.es/sites/default/files/2025-03/r_28022025_en.pdf
