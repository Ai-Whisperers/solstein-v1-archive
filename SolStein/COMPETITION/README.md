# Competitive Landscape Analysis

## Purpose

Identify and profile European competitors to Eneve's eBase platform in energy back-office,
time series management, balancing/settlement, and ETRM software markets.

**Phase**: Identification (deeper analysis to follow)
**Last Updated**: 2026-02-16 (added Hansen Technologies - NL infrastructure provider with full energy suite)

---

## Eneve Positioning Summary

Eneve's eBase platform is a market leader in the Dutch energy back-office market, providing:

| Capability | Details |
|---|---|
| **Time Series Management** | Smart meter data, linked time series, aggregation |
| **Balancing & Settlement** | Power allocation, imbalance, gas balancing |
| **Nominations & Scheduling** | TSO/DSO communication, EDSN protocols |
| **Message Processing** | EDI messages, validation, notification processing |
| **Market Operations** | Market participant mgmt, grid area mgmt, EAN codes |
| **Commodities** | Electricity (primary), Gas (secondary) |
| **Markets** | Netherlands (primary), Belgium (expanding) |
| **Platform** | MSSQL, on-premise, migrating to C#/.NET |

---

## Competitor Tier Classification

### Tier 1 - Direct Competitors

Energy back-office, time series management, balancing/settlement platforms that overlap
significantly with Eneve's core capabilities.

| Company | Product | HQ | Employees | Cloud/On-Prem | File |
|---|---|---|---|---|---|
| **SOPTIM AG** | **SOPTIM Elements** | **Germany** | **377** | **Cloud SaaS + On-prem** | **[soptim.md](soptim/soptim.md)** |
| Trayport (TMX Group) | Periotheus | UK | ~240 | On-premise + SaaS | [trayport-periotheus.md](trayport-periotheus/trayport-periotheus.md) |
| Brady Technologies | PowerDesk Suite | UK | ~200 est. | SaaS + On-premise | [brady-technologies-powerdesk.md](brady-technologies-powerdesk/brady-technologies-powerdesk.md) |
| Volue ASA | Volue Energy suite | Norway | ~650 | SaaS (71% recurring) | [volue.md](volue/volue.md) |
| KISTERS | BelVis / BelVis+ | Germany | 750+ | On-premise + Cloud | [kisters-belvis.md](kisters-belvis/kisters-belvis.md) |
| Sopra Steria | cpX.Energy | Germany | Large (parent: 56k) | Cloud SaaS | [sopra-steria-cpx-energy.md](sopra-steria-cpx-energy/sopra-steria-cpx-energy.md) |
| Engrate | Engrate API Platform | Sweden | <20 est. | Cloud API | [engrate.md](engrate/engrate.md) |
| **Hansen Technologies** | **Hansen Suite (CIS/MDM/EDM/Trade)** | **Australia (global)** | **1,643** | **Hybrid (SaaS + On-prem)** | **[deep-analysis.md](hansen-technologies/deep-analysis.md)** |

> **SOPTIM is Eneve's closest functional twin**: same core capabilities (balancing, scheduling,
> nominations, TSO communication), same market niche, 377 employees, serves 100% of German TSOs.
> Missed in initial research because they position as "energy operations" not "ETRM/trading".
>
> **Hansen Technologies** runs the Dutch energy data backbone (EDSN C-ARM, 100% of NL connections,
> 15M+ metering points) and has full CIS/MDM/EDM/Trading capabilities. A$392M revenue, 1,643
> employees, 550+ customers in 80+ countries. Uniquely positioned to expand from NL infrastructure
> provider to direct back-office competitor.

### Tier 1b - Protocol-Discovered National/Regional Specialists

National market players discovered through protocol research. They compete with Eneve in specific
markets through deep local protocol expertise, utility billing, metering, and market communication.

