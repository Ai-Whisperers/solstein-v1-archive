# Analysis: Michiel's Proposal vs. Existing SOLSTEIN Materials

**Date:** 2025-02-19
**Sources compared:**
- `PROPOSAL/solstein-proposal-michiel.md` (Michiel Kuiper's proposal)
- `SOLSTEIN/README.md`, `modules.md`, `pricing.md`, `why-now.md`, `case-study.md`, `competitive-intelligence-platform-features.md`

---

## 1. Strategic Repositioning -- The Big Shift

Michiel is proposing a fundamental repositioning of Solstein:

| Dimension | Current SOLSTEIN | Michiel's Proposal |
|---|---|---|
| **Identity** | AI-powered competitive intelligence *tool* built by/for Eneve | Standalone AI-native decision intelligence *company* |
| **Core output** | Competitor profiles, Excel dashboards, financial scorecards | "Attractiveness Board" -- ranked, clickable, explainable |
| **Narrative** | "We built this for our own board, now we sell it" | "Capital infrastructure for PE, positioned from day one as independent" |
| **Relationship to Eneve** | Product by Eneve / AI-Whisperers | Separate legal entity, even if initially owned by Eneve |

This is a stronger commercial framing. The current materials still carry the origin story (built for Eneve's CTO). Michiel is saying: **kill the umbilical cord**.

---

## 2. Pricing -- Massively Different Philosophy

This is where the two diverge most sharply:

| | Current SOLSTEIN Pricing | Michiel's Proposal |
|---|---|---|
| Entry point | EUR 500K-1M (single assessment) | EUR 60K pilot (Phase 1) |
| Subscription | EUR 100-200K/yr SaaS (future) | EUR 75-150K/yr PE subscription (now) |
| Scale target | EUR 10-100M ARR at SaaS maturity | EUR 10M ARR by Month 5-8 |
| Commercial model | Consulting-like project fees | Subscription-first from day one |

**Key tension:** The current pricing positions Solstein as a premium consulting replacement at EUR 500K-1M per engagement. Michiel is positioning it as a **subscription product** at EUR 75-150K/yr -- roughly 5-10x cheaper per unit, but designed for volume and recurring revenue.

The current EUR 500K per assessment would scare off a pilot. Michiel's EUR 60K anchor pilot is designed to **get in the door at Vortex** and validate, then scale pricing.

---

## 3. Go-to-Market -- Tighter, Faster, More Disciplined

| Phase | Current SOLSTEIN GTM | Michiel's Proposal |
|---|---|---|
| 1 | Anchor client (vague timing) | Month 1: Paid pilot with Vortex, EUR 60K |
| 2 | Warm network, 3-6 months | Month 2: 3-5 PE funds, EUR 180-300K ARR |
| 3 | Industry verticals, 6-12 months | Month 3-4: 20 PE clients, index publication |
| 4 | SaaS platform, 12-24 months | Month 5-8: 100 PE + Corp Dev, EUR 10M ARR |

Michiel's timeline is **3-4x faster**. The current materials plan 12-24 months to SaaS. Michiel plans EUR 10M ARR in 8 months.

This is aggressive but follows the explicit pattern: **Validate -> Monetize -> Authority -> Scale -> (Sale?)**

The "(Sale?)" at the end is notable -- Michiel is building this with an exit narrative from the start.

---

## 4. Product Concept -- Evolution, Not Revolution

The "Attractiveness Board" maps well to existing capabilities:

| Attractiveness Board Feature | Current SOLSTEIN Capability | Gap? |
|---|---|---|
| Ranked and comparable | Financial Dashboard rankings | Exists |
| Clickable per metric | Excel workbook drill-down | Exists (Excel), needs web UI |
| Fully explainable | Confidence tags, methodology sheet | Exists partially |
| Underlying data exposure | Source-attributed research files | Exists |
| AI reasoning path | Not currently exposed | **New requirement** |
| Weighting logic (partially abstracted) | Scoring methodology documented | Needs abstraction layer |

The biggest product gap is **explainability of AI reasoning** -- exposing the "why" behind each score. The current system has confidence tags and methodology docs, but not an interactive reasoning path. This is what Michiel calls "the explainability layer" and calls "essential."

---

## 5. What's Missing From Michiel's Proposal

Things the current SOLSTEIN materials have that the proposal doesn't address:

- **Module architecture** -- No mention of the 5-module structure (Competitor Deep Analysis, Financial Scoring, Corporate Genealogy, Financial Dashboard, Protocol Mapping)
- **Technical depth** -- No mention of prompts, templars, exemplars, the Python pipeline, test coverage
- **The case study** -- The Eneve/energy market proof case isn't referenced
- **Multi-vertical expansion** -- Michiel focuses purely on PE as the buyer. The current materials emphasize banking, healthcare, industrial software
- **Data confidence framework** -- The Confirmed/Estimated/Unknown tagging system isn't mentioned

This makes sense -- Michiel's document is a **commercial/strategic proposal**, not a technical spec. But for the Vortex pitch, the technical substance from SOLSTEIN needs to back it up. As Michiel says: *"provided the story holds up technically."*

---

## 6. Key Alignment Points

Where both visions agree strongly:

- **PE is the right first buyer** (urgency, budget, repeat usage)
- **The sunstone metaphor** is the brand identity
- **Speed vs consulting** is the core value proposition
- **The expertise moat** (2 years of AI practice) is the defensibility
- **Continuous intelligence** beats static PDF consulting

---

## 7. Action Items / Gaps to Close for Vortex

Based on Michiel's email -- Vortex has "candy shop interest" but needs the story to hold up technically:

1. **Bridge document needed** -- Something that connects Michiel's commercial positioning to the existing SOLSTEIN technical substance. The Attractiveness Board concept needs a prototype or mockup.
2. **Explainability layer** -- The AI reasoning path is a new product requirement that doesn't exist yet. This needs scoping.
3. **Pricing alignment** -- The team needs to decide: EUR 75-150K/yr subscriptions (Michiel) or EUR 500K-1M engagements (current)? These are different businesses.
4. **Second market demo** -- Michiel suggests demonstrating "another market where their portfolio is active." This requires adapting the current energy-specific modules to a new vertical, which the architecture supports but hasn't been done yet.
5. **Legal entity setup** -- Michiel is clear: separate entity from day one. This is an operational decision that needs to happen before (or concurrent with) the Vortex pilot.

---

## Bottom Line

Michiel's proposal is a sharper commercial wrapper around the existing SOLSTEIN substance. The technical foundation is solid and largely built. The gap is in:

- **(a)** The product presentation layer (Attractiveness Board UI)
- **(b)** The explainability features
- **(c)** The organizational/pricing decisions

The Vortex opportunity is real, and the timeline pressure means these gaps need prioritizing now.
