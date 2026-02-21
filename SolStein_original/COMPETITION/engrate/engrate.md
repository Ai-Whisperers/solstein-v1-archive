# Engrate

## Identification

- **Company**: Engrate AB (Swedish startup)
- **Product(s)**: Engrate API Platform (Schedule Management, Settlement Management, Power Tariffs)
- **HQ Country**: Sweden
- **Countries of Operation**: Germany, Netherlands, Sweden
- **Founded**: January 2024 (by Anna Engman and Richard Eklund)
- **Employees**: <20 (estimated)
- **Revenue / Market Cap**: Pre-revenue / early stage. Seed: EUR 2.5M (June 2025), pre-seed: EUR 500K+
- **Ownership**: Private, VC-backed (Maniv lead, Eviny Ventures, Course Corrected, NP Hard Ventures)
- **Website**: engrate.io

## Competitive Profile

- **Tier**: 1 - Direct Competitor (emerging)
- **Specialization**: Energy API platform, settlement management, schedule management, TSO integration
- **Commodities**: Power
- **Platform**: Cloud-native, REST API-first architecture, AI-native integrations
- **Cloud / On-Premise**: Cloud API only

## Product Offering

Engrate provides a harmonized API platform for energy data and market operations:

- **Schedule Management API**: Submitting and managing schedules to TSOs (Amprion, 50Hertz, TenneT DE, TransnetBW, TenneT NL)
- **Settlement Management API**: Validation, matching, reconciliation, and audit across multiple TSOs
- **Power Tariffs API**: Swedish DSO tariff data (currently Sweden only)
- **Unified REST APIs**: Standardized access across markets, reducing integration complexity
- **Bank-Level Security**: Enterprise-grade security for API access
- **AI-Native**: Built-in AI integrations for automated market logic

Key differentiator: unified API abstraction over multiple TSOs and markets, reducing the integration burden for energy companies operating across borders.

## Overlap with Eneve

| Eneve Capability | Overlap | Notes |
|---|---|---|
| Settlement | High | Core product: Settlement Management API |
| Nominations/Scheduling | High | Core product: Schedule Management API |
| TSO Communication | High | Unified API across multiple TSOs |
| Time Series Management | Medium | Within settlement/schedule context |
| Balancing | Medium | Schedule management adjacent |
| Smart Meter Data | Low | Not a focus area |
| NL Market | High | Directly serves TenneT Netherlands |

## AI Adoption Signal: STRONG

- **AI-native from founding**: Built as "AI-native energy API platform" from day one
- **MCP Server**: Provides an MCP (Model Context Protocol) Server for AI-assisted rapid prototyping
- **AI integrations**: Built-in AI capabilities for automated market logic
- AI is not an add-on but a core architectural principle

## Acceleration Signal: VERY STRONG

- Founded January 2024, raised EUR 500K+ pre-seed, then EUR 2.5M seed by June 2025
- Went from zero to working product with NL + DE + SE market coverage in under 18 months
- International expansion plans across Northern Europe with new capital
- Grid flexibility solutions in development for renewable energy transition

## Notes

- Youngest and smallest competitor but operates directly in the NL market (TenneT NL)
- API-first approach is a disruptive model compared to traditional monolithic platforms
- EUR 2.5M seed round (June 2025) led by Maniv (global VC) signals strong investor confidence
- Cross-market standardization (DE + NL) is unique value proposition
- Could evolve into a middleware layer that sits between TSOs and platforms like eBase
- Watch for: expansion to more markets, additional API products, partnership announcements
- Potential acquisition target for larger players seeking API/cloud capabilities

## Deep Analysis

**Research Date**: 2026-02-15
**Confidence Level**: Medium (private startup with limited public financial data; product and strategy data is strong from official sources)

### Company Fundamentals

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Legal Entity | Engrate AB | CBInsights, StartupReporter | Confirmed |
| HQ Address | Stockholm (Djursholm), Sweden | VCBacked, CBInsights | Confirmed |
| Founded | January 2024 | EU-Startups, SiliconCanals, StartupReporter | Confirmed |
| CEO | Anna Engman (co-founder) | EU-Startups, SiliconCanals, Nordic Angels | Confirmed |
| CTO | Richard Eklund (co-founder) | EU-Startups, SiliconCanals | Confirmed |
| Other Founders/Associates | Patrik Fagerfjall, Christopher Engman (Norrsken cohort listing) | LinkedIn, Norrsken Accelerator | Estimated |
| Ownership | Private, VC-backed | Crunchbase-style sources, press | Confirmed |
| Employees (current) | 10-20 | StartupRise.co.uk, general estimates | Estimated |
| Employees (1yr ago) | <10 (founded Jan 2024, pre-seed stage) | Inferred from founding timeline | Estimated |
| Employees (2yr ago) | 0 (company did not exist) | N/A | Confirmed |
| Revenue (current) | Pre-revenue / early revenue (free tier + EUR 499/mo DSO product) | Website pricing, funding stage | Estimated |
| Revenue (1yr ago) | Pre-revenue | Funding stage analysis | Estimated |
| Revenue Growth | N/A (too early stage) | N/A | Unknown |
| Market Cap / Valuation | Undisclosed; EUR 2.5M seed implies ~EUR 10-15M post-money (typical seed multiples) | Estimated from seed round size | Estimated |

