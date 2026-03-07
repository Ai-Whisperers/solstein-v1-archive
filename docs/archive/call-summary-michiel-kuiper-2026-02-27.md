# Call Summary: John van der Pol & Michiel Kuiper

**Date:** February 27, 2026, 09:37  
**Duration:** ~1h 36m  
**Participants:** John van der Pol, Michiel Kuiper  
**Type:** Brainstorm / Strategic Alignment / Long Play Explanation  
**Source:** Auto-transcribed (Dutch/English mixed; reconstructed from context)

---

## Context

This was a wide-ranging strategic conversation covering Solstein's positioning, the Energy 21 transformation opportunity, the private equity landscape, and the long-term value creation play. John explained the technical depth of what's being built, while Michiel brought the PE/market perspective.

---

## Key Topics Discussed

### 1. The Monolith Problem & AI Opportunity

- Energy 21's core platform is a monolith (C++ legacy being migrated to C#) that creates a significant drag on velocity
- SaaS as a standalone model is losing momentum; the real opportunity lies in AI-driven production processes
- The monolith is both the problem and the opportunity: once modernized with AI-native tooling, it becomes a competitive advantage that legacy competitors cannot match
- The gap between companies that adopt AI in their production process vs. those that don't is widening exponentially

### 2. Private Equity Landscape

- PE firms are sitting on portfolio companies that need AI readiness but don't know how to get there
- The typical PE playbook (buy, repackage, sell) is broken; AI has made due diligence smarter and exposed the "perfume on coal" trick
- Vortex is the anchor PE firm; Blythe is the prime investor in Energy 21
- PE firms need both a **technology driver** (modernizing the stack) and a **platform/market driver** (new market entry, cloud, SaaS)
- Current PE landscape: funds are stuck because they don't understand the transformation timeline -- they think it takes years, when it can take weeks with the right methodology

### 3. Solstein Positioning & Go-to-Market

- Solstein should be positioned as an AI-native intelligence platform for PE capital allocation
- Market focus: energy sector software -- compliance & control, forecasting, portfolio management, trading platforms (B2B)
- The machine (Solstein) maps the market, identifies undervalued targets, and tracks transformation progress
- Hit ratio and deal flow quality are key selling points to PE
- Michiel discussed outreach to specific markets: Dutch, Spanish, UK (London team potential)
- Brand positioning needs to be premium and authoritative -- not a dashboard, but capital infrastructure

### 4. Energy Market Dynamics

- Key segments: balancing, protocols, trading, supply, compliance & control
- Data compliance and message format standardization are significant overhead for energy market players
- New traders entering the market need compliance-ready platforms quickly
- Intraday and day-ahead trading, Nord Pool, EDPA -- these are concrete domains where the platform operates
- Multi-commodity support and cross-market optimization are differentiators

### 5. The Long Play (Explained by John)

- The play is not consulting fees or SaaS subscriptions alone -- it's **equity in the companies you transform**
- Solstein identifies targets, AI-Whishperers transforms them from within, equity realizes on PE exit
- The production process transformation is the unlock: turn a team with legacy tools into a team with AI-native velocity
- Current state at Energy 21 serves as the living proof case: everything being built now (CICD, quality automation, standardization) is the methodology that scales to other portfolio companies
- The "bicycle vs. car" metaphor: companies without AI tooling are riding bicycles while the competition is driving cars; the gap only widens

### 6. Technical Transformation (What John Is Building)

John walked Michiel through the concrete capabilities being developed:

| Capability | Description |
|---|---|
| **Ticket Automation** | Automatic ticket lifecycle: duplicate detection, assignment, status tracking, release validation |
| **Feature Development** | All features described in Jira, automation of planning and prioritization |
| **CICD Pipeline** | Automated build, test, deploy for the energy domain; standardized release management |
| **Refactoring with AI** | AI-assisted code refactoring; "no info, no warning, no suggestions" -- zero-tolerance quality |
| **Documentation Export** | Automated documentation generation and export to Confluence |
| **Release Management** | Currently partially manual, moving to fully automated; Helm chart improvements |
| **Standardization** | Standard libraries for common operations (e.g., grid point access layer); reducing repetitive coding |
| **Open Telemetry** | Monitoring and observability rollout across all modules |
| **Python Scripting** | Industry-standard Python replacing legacy scripting; automated quality enforcement |
| **Unit Testing** | Everything rolled out by consultants must be covered by unit tests and documentation |
| **Quality Gates** | Automated scanning of consultant code via Git repositories; quality checks before merge |
| **Prototype-to-Market** | Rapid prototyping capability: "click and deploy" minimal viable demos for market validation |

### 7. Consultant Productivity Problem

