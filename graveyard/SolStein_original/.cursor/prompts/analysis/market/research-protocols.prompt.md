---
name: research-protocols
description: "Please map energy commodity protocols by country and identify which companies implement them"
category: analysis
tags: competition, protocols, energy-market, TSO, settlement, balancing, nominations, discovery
argument-hint: "Country or protocol name to focus on (e.g., Netherlands, or MaBiS, or 'all')"
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Research Energy Protocols - Protocol-to-Company Mapping

Please research and map the specific energy commodity protocols used across European markets, identify which software companies implement each protocol, and use this mapping to discover competitors we may have missed.

**Pattern**: Guided Discovery Pattern
**Effectiveness**: Protocols are the fingerprint of the energy back-office market -- if you implement EDSN, MaBiS, or AS4, you're a player. Following the protocols reveals the full competitive landscape.
**Use When**: After initial competitor identification, to validate completeness and discover missed players

---

## Purpose

Energy markets use highly specific, often national, communication protocols for TSO/DSO interaction, settlement, balancing, nominations, and metering. These protocols are:
- Mandated by national regulators or TSOs
- Implemented by a finite set of software vendors
- Documented in TSO specifications and industry publications
- The single best indicator of who competes in which market

By mapping **Protocol -> Country -> Implementing Companies**, we can:
1. Verify our existing competitor list covers all protocol implementers
2. Discover companies we missed (especially niche national players)
3. Understand which competitors have multi-market protocol coverage
4. Assess protocol convergence trends (ENTSO-E harmonization)

---

## Required Context

- **Focus Area**: Country name, protocol name, or "all" for comprehensive mapping
- **Existing Competitor List**: Reference `@tickets/COMPETITION/README.md` for current landscape
- **Eneve Protocols**: Eneve implements EDSN (NL), communicates with TenneT NL, uses EDI message formats

---

## Process

### Step 1: Read Current Landscape

Read `tickets/COMPETITION/README.md` and note which protocols each competitor already mentions. This is the baseline.

### Step 2: Map Protocol Categories

For the target country/countries, research and map protocols across these categories:

#### A. Market Communication & Messaging Protocols

| Protocol Area | Research Focus |
|---|---|
| TSO communication | How do market participants send schedules, nominations, and data to the TSO? |
| DSO communication | How do suppliers interact with distribution system operators? |
| Market message format | What EDI/XML/JSON formats are used for market messages? |
| Transport protocol | AS2, AS4, MADES, ECP, SMTP, SFTP, or proprietary? |
| Acknowledgment | APERAK, CONTRL, or custom confirmation messages? |

#### B. Balancing & Settlement Protocols

| Protocol Area | Research Focus |
|---|---|
| Balancing group management | National balancing group registration and data exchange format |
| Imbalance settlement | How are imbalance volumes calculated and communicated? |
| Allocation | How is energy allocated to balancing groups (ALOCAT equivalent)? |
| Settlement data format | What format is settlement data exchanged in? |
| Reconciliation | How is post-settlement reconciliation handled? |

#### C. Nomination & Scheduling Protocols

| Protocol Area | Research Focus |
|---|---|
| Day-ahead scheduling | Format for submitting day-ahead schedules to TSO |
| Intraday scheduling | Format for intraday schedule updates |
| Cross-border nominations | ENTSO-E scheduling formats, ESS (Electronic Scheduling System) |
| Gas nominations | EDIG@S formats for gas nominations |
| Capacity booking | Formats for capacity reservation at borders/hubs |

#### D. Metering & Data Exchange Protocols

| Protocol Area | Research Focus |
|---|---|
| Smart meter data | National smart meter data format (DSMR, COSEM/DLMS, etc.) |
| Meter data exchange | How is meter data exchanged between parties? |
| Aggregation protocols | How is metered data aggregated for settlement? |
| Data hub protocols | National data hub communication (if applicable) |

#### E. Market Registration & Master Data