**Key Investors:**

| Investor | Type | Round | Notes |
|---|---|---|---|
| Maniv | Global VC (transport/energy) | Seed lead (EUR 2.5M, June 2025) | Tel Aviv-based, significant energy portfolio |
| Eviny Ventures | Corporate VC (Norwegian renewable energy provider Eviny) | Seed co-investor | Strategic energy investor |
| Course Corrected | Swedish VC | Seed co-investor | Swedish tech focus |
| NP-Hard Ventures | Dutch VC | Pre-seed (EUR 500K+) | Netherlands-based, relevant for NL market entry |
| Norrsken | Accelerator | Pre-seed/accelerator (2024 cohort) | Top 20 from 3,000+ applicants |
| Angel investors | Pia Irell, Maex Ament, Philip Stehlik | Pre-seed | Individual angels |

### Market Position

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Countries Active | Sweden (primary), Germany, Netherlands | engrate.io product pages, press releases | Confirmed |
| Customer Count | Small (named: Flower; likely single-digit paying customers) | Nordic Angels, Golden Wiki | Estimated |
| Notable Customers | Flower (Swedish flexibility operator / renewable energy aggregator) | Nordic Angels, StartupReporter | Confirmed |
| Market Share | Negligible (pre-revenue startup) | Inferred from size/stage | Estimated |
| Rankings / Awards | Norrsken "Energy Startups to Watch" (Future in Focus report, 2024/2025) | LinkedIn, Norrsken | Confirmed |
| Conference Presence | Anna Engman demo of AI-native energy connectivity (LinkedIn post, likely E-world or similar) | LinkedIn | Estimated |
| Competitive Wins | No documented wins vs Eneve or similar incumbents | N/A | Unknown |

**Target Users (from product pages):**
- Energy traders
- Aggregators / flexibility service providers
- Balance responsible parties
- Energy management platform developers
- Virtual Power Plant (VPP) operators
- DSOs (via DSO Connect partnership portal)

### Product & Technology

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Product Portfolio | 4 live products + 4 "Coming Soon" (see below) | engrate.io/data-api-products | Confirmed |
| Tech Stack | Cloud-native, REST/JSON APIs, Mintlify docs, AI-native architecture | engrate.io, docs.engrate.io | Confirmed |
| Deployment Model | Cloud API only (SaaS) | engrate.io | Confirmed |
| API Strategy | RESTful, JSON, versioned, developer-first, free tier available | docs.engrate.io, engrate.io | Confirmed |
| Exchange/TSO Integrations | Amprion, 50Hertz, TenneT DE, TransnetBW (Germany); TenneT NL (Netherlands) | engrate.io/schedule-management | Confirmed |
| DSO Integrations | 170+ Swedish DSOs (2,400+ tariffs), RI-SE API adaptor | engrate.io/power-tariffs, DSO Connect page | Confirmed |
| Release Cadence | Continuous (startup pace, "Coming Soon" pipeline visible) | engrate.io product library | Estimated |
| Documentation | Mintlify-hosted developer docs (docs.engrate.io) | docs.engrate.io | Confirmed |
| Security | Bank-level authentication, authorization, audit trails | engrate.io | Confirmed |

**Live Products:**

| Product | Markets | Description |
|---|---|---|
| Power Tariffs API | Sweden (170+ DSOs) | Harmonized tariff data, queryable by coordinates/address/grid area |
| Settlement Management API | Germany, Netherlands | Validation, matching, reconciliation, audit across TSOs |
| Schedule Management API | Germany, Netherlands | Unified submission to 5 TSOs (4 DE + TenneT NL) |
| Electricity Area Map | Sweden | Precision mapping of metering grid area coordinates |

**Coming Soon Products:**

| Product | Markets | Description |
|---|---|---|
| Grid Transfer Fees | Sweden (expanding) | Grid transport fee calculations |
| Energy Tax | Sweden | Energy tax per metering grid area |
| Feed-in Tariffs | Sweden (expanding) | Feed-in tariff calculations |
| Reactive Power Tariffs | Sweden (expanding) | Reactive power optimization |

