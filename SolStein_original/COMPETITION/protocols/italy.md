# Italy - Energy Market Protocols

**TSO**: Terna S.p.A.
**Market Operator**: GME (Gestore dei Mercati Energetici), owned by GSE
**Regulator**: ARERA (Autorita di Regolazione per Energia Reti e Ambiente)
**NEMO**: GME (designated under EU CACM Regulation)
**Power Exchange**: IPEX (Italian Power Exchange)

**Last Updated**: 2026-02-15

---

## Protocol Map

| Category | Protocol Name | Format | Transport | Governing Body |
|---|---|---|---|---|
| **Day-Ahead Market** | MGP (Mercato del Giorno Prima) | Proprietary / XML | GME/IPEX platform | GME / ARERA |
| **Intraday Market** | MI (Mercato Infragiornaliero, 7 sessions) | Proprietary / XML | GME/IPEX platform | GME / ARERA |
| **Forward Market** | MTE (Mercato a Termine dell'Energia) | Proprietary | GME/IPEX platform | GME |
| **Daily Products** | MPEG | Proprietary | GME platform | GME |
| **Ancillary Services** | MSD (Mercato dei Servizi di Dispacciamento) | XML | Terna platform | Terna / ARERA |
| **Balancing** | MB (Mercato del Bilanciamento) | XML | Terna platform | Terna |
| **OTC Registration** | PCE (Piattaforma dei Conti Energia) | XML | GME platform | GME |
| **Settlement** | GME Settlement (marginal price per zone) | Proprietary | GME platform | GME / ARERA |
| **Cross-border** | SDAC / SIDC (PCR + XBID coupling) | ENTSO-E XML | EUPHEMIA / XBID | ENTSO-E / GME |
| **Scheduling** | ENTSO-E ESS / Terna scheduling | ESS XML | ECP | ENTSO-E / Terna |
| **Metering** | Bilateral meter data exchange | Various | DSO systems | ARERA / DSOs |
| **Switching** | Switching protocol (SII system) | XML | SII platform | AU (Acquirente Unico) |
| **Gas** | Snam protocols, EDIG@S | EDIG@S / XML | Snam platform | Snam / ARERA |

---

## Key Infrastructure

### GME / IPEX Market Segments
- **MGP**: Day-ahead hourly auction, producers and purchasers
- **MI**: Intraday market in 7 sessions, continuous trading
- **MTE**: Physical forward contracts
- **MPEG**: Daily products with delivery obligations
- **MSD**: Ancillary services market (operated for Terna)
- **MB**: Balancing market (Terna selects offers, establishes reserves)
- **PCE**: OTC registration for bilateral contracts

### TIDE Implementation (Jan 2025)
- Major system update coordinating GME and Terna platforms
- New market clearing and scheduling processes

### SII (Sistema Informativo Integrato)
- Operated by Acquirente Unico (AU, Single Buyer)
- Central system for supplier switching and metering data
- Italian equivalent of a data hub for retail market processes

---

## Implementing Companies

### Market Operations & Trading

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **ION Commodities** | Allegro / Endur | ETRM, Italian market | Yes (Tier 2) |
| **Brady Technologies** | PowerDesk | ETRM | Yes (Tier 1) |
| **Hitachi Energy** | Market Operations | Grid and market solutions | Yes (Tier 2) |

### Utility Software

| Company | Product | Role | Already Tracked? |
|---|---|---|---|
| **Engineering Ingegneria Informatica** | Energy solutions | Major Italian IT services for utilities | **NEW** |
| **SAP** | IS-U / S4HANA | Used by Enel, other Italian utilities | **NEW** (infrastructure) |

---

## Newly Discovered Companies (IT)

| Company | Product | Country | Protocols | Relevance |
|---|---|---|---|---|
| **Engineering Ingegneria Informatica** | Utility software | IT | GME, Terna, SII, metering | **Medium** (major Italian IT services company, utility focus) |
| Italy's market features proprietary TSO/exchange platforms (Terna, GME) with limited third-party back-office vendor visibility. Large utilities (Enel, A2A, Edison) tend to have in-house or SAP-based systems. | | | | |

---

## Sources

- GME/IPEX: https://www.gme.it/En/Mercati/default.aspx
- OMIE/GME membership: https://www.europex.org/members/gme/
- Terna Electricity Market: https://www.terna.it/en/electric-system/electricity-market
- Terna documentation: https://download.terna.it/terna/Chapter_4_8dd478073302a25.pdf
- GME TIDE announcement: https://www.mercatoelettrico.org/en-us/Home/NoticesandAnnouncements/NoticesandAnnouncementsME
