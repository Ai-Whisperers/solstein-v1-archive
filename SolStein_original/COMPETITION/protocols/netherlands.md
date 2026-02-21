# Netherlands - Energy Market Protocols

**TSO**: TenneT TSO B.V.
**Market Facilitator**: EDSN (Energie Data Services Nederland)
**Regulator**: ACM (Autoriteit Consument & Markt)
**Gas TSO**: Gasunie Transport Services (GTS)

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Market Communication** | EDSN Market Messaging | EDIFACT (UTILMD, MSCONS, APERAK) | AS4, AMQP 1.0 | EDSN |
| **TSO Communication** | TenneT APIs + ECP | XML, REST API | ECP (ENTSO-E), HTTPS | TenneT |
| **Balancing** | TenneT Balancing (ETPA) | XML | ECP / TenneT portal | TenneT / ETPA |
| **Settlement** | C-ARM Allocation & Reconciliation | EDIFACT (MSCONS, ALOCAT) | EDSN platform | EDSN / CGI |
| **Metering** | DSMR (Dutch Smart Meter Requirements) | P1 serial (IEC 62056-21 Mode D) | RJ-12 serial, P1/P4 | Netbeheer NL |
| **Meter Data Exchange** | EDSN Meter Data Hub | EDIFACT (MSCONS) | AMQP 1.0, REST API | EDSN |
| **Switching** | EDSN Supplier Switching (C-AR) | EDIFACT (UTILMD) | EDSN platform | EDSN / ACM |
| **Connection Register** | C-AR (Central Aansluitingenregister) | EDIFACT (UTILMD) | EDSN platform | EDSN |
| **Cross-border Scheduling** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / TenneT |
| **Gas Nominations** | EDIG@S | EDIFACT / XML (v6.1) | AS4 | GTS / EASEE-gas |
| **FCR/aFRR/mFRR** | TenneT Ancillary Services | XML messages | TenneT portal / API | TenneT |
| **Acknowledgment** | APERAK / CONTRL | EDIFACT | AS4 | EDSN |

---

## Key Infrastructure

### EDSN Platform
- Central market facilitator since 2001 (market liberalization)
- Processes data for **15+ million** electricity and gas metering points
- Peak capacity: **4 million messages/day**
- Cloud infrastructure on AWS (operated by Technolution Spark)
- Provides REST API + AMQP 1.0 notification broker + OAuth authentication

### C-ARM (Central Allocation, Reconciliation and Meter data)
- Processes meter data for all 7 Dutch regional network operators
- Daily volume allocation: 15-minute resolution (electricity), hourly (gas)
- Monthly settlement of allocation differences
- Built on Hansen GENERIS platform by CGI
- 100% of Dutch network connections migrated by October 2020

### C-AR (Central Connection Register)
- Launched 2011 for retail processes
- Holds data for all 15 million Dutch electricity and gas meter points
- Handles supplier switching processes

### TenneT Developer Portal
- REST APIs for settlement prices, reconciliation data, balance information
- ECP (Energy Communication Platform) for ENTSO-E cross-border communication
- XML-based scheduling and nomination messages

---

## Implementing Companies

### Market Communication & Settlement (EDSN/C-ARM)

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **CGI** | C-ARM (Hansen GENERIS) | Built and operates C-ARM for all Dutch DSOs | Yes (Tier 3) |
| **Technolution Spark** | EDSN Platform | Technology partner, operates EDSN cloud infra | **NEW** |
| **Eneve** | eBase | Back-office consuming EDSN messages | Yes (Eneve) |
| **Engrate** | Engrate API Platform | API-based market communication | Yes (Tier 1) |

### TSO Communication & Balancing

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Eneve** | eBase | TenneT communication, balancing, nominations | Yes (Eneve) |
| **Engrate** | Engrate API | Balancing, scheduling | Yes (Tier 1) |
| **ETPA** | ETPA Trading Platform | Intraday trading, balancing market | **NEW** |

### Smart Metering (DSMR)

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Landis+Gyr** | Smart meters (hardware) | Meter manufacturer, DSMR compliant | N/A (hardware) |
| **Itron** | Smart meters (hardware) | Meter manufacturer, DSMR compliant | N/A (hardware) |
| **Iskraemeco** | Smart meters (hardware) | Meter manufacturer, DSMR compliant | N/A (hardware) |

### Back-Office / Market Participant Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Eneve** | eBase | Full back-office: EDSN, TenneT, settlement, metering | Yes (Eneve) |
| **CGI** | C-ARM, market solutions | Market facilitator infrastructure | Yes (Tier 3) |
| **Engrate** | Engrate API Platform | API-native market communication | Yes (Tier 1) |
| **Trayport** | Periotheus | Nominations, scheduling | Yes (Tier 1) |
| **SAP** | SAP IS-U / S4HANA Utilities | Utility billing and processes | **NEW** (infrastructure) |

---

## Newly Discovered Companies (NL)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| Technolution Spark | EDSN Platform operator | NL | EDSN, AMQP, REST | Low (infrastructure partner, not competitor) |
| ETPA | ETPA Trading Platform | NL | TenneT balancing, intraday | Medium (trading platform, not back-office) |
| SAP | IS-U / S4HANA Utilities | Global | EDIFACT, market comm | Low (ERP layer, not specialized back-office) |

---

## Sources

- CGI/EDSN case study: https://www.cgi.com/en/case-study/central-market-solutions/
- TenneT API portal: https://developer.tennet.eu/specs
- EDSN service desk / meterbeheer.nl: https://www.meterbeheer.nl/docs/edsn/
- ENTSO-E ECP: https://www.entsoe.eu/ecco-sp/ecp/
- DSMR P1 specification: IEC 62056-21 Mode D
- Partners in Energie API guide: https://www.partnersinenergie.nl/en-GB/implementation-guide-partners-api
- EDSN GitHub: https://github.com/EDSN-NL
