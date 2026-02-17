# Energy Market Protocols - Competitive Discovery

## Purpose

Map European energy market protocols by country and identify which software companies implement them.
Protocols are the fingerprint of the energy back-office market -- if you implement EDSN, MaBiS, or AS4,
you're a player. Following the protocols reveals the full competitive landscape.

**Parent**: [Competitive Landscape Analysis](../README.md)
**Prompt**: `.cursor/prompts/analysis/market/research-protocols.prompt.md`
**Last Updated**: 2026-02-15

---

## Eneve Protocol Baseline

| Category | Protocol | Market | Notes |
|---|---|---|---|
| Market Communication | EDSN | Netherlands | Central market facilitator |
| TSO Communication | TenneT NL protocols, ECP/MADES | Netherlands | TenneT as TSO |
| Balancing | ETPA, allocation formats | Netherlands | Balancing responsible parties |
| Settlement | C-ARM Allocation & Reconciliation | Netherlands | Via EDSN / CGI |
| Metering | DSMR (P1/P4) | Netherlands | Dutch Smart Meter Requirements |
| Switching | EDSN switching (C-AR) | Netherlands | Standardized supplier switching |
| Transport | AS4, MSCONS, UTILMD, APERAK | Netherlands | EDI message types |
| Expanding | Elia / Atrias (MIG6) | Belgium | Market entry |

---

## Country Research Status

| Country | File | Status | Last Updated |
|---|---|---|---|
| Netherlands | [netherlands.md](netherlands.md) | Complete | 2026-02-15 |
| Germany | [germany.md](germany.md) | Complete | 2026-02-15 |
| Belgium | [belgium.md](belgium.md) | Complete | 2026-02-15 |
| United Kingdom | [uk.md](uk.md) | Complete | 2026-02-15 |
| Norway | [norway.md](norway.md) | Complete | 2026-02-15 |
| Sweden | [sweden.md](sweden.md) | Complete | 2026-02-15 |
| Finland | [finland.md](finland.md) | Complete | 2026-02-15 |
| Denmark | [denmark.md](denmark.md) | Complete | 2026-02-15 |
| France | [france.md](france.md) | Complete | 2026-02-15 |
| Switzerland | [switzerland.md](switzerland.md) | Complete | 2026-02-15 |
| Austria | [austria.md](austria.md) | Complete | 2026-02-15 |
| Spain | [spain.md](spain.md) | Complete | 2026-02-15 |
| Italy | [italy.md](italy.md) | Complete | 2026-02-15 |
| Poland | [poland.md](poland.md) | Complete | 2026-02-15 |
| Convergence | [convergence.md](convergence.md) | Complete | 2026-02-15 |

---

## Company-Protocol Matrix

### Existing Competitors

| Company | NL (EDSN) | DE (MaBiS/MaKo) | BE (MIG6/Elia) | UK (BSC) | NO (Elhub) | SE (Ediel) | FI (Datahub) | DK (DataHub) | FR (RTE) | CH | AT (EDA) | ES (OMIE) | IT (GME) | PL (CSIRE) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Eneve** | **Y** | - | Expanding | - | - | - | - | - | - | - | - | - | - | - |
| SOPTIM | - | **Y** (all 4 TSOs) | - | - | - | - | - | - | - | - | Y (DACH) | - | - | - |
| Trayport | Y | - | - | Y | - | - | - | - | - | - | - | - | - | - |
| Brady | - | - | - | Y | - | - | - | - | - | Y | - | Y | Y | - |
| Volue | - | - | - | Y | **Y** (HQ) | Y | Y | Y | - | - | - | - | - | - |
| KISTERS | - | **Y** | - | - | - | - | - | - | - | Y | Y | - | - | - |
| Sopra Steria | - | **Y** | Y | - | - | - | - | - | Y (HQ parent) | - | - | - | - | - |
| Engrate | Y | Y | - | - | - | Y | - | - | - | - | - | - | - | - |
| ION/Allegro | - | - | - | Y | - | - | - | - | - | - | - | Y | Y | - |
| Hitachi Energy | - | - | - | Y | - | - | - | - | Y | **HQ** | - | - | Y | - |
| Energy One | - | - | - | Y | - | - | - | - | - | - | - | - | - | - |
| Previse | - | - | - | - | - | - | - | - | - | Y | - | Y (entering) | - | - |
| Orchestrade | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| Molecule | - | - | - | Y (entering) | - | - | - | - | - | - | - | - | - | - |
| Qualia | - | - | - | Y | - | - | - | - | - | - | - | - | - | - |
| CGI | **Y** (C-ARM) | - | - | Y | - | - | - | **Y** (DataHub) | - | - | - | - | - | - |
| Worldgrid/ALTEN | - | - | - | - | - | - | - | - | Y | - | - | - | - | - |
| tem | - | - | - | Y | - | - | - | - | - | - | - | - | - | - |

### Key Observations
- **SOPTIM** dominates Germany (all 4 TSOs) with strong DACH presence (AT)
- **Volue** has broadest Nordic coverage (NO, SE, FI, DK + UK)
- **CGI** is the data hub specialist (NL C-ARM, DK DataHub)
- **Engrate** is uniquely positioned across NL + DE + SE (3 key markets)
- **Sopra Steria** has strong DE + BE + FR triangle
- **Brady, ION, Hitachi** focus on UK + Southern Europe (ES, IT)
- **Eneve** concentrated in NL with BE expansion -- protocol-based expansion to DE or Nordics would require significant new protocol implementation

