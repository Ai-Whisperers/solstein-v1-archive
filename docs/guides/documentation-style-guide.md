# Solstein Documentation Style Guide

**Version:** 1.0  
**Last Updated:** February 24, 2026  
**Applies To:** All documentation in the Solstein repository

---

## Table of Contents

1. [Writing Style](#1-writing-style)
2. [Markdown Formatting Standards](#2-markdown-formatting-standards)
3. [Code Example Standards](#3-code-example-standards)
4. [Cross-Reference Standards](#4-cross-reference-standards)
5. [Visual Design Standards](#5-visual-design-standards)
6. [Documentation Templates](#6-documentation-templates)
7. [File Organization](#7-file-organization)
8. [Quality Checklist](#8-quality-checklist)

---

## 1. Writing Style

### 1.1 Voice and Tone

**Voice Characteristics:**
- **Professional but engaging** — Business-appropriate without being dry
- **Authoritative** — Confident statements about capabilities and architecture
- **Wizard/Alchemy metaphor** — Use guild terminology when appropriate (wizards, scrolls, grimoire, spells)
- **Clear and direct** — No corporate fluff or passive voice

**Tone Guidelines:**

| Context | Tone | Example |
|---------|------|---------|
| Business value | Confident, authoritative | "Solstein transforms the Private Equity due diligence process" |
| Technical explanation | Clear, precise | "FastAPI's `Depends()` injection system makes testing trivial" |
| Origin story | Narrative, engaging | "Companies are born with wings. They start light, agile, and fast." |
| Instructions | Direct, actionable | "Clone the repository and install dependencies" |

### 1.2 Audience Segments

**Primary Audiences:**
1. **PE Partners & Investors** — Need business value, ROI, and competitive advantage
2. **Deal Teams** — Need methodology, data sources, and practical usage
3. **Technical Teams** — Need implementation details, API specs, and integration guides
4. **Internal Developers** — Need architecture, patterns, and contribution guidelines

**Writing for Each Audience:**

- **PE Partners:** Lead with business outcomes, use business terminology, minimize technical detail
- **Deal Teams:** Balance methodology explanation with practical examples
- **Technical Teams:** Comprehensive technical detail, code examples, API specs
- **Developers:** Implementation patterns, testing strategies, code structure

### 1.3 Language Standards

**Do:**
- Use active voice: "The API returns results" (not "Results are returned by the API")
- Use present tense for current capabilities
- Use second person for instructions: "You should configure..."
- Define acronyms on first use: "Private Equity (PE)"
- Use consistent terminology throughout

**Don't:**
- Use future tense for existing features: "The system will provide" → "The system provides"
- Overuse passive voice
- Use ambiguous qualifiers: "very", "quite", "rather"
- Mix metaphors (stick to the wizard/guild/alchemy theme)

### 1.4 Terminology Dictionary

| Term | Usage | Avoid |
|------|-------|-------|
| **Attractiveness Board** | Capitalized, the main output dashboard | "dashboard", "scorecard" |
| **Phoenix** | Capitalized, score ≥ 7.0 | "high-growth" (alone) |
| **Salt** | Capitalized, score 4.0–7.0 | "mid-tier" |
| **Lead** | Capitalized, score ≤ 4.0 | "low-growth" (alone) |
| **Sunstone** | The product concept/metaphor | Lowercase "sunstone" |
| **Guild of Architects** | The development team metaphor | "engineering team" |
| **PE** | Private Equity (after first definition) | Mixing with "Private Equity" inconsistently |

---

## 2. Markdown Formatting Standards

### 2.1 File Structure

**Standard Document Header:**
```markdown
# 📜 Document Title

**Subtitle or brief description**

---
```

**Required Elements:**
1. Main title with emoji prefix (see Visual Design Standards)
2. Subtitle in bold describing document purpose
3. Horizontal rule (`---`) separating header from content

### 2.2 Headers

**Hierarchy:**
```markdown
# H1 — Document Title (use once per document)
## H2 — Major sections
### H3 — Subsections
#### H4 — Detailed subsections (rare)
```

**Formatting Rules:**
- H1: Include emoji prefix (📜, 🏗️, ⚡, etc.)
- H2: Always preceded and followed by `---` horizontal rule
- H3: Directly followed by content
- Never skip header levels (don't go H2 → H4)

### 2.3 Tables

**Standard Table Format:**
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
```

**Table Usage Guidelines:**

| Table Type | Use Case | Alignment |
|------------|----------|-----------|
| Data tables | API parameters, config options | Left-aligned |
| Comparison tables | Feature comparisons | Center-aligned |
| Classification tables | Phoenix/Salt/Lead definitions | Left-aligned |

**Table Rules:**
- Always include header separator line (`|---|---|`)
- Keep columns to 4 or fewer when possible
- Use code formatting for technical values: `GET`, `200`, `true`
- Include units in headers: `Revenue (EUR M)`, `Score (0-10)`

### 2.4 Lists

**Unordered Lists:**
```markdown
- Item one
- Item two with **bold** emphasis
- Item three with `code` reference
  - Nested item (2-space indent)
  - Another nested item
```

**Ordered Lists:**
```markdown
1. First step
2. Second step
3. Third step with code:
   ```bash
   command here
   ```
```

**List Rules:**
- Use `-` (dash) for unordered lists, not `*` or `+`
- Use consistent punctuation: no periods for fragments, periods for complete sentences
- Maximum 2 levels of nesting

### 2.5 Code Blocks

**Syntax Highlighting:**
```markdown
```python
# Python code
```

```bash
# Shell commands
```

```json
# JSON data
```

```yaml
# YAML configuration
```
```

**Supported Languages:**
- `python` — Python code examples
- `bash` — Shell commands and scripts
- `json` — API responses and data structures
- `yaml` — Configuration files
- `javascript` — Frontend code
- `typescript` — TypeScript code
- `sql` — Database queries
- `markdown` — Markdown examples

### 2.6 Inline Formatting

| Element | Format | Example |
|---------|--------|---------|
| Code/Commands | Backticks | `uvicorn`, `GET /health` |
| File paths | Backticks | `docs/guides/developer.md` |
| UI elements | Bold | Click **Submit** |
| Key terms (first use) | Bold | The **Attractiveness Board** |
| Emphasis | Italics | *The wings turn to lead.* |
| Strong emphasis | Bold | **Critical:** Never do this |

### 2.7 Blockquotes

**Usage:**
```markdown
> This is a blockquote for important callouts or quotes.
> Multi-line blockquotes use the same prefix.

> **Note:** Use bold prefixes for note types:
> - **Note:** General information
> - **Warning:** Cautionary information
> - **Critical:** Essential warnings
```

**Blockquote Types:**
- **Note:** — General supplementary information
- **Warning:** — Caution about potential issues
- **Critical:** — Essential warnings that must not be ignored
- **Tip:** — Helpful suggestions or shortcuts

---

## 3. Code Example Standards

### 3.1 Code Block Structure

**Every Code Block Must Include:**
1. Language identifier for syntax highlighting
2. Comments explaining key steps
3. Working, tested code
4. Realistic data (no `foo`, `bar`, `example`)

**Template:**
```python
# 1. Import required modules
from solstein.analytics.scoring import GrowthScorer

# 2. Initialize with configuration
scorer = GrowthScorer(config)

# 3. Execute with sample data
result = scorer.calculate_scores(company)

# 4. Validate output
assert result.growth_score > 0
```

### 3.2 Code Example Requirements

| Requirement | Standard | Verification |
|-------------|----------|--------------|
| **Syntax correctness** | Code must be valid and runnable | Manual review + automated testing |
| **Realistic data** | Use actual company names or plausible examples | Review against production data |
| **Complete context** | Include imports and setup | Must compile/parse standalone |
| **Comments** | Explain *why*, not just *what* | Every non-obvious line |
| **Error handling** | Show proper error patterns | Follow error handling rules |

### 3.3 Code Example Categories

**Quick Start Examples:**
```bash
# Clone and setup
git clone <repo> && cd solstein
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
```

**API Usage Examples:**
```python
import requests

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# List companies
response = requests.get(f"{BASE_URL}/companies", headers=HEADERS)
companies = response.json()
```

**Configuration Examples:**
```yaml
# Scoring configuration
scoring:
  growth:
    revenue_large_threshold: 100.0  # EUR Millions
    high_growth_threshold: 25.0     # Percentage
```

### 3.4 Testing Code Examples

**All code examples must be:**
1. **Copy-paste ready** — User can run without modification
2. **Environment-aware** — Note if specific setup is required
3. **Version-synced** — Updated when APIs change

**Example Testing Checklist:**
- [ ] Code runs without errors in target environment
- [ ] Output matches documented example
- [ ] All imports resolve correctly
- [ ] No hardcoded credentials or secrets

---

## 4. Cross-Reference Standards

### 4.1 Internal Links

**Link Format:**
```markdown
[Link Text](relative/path/to/file.md)
[Link Text](relative/path/to/file.md#section-anchor)
```

**Internal Link Patterns:**

| Target | Format | Example |
|--------|--------|---------|
| Other guides | `[Developer Guide](guides/developer.md)` | `[Developer Guide](guides/developer.md)` |
| API reference | `[API Reference](api/reference.md)` | `[API Reference](api/reference.md)` |
| Specific section | `[Scoring Section](guides/developer.md#scoring-pipeline)` | `[Scoring Section](guides/developer.md#scoring-pipeline)` |
| README sections | `[Quick Start](../README.md#quick-start)` | `[Quick Start](../README.md#quick-start)` |

**Internal Link Rules:**
- Use relative paths from the current file
- Always include `.md` extension
- Use descriptive link text (not "click here")
- Verify links work before committing

### 4.2 External Links

**External Link Format:**
```markdown
[Link Text](https://example.com)
[Link Text](https://example.com "Title attribute")
```

**External Link Patterns:**

| Type | Format | Example |
|------|--------|---------|
| Documentation | `[FastAPI Docs](https://fastapi.tiangolo.com)` | `[FastAPI Docs](https://fastapi.tiangolo.com)` |
| GitHub repos | `[Repository](https://github.com/org/repo)` | `[Repository](https://github.com/org/repo)` |
| API docs | `[OpenAPI Spec](http://localhost:8000/openapi.json)` | `[OpenAPI Spec](http://localhost:8000/openapi.json)` |

**External Link Rules:**
- Use HTTPS when available
- Include title attribute for clarity
- Prefer official documentation over third-party
- Test links periodically

### 4.3 Navigation Tables

**Standard Navigation Table:**
```markdown
| Scroll | Contents |
|--------|----------|
| 📜 [`docs/LORE/origin.md`](LORE/origin.md) | The origin story |
| 📜 [`docs/guides/developer.md`](guides/developer.md) | Developer setup guide |
```

**Rules:**
- Use "Scroll" column header for documentation index
- Include emoji prefix for document type
- Use code formatting for file paths
- Keep descriptions under 10 words

---

## 5. Visual Design Standards

### 5.1 Emoji Usage

**Document Type Emojis:**

| Emoji | Document Type | Usage |
|-------|--------------|-------|
| 📜 | Lore/Origin stories | Historical, narrative documentation |
| ⚔️ | Pitch/Investment docs | Business proposals, executive briefs |
| ⚙️ | Technical guides | Developer docs, API references |
| 🏛️ | Architecture docs | ADRs, system design |
| 📊 | Data/Analytics docs | Scoring methodology, data sources |
| 🔥 | Phoenix classification | Score ≥ 7.0 indicators |
| 🧂 | Salt classification | Score 4.0–7.0 indicators |
| ⚖️ | Lead classification | Score ≤ 4.0 indicators |
| 💎 | Value proposition | Business value statements |
| ⚡ | Quick start/Setup | Getting started sections |

**Emoji Rules:**
- Use emoji in H1 headers only
- Don't use emoji in running text (except classification indicators)
- Maximum 2 emojis per document header

### 5.2 Badge Standards

**Badge Format (Shields.io):**
```markdown
[![Label](https://img.shields.io/badge/Label-Value-COLOR?style=for-the-badge&logo=LOGO&logoColor=COLOR)](link)
```

**Solstein Brand Colors:**
- Primary: `#4b0082` (Indigo/Purple)
- Accent: `#ffd700` (Gold)

**Standard Badges:**
```markdown
[![Python](https://img.shields.io/badge/Python-3.12-4b0082?style=for-the-badge&logo=python&logoColor=ffd700)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Live-4b0082?style=for-the-badge&logo=fastapi&logoColor=ffd700)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-90%20Passing-4b0082?style=for-the-badge&logo=pytest&logoColor=ffd700)](tests/)
```

### 5.3 ASCII Diagrams

**Directory Structure:**
```
solstein/
├── src/solstein/
│   ├── api/              ← FastAPI application & routers
│   ├── infrastructure/   ← Stone Layer: PostgreSQL, SQLAlchemy
│   ├── analytics/        ← Logic Fusion: Scoring, Analysis
│   └── ...
├── docs/                 ← Technical Grimoire
└── data/                 ← Market intelligence datasets
```

**Diagram Rules:**
- Use box-drawing characters for structure
- Include brief descriptions after arrows (`←`)
- Keep width under 80 characters
- Use consistent indentation (2 or 4 spaces)

### 5.4 Classification Visuals

**Classification Table:**
```markdown
| Classification | Growth Score | What It Means |
|---|---|---|
| 🔥 **Phoenix** | ≥ 7.0 | High-growth, AI-native or rapidly adopting. Act now. |
| 🧂 **Salt** | 4.0 – 7.0 | Stable players. Watch for directional signals. |
| ⚖️ **Lead** | ≤ 4.0 | Legacy weight. Hidden diamonds or dead weight. |
```

**Formatting:**
- Classification names in **bold**
- Emoji prefix
- Score ranges in code blocks or plain text
- Descriptions are actionable

---

## 6. Documentation Templates

### 6.1 README Section Template

```markdown
## ⚡ Section Title

Brief paragraph explaining this section's purpose.

### Subsection

Detailed content here.

```bash
# Code example
command --flag value
```

**Key points:**
- Point one
- Point two
- Point three
```

### 6.2 API Endpoint Documentation Template

```markdown
### `METHOD /endpoint/path`

Brief description of what this endpoint does.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `param1` | string | Yes | Description of parameter |
| `param2` | integer | No | Description (default: 10) |

**Request Body:**
```json
{
  "field": "value",
  "optional_field": "value"
}
```

**Response:**
```json
{
  "data": {...},
  "meta": {
    "timestamp": "2026-02-20T10:00:00Z"
  }
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| `404` | `NOT_FOUND` | Resource doesn't exist |
| `422` | `VALIDATION_ERROR` | Invalid request schema |

**Example:**
```bash
curl -X POST http://localhost:8000/endpoint \
  -H "Content-Type: application/json" \
  -d '{"field": "value"}'
```
```

### 6.3 Guide Document Template

```markdown
# 📜 Guide Title

**One-line description of the guide's purpose**

---

## Prerequisites

- Requirement 1
- Requirement 2
- Requirement 3

---

## Main Section

Content here.

### Subsection

More content.

---

## Another Section

Content continues.

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Related Doc](path.md) | Brief description |
```

### 6.4 ADR (Architecture Decision Record) Template

```markdown
## ADR-XXX: Decision Title

**Date:** YYYY-QX  
**Status:** Proposed | Accepted | Deprecated | Superseded

**Context:**

Describe the forces at play, including technological, political, social, and project-local factors.

**Decision:**

The change that we're proposing or have agreed to implement.

**Rationale:**

- Reason 1
- Reason 2
- Reason 3

**Consequences:**

Positive:
- Benefit 1
- Benefit 2

Negative:
- Drawback 1
- Drawback 2

**Caveat:** (optional)

Known limitations or technical debt introduced.

**Upgrade path:** (optional)

How to migrate away from this decision if needed.
```

### 6.5 Business/Pitch Document Template

```markdown
# ⚔️ Document Title | Subtitle

**Strategic positioning statement**

---

## The Positioning Principle

Opening paragraph establishing the strategic framework.

---

## Section Title

### Subsection

| Parameter | Value |
|-----------|-------|
| Key metric | Value |
| Another metric | Value |

---

*Attribution line referencing AI Whisperers*
```

---

## 7. File Organization

### 7.1 Directory Structure

```
docs/
├── README.md                    # Documentation index
├── DOCUMENTATION_INDEX.md       # Master navigation
├── guides/                      # How-to guides
│   ├── developer.md
│   ├── operator.md
│   └── documentation-style-guide.md
├── api/                         # API documentation
│   └── reference.md
├── architecture/                # Architecture docs
│   └── decisions.md
├── PITCH/                       # Business/pitch docs
│   ├── executive-brief.md
│   ├── business-model.md
│   └── case-study.md
├── LORE/                        # Origin/narrative docs
│   ├── origin.md
│   └── the-play.md
└── archive/                     # Historical docs
    └── root-docs/
```

### 7.2 File Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Standard docs | kebab-case | `developer-guide.md` |
| Special docs | UPPERCASE | `README.md`, `CONTRIBUTING.md` |
| ADRs | `ADR-NNN-description.md` | `ADR-001-fastapi-framework.md` |
| Indexes | UPPERCASE | `DOCUMENTATION_INDEX.md` |

### 7.3 README Files

**Every directory should have a README.md containing:**
1. Brief description of the directory's purpose
2. List of files with one-line descriptions
3. Navigation to parent/child directories

---

## 8. Quality Checklist

### 8.1 Before Publishing Documentation

**Content Quality:**
- [ ] Document has clear purpose and audience
- [ ] Title accurately reflects content
- [ ] All sections have appropriate headers
- [ ] No placeholder text or TODOs remain
- [ ] Technical accuracy verified

**Formatting Quality:**
- [ ] Consistent header hierarchy
- [ ] All tables have proper formatting
- [ ] Code blocks have language identifiers
- [ ] All links are valid and functional
- [ ] Consistent use of emojis and badges

**Code Quality:**
- [ ] All code examples tested and working
- [ ] No hardcoded credentials or secrets
- [ ] Realistic data used (not foo/bar)
- [ ] Error handling patterns followed

**Cross-Reference Quality:**
- [ ] Internal links use relative paths
- [ ] External links use HTTPS
- [ ] Navigation tables are complete
- [ ] Related documents referenced

### 8.2 Peer Review Checklist

**Review Questions:**
1. Is the document's purpose immediately clear?
2. Can a new reader follow the instructions/examples?
3. Are technical terms defined or linked?
4. Is the tone appropriate for the audience?
5. Are there any broken links or references?
6. Do code examples work as written?

**Sign-off Requirements:**
- Technical docs: Reviewed by 1+ developers
- Business docs: Reviewed by 1+ business stakeholders
- API docs: Reviewed by API maintainer

---

## Appendix A: Quick Reference

### Markdown Cheat Sheet

```markdown
# Header 1
## Header 2
### Header 3

**Bold text**
*Italic text*
`Code text`

[Link text](path/to/file.md)
![Alt text](image.png)

- Bullet item
- Another bullet
  - Nested bullet

1. Numbered item
2. Another item

| Col 1 | Col 2 |
|-------|-------|
| A     | B     |

> Blockquote

```python
code_block()
```
```

### Common Patterns

**Classification Display:**
```markdown
| Classification | Score | Meaning |
|---|---|---|
| 🔥 **Phoenix** | ≥ 7.0 | Description |
| 🧂 **Salt** | 4.0–7.0 | Description |
| ⚖️ **Lead** | ≤ 4.0 | Description |
```

**Badge Strip:**
```markdown
[![Python](https://img.shields.io/badge/Python-3.12-4b0082?style=for-the-badge&logo=python&logoColor=ffd700)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Live-4b0082?style=for-the-badge&logo=fastapi&logoColor=ffd700)](https://fastapi.tiangolo.com)
```

**API Endpoint Block:**
```markdown
#### `METHOD /path`

Description.

**Parameters:**
| Param | Type | Description |

**Response:**
```json
{}
```
```

---

*This style guide is a living document. Updates should be proposed via PR and reviewed according to the Quality Checklist.*

**Last Updated:** February 24, 2026  
**Version:** 1.0  
**Maintained by:** AI Whisperers Documentation Guild
