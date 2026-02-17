# European Protocol Convergence Assessment

## Purpose

Analyze how protocol harmonization trends across European energy markets affect the competitive landscape and Eneve's market position.

**Last Updated**: 2026-02-15

---

## 1. ENTSO-E Balancing Platform Harmonization

Three pan-European platforms are unifying balancing protocols under EU Regulation 2017/2195 (Electricity Balancing Guideline):

| Platform | Purpose | Reserves Type | Status (2025) |
|---|---|---|---|
| **PICASSO** | Automatic Frequency Restoration | aFRR | Live, expanding (PSE, REE, Elering joining) |
| **MARI** | Manual Frequency Restoration | mFRR | Live, most TSOs connected |
| **TERRE** | Replacement Reserves | RR | Live, limited participation |

**Impact on competitive landscape**: Companies implementing these platforms (SOPTIM, Volue, Sopra Steria) gain cross-border portability. A vendor that connects to MARI in Germany can more easily expand to France or Spain using the same balancing protocol. This lowers barriers for cross-border expansion.

**Impact on Eneve**: As PICASSO/MARI replace national balancing protocols, Eneve's TenneT-specific balancing implementation becomes less unique. However, Eneve could leverage MARI/PICASSO standardization to expand into new markets using familiar protocols.

---

## 2. ISP15 Harmonization (15-Minute Settlement)

The EU is standardizing **15-minute imbalance settlement periods** across all member states:

| Country | ISP15 Status | Timeline |
|---|---|---|
| Netherlands | Already 15-min (PTU) | In place |
| Germany | Already 15-min | In place |
| France | **Transitioned Jan 2025** | Complete |
| Belgium | Already 15-min | In place |
| Nordics | Transitioning | Varies by country |
| Spain | **15-min products launched 2025** | Ongoing |
| Italy | Transitioning | In progress |
| Poland | Transitioning | Aligned with CSIRE launch |

**Impact on competitive landscape**: ISP15 standardization means all vendors must handle quarter-hourly resolution data. This creates a common technical baseline, making it easier for vendors to operate across borders. Vendors already handling 15-min resolution (NL, DE specialists like Eneve, SOPTIM) have an advantage.

---

## 3. Data Hub Convergence

Centralized national data hubs are becoming the standard pattern:

| Country | Data Hub | Status | Builder |
|---|---|---|---|
| Denmark | DataHub (Energinet) | **Live since 2013** (pioneer) | CGI |
| Norway | Elhub | **Live since 2019** | Accenture |
| Finland | Datahub (Fingrid) | **Live** | Fingrid Datahub Oy |
| Belgium | Atrias Clearing House | **Live** | Accenture/Avanade |
| Netherlands | EDSN/C-ARM | **Live** (evolving) | CGI |
| Poland | CSIRE | **Launched Jul 2025** | PSE |
| Sweden | Elmarknadshubb | **On hold** (legislative delays) | SvK (planned) |
| Austria | EDA | **Live** (expanding) | EDA GmbH |
| Germany | MaBiS Hub | **Planned** (consultation 2024, target 2030) | TBD |
| UK | MHHS DIP | **Transitioning** (2025) | Elexon |
| France | No central hub | Enedis SGE for metering | N/A |
| Spain | SIPS (partial) | Limited centralization | DSOs |
| Italy | SII (partial) | Acquirente Unico | AU |
| Switzerland | No hub | Bilateral | N/A |

**Impact on competitive landscape**: Data hubs create single integration points, lowering entry barriers for new vendors. But they also reduce the value of proprietary DSO/TSO integration knowledge -- a key Eneve differentiator in the Netherlands.

**Impact on Eneve**: Eneve's deep EDSN/C-ARM integration is a competitive moat in NL. As more countries adopt hubs, this pattern could be replicated. However, each hub is unique (different protocols: ebIX, MIG6, IES, ebUtilities), so "write once, deploy everywhere" is not yet realistic.

---

## 4. AS4/ECP Transport Harmonization

Transport protocols are converging toward AS4 and ECP (Energy Communication Platform):

| Protocol | Region | Status |
|---|---|---|
| **AS4** | Germany (mandatory since Oct 2023), EU trend | Rapidly expanding |
| **ECP** | ENTSO-E cross-border (all TSOs) | Standard for TSO-TSO communication |
| **MADES** | ENTSO-E alternative/complement to ECP | Used alongside ECP |
| **ebIX** | Nordics | Standard for Nordic data hubs |
| **ebUtilities** | Austria | Austrian-specific variant |
| **EDIFACT** | Legacy across EU | Being replaced by XML, but still dominant in DE/NL |