| Company | Product | HQ | Markets | AI Signal | File |
|---|---|---|---|---|---|
| **Robotron** | **Energy Market Platform** | **Germany** | **DE** | **MODERATE-STRONG** | **[robotron.md](robotron/robotron.md)** |
| **EG (Vitec/PowerEL)** | **EG Utility** | **Denmark** | **DK, SE, NO, FI** | **STRONG** | **[eg-utility.md](eg-utility/eg-utility.md)** |
| **TietoEVRY** | **Energy & Utilities** | **Finland** | **FI, NO, Nordics** | **STRONG** | **[tietoevry.md](tietoevry/tietoevry.md)** |
| **MaxBill** | **AI Billing Platform** | **UK (global ops)** | **NL, PL, Baltics, EV** | **VERY STRONG** | **[maxbill.md](maxbill/maxbill.md)** |
| **Indra / Minsait** | **Onesait Utilities** | **Spain** | **ES, 5 continents** | **STRONG** | **[indra-minsait.md](indra-minsait/indra-minsait.md)** |
| **Engineering Group** | **Neta Open Suite** | **Italy** | **IT, ES, LatAm** | **MODERATE-STRONG** | **[engineering-group.md](engineering-group/engineering-group.md)** |
| **Ferranti** | **MECOMS 365** | **Belgium** | **BE, UK, SG** | **LOW-MODERATE** | **[ferranti.md](ferranti/ferranti.md)** |
| **Asseco** | **Utility solutions** | **Poland** | **PL (65% market)** | **MODERATE** | **[asseco.md](asseco/asseco.md)** |

> **Robotron** is particularly notable: full energy market platform serving E.ON, ENGIE, Shell Energy
> with AI forecasting (ePredict) and all German MaKo protocols. **MaxBill** is AI-native from inception
> with 80% faster time-to-market claims. **EG** just acquired Bright Energy (Dec 2025) for AI-driven
> energy management. These were invisible in traditional ETRM market research.

### Tier 2 - Broader ETRM with Back-Office

Full-spectrum ETRM platforms that include back-office capabilities but compete on a
broader front-to-back trading basis.

| Company | Product | HQ | Employees | Cloud/On-Prem | File |
|---|---|---|---|---|---|
| ION Commodities (ION Group) | Allegro / Endur | Global | Large (parent: 13k+) | Both | [ion-commodities-allegro.md](ion-commodities-allegro/ion-commodities-allegro.md) |
| Hitachi Energy | RiskTracker / Market Ops | Switzerland | Large (parent: 40k+) | Both | [hitachi-energy.md](hitachi-energy/hitachi-energy.md) |
| Energy One / Contigo | enTrader | Australia/UK | ~200 est. | SaaS + On-premise | [energy-one-entrader.md](energy-one-entrader/energy-one-entrader.md) |
| Previse Systems | Coral | Switzerland | ~52 | Cloud-native SaaS | [previse-systems-coral.md](previse-systems-coral/previse-systems-coral.md) |
| **Orchestrade** | **Orchestrade ETRM** | **USA/Europe** | **Mid-size** | **Cloud + On-prem** | **[orchestrade.md](orchestrade/orchestrade.md)** |
| **Molecule** | **Molecule ETRM** | **USA (expanding EU)** | **Mid-size** | **Cloud-only SaaS** | **[molecule.md](molecule/molecule.md)** |
| **Qualia Trading** | **Qualia AI ETRM** | **UK (est.)** | **Small (startup)** | **Cloud-only SaaS** | **[qualia-trading.md](qualia-trading/qualia-trading.md)** |