| Protocol Area | Research Focus |
|---|---|
| Connection point registration | EAN/GSRN/MeteringPoint identification |
| Supplier switching | Protocol for customer switching between suppliers |
| Market participant registration | How are market parties registered? |
| Grid area data | How is grid topology data exchanged? |

### Step 3: Identify Protocol Names per Country

For each target country, document the specific protocol names, versions, and governing bodies:

**Output format per country:**

```markdown
### [Country Name]

**Governing Body**: [TSO name, regulator, market operator]
**Protocol Framework**: [National framework name if any]

| Category | Protocol Name | Version | Format | Transport | Governing Body |
|---|---|---|---|---|---|
| TSO Communication | [name] | [version] | [XML/EDI/JSON] | [AS4/ECP/...] | [TSO/regulator] |
| Balancing | [name] | [version] | [format] | [transport] | [governing body] |
| Settlement | [name] | [version] | [format] | [transport] | [governing body] |
| Nominations | [name] | [version] | [format] | [transport] | [governing body] |
| Metering | [name] | [version] | [format] | [transport] | [governing body] |
| Switching | [name] | [version] | [format] | [transport] | [governing body] |
```

### Step 4: Map Software Companies to Protocols

For each protocol identified, research which software companies implement it:

**Search strategies:**
- TSO website -> "certified software" or "qualified service providers" lists
- Protocol specification documents -> "implementing parties" or "vendor list"
- Industry conference (E-world, Enlit) exhibitor lists filtered by protocol keywords
- Job postings mentioning specific protocol names
- GitHub / open source projects implementing protocols
- Trade press / case studies mentioning protocol implementations

**Output format:**

```markdown
### Protocol: [Protocol Name] ([Country])

| Company | Product | Implementation Level | Source |
|---|---|---|---|
| [company] | [product] | Full / Partial / Planned | [source URL or reference] |
```

### Step 5: Cross-Reference with Existing Competitor List

Compare the protocol-discovered companies against `tickets/COMPETITION/README.md`:
- Mark companies already tracked with a checkmark
- Flag new companies not yet in the competitor list
- Note multi-protocol companies (implement protocols in multiple countries)

### Step 6: Assess Protocol Convergence

Document trends in protocol harmonization:
- ENTSO-E standardization efforts (which protocols are converging?)
- EU regulations driving protocol changes (Clean Energy Package, Electricity Balancing Guideline)
- National protocols being replaced by European standards
- Impact on competitive landscape (does convergence lower barriers for cross-border entry?)

### Step 7: Write Protocol Files

Write the protocol mapping output to **separate files**:

- **Cross-cutting protocol map**: Write to `tickets/COMPETITION/protocol-map.md` (the overall country-protocol-company matrix)
- **Per-competitor protocol data**: For each competitor with protocol findings, write to `tickets/COMPETITION/[company-slug]/protocol-map.md` within their company folder
- **Create the company folder** if it doesn't exist yet
- For newly discovered companies, create a new company folder with an identification file and protocol map
- Do NOT append protocol data to the main identification files -- keep research outputs in their own dedicated files

---

## Key Protocols by Country (Starting Reference)

This is a starting point -- research should verify and expand this list.

### Netherlands

| Category | Known Protocols | Notes |
|---|---|---|
| Market Communication | EDSN (Energy Data Services Netherlands) | Central market facilitator |
| TSO Communication | TenneT NL protocols, ECP/MADES | TenneT as TSO |
| Balancing | ETPA, allocation formats | Balancing responsible parties |
| Settlement | Allocation reconciliation formats | Via EDSN |
| Metering | DSMR (Dutch Smart Meter Requirements) | P1/P4 data formats |
| Switching | EDSN switching protocol | Standardized supplier switching |
| Transport | AS4, MSCONS, UTILMD | EDI message types |

### Germany

