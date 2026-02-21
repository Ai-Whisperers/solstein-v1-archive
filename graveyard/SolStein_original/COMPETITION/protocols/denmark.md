# Denmark - Energy Market Protocols

**TSO**: Energinet
**Data Hub**: DataHub (operated by Energinet, built by CGI)
**Regulator**: Forsyningstilsynet (Danish Utility Regulator)
**Power Exchange**: Nord Pool
**Standards Body**: Ediel / NMEG (Nordic Market Expert Group)

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Market Communication** | Ediel Nordic (BRS) + Danish APERAK | ebIX XML, EDIFACT | DataHub platform | NMEG / Energinet |
| **Data Hub** | Energinet DataHub Messaging | ebIX XML | DataHub API / web services | Energinet |
| **Balancing** | Nordic Balancing Model | ENTSO-E XML | ECP/EDX | Energinet / ENTSO-E |
| **Settlement** | DataHub Settlement | ebIX XML | DataHub platform | Energinet |
| **Metering** | DataHub Meter Data | ebIX XML | DataHub platform | Energinet |
| **Switching** | DataHub Supplier Switching | ebIX XML | DataHub platform | Energinet |
| **Scheduling** | ENTSO-E scheduling | ENTSO-E XML | ECP | Energinet |
| **Cross-border** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / Energinet |
| **Gas** | Energinet Gas protocols | EDIG@S / XML | Energinet platform | Energinet |
| **Acknowledgment** | APERAK (Danish implementation) | EDIFACT | DataHub | Energinet |

---

## Key Infrastructure

### DataHub
- Built by **CGI**, went live in **2013**
- Central repository for ~**3.3 million** metering points
- Standardizes all market processes and communication
- **April 2016**: Upgraded to supplier-centric model (supplier = single customer contact)
- Equal data access for all market participants
- Pioneered the Nordic DataHub model (Norway, Finland, Sweden followed)
- Enables automated supplier switching and real-time data access

### Supplier-Centric Model (since 2016)
- Electricity supplier is single point of contact for customers
- Supplier handles all customer communication and billing (incl. distribution)
- Increased competition and encouraged product innovation
- Simplified switching process for consumers

---

## Implementing Companies

### Data Hub Operations

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **CGI** | DataHub platform | Built and maintains the Danish DataHub | Yes (Tier 3) |
| **Energinet** | DataHub operator | TSO, operates DataHub | N/A (TSO) |

### Market Participant Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Volue** | Volue Energy suite | Trading, optimization (Nordic) | Yes (Tier 1) |
| **TietoEVRY** | Energy solutions | Utility billing, Nordic market | **NEW** (see Norway) |
| **EG (Vitec/PowerEL)** | EG Utility | Billing, settlement for Danish utilities | **NEW** (see Norway) |
| **CGI** | Market solutions | Beyond DataHub: market participant software | Yes (Tier 3) |

### Trading & Balancing

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Volue** | Energy suite | Nordic power trading, optimization | Yes (Tier 1) |
| **Nord Pool** | Trading platform | Power exchange | N/A (exchange) |

---

## Newly Discovered Companies (DK)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| Nordic-wide vendors (TietoEVRY, EG/Vitec) already flagged in Norway. CGI already tracked. | | | | |

Denmark's market is well-served by CGI (DataHub builder) and Nordic-wide vendors. The centralized DataHub model means most protocol complexity is handled by the hub itself rather than individual software vendors.

---

## Sources

- CGI DataHub case study: https://www.cgi.com/nl/nl/media/case-study/cgi-datahub-solution-sets-foundation-future-danish-electricity-retail-market
- Energinet DataHub: https://en.energinet.dk/Energy-data/DataHub/
- CGI Market Facilitation Hubs: https://www.cgi.com/en/article/energy-utilities/market-facilitation-hubs-EU-enabling-resilient-transparent-energy-markets
- Energinet DataHub Terms: https://en.energinet.dk/media/eaugqieg/terms-of-access-to-and-use-of-the-datahub-third-party.pdf
- Ediel.org: https://ediel.org/
