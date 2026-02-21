# Poland - Energy Market Protocols

**TSO**: PSE (Polskie Sieci Elektroenergetyczne)
**Market Operator**: TGE (Towarowa Gielda Energii / Polish Power Exchange)
**Data Hub**: CSIRE (Centralny System Informacji Rynku Energii), operated by PSE as OIRE
**Regulator**: URE (Urzad Regulacji Energetyki / Energy Regulatory Office)

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Market Communication** | CSIRE (Central Energy Market Information System) | IES XML | CSIRE platform / API | PSE (as OIRE) |
| **Data Hub** | CSIRE Messaging | IES XML | CSIRE platform | PSE |
| **Balancing** | PSE Balancing Market | XML | PSE platform | PSE / URE |
| **Settlement** | PSE Settlement (quarter-hourly) | Proprietary | PSE platform | PSE |
| **Metering** | CSIRE Meter Data (smart meter integration) | IES XML | CSIRE platform | PSE / DSOs |
| **Switching** | CSIRE Supplier Switching (UC17) | IES XML | CSIRE platform | PSE / URE |
| **Day-Ahead Market** | TGE Day-Ahead | Proprietary | TGE platform | TGE / URE |
| **Intraday** | TGE Intraday / SIDC coupling | Proprietary / XBID | TGE / XBID | TGE / ENTSO-E |
| **Scheduling** | ENTSO-E ESS / PSE scheduling | ESS XML | ECP | ENTSO-E / PSE |
| **Cross-border** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / PSE |
| **Gas** | GAZ-SYSTEM protocols | EDIG@S / XML | GAZ-SYSTEM platform | GAZ-SYSTEM |
| **Information Exchange** | IES (Information Exchange Standards) | XML | CSIRE | PSE |

---

## Key Infrastructure

### CSIRE (Central Energy Market Information System)
- Poland's centralized data hub, managed by PSE as Energy Market Information Operator (OIRE)
- **Integration began July 1, 2025** with staggered rollout
- Standardizes data collection, processing, and exchange for all electricity market participants
- Handles: supplier switching, metering, billing, settlement (UC17 regulation)
- Real-time access to meter readings, supplier contracts, consumption data
- Must handle massive data volumes from smart meter rollout

### IES (Information Exchange Standards)
- Published by PSE to govern all CSIRE communication protocols
- Standardized XML-based data formats
- Mandatory for all market participants (suppliers, DSOs, metering operators)

### Smart Meter Rollout
- Poland undergoing large-scale smart meter deployment
- CSIRE must integrate and process high-volume smart meter data
- Scalability is a key challenge for integration vendors

---

## Implementing Companies

### CSIRE Integration

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **MaxBill** | MaxBill platform | CSIRE integration, billing, CIS for Polish suppliers | **NEW** |
| **Univio** | CSIRE integration services | Integration consulting and development | **NEW** |
| **PSE** | CSIRE operator | Operates the central data hub as OIRE | N/A (TSO/OIRE) |

### Market Participant Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **SAP** | IS-U / S4HANA | Utility billing (major Polish utilities) | **NEW** (infrastructure) |
| **Asseco** | Utility solutions | Polish IT company, utility billing | **NEW** |

### Trading

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **TGE** | Polish Power Exchange | Market operator | N/A (exchange) |

---

## Newly Discovered Companies (PL)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| **MaxBill** | Billing/CIS platform | UA/Global | CSIRE, billing, metering | **Medium** (billing platform targeting Polish energy market integration) |
| **Univio** | CSIRE integration | PL | CSIRE, IES | Low (integration consulting) |
| **Asseco** | Utility solutions | PL | CSIRE, billing | **Medium** (major Polish IT company with energy utility practice) |

Poland's CSIRE launch (July 2025) is creating demand for integration vendors. The market is nascent compared to NL/DE but the centralized hub model will eventually standardize the competitive landscape. Vendors with Eastern European energy expertise and liberalized market knowledge are best positioned.

---

## Sources

- MaxBill/CSIRE: https://maxbill.com/blog/csire-integration-polish-energy-suppliers/
- PSE IES: https://www.pse.pl/web/pse-eng/oire/information-exchange-standards-ies
- Univio/CSIRE: https://www.univio.com/blog/integration-with-csire-or-the-biggest-challenge-of-the-energy-market-through-the-eyes-of-an-expert/
- PSE Settlement: https://www.pse.pl/web/pse-eng/data/balancing-market-operation/settlement-prices