| Category | Known Protocols | Notes |
|---|---|---|
| Market Communication | MaBiS (Marktregeln Bilanzkreisabrechnung Strom) | Market rules for BG settlement |
| TSO Communication | ENTSO-E formats, 4 TSOs (Amprion, 50Hertz, TenneT DE, TransnetBW) | |
| Balancing | ALOCAT, MaBiS | Allocation and balancing |
| Settlement | MaBiS format files | Bilanzkreis settlement |
| Metering | MSCONS, SLP profiles | Meter data exchange |
| Switching | GPKE (Geschaeftsprozesse Kundenbelieferung Energie) | Supplier switching |
| Acknowledgment | APERAK | Message confirmations |
| Transport | AS4, Email/AS2 (transitioning) | Moving to AS4 |
| Gas | EDIG@S, GeLi Gas (Geschaeftsprozesse Lieferantenwechsel Gas) | Gas market processes |

### Nordics (Norway, Sweden, Finland, Denmark)

| Category | Known Protocols | Notes |
|---|---|---|
| Market Communication | Nordic market model, Datahub protocols | |
| TSO Communication | Statnett (NO), SvK (SE), Fingrid (FI), Energinet (DK) | |
| Data Hub | Elhub (NO), national data hubs | Centralized metering data |
| Balancing | Nordic balancing model | Harmonizing under EU regulations |

### UK

| Category | Known Protocols | Notes |
|---|---|---|
| Settlement | BSC (Balancing and Settlement Code) / Elexon | |
| Balancing | National Grid ESO protocols | |
| Metering | MHHS (Market-wide Half Hourly Settlement) | New from 2025 |
| Switching | CSS (Central Switching Service) | |

### Belgium

| Category | Known Protocols | Notes |
|---|---|---|
| TSO Communication | Elia protocols | |
| Market Communication | Atrias (metering data exchange) | |
| Balancing | Belgian balancing mechanism | |

---

## Output Format

The final deliverable should contain:

### 1. Protocol Map (per country)

Complete table of protocols per country with versions, formats, and governing bodies.

### 2. Company-Protocol Matrix

| Company | NL (EDSN) | DE (MaBiS) | Nordics | UK (BSC) | BE (Elia) | Other |
|---|---|---|---|---|---|---|
| Eneve | Y | - | - | - | Expanding | - |
| SOPTIM | - | Y | - | - | - | - |
| Engrate | Y | Y | Y (SE) | - | - | - |
| [etc.] | | | | | | |

### 3. Newly Discovered Companies

List of companies found through protocol research that are NOT yet in `tickets/COMPETITION/`:

```markdown
| Company | Product | Country | Protocols Implemented | Relevance to Eneve |
|---|---|---|---|---|
| [company] | [product] | [country] | [protocol list] | [High/Medium/Low] |
```

### 4. Protocol Convergence Assessment

Narrative on how protocol harmonization trends affect competitive dynamics and Eneve's market position.

---

## Quality Criteria

### Output Completeness
- [ ] At least 5 European countries mapped (NL, DE, UK, Nordics, BE/FR minimum)
- [ ] All 5 protocol categories covered per country (communication, balancing, settlement, nominations, metering)
- [ ] Each protocol has governing body and format type identified
- [ ] Company-protocol matrix covers all existing competitors
- [ ] Newly discovered companies flagged with relevance assessment
- [ ] Protocol convergence trends documented

### Output Files
- [ ] Cross-cutting protocol map saved to `tickets/COMPETITION/protocol-map.md` (standalone file)
- [ ] Per-competitor protocol data saved to `tickets/COMPETITION/[company-slug]/protocol-map.md` (not appended to main file)

### Source Quality
- [ ] Sources cited for each protocol identification
- [ ] TSO/regulator primary sources used where available (not only secondary)
- [ ] Cross-referenced against tickets/COMPETITION/README.md

### Accuracy
- [ ] Protocol names verified against official TSO/regulator documentation
- [ ] Companies listed are software vendors (not just market participants)
- [ ] "Newly discovered" companies confirmed absent from existing competitor list

---

## Usage

### Full European scan

```
@research-protocols all
```

### Single country focus

```
@research-protocols Netherlands
```

```
@research-protocols Germany
```

### Single protocol focus

```
@research-protocols EDSN
```

```
@research-protocols MaBiS
```