> **New Tier 2 entrants**: Orchestrade (#6 Energy50, 6 major awards in 2025), Molecule
> (cloud-native, expanding EU with $100B+ daily value), Qualia (AI-native ETRM, same-day go-live).

### Tier 3 - Adjacent / Disruptors / Infrastructure

Companies providing energy consulting, infrastructure, marketplace platforms, integration layers,
or disruptive models that are not direct product competitors but signal market direction.

| Company | Product | HQ | Employees | File |
|---|---|---|---|---|
| ALTEN Worldgrid | Consulting/Engineering | France | ~1,100 | [alten-worldgrid.md](alten-worldgrid/alten-worldgrid.md) |
| CGI | C-ARM (EDSN partner) | Canada/NL | Large (parent: 90k+) | [cgi-edsn.md](cgi-edsn/cgi-edsn.md) |
| **tem** | **Rosso / RED** | **UK (London)** | **Scale-up** | **[tem-energy.md](tem-energy/tem-energy.md)** |
| **SEEBURGER** | **MaKo AS4 Cloud** | **Germany** | **~1,200** | **[seeburger.md](seeburger/seeburger.md)** |
| **Arvato Systems** | **AEP MaKo Cloud** | **Germany** | **~3,500** | **[arvato-systems.md](arvato-systems/arvato-systems.md)** |
| **Schleupen** | **Schleupen.CS** | **Germany** | **~630** | **[schleupen.md](schleupen/schleupen.md)** |
| **Octopus Energy / Kraken** | **Kraken Platform** | **UK (London)** | **2,000+ (Kraken)** | **[deep-analysis.md](octopus-energy-kraken/deep-analysis.md)** |
| **Creatica** | **FlexBid Autotrader** | **Germany (Munich)** | **<20 est.** | **[deep-analysis.md](creatica/deep-analysis.md)** |
| **Dexter Energy** | **AI Forecasting & Trade Optimization** | **Netherlands (Amsterdam)** | **~90-100** | **[deep-analysis.md](dexter/deep-analysis.md)** |

> **Octopus Energy / Kraken** is the most significant adjacent threat discovered. Kraken raised
> $1B in Dec 2025 at $8.65B valuation, serves 70M+ utility accounts globally, and is IPO-bound
> at potential $15B. AI-native platform (15B data points/day, 100+ deploys/day). Rotterdam hub
> via Jedlix acquisition. Not a direct competitor today (utility CRM/billing vs energy market
> operations), but with $1B fresh capital could acquire into Eneve's space.
>
> **tem** raised $75M Series B (Feb 2026) at $300M+ valuation as the "Stripe of energy".
> AI-native transaction engine with 2,600+ customers. Signals where AI-native energy
> platforms are heading -- and the funding levels they attract.
>
> **SEEBURGER** (450+ participants, 50M+ msgs/month) and **Arvato Systems** are the dominant
> German MaKo integration layer. **Schleupen** provides ERP/billing with integrated MaKo on AWS.
>
> **Dexter Energy** is Amsterdam-based, AI-native from founding (2017), with EUR 36M total
> funding. 59% of staff are AI/data science specialists. Provides ML-powered renewable
> generation forecasting, probabilistic price forecasting, and automated trading signals for
> short-term power markets. Operates in Eneve's home market (NL) serving shared customers
> (Greenchoice). Energy Risk "One to Watch" 2025. Complementary threat -- intelligence layer
> sitting above back-office operations.

---

## Quick-Reference Comparison Matrix

| Capability | Eneve | Trayport | Brady | Volue | KISTERS | Sopra Steria | Engrate | Hansen | ION | Hitachi | Energy One | Previse |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Time Series Mgmt | Y | Y | Partial | Y | Y | Y | Partial | Y | - | - | - | - |
| Balancing | Y | Y | Y | Y | Y | Y | Partial | Y | - | - | - | - |
| Settlement | Y | - | Y | - | Y | Y | Y | Y | Y | Y | Y | Y |
| Nominations/Scheduling | Y | Y | - | - | - | Y | Y | Y | - | - | Y | - |
| TSO Communication | Y | Y | - | Y | - | Y | Y | Y | - | - | Y | - |
| Smart Meter Data | Y | - | - | - | Y | Y | - | Y | - | - | - | - |
| Power Trading | - | - | Y | Y | Y | - | - | Y | Y | Y | Y | Y |
| Risk Management | - | - | Y | - | - | - | - | - | Y | Y | Y | Y |
| Gas | Y | Y | - | - | Y | Y | - | Y | Y | - | - | Y |
| NL Market | Y | Y | - | - | - | - | Y | Y | - | - | - | - |
| Cloud-Native | - | - | Y | Y | Partial | Y | Y | Partial | - | - | Partial | Y |

---

## AI Adoption Ranking

All competitors ranked by strength of AI signal in their product development:

| Rank | Company | Tier | AI Signal | Key Evidence |
|---|---|---|---|---|
| 1 | **Octopus / Kraken** | 3 | VERY STRONG | AI-native utility OS: 15B data points/day, ML forecasting, Agent Assist (30% productivity), 700MW grid balancing, 1.5M demand response participants. $8.65B valuation, $1B raised. AI IS the platform. |
| 2 | **tem** | 3 | VERY STRONG | AI-native core: Rosso engine uses ML + LLMs for supply/demand prediction. AI IS the product. $75M to scale it. |
| 3 | **Qualia Trading** | 2 | VERY STRONG | AI-native ETRM from founding, AI powers same-day go-live and automated reconciliation |
| 4 | **Dexter Energy** | 3 | VERY STRONG | AI-native from founding (2017). 59% of staff (53/90) are AI/data science specialists. ML-powered generation forecasting, probabilistic price forecasting, automated trading signals. 1TB weather data/day, 200+ TB total. Google Cloud + Xebia partnership. Dutch Ministry AI showcase. Energy Risk "One to Watch" 2025. AI IS the entire product. |
| 5 | **MaxBill** | 1b | VERY STRONG | AI-native billing: AI Product Catalog, AI CRM, AI Billing. 80% faster time-to-market. Expanding PL/Baltics. |
| 6 | **Engrate** | 1 | STRONG | AI-native from founding, MCP Server, AI-first architecture |
| 7 | **Hitachi Energy** | 2 | VERY STRONG | OpenAI + NVIDIA partnerships, AI-Ready Grid, FastTracker AI integration |
| 8 | **EG (Vitec/PowerEL)** | 1b | STRONG | Acquired Bright Energy (Dec 2025) for AI energy management. AI across all solutions. 240 specialists. |
| 9 | **TietoEVRY** | 1b | STRONG | SmartGen AI Suite, AIOps, predictive maintenance, Siemens Gridscale X, Microsoft Copilot partner |
| 10 | **Volue ASA** | 1 | STRONG | AI-weather forecasting, Algo Trader, PowerBot acquisition |
| 11 | **Indra / Minsait** | 1b | STRONG | IA4TES AI for energy transition, smart grid AI, DER prediction, 80% Copilot adoption |
| 12 | **Brady Technologies** | 1 | STRONG | PowerDesk Edge ML, peer-reviewed ML research, grid signal ML |
| 13 | **Sopra Steria** | 1 | STRONG | cpX.AI module, neural network forecasting, anomaly detection |
| 14 | **Hansen Technologies** | 1 | MODERATE-STRONG | AI Virtual Agent (ConvAI/GenAI), AI-Optimised Power Trading (autonomous bidding), powercloud payment AI (98% accuracy). AWS GenAI partnership. |
| 15 | **Robotron** | 1b | MODERATE-STRONG | AI Workstation product, ePredict AI forecasting, IoTHub4U. Serves E.ON, ENGIE, Shell. |
| 16 | **Engineering Group** | 1b | MODERATE-STRONG | EngGPT ("AI Made in Italy"), Neta with AI/ML for 40M+ users. Energy community AI. |
| 17 | **KISTERS** | 1 | MODERATE | AI-based BelVis PRO forecasting, digital twins |
| 18 | **Orchestrade** | 2 | MODERATE | Event-driven real-time architecture, AI-ready but not yet AI-branded |
| 19 | **Asseco** | 1b | MODERATE | AI-driven automation, 13 acquisitions for AI/cyber, 65% Polish energy market |
| 20 | **Trayport** | 1 | MODERATE | autoTRADER algorithms (more rule-based than ML) |
| 21 | **Molecule** | 2 | MODERATE | Cloud-native, automated trade capture, "data ecosystem" focus |
| 22 | **SOPTIM** | 1 | LOW-MODERATE | Cloud SaaS platform, no explicit AI features, compliance-focused |
| 23 | **Ferranti** | 1b | LOW-MODERATE | Anomaly detection in meter data, pattern-based estimation, no explicit AI branding |
| 24 | **Schleupen** | 3 | LOW-MODERATE | Modern SaaS on AWS, dynamic tariffs, no explicit AI |
| 25 | **Previse Systems** | 2 | LOW | Cloud-native but no explicit AI features yet |
| 26 | **Energy One** | 2 | LOW | No visible AI product features |
| 27 | **ION (Allegro)** | 2 | LOW | Blog content only, no product AI announcements |
| 28 | **SEEBURGER** | 3 | MODERATE | Agentic AI, MCP integration, LLM support (OpenAI/Anthropic) in BIS platform; not energy-specific |
| 29 | **Arvato Systems** | 3 | MODERATE | AEP.DataHub AI modules (anomaly detection, forecasting), OGE AI pipeline monitoring, ISG Leader in Generative AI for Microsoft Clouds |

**Eneve implication**: The AI-native wave extends beyond ETRM into utility billing (MaxBill),
Nordic energy management (EG + Bright Energy), national market platforms (Robotron ePredict),
and now renewable trading optimization in Eneve's own backyard (Dexter Energy, Amsterdam-based,
rank 4). Dexter's 59% AI staff ratio and EUR 36M funding demonstrate that AI-native companies
are building intelligence layers directly above Eneve's operations layer -- in the same Dutch
market, serving shared customers. SOPTIM (Eneve's closest twin) at rank 22 means both
companies risk being outflanked by AI-native entrants in their own national markets.

---

## Acceleration Ranking (Last 12 Months)

Competitors ranked by observable acceleration in the last year:

| Rank | Company | Acceleration | Key Evidence |
|---|---|---|---|
| 1 | **Octopus / Kraken** | VERY STRONG | $1B raised Dec 2025, $8.65B valuation, Kraken spun off as independent company, 4 acquisitions (Jedlix/Sennen/Kwest/Energetiq), IPO planned at potential $15B, National Grid US (6.5M) + TalkTalk wins |
| 2 | **tem** | VERY STRONG | $75M Series B (Feb 2026), $300M+ valuation, 2,600 customers, expanding to AU+US |
| 3 | **Previse Systems** | VERY STRONG | 5x customer growth in 2yr, Lightrock funding, Energy Risk Award, entering Spain + North America |
| 4 | **Volue ASA** | VERY STRONG | SaaS +42%, EBITDA 17%->22%, PowerBot + Quorum acquisitions, divested non-core |
| 5 | **Engrate** | VERY STRONG | Founded Jan 2024, EUR 3M+ raised, product live in NL+DE+SE in 18 months |
| 6 | **Dexter Energy** | STRONG | EUR 23M Series C (Jul 2025), total EUR 36M raised, 43% employee growth, expanded from 9 to 13 EU countries, Energy Risk "One to Watch" 2025, PowerBot/Volue integration, BESS product expansion |
| 7 | **Orchestrade** | STRONG | 6 major awards in 2025, 3rd consecutive "Best Power Trade Management", BB Energy <10wk deploy, Singapore expansion |
| 8 | **Molecule** | STRONG | Series B (Jul 2025), EU/UK expansion, dedicated EU production, Nuveen as customer, 2x Power Tech Awards |
| 9 | **Sopra Steria** | STRONG | New customer wins, cpX.AI launch, Hydrogen module, mobile app |
| 10 | **KISTERS** | STRONG | BelVis+ PFM cloud pivot (June 2026), E-world 2026 showcase |
| 11 | **Hitachi Energy** | STRONG | OpenAI/NVIDIA partnerships, AI pivot, but ETRM-specific unclear |
| 12 | **Brady Technologies** | MODERATE | PowerDesk Data Manager launch, geographic expansion |
| 13 | **Energy One** | MODERATE | 17% revenue growth, 74% NPAT increase, brand consolidation |
| 14 | **SOPTIM** | MODERATE | SOPTIM Elements cloud SaaS launch, REMIT II compliance, E-world 2026 |
| 15 | **Qualia Trading** | MODERATE-STRONG | New AI-native ETRM entrant, disruptive same-day deploy model, early stage |
| 16 | **Trayport** | LOW-MODERATE | Stable, no major launches or acquisitions |
| 17 | **ION (Allegro)** | LOW | No major Allegro developments, appears in maintenance mode |

**Eneve implication**: The market is bifurcating. On one side: AI-native startups with
massive funding (tem $75M, Previse $52M+, Dexter EUR 36M, Engrate EUR 3M). On the other:
legacy vendors in maintenance mode (ION, Trayport). The cloud-native middle tier
(Orchestrade, Molecule) is eating the traditional ETRM market. Dexter Energy (rank 6)
is particularly notable as it operates in Eneve's own Amsterdam backyard with EUR 23M
fresh capital. SOPTIM (Eneve's twin) shows only moderate acceleration -- both companies
risk being squeezed between well-funded disruptors and entrenched incumbents.

---

## Data Collection Status

### Tier 1 - Direct Competitors

| File | Status | Last Updated |
|---|---|---|
| [soptim.md](soptim/soptim.md) | Financial analysis complete | 2026-02-15 |
| [trayport-periotheus.md](trayport-periotheus/trayport-periotheus.md) | Financial analysis complete | 2026-02-15 |
| [brady-technologies-powerdesk.md](brady-technologies-powerdesk/brady-technologies-powerdesk.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [volue.md](volue/volue.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [kisters-belvis.md](kisters-belvis/kisters-belvis.md) | ID + AI/Acceleration complete | 2026-02-15 |
| [sopra-steria-cpx-energy.md](sopra-steria-cpx-energy/sopra-steria-cpx-energy.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [engrate.md](engrate/engrate.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [deep-analysis.md](hansen-technologies/deep-analysis.md) | Deep analysis + Financial analysis complete | 2026-02-16 |

### Tier 1b - Protocol-Discovered National Specialists

| File | Status | Last Updated |
|---|---|---|
| [robotron.md](robotron/robotron.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [eg-utility.md](eg-utility/eg-utility.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [tietoevry.md](tietoevry/tietoevry.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [maxbill.md](maxbill/maxbill.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [indra-minsait.md](indra-minsait/indra-minsait.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [engineering-group.md](engineering-group/engineering-group.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [ferranti.md](ferranti/ferranti.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [asseco.md](asseco/asseco.md) | Deep analysis + Financial analysis complete | 2026-02-15 |

### Tier 2 - Broader ETRM

| File | Status | Last Updated |
|---|---|---|
| [ion-commodities-allegro.md](ion-commodities-allegro/ion-commodities-allegro.md) | Financial analysis complete | 2026-02-15 |
| [hitachi-energy.md](hitachi-energy/hitachi-energy.md) | ID + AI/Acceleration + Financial analysis complete | 2026-02-15 |
| [energy-one-entrader.md](energy-one-entrader/energy-one-entrader.md) | ID + AI/Acceleration + Financial analysis complete | 2026-02-15 |
| [previse-systems-coral.md](previse-systems-coral/previse-systems-coral.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [orchestrade.md](orchestrade/orchestrade.md) | ID + AI/Acceleration + Financial analysis complete | 2026-02-15 |
| [molecule.md](molecule/molecule.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [qualia-trading.md](qualia-trading/qualia-trading.md) | ID + AI/Acceleration complete | 2026-02-15 |

### Tier 3 - Adjacent / Infrastructure

| File | Status | Last Updated |
|---|---|---|
| [tem-energy.md](tem-energy/tem-energy.md) | Financial analysis complete | 2026-02-15 |
| [alten-worldgrid.md](alten-worldgrid/alten-worldgrid.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [cgi-edsn.md](cgi-edsn/cgi-edsn.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [seeburger.md](seeburger/seeburger.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [arvato-systems.md](arvato-systems/arvato-systems.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [schleupen.md](schleupen/schleupen.md) | Deep analysis + Financial analysis complete | 2026-02-15 |
| [deep-analysis.md](octopus-energy-kraken/deep-analysis.md) | Deep analysis + Financial analysis complete | 2026-02-16 |
| [deep-analysis.md](creatica/deep-analysis.md) | Deep analysis + Financial analysis complete | 2026-02-16 |
| [deep-analysis.md](dexter/deep-analysis.md) | Deep analysis + Financial analysis complete | 2026-02-16 |

### Eneve Self-Assessment (Baseline)

| File | Status | Last Updated |
|---|---|---|
| [deep-analysis.md](eneve/deep-analysis.md) | Deep analysis complete (self-assessment) | 2026-02-15 |
| [financial-growth.md](eneve/financial-growth.md) | Financial analysis complete (self-assessment) | 2026-02-15 |

---

## Protocol-Based Discovery

Protocol mapping research to validate competitor completeness and discover missed players.
Energy protocols (EDSN, MaBiS, BSC, etc.) are mandated and finite -- every implementer is discoverable.

See: **[protocols/](protocols/README.md)** for country-by-country protocol maps and Company-Protocol Matrix.

---

## Deep Research Priority Order

All 29 competitors ordered for deeper investigation. AI upcomers first, then by strategic relevance.

### Priority 1 -- AI Upcomers (investigate first)

| # | Company | Tier | AI Signal | Why Prioritize |
|---|---|---|---|---|
| 1 | **MaxBill** | 1b | VERY STRONG | AI-native billing from inception. 80% faster time-to-market. Aggressively expanding Poland/Baltics/EV. If this model works, it threatens Eneve's billing layer. |
| 2 | **EG (Vitec/PowerEL)** | 1b | STRONG | Just acquired Bright Energy (Dec 2025) for AI. 240 specialists. Market leader DK/SE, expanding NO/FI. Nordic mirror of what Eneve does in NL. |
| 3 | **Robotron** | 1b | MOD-STRONG | AI Workstation + ePredict AI forecasting. Serves E.ON, ENGIE, Shell Energy. Full German MaKo platform. Direct SOPTIM/KISTERS competitor with AI edge. |
| 4 | **TietoEVRY** | 1b | STRONG | SmartGen AI Suite, AIOps, Siemens Gridscale X. ~24K employees. Enterprise AI capabilities applied to energy. |
| 5 | **Indra / Minsait** | 1b | STRONG | Leading IA4TES (national AI for energy transition). 90+ clients on 5 continents. Smart grid AI, DER prediction. |

### Priority 2 -- Moderate AI + High Strategic Relevance

| # | Company | Tier | AI Signal | Why Prioritize |
|---|---|---|---|---|
| 6 | **Engineering Group** | 1b | MOD-STRONG | EngGPT ("AI Made in Italy") + Neta platform with 40M+ users. Dominant Italian CIS. Massive data advantage. |
| 7 | **Asseco** | 1b | MODERATE | 65% of Polish energy companies. 13 acquisitions in H1 2025 targeting AI. If Poland opens, Asseco owns it. |
| 8 | **Ferranti** | 1b | LOW-MOD | MECOMS 365 in Belgian market where Eneve is expanding. Direct overlap in metering/CIS. Must understand for BE strategy. |

### Priority 3 -- Infrastructure Understanding (lower urgency)

| # | Company | Tier | AI Signal | Why Investigate |
|---|---|---|---|---|
| 9 | **Schleupen** | 3 | LOW-MOD | German ERP/billing on AWS with MaKo. adesso partnership. Understand German landscape. |
| 10 | **SEEBURGER** | 3 | LOW | 450+ participants, 50M+ msgs/month. Dominant German MaKo pipe. Integration layer context. |
| 11 | **Arvato Systems** | 3 | LOW | AEP MaKo Cloud, API transition 2025. Bertelsmann-backed. German infrastructure context. |

---

## Deeper Analysis Phase (Planned)

- Exact pricing models for all vendors
- Customer lists and win/loss data
- Feature-by-feature comparison matrix with scoring
- Market share estimates per country
- Eneve-specific differentiators vs each competitor
- Technology stack deep-dive
- Growth rates and financial trajectory
- SWOT analysis per competitor
- Threat assessment and strategic implications
