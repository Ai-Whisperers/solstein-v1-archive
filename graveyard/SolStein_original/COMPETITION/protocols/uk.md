# United Kingdom - Energy Market Protocols

**TSO (Electricity)**: NESO (National Energy System Operator, formerly National Grid ESO)
**Settlement**: Elexon (BSC Agent)
**Gas**: Xoserve (Central Data Services Provider), National Gas Transmission
**Regulator**: Ofgem
**Smart Metering**: DCC (Data Communications Company)

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Settlement** | BSC (Balancing and Settlement Code) | Proprietary / XML | Elexon portal / APIs | Elexon |
| **Half-Hourly Settlement** | MHHS (Market-wide Half Hourly Settlement) | XML / DIP messaging | Data Integration Platform | Elexon / Ofgem |
| **Balancing Mechanism** | BM (Balancing Mechanism) | XML | NESO systems | NESO |
| **Switching** | CSS (Central Switching Service) | XML | DCC infrastructure | Ofgem / DCC |
| **Smart Metering** | SMETS2 / DCC Comms Hub | DLMS/COSEM, ZigBee, WAN | DCC network | DCC / BEIS |
| **Meter Data Collection** | EAC/AA, NHHDA | Proprietary | Elexon systems | Elexon |
| **Gas Settlement** | UK Link | EDI / XML | Xoserve platform | Xoserve |
| **Cross-border** | ENTSO-E ESS | ESS XML | ECP / MADES | ENTSO-E / NESO |
| **Gas Nominations** | Gemini | Proprietary | National Gas portal | National Gas |
| **Network Codes** | CUSC, Grid Code, Distribution Code | Various | Respective code admins | NESO / Ofgem |
| **Flexibility** | Flexibility market protocols | XML / API | Various platforms | NESO |

---

## Key Infrastructure

### Elexon / BSC
- Manages the Balancing and Settlement Code for GB electricity
- 2025/26 budget: £118.9M (significant increase due to MHHS programme)
- Operates settlement software: EAC/AA systems, NHHDA systems
- Decommissioning Radio Teleswitch Service and Profiling services (£3.8M savings)
- Building smart meter data repository for open access to half-hourly consumption data

### MHHS (Market-wide Half Hourly Settlement)
- Major market reform: all meters settled on half-hourly basis
- Milestone 10 (central systems ready): September 2025
- Data Integration Platform (DIP): new messaging service for settlement data
- Dual-running: old and new settlement processes during transition
- Enables time-of-use tariffs and flexibility services

### CSS (Central Switching Service)
- Centralized switching replacing bilateral processes
- Procured via DCC through competitive tender
- Enables faster, more reliable supplier switching
- Xoserve proposed leveraging UK Link as foundation

### DCC (Data Communications Company)
- Operates smart meter communications network
- SMETS2 meters connected via DCC infrastructure
- Provides meter data to authorized parties

---

## Implementing Companies

### Settlement & Market Operations

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Elexon** | BSC Settlement Systems | Settlement agent, operates EAC/AA, NHHDA, DIP | N/A (market operator) |
| **CGI** | Various UK energy systems | Market infrastructure support | Yes (Tier 3) |
| **Brady Technologies** | PowerDesk Suite | Energy trading, settlement, risk | Yes (Tier 1) |

### Trading & Back-Office

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Trayport** | Joule, Periotheus | Trading platform, exchange connectivity | Yes (Tier 1) |
| **Brady Technologies** | PowerDesk Suite | ETRM, settlement, risk management | Yes (Tier 1) |
| **ION Commodities** | Allegro / Endur | Front-to-back ETRM | Yes (Tier 2) |
| **Energy One / Contigo** | enTrader | Power scheduling, trading, settlement | Yes (Tier 2) |
| **Previse Systems** | Coral | Cloud-native CTRM/ETRM | Yes (Tier 2) |
| **Qualia Trading** | Qualia AI ETRM | AI-native trading platform | Yes (Tier 2) |

### Balancing & Flexibility

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Hitachi Energy** | Market Operations suite | Balancing, market operations | Yes (Tier 2) |
| **Volue** | Energy suite | Trading, optimization | Yes (Tier 1) |
| **tem** | Rosso / RED | AI-native transaction engine | Yes (Tier 3) |

### Gas Market

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Xoserve** | UK Link | Central gas data services provider | N/A (market operator) |
| **National Gas Transmission** | Gemini | Gas nominations platform | N/A (infrastructure) |

### Smart Metering

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **DCC** | Smart meter comms network | Communications infrastructure | N/A (infrastructure) |
| **Capita** | DCC service provider | Operates DCC services | **NEW** (infrastructure) |

---

## Newly Discovered Companies (UK)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| **Capita** | DCC smart meter services | UK | SMETS2, DCC | Low (infrastructure operator, not back-office) |
| **Xoserve** | UK Link gas platform | UK | Gas settlement | Low (market operator, not competitor) |

The UK market is heavily covered by existing competitors (Trayport, Brady, ION, Energy One, Previse, Qualia, Hitachi, Volue, tem). Protocol-based discovery yielded few new players because the UK market is dominated by established ETRM vendors rather than specialized back-office platforms like those in NL/DE.

---

## Sources

- Elexon 2025/26 Business Plan: https://www.elexon.co.uk/2025/03/25/elexon-publishes-final-version-of-the-2025-26-business-plan/
- Elexon Settlement Software: https://bscdocs.elexon.co.uk/settlement-software-documents
- BSC Documentation: https://bscdocs.elexon.co.uk/bsc
- MHHS Programme: https://www.mhhsprogramme.co.uk/
- Ofgem CSS Design: https://ofgem.gov.uk/guidance/css-design-and-delivery-products
- NESO Data Portal: https://www.nationalgrideso.com/data-portal
- Elexon Change Releases 2025: https://www.elexon.co.uk/bsc/release/list-of-change-releases-for-2025/