### Discovery mode (find missed competitors)

```
@research-protocols all -- focus on finding certified/qualified vendor lists from TSOs and regulators to discover companies not yet in our competitor list
```

---

## Search Query Templates

**TSO certified vendor lists:**
- `"[TSO name]" certified software vendors qualified partners`
- `"[TSO name]" market participant portal software`
- `site:[tso-domain] approved systems OR qualified vendors`

**Protocol implementers:**
- `"[protocol name]" implementation software vendor energy`
- `"[protocol name]" certified system energy market`
- `"[protocol name]" "[protocol name 2]" software provider`

**National regulator lists:**
- `"[regulator]" registered software energy market communication`
- `"[country] energy market" qualified software systems list`

**Industry events (E-world, Enlit):**
- `"E-world 2026" exhibitor "[protocol name]"`
- `"Enlit" "[protocol name]" software vendor`

**Job postings (reveal stack):**
- `"[protocol name]" developer OR engineer job energy`
- `"[protocol name]" "[protocol name 2]" software development`

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Read current state**: Load README.md and note existing protocol mentions per competitor
2. **Determine scope**: All countries, specific country, or specific protocol
3. **Research systematically**: For each country in scope, research all 5 protocol categories
4. **Find vendor lists**: Prioritize TSO/regulator certified vendor lists as these are the most complete sources
5. **Cross-reference**: Compare discovered companies against existing competitor list
6. **Flag gaps**: Any company found implementing energy protocols that isn't in our list is a potential missed competitor
7. **Assess convergence**: Note where protocols are harmonizing (opportunities/threats for Eneve)
8. **Document everything**: Protocol names, versions, formats, governing bodies, implementing companies, with sources. Write the cross-cutting map to `tickets/COMPETITION/protocol-map.md` and per-company data to `tickets/COMPETITION/[company-slug]/protocol-map.md`

**Self-correction checkpoints** (validate before finalizing):
- Did I distinguish between protocol *names* and *categories*? (e.g., "MaBiS" is a specific protocol, "balancing" is a category)
- Did I verify protocol names against TSO/regulator source documents, or am I relying on secondary sources?
- Are the companies I listed actual software *vendors*, or are they market participants *using* protocols?
- Did I miss any protocol category for any country in scope?
- Are the "newly discovered" companies genuinely absent from the competitor list, or did I overlook an alias/subsidiary?

**Edge case handling**:
- **TSO website in local language only**: Use translated search queries and note language barrier in findings
- **Protocol being deprecated/replaced**: Document both the current protocol and its successor with transition timeline
- **Protocol with no public vendor list**: Note as a gap and suggest alternative discovery methods (job postings, conference exhibitors)
- **Multi-country protocol variants**: Distinguish national implementations of the same European standard (e.g., AS4 implementations differ by country)

The key insight: **energy protocols are mandated, specific, and finite**. Every company that implements them is discoverable. This is the most reliable method for ensuring our competitor list is complete.

---

## Examples (Few-Shot)

### Example 1: Single Country Focus (Netherlands)

**Input**: `@research-protocols Netherlands`

**Expected Output** (abbreviated):

```markdown
## Netherlands - Protocol Map

**Governing Body**: TenneT (TSO), ACM (Regulator), EDSN (Market Facilitator)
**Protocol Framework**: EDSN Sector Model

| Category | Protocol Name | Version | Format | Transport | Governing Body |
|---|---|---|---|---|---|
| TSO Communication | TenneT Market Protocol | 2024 | XML | ECP/MADES | TenneT |
| Market Communication | EDSN Sector Messages | v5.x | XML/EDIFACT | MSH (Message Service Handler) | EDSN |
| Balancing | ETPA / ALOCAT NL | Current | EDIFACT | EDSN MSH | TenneT/EDSN |
| Settlement | Allocation Reconciliation | Current | EDIFACT | EDSN MSH | EDSN |
| Metering | DSMR (P1/P4) | 5.0 | Telegram/XML | EDSN MSH | Netbeheer NL |
| Switching | EDSN Switchprotocol | Current | XML | EDSN MSH | EDSN |

### Protocol: EDSN Sector Messages (Netherlands)

| Company | Product | Implementation Level | Source |
|---|---|---|---|
| Eneve | eBase | Full | Internal knowledge |
| Found.ation (Essent/RWE) | Found.ation | Full | EDSN certified list |
| Nvisio / Ferranti | Market Communication Suite | Full | Company website |
| [etc.] | | | |

### Cross-Reference
- Eneve: Already tracked ✓
- Found.ation: Already tracked ✓
- [New Company X]: **NEW** - Not in competitor list, relevance: High
```

