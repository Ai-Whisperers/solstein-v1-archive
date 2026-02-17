# Finland - Energy Market Protocols

**TSO**: Fingrid Oyj
**Data Hub**: Fingrid Datahub Oy (Fingrid subsidiary)
**Regulator**: Energy Authority (Energiavirasto)
**Power Exchange**: Nord Pool
**Standards Body**: Ediel / NMEG (Nordic Market Expert Group)

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Market Communication** | Ediel Nordic (BRS) | ebIX XML | Fingrid Datahub | NMEG / Ediel |
| **Data Hub** | Fingrid Datahub Messaging | ebIX XML | Datahub platform / API | Fingrid Datahub Oy |
| **Balancing** | Nordic Balancing Model | ENTSO-E XML | ECP/EDX, Vaksi, Fifty NMMS | Fingrid / ENTSO-E |
| **Settlement** | Balance Settlement via Datahub | ebIX XML | Datahub platform | Fingrid Datahub Oy |
| **Metering** | Datahub Meter Data | ebIX XML | Datahub platform | Fingrid Datahub Oy |
| **Switching** | Datahub Supplier Switching | ebIX XML | Datahub platform | Fingrid Datahub Oy |
| **Scheduling** | ENTSO-E scheduling | ENTSO-E XML | ECP | Fingrid |
| **Cross-border** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / Fingrid |
| **Reserve Markets** | FCR/aFRR/mFRR | Various | RT Lite, ICCP, ECP/EDX, Vaksi | Fingrid |
| **Reserve Trading** | Vaksi + Fifty NMMS | XML / Web | Fingrid platforms | Fingrid |

---

## Key Infrastructure

### Fingrid Datahub
- Centralized information exchange for Finnish electricity retail market
- Manages ~**3.9-4 million** electricity accounting points
- Serves ~80 electricity suppliers, ~80 DSOs, ~60 service providers
- Handles all retail market processes: switching, metering, settlement, master data

### Reserve Market Platforms
- **Vaksi**: Web-based trading platform for FFR, FCR hourly markets, aFRR/mFRR energy
- **Fifty NMMS**: Nordic market management system for aFRR/mFRR capacity markets
- **RT Lite**: Web service for smaller BSPs (alternative to ICCP)
- **ECP/EDX**: For bid submission and market results
- **ICCP**: Real-time reporting and activation

---

## Implementing Companies

### Data Hub Operations

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Solteq Consulting** | Datahub support | Onboarding, testing, project management since 2020 | **NEW** (consulting) |
| **Fingrid Datahub Oy** | Datahub | Operates the central data hub | N/A (market operator) |

### Market Participant Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Volue** | Volue Energy suite | Trading, optimization (Nordic presence) | Yes (Tier 1) |
| **TietoEVRY** | Energy solutions | Utility billing, Finnish market specialist | **NEW** (see Norway) |
| **EG (Vitec/PowerEL)** | EG Utility | Nordic utility billing | **NEW** (see Norway) |
| **Elenia** | Grid operator systems | DSO-specific (not competitor) | N/A |

### Trading & Balancing

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Volue** | Algo Trader, energy suite | Nordic power trading | Yes (Tier 1) |
| **Nord Pool** | Trading platform | Power exchange | N/A (exchange) |

---

## Newly Discovered Companies (FI)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| **Solteq** | Datahub consulting | FI | Datahub, Ediel | Low (consulting/onboarding, not product) |
| Nordic-wide vendors (TietoEVRY, EG/Vitec) already flagged in Norway file. | | | | |

---

## Sources

- Fingrid Datahub FAQ: https://www.fingrid.fi/en/electricity-market/datahub/questions-and-answers-about-datahub/
- Fingrid Datahub overview: https://www.fingrid.fi/en/electricity-market/datahub/
- Fingrid Reserve Trading: https://www.fingrid.fi/en/electricity-market/reserves/reserve-products/reserve-trading-and-information-exchange/
- Fingrid Information Exchange: https://developers.fingrid.fi/information_exchange
- Solteq/Datahub: https://www.solteq.com/en/success-stories/fingrid-datahub-oy