---

## Newly Discovered Companies (All Countries)

### High Relevance (Direct Competitor Space)

| Company | Product | Country | Markets | Protocols | Why Relevant |
|---|---|---|---|---|---|
| **Robotron** | Energy Market Platform | DE | Germany | MaBiS, GPKE, GeLi, GaBi, WiM, EDIFACT | Full energy market platform covering all German protocols -- direct competitor to SOPTIM/KISTERS in DE |
| **Ferranti** | MECOMS 365 | BE | Belgium | MIG6, meter data, CIS | Meter data management + CIS for Belgian grid operators -- overlaps with eBase metering capabilities |
| **TietoEVRY** | Energy solutions | FI/NO | Nordics | Ediel, Elhub, Nordic market | Major Nordic utility software vendor -- billing, market processes |
| **EG (Vitec/PowerEL)** | EG Utility | DK/NO | Nordics | Ediel, Elhub, DataHub | Nordic utility billing/settlement specialist |

### Medium Relevance (Adjacent / Niche)

| Company | Product | Country | Markets | Protocols | Why Relevant |
|---|---|---|---|---|---|
| **SEEBURGER** | MaKo AS4 Cloud | DE | Germany | AS4, MaKo, EDIFACT | 450+ market participants, 50M+ msgs/month -- B2B integration layer, not full back-office |
| **Arvato Systems** | AEP MaKo Cloud | DE | Germany | AS4, MaKo, MaBiS | MaKo SaaS, Bertelsmann subsidiary |
| **Indra / Minsait** | Onesait Utilities | ES | Spain | OMIE, REE, SIPS | Major Iberian utility software vendor |
| **Engineering Ingegneria** | Utility software | IT | Italy | GME, Terna, SII | Major Italian IT services company |
| **MaxBill** | Billing/CIS platform | UA/Global | Poland | CSIRE, billing | Targeting Polish energy market CSIRE integration |
| **Asseco** | Utility solutions | PL | Poland | CSIRE, billing | Major Polish IT company with energy practice |
| **Schleupen** | Schleupen.CS | DE | Germany | MaKo, EDIFACT | ERP/billing with integrated MaKo |

### Low Relevance (Infrastructure / Consulting)

| Company | Product | Country | Markets | Why Low |
|---|---|---|---|---|
| Technolution Spark | EDSN Platform operator | NL | NL | Infrastructure partner, not competitor |
| ETPA | Trading Platform | NL | NL | Trading platform, not back-office |
| Accenture | Elhub, Atrias builder | Global | NO, BE | System integrator, not product company |
| Cegal | Elhub operations | NO | NO | IT operations, not product |
| Ponton GmbH | PONTON X/P | DE/AT | AT | Connectivity middleware |
| SAP | IS-U / S4HANA | Global | All | ERP infrastructure layer |
| Capita | DCC services | UK | UK | Smart meter infrastructure |
| Solteq | Datahub consulting | FI | FI | Consulting/onboarding |
| Univio | CSIRE integration | PL | PL | Integration consulting |

---

## Protocol Coverage Heat Map

Markets ranked by protocol density (number of distinct protocol categories with active implementations):

| Rank | Market | Data Hub | Msg Standard | Transport | Protocol Maturity |
|---|---|---|---|---|---|
| 1 | **Germany** | Planned (MaBiS Hub 2030) | EDIFACT | AS4 (mandatory) | Very High |
| 2 | **Netherlands** | EDSN/C-ARM | EDIFACT | AS4, AMQP | Very High |
| 3 | **Belgium** | Atrias/MIG6 | MIG6 XML | Atrias platform | High |
| 4 | **Norway** | Elhub | ebIX XML | Elhub platform | High |
| 5 | **Denmark** | DataHub | ebIX XML | DataHub platform | High |
| 6 | **Finland** | Datahub | ebIX XML | Datahub platform | High |
| 7 | **UK** | MHHS DIP (transitioning) | Proprietary/XML | Various | High |
| 8 | **Austria** | EDA | ebUtilities XML | PONTON CEP | Medium-High |
| 9 | **Poland** | CSIRE (launched Jul 2025) | IES XML | CSIRE platform | Medium (emerging) |
| 10 | **France** | None (Enedis SGE partial) | Various | RTE portal/API | Medium |
| 11 | **Spain** | SIPS (partial) | Proprietary | OMIE/REE platforms | Medium |
| 12 | **Italy** | SII (partial) | Proprietary | GME/Terna platforms | Medium |
| 13 | **Sweden** | On hold | EDIFACT/ebIX | Bilateral | Low-Medium |
| 14 | **Switzerland** | None | Various | Bilateral | Low |

---

## How to Use

Run the research-protocols prompt to update this folder:

```
@research-protocols all                    # Full European scan
@research-protocols Netherlands            # Single country
@research-protocols MaBiS                  # Single protocol
```

Output from each run should update the relevant country file and this README's matrices.
