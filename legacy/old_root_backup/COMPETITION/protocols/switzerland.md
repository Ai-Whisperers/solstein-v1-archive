# Switzerland - Energy Market Protocols

**TSO**: Swissgrid
**Regulator**: ElCom (Federal Electricity Commission)
**Market Operator**: EPEX SPOT (coupled via CWE)
**Standards**: Swiss balance group regulations

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Balancing** | Swissgrid Balance Group Regulations (v3.1) | XML / Proprietary | Swissgrid portal | Swissgrid / ElCom |
| **Settlement** | Swissgrid Imbalance Settlement (single-price from Jan 2026) | Proprietary | Swissgrid portal | Swissgrid |
| **Schedule Management** | Swissgrid scheduling | ESS XML | ECP | Swissgrid |
| **Control Energy** | Control Energy Market (reformed 2022+) | XML | Swissgrid platforms | Swissgrid |
| **Cross-border** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / Swissgrid |
| **Metering** | Bilateral meter data exchange | Various | Bilateral | DSOs / ElCom |
| **Switching** | Bilateral switching (liberalized since 2009 for large consumers) | Various | Bilateral | ElCom |
| **Gas** | Limited (gas market not fully liberalized) | Various | Various | SVGW |

---

## Key Developments

### New Pricing Mechanism (Jan 2026)
- Single-price mechanism for balancing energy replaced previous dual-price model
- Financial incentives for ALL balance groups to contribute to Swiss control area balance
- Previously only individual portfolio balance was incentivized

### AI-Based Control Energy (2025)
- Swissgrid implemented AI solution for control energy requests
- Achieved **22% decrease** in secondary control energy activations (first 10 months 2024 vs 2025)

### Market Note
- Switzerland is NOT an EU member -- no obligation to implement EU energy market regulations
- However, Swissgrid participates in ENTSO-E and uses ECP for cross-border scheduling
- Full retail market liberalization delayed (large consumers only since 2009)
- Small consumer market opening still under political discussion

---

## Implementing Companies

### TSO & Market Operations

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Previse Systems** | Coral | CTRM, entering Swiss market | Yes (Tier 2) |
| **Hitachi Energy** | Various | HQ in Switzerland, grid solutions | Yes (Tier 2) |

### Trading & Portfolio Management

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **KISTERS** | BelVis | Portfolio management, used by Swiss utilities | Yes (Tier 1) |
| **Brady Technologies** | PowerDesk | ETRM | Yes (Tier 1) |

---

## Newly Discovered Companies (CH)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| Switzerland's partially liberalized market and non-EU status result in less standardized protocol landscape. Few specialized back-office vendors discovered beyond existing competitors. | | | | |

---

## Sources

- Swissgrid Control Energy: https://www.swissgrid.ch/en/home/newsroom/newsfeed/20260115-01.html
- Swissgrid New Pricing: https://www.swissgrid.ch/en/home/newsroom/newsfeed/20250328-01.html
- Swissgrid Balance Groups: https://www.swissgrid.ch/en/home/customers/balance-groups.html
- Balance Group Regulations v3.1: https://www.swissgrid.ch/content/dam/swissgrid/customers/topics/legal-system/balance-group/1/01-Appendix-1-General-BG-Regulations-V3-1-en.pdf
