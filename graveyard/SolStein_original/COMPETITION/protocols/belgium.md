# Belgium - Energy Market Protocols

**TSO**: Elia Group
**DSOs**: Fluvius (Flanders), ORES (Wallonia), Sibelga (Brussels)
**Market Facilitator**: Atrias
**Regulator**: CREG (Commission de Regulation de l'Electricite et du Gaz)
**Gas TSO**: Fluxys Belgium

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Market Communication** | MIG6 (Market Implementation Guide 6.0) | XML / EDIFACT | Atrias platform | Atrias |
| **TSO Communication** | Elia B2B Interface | XML | HTTPS / API | Elia |
| **Balancing** | Elia Balancing Mechanism (BMAP, iCAROS) | XML | Elia portal / B2B | Elia |
| **Settlement** | Elia Settlement Platform | XML | Elia portal | Elia |
| **Metering Data Exchange** | Atrias Clearing House | MIG6 XML | Atrias platform | Atrias / DSOs |
| **Switching** | MIG6 Supplier Switching | XML (UTILMD equivalent) | Atrias platform | Atrias |
| **Ancillary Services** | STAR (Short-Term Auctioning of Reserves) | XML | Elia portal | Elia |
| **Scheduling** | OPTIFLEX (outage planning + daily scheduling) | XML | Elia portal | Elia |
| **Cross-border Scheduling** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / Elia |
| **Gas Nominations** | EDIG@S | EDIFACT / XML (v6.1) | AS4 | Fluxys / EASEE-gas |
| **FCR/aFRR/mFRR** | Elia Ancillary Services (BMAP) | XML | Elia B2B / GUI | Elia |
| **Connection Register** | Atrias Central Register | MIG6 | Atrias platform | Atrias |

---

## Key Infrastructure

### Elia Platforms
- **EPIC** (Elia Portal Interface for Customer): Central portal for Grid Users, Access Contract Holders, BRPs -- manages metering, invoices, contracts
- **BMAP** (Bidding Market Platform): BSP capacity and energy bid submission via GUI or B2B/XML
- **STAR** (Short-Term Auctioning of Reserves): Balancing service capacity bidding
- **OPTIFLEX**: Outage planning and daily scheduling
- **Settlement UI Platform**: Ancillary services settlement details
- **Open Data Platform**: Grid data access with API, replacing legacy B2B XML services

### Atrias Clearing House
- Founded 2011 by major Belgian DSOs (Eandis, Infrax, Sibelga, ORES, Resa)
- **MIG6** replaced MIG 4.1: simplified switching, prepayment, smart meter support
- Federal clearing house for data exchange between suppliers, DSOs, TSOs, and BRPs
- Built on Microsoft Azure (private cloud via Proximus Belgian data centers)
- Integration layer: Software AG webMethods

### iCAROS (2024)
- Elia's new imbalance settlement system (Phase 1 + MARI integration, May 2024)
- Changed imbalance price calculations and data publication protocols

---

## Implementing Companies

### Clearing House & Market Communication (Atrias/MIG6)

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Accenture / Avanade** | Atrias Clearing House | Built and manages the clearing house application (Azure) | **NEW** (consulting/integration) |
| **Software AG** | webMethods | Integration layer for Atrias platform | **NEW** (middleware) |
| **Ferranti** | MECOMS 365 | Meter data management and CIS for grid operators | **NEW** |
| **Methis Consulting** | Business analysis | Functional analysis and testing for Atrias | **NEW** (consulting) |

### TSO Operations & Balancing (Elia)

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Elia Group** | EPIC, BMAP, STAR, OPTIFLEX | Operates all TSO platforms | N/A (TSO itself) |
| **Sopra Steria** | cpX.Energy | Belgian market operations (parent: Sopra Steria Group) | Yes (Tier 1) |
| **Eneve** | eBase | Expanding into Belgian market (Elia protocols) | Yes (Eneve) |

### Market Participant Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Eneve** | eBase | Back-office, expanding to Belgian market | Yes (Eneve) |
| **Ferranti** | MECOMS 365 | Meter data + CIS for Belgian grid operators | **NEW** |
| **SAP** | IS-U / S4HANA | Utility billing for Belgian utilities | **NEW** (infrastructure) |

### Gas Market (Fluxys)

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Fluxys** | Fluxys Platform | Gas TSO infrastructure, nominations | N/A (TSO itself) |
| **KISTERS** | BelVis | Gas portfolio management (if present in BE) | Yes (Tier 1) |

---

## Newly Discovered Companies (BE)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| **Ferranti** | MECOMS 365 | BE | MIG6, meter data, CIS | **High** (meter data + customer mgmt for grid operators, direct overlap with eBase metering) |
| **Accenture / Avanade** | Atrias Clearing House | Global | MIG6, Azure | Low (system integrator, not product company) |
| **Software AG** | webMethods | Global | Integration/middleware | Low (middleware layer) |
| **Methis Consulting** | Business analysis | BE | Atrias, MIG6 | Low (consulting only) |

---

## Sources

- Elia Grid Data: https://www.elia.be/en/grid-data
- Atrias/MIG6 overview: https://www.sia-partners.com/en/insights/publications/atrias-and-mig60-towards-a-new-energy-market-model-belgium
- Elia Customer Tools: https://www.elia.be/en/customers/customer-tools-and-extranet
- Elia BSP Onboarding: https://www.elia.be/en/electricity-market-and-system/system-services/keeping-the-balance/onboarding-bsp
- Ferranti/Atrias: https://www.ferranti.be/customers/atrias/
- Accenture/Atrias: https://britishreporter.com/atrias-selects-accenture-to-centralize-belgium-s-energy-market-data-in-the-cloud/
- Methis/Atrias: https://www.methisconsulting.com/case-atr/
