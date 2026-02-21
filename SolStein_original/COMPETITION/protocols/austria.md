# Austria - Energy Market Protocols

**TSO**: APG (Austrian Power Grid)
**Clearing**: APCS (Power Clearing & Settlement)
**Data Exchange**: EDA (Energiewirtschaftlicher Datenaustausch GmbH)
**Regulator**: E-Control
**Market Operator**: EXAA (Energy Exchange Austria) + EPEX SPOT

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Market Communication** | EDA (Electronic Data Exchange) | ebUtilities XML | PONTON X/P CEP, Email, EDA Portal | EDA GmbH |
| **Balancing** | APG Balancing Market | XML | APG portal / APCS | APG / E-Control |
| **Settlement** | APCS Quarter-hourly Clearing | Proprietary | APCS platform | APCS |
| **Metering** | EDA Meter Data Exchange | ebUtilities XML | EDA platform (CEP) | EDA GmbH |
| **Switching** | EDA Supplier Switching | ebUtilities XML | EDA platform | EDA GmbH / E-Control |
| **Energy Communities** | EDA Energy Community Protocol | ebUtilities XML | EDA Portal | EDA GmbH |
| **Scheduling** | APG Schedule Management | ESS XML | ECP | APG |
| **Cross-border** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / APG |
| **Control Energy** | APG Primary/Secondary/Tertiary | XML | APG portal, APCS | APG |
| **Gas** | EDIG@S | EDIG@S XML | Various | Gas Connect Austria |

---

## Key Infrastructure

### EDA (Electronic Data Exchange)
- Central data exchange platform for Austrian energy market
- Uses **ebUtilities** XML format (Austrian-specific variant)
- Connection types: PONTON X/P CEP (high-volume), EDA Portal (smaller operators), Email
- Handles supplier switching, meter data, master data, energy community data
- Supports prosumers and energy community generation facilities

### APCS (Power Clearing & Settlement)
- Monthly clearing of imbalance energy in **quarter-hour intervals**
- Market-oriented clearing price model (balancing market + exchange prices)
- Clearing platform for balancing service providers
- Manages balance groups through Balance Group Representatives (BGRs)

### APG Balancing
- Weekly tenders for primary control energy capacity
- Secondary and tertiary control markets since January 2012
- Based on EU Regulation 2017/2195 (Electricity Balancing)

---

## Implementing Companies

### Data Exchange (EDA/ebUtilities)

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Ponton GmbH** | PONTON X/P Messenger/Listener | Standard CEP software for EDA connectivity | **NEW** |
| **EDA GmbH** | EDA Portal | Operates the data exchange platform | N/A (market operator) |

### Market Participant Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **KISTERS** | BelVis | Portfolio management, used by Austrian utilities | Yes (Tier 1) |
| **SOPTIM** | SOPTIM Elements | Austrian market presence (DACH region) | Yes (Tier 1) |
| **SAP** | IS-U / S4HANA | Utility billing (Austrian utilities) | **NEW** (infrastructure) |

### Trading & Balancing

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Previse Systems** | Coral | Swiss/Austrian market expansion | Yes (Tier 2) |

---

## Newly Discovered Companies (AT)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| **Ponton GmbH** | PONTON X/P | DE/AT | EDA CEP, ebUtilities | Low (connectivity middleware, not back-office) |
| Austria's market uses ebUtilities (not standard EDIFACT), which limits cross-border vendor portability. Existing DACH-focused vendors (KISTERS, SOPTIM) dominate. | | | | |

---

## Sources

- APG Electricity Balancing: https://markt.apg.at/en/legal-framework/electricity-balancing/
- APCS Balancing Market: https://www.apcs.at/en/balancing-market
- APCS Clearing: https://www.apcs.at/en/clearing
- EDA Energy Communities: https://www.eda.at/energiegemeinschaften?lang=en
- EDA CEP: https://www.eda.at/kommunikationsendpunkt?lang=en
- E-Control Market Model: https://www.e-control.at/documents/1785851/1811528/Strommarktmodell_%C3%96sterreich_030413_en.pdf