### AI & Innovation

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| AI Features in Production | MCP Server for natural-language energy data queries; AI-native API design; AI-generated DSO tariff summaries | engrate.io, DSO Connect page | Confirmed |
| AI Roadmap | "AI-native by design" core principle; all data products built for AI consumption | engrate.io/energy-api-platform | Confirmed |
| AI Hiring Signals | Not observable (too small for public job postings) | N/A | Unknown |
| AI Partnerships | No formal AI partnerships announced; built on MCP open standard | N/A | Unknown |
| Published Research | No academic papers or patents found | Google Scholar, patent search | Confirmed (none found) |
| AI Acquisitions | None | N/A | Confirmed (none) |

**AI Architecture Detail:**
- **MCP Server**: Engrate provides an MCP (Model Context Protocol) server allowing any AI assistant (Claude, ChatGPT, etc.) to query energy data via natural language prompts without developer involvement
- **Deterministic data models**: All data is machine-readable by design, not retrofitted for AI
- **AI-native DSO summaries**: Complementary AI explanations of all DSO tariffs provided to partners
- **"No additional data preparation"**: API outputs are structured for direct AI consumption

This is a fundamentally different approach from incumbents adding AI features to existing platforms. Engrate was *born* AI-native, meaning AI compatibility is a design constraint, not an afterthought.

### Growth & Trajectory

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Revenue Growth (YoY) | N/A (pre-revenue / early revenue) | N/A | Unknown |
| Employee Growth (YoY) | From 0 (Jan 2024) to 10-20 (Feb 2026) in ~2 years | StartupRise, inferred | Estimated |
| Geographic Expansion | SE -> DE + NL in first 18 months | Product pages, press | Confirmed |
| Product Launches (2yr) | 4 live products + 4 announced in pipeline within 2 years of founding | engrate.io | Confirmed |
| Acquisitions (3yr) | None | N/A | Confirmed (none) |
| Funding Rounds (3yr) | Pre-seed EUR 500K+ (2024), Seed EUR 2.5M (June 2025) = EUR 3M+ total | EU-Startups, SiliconCanals | Confirmed |
| Strategic Pivots | None (consistent API-first energy platform vision since founding) | Press coverage | Confirmed |
| Accelerator | Norrsken Accelerator 2024 (top 20 from 3,000+ applicants) | Norrsken, StartupReporter | Confirmed |

**Growth Timeline:**
- **Jan 2024**: Founded by Anna Engman + Richard Eklund
- **2024 H1**: Joined Norrsken Accelerator cohort
- **2024**: Raised EUR 500K+ pre-seed from NP-Hard Ventures + angels
- **2024-2025**: Built platform, launched Power Tariffs + Electricity Area Map (Sweden)
- **2025 H1**: Launched Schedule Management + Settlement Management (Germany + Netherlands)
- **June 2025**: Raised EUR 2.5M seed led by Maniv
- **2025-2026**: 4 additional products in pipeline ("Coming Soon")

**Velocity Assessment**: Extremely fast for energy sector. Going from zero to multi-market, multi-product platform with TSO integrations in ~18 months is remarkable. Traditional energy software companies take years to achieve single-market TSO connectivity.

### Commodities & Specialization

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Commodities | Power (electricity only) | Product pages | Confirmed |
| Market Segments | Wholesale scheduling, settlement, flexibility/VPP, DSO tariff optimization, energy management platforms | engrate.io use cases | Confirmed |
| Regulatory Compliance | TSO communication standards (DE: Amprion/50Hertz/TenneT/TransnetBW; NL: TenneT), EIC code validation | Schedule Management docs | Confirmed |
| Protocol Support | REST/JSON unified API abstracting TSO-specific protocols; RI-SE API adaptor for Swedish DSOs | engrate.io, DSO Connect | Confirmed |
| EDSN Support | Not explicitly mentioned | N/A | Unknown |
| ENTSO-E Support | Implicit via TSO integrations (schedule submission follows ENTSO-E frameworks) | Inferred | Estimated |

**Notable Absence**: No gas, carbon, or other commodity support. Pure electricity focus.

### Pricing & Business Model

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Pricing Model | Freemium API (free tier to start) + paid tiers | engrate.io, Power Tariffs page | Confirmed |
| Est. Price Range | Free tier available; DSO cross-tariff access at EUR 499/month; commercial API pricing undisclosed | DSO Connect page | Partial |
| Implementation Timeline | "Days, not months" - basic integration < 1 day, advanced < 1 week | engrate.io/energy-api-platform | Confirmed |
| Services vs Product Revenue | 100% product (API subscriptions); no services revenue model visible | Website analysis | Estimated |