**Convergence trend**: AS4 is becoming the dominant transport protocol for B2B market communication (Germany led, others following). ECP is standard for TSO-level cross-border exchange. EDIFACT message content remains widespread but is gradually being complemented or replaced by XML schemas (ebIX, CIM).

**Impact on Eneve**: Eneve should ensure AS4 readiness. As more markets mandate AS4, it becomes a required capability for any market expansion.

---

## 5. EU Regulatory Drivers

Key EU regulations driving protocol convergence:

| Regulation | Impact |
|---|---|
| **Electricity Balancing Guideline (2017/2195)** | MARI/PICASSO/TERRE platforms, harmonized balancing |
| **CACM Regulation (2015/1222)** | SDAC/SIDC, day-ahead and intraday coupling (EUPHEMIA, XBID) |
| **Clean Energy Package (2019)** | Prosumer rights, energy communities, aggregator roles |
| **Network Code on Interoperability** | EDIG@S required for gas nomination/matching |
| **REMIT II** | Enhanced transparency, transaction reporting |
| **Metering Point Administration** | Push toward centralized data hubs |

---

## 6. Protocol Convergence vs. National Fragmentation

### Areas of High Convergence
- Cross-border scheduling (ENTSO-E ESS -- universal)
- Balancing markets (MARI/PICASSO -- expanding to all TSOs)
- Gas nominations (EDIG@S -- EU-wide standard)
- Transport (AS4 -- becoming EU standard)
- Market coupling (SDAC/SIDC -- nearly all NEMO countries)

### Areas of Persistent Fragmentation
- Retail market processes (switching, metering, billing -- still national)
- Data hub implementations (each country has unique architecture)
- Message content standards (EDIFACT vs ebIX vs ebUtilities vs proprietary)
- Smart meter specifications (DSMR, Linky, SMETS2 -- all different)
- Settlement methodologies (marginal vs pay-as-bid, various time resolutions)

### Implication for Competitors
- **Cross-border TSO/wholesale vendors** (SOPTIM, Volue, KISTERS) benefit from convergence -- standardized balancing and scheduling protocols are portable
- **Retail/back-office vendors** (Eneve, Engrate, Sopra Steria) face persistent national barriers -- each market has unique data hub, switching, and metering protocols
- **Cloud-native API vendors** (Engrate, Previse) can adapt faster to new protocols than legacy on-premise systems
- **System integrators** (CGI, Accenture) benefit from fragmentation -- each data hub is a new implementation project

---

## 7. Strategic Implications for Eneve

### Opportunities
1. **MARI/PICASSO expertise is portable**: If Eneve implements ENTSO-E balancing platform connectivity, it works in multiple countries
2. **ISP15 already native**: Eneve's 15-min PTU resolution is ahead of countries still transitioning (FR, ES, IT, PL)
3. **Data hub pattern repeats**: EDSN/C-ARM integration experience is valuable as more countries (DE with MaBiS Hub, PL with CSIRE) launch hubs
4. **Belgium expansion is protocol-adjacent**: Elia/Atrias protocols share structural similarities with EDSN

### Threats
1. **Hub standardization reduces moats**: As data hubs lower integration complexity, new entrants can enter NL market more easily
2. **Cloud-native vendors adapt faster**: Engrate, Previse can implement new protocols faster than on-premise systems
3. **AI-native entrants skip legacy protocols**: tem, Qualia may build on top of hub APIs rather than implementing traditional protocols
4. **Cross-border vendors coming to NL**: As protocols harmonize, SOPTIM, KISTERS, Sopra Steria could more easily target Dutch market

---

## Sources

- ENTSO-E PICASSO: https://www.entsoe.eu/network_codes/eb/picasso/
- ENTSO-E MARI: https://www.entsoe.eu/network_codes/eb/mari/
- MARI/PICASSO/TERRE overview: https://nanoenergies.eu/knowledge-base/mari-picasso-and-terre
- ACER PICASSO amendments: https://www.acer.europa.eu/news/acer-amends-eu-electricity-balancing-rules-improve-efficiency-picasso-platform
- ENTSO-E Balancing Workshop: https://www.entsoe.eu/events/2025/11/04/balancing-platforms-stakeholders-workshop/
