# Germany - Energy Market Protocols

**TSOs**: Amprion, 50Hertz, TenneT DE, TransnetBW
**Regulator**: BNetzA (Bundesnetzagentur / Federal Network Agency)
**Gas TSO**: Multiple (e.g., bayernets, Gasunie DE, GASCADE, OGE, terranets bw)
**Market Framework**: MaKo (Marktkommunikation)

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Market Communication** | MaKo (Marktkommunikation) | EDIFACT | AS4 (since Oct 2023) | BNetzA |
| **Balancing Settlement** | MaBiS (Marktregeln Bilanzkreisabrechnung Strom) | EDIFACT (MSCONS, ALOCAT, IMBNOT) | AS4 | BNetzA |
| **Supplier Switching (Electricity)** | GPKE (Geschaeftsprozesse Kundenbelieferung Energie) | EDIFACT (UTILMD) | AS4 | BNetzA |
| **Supplier Switching (Gas)** | GeLi Gas (Geschaeftsprozesse Lieferantenwechsel Gas) | EDIFACT (UTILMD) | AS4 | BNetzA |
| **Gas Balancing** | GaBi Gas (Grundmodell Ausgleichsleistungen/Bilanzierung Gas) | EDIFACT | AS4 | BNetzA |
| **Meter Operations** | WiM (Wechselprozesse im Messwesen) | EDIFACT (UTILMD) | AS4 | BNetzA |
| **Metering Data Exchange** | MSCONS | EDIFACT | AS4 | BNetzA / BDEW |
| **Allocation** | ALOCAT | EDIFACT | AS4 | BNetzA |
| **Imbalance Notification** | IMBNOT | EDIFACT | AS4 | BNetzA |
| **Master Data Exchange** | PARTIN (since Oct 2023) | EDIFACT | AS4 | BNetzA |
| **Acknowledgment** | APERAK / CONTRL | EDIFACT | AS4 | BNetzA |
| **Cross-border Scheduling** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E |
| **Gas Nominations** | EDIG@S (v6.1) | EDIFACT / XML | AS4 | EASEE-gas |
| **Green Certificates** | HKNR (Herkunftsnachweisregister) | EDIFACT | AS4 | UBA |
| **SLP Profiles** | Standard Load Profiles | MSCONS | AS4 | BDEW |

---

## Key Regulatory Milestones

### AS4 Transition (2023-2024)
- **Oct 1, 2023**: AS4 replaces encrypted email and AS2 for all EDIFACT market communication
- **Nov 30, 2024**: Schedule management changeover complete
- Security: Digital signatures, HSM-based encryption, synchronous receipts

### MaBiS Hub (2025-2030)
- BNetzA consultation launched Oct 2024 to centralize balancing
- Will replace decentralized EDM (Electronic Data Management) at distribution operators
- Centralized aggregation of metering values for all market participants
- Target completion by 2030 (aligned with MsbG data protection requirements)

### MaKo 2020/2022
- MaKo 2020: Updated market communication requirements
- MaKo 2022: Extended to EV charging station operators and energy storage systems

---

## Implementing Companies

### Market Communication (MaKo/AS4)

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **SEEBURGER** | MaKo AS4 Cloud Service | Managed AS4 messaging for 450+ market participants, 50M+ msgs/month | **NEW** |
| **Arvato Systems** | AEP MaKo Cloud | End-to-end MaKo SaaS with AS4 and HSM | **NEW** |
| **SOPTIM** | SOPTIM Elements, AS4 communication | TSO operations, market communication | Yes (Tier 1) |
| **Robotron** | EdifactKonverter, Energy Market Platform | EDIFACT processing (GPKE, MaBiS, WiM, GeLi, GaBi) | **NEW** |
| **SAP** | SAP Market Communication for Utilities | Cloud MaKo integrated with S/4HANA Utilities | **NEW** (infrastructure) |
| **Schleupen** | Schleupen.CS | ERP/billing with integrated MaKo | **NEW** |

