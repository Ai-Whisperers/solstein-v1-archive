# Norway - Energy Market Protocols

**TSO**: Statnett SF
**Data Hub**: Elhub (operated by Statnett subsidiary)
**Regulator**: RME (Reguleringsmyndigheten for energi, part of NVE)
**Power Exchange**: Nord Pool
**Standards Body**: Ediel / NMEG (Nordic Market Expert Group)

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Market Communication** | Ediel Nordic (BRS) | ebIX XML, EDIFACT | Elhub platform | NMEG / Ediel |
| **Data Hub** | Elhub Messaging | ebIX XML | Elhub API / web services | Elhub / Statnett |
| **Balancing** | Nordic Balancing Model | ENTSO-E XML | ECP/EDX, Vaksi | Statnett / ENTSO-E |
| **Settlement** | Balance Settlement via Elhub | ebIX XML (MSCONS equiv.) | Elhub platform | Elhub |
| **Metering** | Elhub Meter Data | ebIX XML | Elhub platform | Elhub |
| **Switching** | Elhub Supplier Switching | ebIX XML (UTILMD equiv.) | Elhub platform | Elhub |
| **Scheduling** | Nord Pool / Statnett scheduling | ENTSO-E XML | ECP | Statnett |
| **Cross-border** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / Statnett |
| **Reserve Markets** | FCR/aFRR/mFRR | Various | ICCP, EDI, ECP/EDX, Vaksi | Statnett |
| **Real-time Data** | ICCP protocol | ICCP | Dedicated links | Statnett |

---

## Key Infrastructure

### Elhub
- Launched February 2019, developed by Accenture for Statnett
- Central data hub for ALL Norwegian electricity market processes
- Processes **70+ million meter readings daily**
- ~2.9 million metering points
- Functions: meter data management, supplier switching, balance settlement, master data
- Operated by Cegal and Basefarm (5-year agreement from 2020)
- System approval process for all vendor software integrating with Elhub

### Ediel Nordic Standards
- Data exchange documentation since 1995
- Supports EDIFACT, ebIX XML, NOIS XML, ENTSO-E XML, IEC CIM/XML
- Business Requirements Specifications (BRS) for trading, operations, scheduling, settlement
- Maintained by Nordic Market Expert Group (NMEG)

### Reserve Markets
- Vaksi: Web-based trading platform for FFR, FCR hourly, aFRR/mFRR energy markets
- Fifty NMMS: Nordic market management system for aFRR and mFRR capacity markets
- RT Lite: Web service for smaller reserve market participants
- ICCP: Real-time measurement reporting

---

## Implementing Companies

### Data Hub Operations

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Accenture** | Elhub (development) | Built the Elhub platform | **NEW** (consulting/integration) |
| **Cegal** | Elhub operations | Operates and secures Elhub IT services | **NEW** |
| **Basefarm (Orange)** | Elhub hosting | Infrastructure hosting for Elhub | **NEW** (infrastructure) |

### Market Participant Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Volue** | Volue Energy suite | Trading, optimization, forecasting (Norwegian company) | Yes (Tier 1) |
| **Engrate** | Engrate API Platform | API-native market communication | Yes (Tier 1) |
| **CGI** | Market solutions | Market infrastructure (also built DK DataHub) | Yes (Tier 3) |
| **Tieto Evry (TietoEVRY)** | Energy solutions | Utility billing, market processes for Nordics | **NEW** |
| **EG (formerly Vitec/PowerEL)** | EG Utility | Billing, settlement for Nordic utilities | **NEW** |

### Trading & Balancing

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Volue** | Algo Trader, energy suite | Nordic power trading, optimization | Yes (Tier 1) |
| **Nord Pool** | Trading platform | Power exchange | N/A (exchange) |

---

## Newly Discovered Companies (NO)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| **Cegal** | Elhub operations | NO | Ediel, ebIX, Elhub | Low (IT operations, not product) |
| **TietoEVRY** | Energy solutions | FI/NO | Ediel, Elhub, Nordic market | **Medium** (utility software for Nordic markets) |
| **EG (Vitec/PowerEL)** | EG Utility | DK/NO | Ediel, Elhub, billing | **Medium** (Nordic utility billing/settlement) |
| **Solteq** | Consulting for Datahub | FI | Datahub onboarding | Low (consulting) |

---

## Sources

- Elhub System Approval: https://elhub.no/systemgodkjenning-system-vendor-trial/system-approval-instructions/
- Elhub Testing: https://elhub.no/aktorer-og-markedsstruktur/testing/systemgodkjenning-system-vendor-trial/
- NVE/Elhub: https://www.nve.no/norwegian-energy-regulatory-authority/retail-market/elhub/
- Cegal/Elhub: https://www.cegal.com/en/dictionary/elhub
- Statnett Elhub launch: https://www.statnett.no/en/about-statnett/news-and-press-releases/news-archive-2019/elhub-is-now-operational/
- Ediel.org: https://ediel.org/
- Ediel BRS documents: https://ediel.org/common-ediel-documents/
