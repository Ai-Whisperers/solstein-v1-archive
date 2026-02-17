# France - Energy Market Protocols

**TSO**: RTE (Reseau de Transport d'Electricite)
**DSO**: Enedis (95% of mainland distribution)
**Regulator**: CRE (Commission de Regulation de l'Energie)
**Market Operator**: EPEX SPOT (day-ahead/intraday)
**Gas TSO**: GRTgaz, Terega

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **TSO Communication** | RTE Services Portal / B2B APIs | XML, REST API | HTTPS, ECP | RTE |
| **Balancing** | RTE Balancing Mechanism (MA) | XML | RTE portal / B2B | RTE |
| **Settlement** | RTE Imbalance Settlement (ISP15 from Jan 2025) | XML | RTE portal | RTE / CRE |
| **Tariff** | TURPE 7 (since Aug 2025) | Proprietary | RTE systems | CRE |
| **Demand Response** | NEBEF Mechanism | XML | RTE portal | RTE |
| **Smart Metering** | Linky TIC (TeleInformation Client) | Serial / EEBUS (SPINE/SHIP) | Local (TIC port), IP | Enedis |
| **Meter Data Exchange** | Enedis SGE (Systeme de Gestion des Echanges) | XML | Enedis portal | Enedis |
| **Data Portal** | RTE Data Portal / ODRE | REST API, JSON/CSV | HTTPS | RTE |
| **Switching** | Bilateral switching (supplier changes) | Various | Enedis platform | CRE / Enedis |
| **Cross-border** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / RTE |
| **Gas** | GRTgaz / Terega protocols, EDIG@S | EDIG@S / XML | AS4 | GRTgaz / EASEE-gas |
| **Scheduling** | ENTSO-E scheduling / RTE nomination | XML | ECP / RTE portal | RTE / ENTSO-E |

---

## Key Developments (2025)

### ISP15 Transition
- France transitioned from 30-minute to **15-minute imbalance settlement periods** (ISP15) effective January 1, 2025
- Impacts BRPs, metering, profiling, scheduling gates, balancing mechanism, frequency ancillary services
- Aligns with EU Electricity Balancing Guideline requirements

### TURPE 7
- New transmission tariff since August 1, 2025
- 4-year period with annual adjustments
- Postage stamp pricing, territorial equalization, non-discrimination

### Linky Smart Meters
- **37+ million** Linky meters deployed (as of 2024)
- TIC interface for local data access
- Integration with EEBUS ecosystem (SPINE/SHIP protocols) for HEMS

---

## Implementing Companies

### TSO Operations & Trading

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Sopra Steria** | cpX.Energy | French market operations (parent HQ in France) | Yes (Tier 1) |
| **Hitachi Energy** | Grid solutions | French grid infrastructure | Yes (Tier 2) |
| **Worldgrid / ALTEN** | Consulting/Engineering | Energy consulting in French market | Yes (Tier 3) |

### Market Participant Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Sopra Steria** | cpX.Energy | Back-office, trading, settlement | Yes (Tier 1) |
| **SAP** | IS-U / S4HANA | Utility billing (used by EDF, Engie) | **NEW** (infrastructure) |

### Smart Metering (Linky)

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Itron** | Linky meter manufacturing | Hardware manufacturer | N/A (hardware) |
| **Sagemcom** | Linky meter manufacturing | Hardware manufacturer | N/A (hardware) |
| **Landis+Gyr** | Linky meter manufacturing | Hardware manufacturer | N/A (hardware) |

---

## Newly Discovered Companies (FR)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| France's market is dominated by vertically integrated players (EDF, Engie) with less visible independent back-office software vendors. The protocol landscape is RTE/Enedis-centric. No significant new competitors discovered. | | | | |

---

## Sources

- RTE TURPE: https://www.services-rte.com/en/learn-more-about-our-services/understanding-the-public-transmission-system-access-tariff-turpe.html
- RTE Balancing: https://www.services-rte.com/en/learn-more-about-our-services/becoming-a-balancing-service-provider.html
- RTE ISP15: https://www.services-rte.com/en/learn-more-about-our-services/preparation-for-the-upcoming-amendments-related-to-the-transition-to-the-15-minute-imbalance-settlement-period-isp15.html
- RTE NEBEF: https://www.services-rte.com/en/learn-more-about-our-services/participate-nebef-mechanism
- Linky/EEBUS: https://www.eebus.org/wp-content/uploads/2025/05/Integration-of-the-Linky-Smart-Meter-within-EEBUS-ecosystem.pdf
- RTE Data Portal: https://data.rte-france.org/