- The Portugal team (and others) do repetitive coding under time pressure
- No time to extract standards or follow them -- leading to inconsistent quality
- Solution: consolidate code into standard libraries, enforce quality via automated pipelines
- Consultants work in Git repositories; the moment code is committed, automated quality scans run
- This is sellable: "we can scan your code, refactor it, and guarantee quality output"

### 8. Proof of Concept Approach

- Start with standalone proof of concepts that demonstrate the methodology
- Can be run on existing protocols and modules to show the difference
- "Night and day difference in quality" between legacy scripted protocols and AI-assisted Python implementations
- The proof of concept serves both internal transformation and external sales (PE demos)

---

## Brainstorm Insights

- **Michiel's PE lens**: He sees the value in framing Solstein as the radar and AI-Whishperers as the transformation engine; understands the "share of wallet" and "new market entry" angles
- **Workshops with CEOs/founders**: Michiel mentioned running workshops with Vortex portfolio company CEOs/founders to demonstrate AI capabilities
- **Subscription model**: Discussed micro-subscriptions and tiered access as revenue channels
- **Domain expertise is the moat**: AI sharks (fast but shallow) cannot compete with domain-experienced teams augmented by AI -- this is the defensibility argument for PE
- **Cloud initiative**: Moving to cloud is table stakes; the real differentiator is the AI layer on top

---

## Action Points

### For John

| # | Action | Priority | Timeline |
|---|---|---|---|
| 1 | **Prepare a demo-ready prototype** showing the automated production process (ticket lifecycle, CICD, quality gates) | High | Before next Michiel meeting |
| 2 | **Document the Energy 21 transformation as a showcase** -- concrete metrics on velocity improvement, quality improvement, automation rate | High | Ongoing |
| 3 | **Complete the standard library consolidation** -- extract common patterns from Portugal team's code into reusable components | Medium | 2-4 weeks |
| 4 | **Finalize the Python scripting standard** with automated quality enforcement (linting, unit tests, documentation) | Medium | 2-4 weeks |
| 5 | **Open Telemetry rollout plan** -- stop discussing, start deploying across all modules | Medium | Plan this week |
| 6 | **Helm chart cleanup** -- resolve the current configuration/versioning issues | Medium | 2 weeks |

### For Michiel

| # | Action | Priority | Timeline |
|---|---|---|---|
| 7 | **Organize CEO/founder workshop** with Vortex portfolio companies to demonstrate AI production process capabilities | High | Schedule within 4 weeks |
| 8 | **Refine the go-to-market pitch** incorporating the production process transformation angle (not just market intelligence) | High | Before Vortex pilot |
| 9 | **Map the energy market competitive landscape** -- identify which segments (compliance, trading, forecasting) have the highest PE interest | Medium | 2 weeks |
| 10 | **Explore London / UK market entry** -- Michiel mentioned potential team and contacts there | Medium | 4-6 weeks |
| 11 | **Brand positioning for Solstein** -- ensure premium positioning as capital infrastructure, not a tool | Medium | Ongoing |

### Joint

| # | Action | Priority | Timeline |
|---|---|---|---|
| 12 | **Align on the dual-value proposition**: Solstein as intelligence + production process transformation as the delivery mechanism | High | Next call |
| 13 | **Prepare proof of concept** that can be presented to Vortex: market intelligence (Solstein) + transformation capability (live demo of automated quality/deployment) | High | 4-6 weeks |
| 14 | **Define the "AI-ready" assessment framework** for PE portfolio companies -- what does it mean to be AI-ready, and how does Solstein measure it? | Medium | 4 weeks |

---

## Key Quotes (Reconstructed from Clear Segments)

> "The release management is partially done manually still -- that one can go also a lot more automatically."  
> -- John, on current state of Energy 21 automation

> "If you know how many discussions we had on [Open Telemetry] -- 3-4 discussions with four people. That should have been rolled out everywhere already."  
> -- John, on the cost of indecision

> "There's a lot of repetitive coding happening because it's always done under time pressure. They don't know what is standard. They don't have time to extract the standard."  
> -- John, on the Portugal team's consultant productivity problem

> "It's not just making things easier and faster, but it's also to consolidate things -- consolidate code. Standard libraries for standard things."  
> -- John, on the standardization approach

> "A consultant can make something, it can be converted, and the customer's like: why are we still doing that in scripting? That is like night and day difference in quality."  
> -- John, on the transformation potential of Python + AI quality enforcement

---

## Session Character

This was not a formal meeting but a brainstorm and explanation session. John walked Michiel through the technical depth of what's being built at Energy 21 and how it maps to the broader Solstein/PE play. Michiel contributed the market and investor perspective, connecting the technical capabilities to PE value creation narratives. The conversation moved fluidly between strategic vision (the long play) and tactical detail (Helm charts, Open Telemetry), reflecting the hands-on nature of both participants.
