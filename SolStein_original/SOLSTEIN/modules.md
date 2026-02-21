# Solstein -- Module Details

---

## Module 1: Competitor Deep Analysis

**Input**: Company name
**Output**: Structured competitive profile across 8 dimensions

| Dimension | What You Get |
|---|---|
| Company Fundamentals | Size, revenue, headcount, HQ, founding date |
| Market Position | Market share, geographic presence, customer segments |
| Product & Technology | Architecture, tech stack, platform maturity, cloud readiness |
| AI & Innovation | AI adoption level, R&D investment, innovation signals |
| Growth & Trajectory | Revenue CAGR, employee growth, expansion patterns |
| Commodities & Specialization | Which markets, which instruments, which niches |
| Pricing & Business Model | SaaS vs license, ARPU signals, contract models |
| Threat Assessment | Competitive overlap, threat level, strategic implications |

Every data point tagged with confidence level: Confirmed, Estimated, or Unknown.

---

## Module 2: Financial Growth Scoring

**Input**: Company name
**Output**: Multi-dimensional Growth Scorecard (1-10 per dimension)

| Dimension | What It Measures |
|---|---|
| Revenue & Profitability | 3-5 year revenue trajectory, margins, ARR growth |
| Funding & Investment | Round sizes, valuations, investor quality |
| Employee Growth | Headcount trajectory, hiring patterns, talent signals |
| Geographic Expansion | New markets entered, international revenue % |
| M&A Activity | Acquisition pace, deal rationale, integration success |
| SaaS Transition | Recurring revenue %, cloud maturity, migration progress |

**Classification**:
- **Rocket** (7.0-10.0): Explosive growth, heavy investment
- **Riser** (5.0-6.9): Solid growth, well-positioned
- **Steady** (3.0-4.9): Stable but not accelerating
- **Dinosaur** (1.0-2.9): Flat or declining, legacy mode

---

## Module 3: Corporate Genealogy

**Input**: Company name
**Output**: Full corporate history with Mermaid diagrams

Reconstructs the complete corporate family tree:
- Mergers and acquisitions (who bought whom, when, for how much)
- Name changes and rebrands (what's the real age of the product?)
- Spin-offs and divestitures (what was considered non-core?)
- Investment rounds and ownership changes (who's driving strategy?)
- Critical events (IPOs, delistings, PE buyouts, management changes)

Many companies are icebergs. The visible brand is new, but the codebase is 20 years old. Corporate genealogy reveals what's really under the hood.

---

## Module 4: Financial Dashboard

**Input**: All competitor profiles (auto-reads from portfolio)
**Output**: Cross-competitor ranking dashboard with charts

Synthesizes all individual analyses into a single strategic document:
- Composite growth rankings across all competitors
- Revenue leaderboards with CAGR comparisons
- Growth vs Size quadrant charts (Mermaid-rendered)
- SaaS maturity rankings
- AI adoption rankings
- "Meteor Warning" narrative for decision-makers
- Portfolio company positioned on every ranking for visceral contrast

---

## Module 5: Market Protocol Mapping

**Input**: Country, industry, or market segment
**Output**: Protocol-to-company matrix revealing the full competitive landscape

Maps the regulatory and technical protocols that define market participation:
- Which standards exist in which markets
- Which companies implement which protocols
- Gaps in the competitor list (who did we miss?)
- Market entry barriers by protocol complexity

In regulated industries, protocols are the fingerprint. If you implement the protocol, you're a player. Following the protocols reveals competitors that web searches miss.

---

## Architecture

Solstein is built on a modular three-layer architecture:

| Layer | What It Is | Why It Matters |
|---|---|---|
| **Prompts** (5 modules) | Research instructions that drive AI through systematic analysis | Defines WHAT to research and HOW to structure it |
| **Templars** (5 templates) | Reusable prompt architecture patterns | Makes it trivial to adapt to any industry |
| **Exemplars** (5 examples) | Proven output examples that guide quality | Ensures consistent, high-quality results |

Adapting Solstein to a new industry vertical (banking, hospitality, logistics, healthcare) requires modifying the domain context, not rebuilding the system.
