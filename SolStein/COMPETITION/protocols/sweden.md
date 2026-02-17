# Sweden - Energy Market Protocols

**TSO**: Svenska kraftnat (SvK)
**Data Hub**: Elmarknadshubb (project on hold since Sep 2020, legislative delays)
**Regulator**: Ei (Energimarknadsinspektionen / Energy Markets Inspectorate)
**Power Exchange**: Nord Pool
**Standards Body**: Ediel / NMEG (Nordic Market Expert Group)

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Market Communication** | Ediel Nordic (BRS) | ebIX XML, EDIFACT | Bilateral (no central hub yet) | NMEG / Ediel |
| **Balancing** | Nordic Balancing Model (NBM) | ENTSO-E XML | ECP/EDX | SvK / ENTSO-E |
| **Settlement** | Bilateral settlement | EDIFACT (MSCONS) | Point-to-point | Ei / SvK |
| **Metering** | Bilateral meter data exchange | EDIFACT (MSCONS) | Point-to-point | Ei |
| **Switching** | Bilateral switching process | EDIFACT (UTILMD) | Point-to-point | Ei |
| **Scheduling** | ENTSO-E scheduling | ENTSO-E XML | ECP | SvK |
| **Cross-border** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / SvK |
| **Reserve Markets** | aFRR/mFRR/FCR | Various | ICCP, IEC 61850, ECP/EDX | SvK |
| **Real-time Telemetry** | ICCP / ELCOM | ICCP | Fiber networks | SvK |
| **Future Standard** | IEC 61850 | IEC 61850 | IP-based | SvK (planned) |

---

## Key Infrastructure

### Elmarknadshubb (Data Hub - On Hold)
- Swedish Government assigned SvK to develop a central data hub
- Goal: supplier-centric market model (single contact point for consumers)
- **Project on hold since September 2020** due to legislative delays
- Sweden is the only Nordic country without a functioning central data hub
- Impact: market processes remain bilateral and decentralized

### Nordic Balancing Markets (NBM) Roadmap
- SvK implementing Nordic-wide balancing market reforms through 2026
- Integration with European platforms: PICASSO (aFRR) and MARI (mFRR)
- Multiple capacity and energy auction markets being developed
- Coordinated with Statnett (NO), Fingrid (FI), Energinet (DK)

### Real-time Communication
- Currently uses ICCP or ELCOM protocols via fiber networks
- SvK planned IEC 61850 as alternative for smaller market actors (target: end 2022)

---

## Implementing Companies

### Market Participant Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Volue** | Volue Energy suite | Trading, optimization (strong Nordic presence) | Yes (Tier 1) |
| **Engrate** | Engrate API Platform | API-native, active in SE market | Yes (Tier 1) |
| **KISTERS** | BelVis | Portfolio management (if present in SE) | Yes (Tier 1) |
| **TietoEVRY** | Energy solutions | Utility billing, market processes | **NEW** (see Norway) |
| **EG (Vitec/PowerEL)** | EG Utility | Nordic utility billing/settlement | **NEW** (see Norway) |

### Trading & Balancing

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Volue** | Algo Trader | Nordic power trading | Yes (Tier 1) |
| **Nord Pool** | Trading platform | Power exchange | N/A (exchange) |

---

## Market Note

Sweden's lack of a central data hub means market communication remains **bilateral and decentralized** -- similar to Germany's pre-AS4 era. This creates higher integration costs for market participants and means fewer specialized protocol implementers are visible. When/if the Elmarknadshubb launches, it will likely create demand for new software integrations (similar to Norway's Elhub and Denmark's DataHub experiences).

---

## Newly Discovered Companies (SE)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| No significant new discoveries beyond Nordic-wide vendors (TietoEVRY, EG/Vitec) already flagged in Norway. | | | | |

---

## Sources

- SvK Data Hub: https://www.svk.se/en/stakeholders-portal/electricity-market/data-hub/
- SvK Electricity Market: https://www.svk.se/en/stakeholders-portal/electricity-market/
- SvK Real-time Reporting: https://www.svk.se/en/stakeholders-portal/electricity-market/provision-of-ancillary-services/questions-and-answers-about-reserves/reporting-of-real-time-telemetry/
- SvK NBM Roadmap: https://www.svk.se/49a86b/siteassets/2.utveckling-av-kraftsystemet/systemansvar-o-elmarknad/nbm/roadmap-update-may-2025.pdf
- Ediel.org: https://ediel.org/