### Balancing & Settlement (MaBiS)

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **SOPTIM** | SOPTIM Elements | Balancing group management, 100% of German TSOs | Yes (Tier 1) |
| **KISTERS** | BelVis / BelVis+ PFM | Portfolio management, balancing, forecasting | Yes (Tier 1) |
| **Robotron** | Energy Market Platform | Balancing, settlement, EDM | **NEW** |
| **Sopra Steria** | cpX.Energy | Balancing, settlement (German market) | Yes (Tier 1) |

### Metering & Data Management

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **KISTERS** | BelVis, MSB Cockpit | Meter data management, metering point operations | Yes (Tier 1) |
| **Robotron** | robotron*ecount | Energy data management, smart meter integration | **NEW** |
| **SAP** | IS-U / S4HANA | Utility billing, meter-to-cash | **NEW** (infrastructure) |

### TSO Operations

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **SOPTIM** | SOPTIM Elements | Serves all 4 German TSOs | Yes (Tier 1) |
| **PSI Software** | PSIcontrol, PSImarket | Grid control, energy trading | **NEW** |

### Gas Market (EDIG@S, GeLi Gas, GaBi Gas)

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **SOPTIM** | SOPTIM Elements | Gas market communication | Yes (Tier 1) |
| **KISTERS** | BelVis | Gas portfolio management | Yes (Tier 1) |
| **Robotron** | EdifactKonverter | GaBi Gas, GeLi Gas message processing | **NEW** |

---

## Newly Discovered Companies (DE)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| **SEEBURGER** | MaKo AS4 Cloud Service | DE | AS4, EDIFACT, MaKo | Medium (B2B integration, not back-office) |
| **Arvato Systems** | AEP MaKo Cloud | DE | AS4, MaKo, MaBiS | Medium (MaKo SaaS, Bertelsmann subsidiary) |
| **Robotron** | Energy Market Platform | DE | MaBiS, GPKE, GeLi, GaBi, WiM, EDIFACT | **High** (full energy market platform, direct competitor space) |
| **Schleupen** | Schleupen.CS | DE | MaKo, EDIFACT, billing | Medium (ERP/billing focus, less back-office) |
| **SAP** | Market Communication for Utilities | Global | MaKo, AS4, EDIFACT | Low (infrastructure ERP layer) |
| **PSI Software** | PSIcontrol, PSImarket | DE | TSO grid control, trading | Low (grid/control focus, not market comm) |

---

## Sources

- TransnetBW MaBiS: https://www.transnetbw.de/en/energy-market/balancing-group-management/mabis
- Arvato Systems MaBiS Hub: https://www.arvato-systems.com/blog/mabis-hub-what-challenges-and-opportunities-does-this-bring
- 50Hertz Market Communication: https://www.50hertz.com/en/Market/Marketroles
- SEEBURGER MaKo: https://www.seeburger.com/resources/good-to-know/mako-how-the-players-in-the-unbundled-german-energy-market-communicate
- SEEBURGER MaKo AS4 Cloud: https://blog.seeburger.com/how-seeburger-powers-the-future-of-energy-market-communication/
- Arvato Systems AS4: https://arvato-systems.com/more/press/as4-based-market-communication-in-the-utilities-sector
- Robotron EDIFACT: https://www.robotron.de/en/products/robotronedifactkonverter
- SOPTIM: https://www.soptim.de/en/
- KISTERS E-world 2026: https://www.kisters.eu/kisters-at-eworld-2026/
- SAP MaKo: https://www.sap.com/germany/products/scm/market-communication-for-utilities.html
- SEEBURGER PARTIN: https://blog.seeburger.com/partin-new-format-for-market-communication-in-the-german-energy-sector/
- EDIG@S: https://www.edigas.org/
- BNetzA Core Data Register: https://www.bundesnetzagentur.de/EN/Areas/Energy/CoreEnergyMarketDataRegister/