### Example 2: Single Protocol Focus (MaBiS)

**Input**: `@research-protocols MaBiS`

**Expected Output** (abbreviated):

```markdown
## Protocol: MaBiS (Marktregeln Bilanzkreisabrechnung Strom)

**Country**: Germany
**Governing Body**: BNetzA (Bundesnetzagentur), BDEW
**Purpose**: Standardized rules for balancing group settlement in electricity
**Current Version**: MaBiS 2.0 (effective 2024)
**Format**: EDIFACT (MSCONS, UTILMD)
**Transport**: AS4 (transitioning from AS2/email)

### Implementing Software Companies

| Company | Product | Implementation Level | Source |
|---|---|---|---|
| SOPTIM | SOPTIM BPM | Full | Company website, E-world exhibitor |
| Schleupen | Schleupen.CS | Full | BDEW certified list |
| [etc.] | | | |

### Cross-Reference with Competitor List
- SOPTIM: Already tracked ✓ (tickets/COMPETITION/soptim/)
- Schleupen: Already tracked ✓
- [New Company Y]: **NEW** - Not in competitor list, relevance: Medium
```

---

## Troubleshooting

**Issue**: TSO website returns results only in local language
**Cause**: Many national TSOs (especially smaller markets) publish documentation only in the national language
**Solution**: Use translated search queries (e.g., German: "zertifizierte Softwareanbieter", Dutch: "gecertificeerde softwareleveranciers"). Note the language barrier in findings and flag for manual follow-up.

**Issue**: Cannot find a public certified vendor list for a specific TSO
**Cause**: Not all TSOs publish vendor lists; some only maintain internal registries
**Solution**: Pivot to alternative discovery methods: job postings mentioning the protocol, conference exhibitor lists (E-world, Enlit), GitHub repositories, and trade press case studies.

**Issue**: Found company appears to be a market participant, not a software vendor
**Cause**: Market participants (energy traders, suppliers) use protocols but don't sell software
**Solution**: Verify by checking the company website for "software", "platform", "SaaS", or "product" keywords. Exclude pure market participants; include companies that both participate AND sell software to others.

**Issue**: Protocol name appears in multiple countries with different implementations
**Cause**: European standards (e.g., AS4, ENTSO-E ESS) have national variants
**Solution**: Document each national implementation separately, noting which base standard it derives from and what country-specific extensions exist.

---

## Pattern Used

This prompt follows the **Systematic Mapping Research** pattern: `.cursor/templars/analysis/market/systematic-mapping-research-templar.md`

## Reference Example

See exemplar: `.cursor/exemplars/analysis/market/research-protocols-exemplar.md`

## Related Prompts

- `analysis/market/research-competitor.prompt.md` - Deep-dive analysis of individual competitors
- `analysis/market/research-company-history.prompt.md` - Historical analysis of discovered companies
- `analysis/market/research-financial-growth.prompt.md` - Financial analysis of competitor growth
- `analysis/market/generate-financial-dashboard.prompt.md` - Dashboard generation for competitor financials
- `prompt/create-new-prompt.prompt.md` - Template used to create this prompt

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

---

**Created**: 2026-02-15
**Improved**: 2026-02-15 (improve-prompt + enhance-prompt: added Few-Shot examples, troubleshooting, self-correction, edge cases, expanded references, fixed encoding)
**Context**: tickets/COMPETITION/ competitive landscape validation via protocol mapping
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