**Business Model Analysis:**
- **API-as-a-product**: Pure SaaS/API subscription model. No implementation services, no consulting, no on-premise deployments.
- **Developer self-service**: Sign up, get API keys, start building. No sales cycle for initial adoption.
- **Land and expand**: Free tier drives adoption; value increases as usage scales.
- **Platform network effects**: More DSOs on DSO Connect = more valuable tariff data = more API customers.
- **Low friction**: No credit card required for free tier; "Book a demo" link for commercial discussion.

This is a fundamentally different commercial model from traditional energy software (long sales cycles, large implementation projects, per-seat licensing).

### Threat Assessment vs Eneve

**Direct Overlap Areas**:
- **Settlement Management**: Engrate's Settlement Management API directly competes with eBase's settlement/allocation capabilities in the NL market (TenneT NL). Both handle validation, matching, reconciliation.
- **Schedule Management / Nominations**: Engrate's Schedule Management API overlaps with eBase's nomination/scheduling functions. Both submit schedules to TenneT NL.
- **TSO Communication**: Both platforms communicate with TenneT Netherlands. Engrate also covers all 4 German TSOs, giving it broader European coverage.
- **Time Series (partial)**: Settlement and scheduling inherently involve time series data, though Engrate doesn't offer standalone time series management.

**Where Competitor is Stronger**:
- **API-first architecture**: Modern REST/JSON developer experience vs eBase's MSSQL/on-premise model. Dramatically lower integration barrier for new customers.
- **Multi-market from day one**: Germany + Netherlands + Sweden unified in single API. eBase is primarily NL-focused.
- **AI-native design**: MCP server, machine-readable data, AI-first architecture. Not a bolt-on but a founding principle.
- **Speed to market**: Customers can integrate in days vs months-long eBase implementation projects.
- **Developer experience**: Mintlify docs, free tier, self-service signup. Modern SaaS expectations vs traditional enterprise software sales.
- **Cost structure**: API subscription likely far cheaper than full eBase platform licensing + implementation.
- **Cloud-native**: No infrastructure burden on customers. No upgrades, no maintenance.

**Where Eneve is Stronger**:
- **Deep NL market expertise**: 25+ years of Dutch energy market knowledge, established relationships, proven at scale.
- **Comprehensive platform**: eBase covers the full energy back-office (smart meter data, gas, balancing, market operations, EAN codes) - Engrate covers only a fraction.
- **Gas capabilities**: Engrate is electricity-only; eBase handles gas balancing and operations.
- **EDSN protocol expertise**: Deep integration with Dutch market-specific protocols that Engrate hasn't demonstrated.
- **Smart meter data management**: Core eBase capability with no Engrate equivalent.
- **Production-proven at scale**: eBase handles real production volumes for major Dutch energy companies. Engrate is unproven at scale.
- **Existing customer relationships**: Switching costs are high for established eBase customers.
- **Regulatory compliance depth**: Years of Dutch regulatory knowledge embedded in eBase.

**NL Market Entry Likelihood**: **Already Present** - Engrate already serves the NL market through TenneT NL integration for schedule and settlement management. This is not a future threat - it's a current reality. Their Dutch VC (NP-Hard Ventures) pre-seed funding further confirms NL market intent.

**Capability Expansion Likelihood**: **High** - The "Coming Soon" product pipeline (Grid Transfer Fees, Energy Tax, Feed-in Tariffs, Reactive Power) shows active expansion. The API platform model makes adding new data products relatively low-effort compared to monolithic platform extensions.

**Strategic Implications**:
Engrate represents a qualitatively different competitive threat than traditional incumbents. Rather than competing feature-for-feature with eBase's comprehensive platform, Engrate is attacking from below with an API-first "unbundling" strategy. Energy companies building new applications or modernizing integration layers may choose Engrate's APIs for specific functions (scheduling, settlement) while retaining eBase for core operations. The risk is that over time, as Engrate's product library grows, it could replace enough eBase functionality to make the full platform less essential. The AI-native positioning also appeals to the next generation of energy developers who expect modern API experiences. Eneve should monitor: (1) Engrate customer wins in NL, (2) expansion into EDSN/smart meter territory, (3) gas market entry, and (4) any partnerships with larger platforms that could accelerate Engrate's reach.

## Corporate History

See [corporate-history.md](corporate-history.md) for the full corporate genealogy including ownership structure, origin story, investment rounds, M&A timeline, Mermaid diagrams, and strategic implications for Eneve.
