---
type: templar
artifact-type: prompt
pattern-name: systematic-mapping-research
version: 1.0.0
applies-to: analysis and discovery prompts
implements: analysis.mapping-research
consumed-by:
  - .cursor/prompts/analysis/market/research-protocols.prompt.md
---

# Systematic Mapping Research Templar

## Pattern Purpose

Discover and map entities (companies, products, services) by systematically researching a **domain dimension** (protocols, certifications, standards, regulations, APIs) and cross-referencing findings against a known list. The key insight: domain dimensions that are **mandated, finite, and documented** produce the most complete discovery results.

## When to Use

- Mapping which companies implement specific standards, protocols, or certifications
- Discovering missed entities by researching a structured domain dimension
- Building cross-reference matrices (entity x dimension x region/category)
- Validating completeness of an existing entity list via an orthogonal research axis

## Reusability

This pattern applies to any domain where:
1. A **finite set of formal artifacts** (protocols, certifications, standards, APIs) exists
2. Entities (companies, products) must **implement or comply** with those artifacts
3. Governing bodies or registries **publish** implementer/compliant-entity lists
4. Cross-referencing discovered entities against a **known list** reveals gaps

**Example domains**: energy market protocols, ISO certifications, API standard implementations, regulatory compliance registries, technology platform certifications, industry association memberships.

## Template Structure

### Frontmatter

```yaml
---
name: [PROMPT_SLUG]
description: "[ACTION_VERB] [DOMAIN_DIMENSION_PLURAL] by [REGION_OR_SCOPE] and identify which [ENTITY_TYPE_PLURAL] [RELATIONSHIP_VERB] them"
category: analysis
tags: [RELEVANT_TAGS]
argument-hint: "[SCOPE_PARAMETER_HINT]"
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---
```

### Title and Introduction

```markdown
# Research [DOMAIN_DIMENSION_PLURAL] - [DIMENSION]-to-[ENTITY_TYPE] Mapping

Please research and map the specific [DOMAIN_DIMENSION_PLURAL] used across [SCOPE],
identify which [ENTITY_TYPE_PLURAL] [RELATIONSHIP_VERB] each [DOMAIN_DIMENSION_SINGULAR],
and use this mapping to discover [ENTITY_TYPE_PLURAL] we may have missed.

**Pattern**: Guided Discovery Pattern
**Effectiveness**: [WHY_THIS_DIMENSION_IS_A_RELIABLE_INDICATOR]
**Use When**: [TRIGGER_CONDITION]
```

### Purpose Section

```markdown
## Purpose

[DOMAIN_CONTEXT] uses highly specific [DOMAIN_DIMENSION_PLURAL] that are:
- Mandated by [GOVERNING_BODIES]
- Implemented by a finite set of [ENTITY_TYPE_PLURAL]
- Documented in [PRIMARY_SOURCES]
- A reliable indicator of [WHAT_PARTICIPATION_SIGNALS]

By mapping **[DOMAIN_DIMENSION_SINGULAR] -> [SCOPE_UNIT] -> [ENTITY_TYPE]**, we can:
1. Verify our existing [ENTITY_TYPE] list covers all [DIMENSION] implementers
2. Discover [ENTITY_TYPE_PLURAL] we missed (especially niche/regional players)
3. Understand which [ENTITY_TYPE_PLURAL] have multi-[SCOPE_UNIT] coverage
4. Assess [DIMENSION] convergence/harmonization trends
```

### Required Context

```markdown
## Required Context

- **Focus Area**: [SCOPE_PARAMETER] or "all" for comprehensive mapping
- **Existing [ENTITY_TYPE] List**: Reference [KNOWN_LIST_PATH]
- **Own Position**: [OWN_ENTITY_CONTEXT]
```

### Process (7-Step Research Workflow)

```markdown
## Process

### Step 1: Read Current State
Read [KNOWN_LIST_PATH] and note which [DOMAIN_DIMENSION_PLURAL] each [ENTITY_TYPE]
already mentions. This is the baseline.

### Step 2: Map [DOMAIN_DIMENSION] Categories
For the target [SCOPE_UNIT(S)], research and map [DOMAIN_DIMENSION_PLURAL] across
these categories:

#### A. [CATEGORY_A_NAME]
| [DIMENSION] Area | Research Focus |
|---|---|
| [SUBCATEGORY] | [RESEARCH_QUESTION] |

#### B. [CATEGORY_B_NAME]
[... repeat per category ...]

### Step 3: Identify Specific [DOMAIN_DIMENSION_PLURAL] per [SCOPE_UNIT]
For each target [SCOPE_UNIT], document the specific [DIMENSION] names, versions,
and governing bodies.

**Output format per [SCOPE_UNIT]:**
| Category | [DIMENSION] Name | Version | Format | Governing Body |
|---|---|---|---|---|

### Step 4: Map [ENTITY_TYPE_PLURAL] to [DOMAIN_DIMENSION_PLURAL]
For each [DIMENSION] identified, research which [ENTITY_TYPE_PLURAL] implement it.

**Search strategies:**
- [GOVERNING_BODY] website -> certified/qualified [ENTITY_TYPE] lists
- [DIMENSION] specification documents -> implementing parties
- Industry events -> exhibitor lists filtered by [DIMENSION] keywords
- Job postings mentioning specific [DIMENSION] names
- Open source projects implementing [DIMENSION_PLURAL]

**Output format:**
| [ENTITY_TYPE] | Product | Implementation Level | Source |
|---|---|---|---|

### Step 5: Cross-Reference with Existing List
Compare discovered [ENTITY_TYPE_PLURAL] against [KNOWN_LIST_PATH]:
- Mark already-tracked entities with a checkmark
- Flag new entities not yet in the list
- Note multi-[DIMENSION] entities (breadth indicator)

### Step 6: Assess [DIMENSION] Convergence
Document trends in [DIMENSION] harmonization:
- Standardization efforts (which [DIMENSION_PLURAL] are converging?)
- Regulations driving changes
- National [DIMENSION_PLURAL] being replaced by international standards
- Impact on competitive/market landscape

### Step 7: Write Output Files
Write the mapping output to separate files:
- Cross-cutting map: [OUTPUT_PATH_MATRIX]
- Per-[ENTITY_TYPE] data: [OUTPUT_PATH_PER_ENTITY]
```

### Output Format

```markdown
## Output Format

### 1. [DIMENSION] Map (per [SCOPE_UNIT])
Complete table of [DIMENSION_PLURAL] per [SCOPE_UNIT] with versions, formats,
and governing bodies.

### 2. [ENTITY_TYPE]-[DIMENSION] Matrix
| [ENTITY_TYPE] | [SCOPE_A] ([DIM_A]) | [SCOPE_B] ([DIM_B]) | ... |
|---|---|---|---|

### 3. Newly Discovered [ENTITY_TYPE_PLURAL]
| [ENTITY_TYPE] | Product | [SCOPE_UNIT] | [DIMENSION_PLURAL] Implemented | Relevance |
|---|---|---|---|---|

### 4. [DIMENSION] Convergence Assessment
Narrative on how harmonization trends affect dynamics.
```

### Reasoning Process

```markdown
## Reasoning Process (for AI Agent)

1. **Read current state**: Load [KNOWN_LIST] and note existing [DIMENSION] mentions
2. **Determine scope**: All [SCOPE_UNITS], specific one, or specific [DIMENSION]
3. **Research systematically**: For each [SCOPE_UNIT], research all categories
4. **Find official lists**: Prioritize [GOVERNING_BODY] certified lists as most complete sources
5. **Cross-reference**: Compare discovered [ENTITY_TYPE_PLURAL] against known list
6. **Flag gaps**: Any [ENTITY_TYPE] implementing [DIMENSION_PLURAL] not in our list is a potential miss
7. **Assess convergence**: Note where [DIMENSION_PLURAL] are harmonizing
8. **Document everything**: With sources, write cross-cutting map + per-entity data

**Self-correction checkpoints:**
- Did I distinguish between [DIMENSION] *names* and *categories*?
- Did I verify [DIMENSION] names against [GOVERNING_BODY] source documents?
- Are the [ENTITY_TYPE_PLURAL] I listed actual [ENTITY_ROLE] (not just users/participants)?
- Did I miss any category for any [SCOPE_UNIT] in scope?
- Are "newly discovered" entities genuinely absent from the known list?

**Edge case handling:**
- [GOVERNING_BODY] website in local language only -> translated search queries
- [DIMENSION] being deprecated/replaced -> document both + transition timeline
- No public [ENTITY_TYPE] list -> pivot to job postings, events, open source
- Multi-[SCOPE_UNIT] [DIMENSION] variants -> distinguish national implementations
```

### Search Query Templates

```markdown
## Search Query Templates

**[GOVERNING_BODY] certified lists:**
- `"[GOVERNING_BODY_NAME]" certified software vendors qualified partners`
- `site:[governing-body-domain] approved systems OR qualified vendors`

**[DIMENSION] implementers:**
- `"[DIMENSION_NAME]" implementation software vendor [DOMAIN]`
- `"[DIMENSION_NAME]" certified system [DOMAIN]`

**Industry events:**
- `"[EVENT_NAME] [YEAR]" exhibitor "[DIMENSION_NAME]"`

**Job postings (reveal technology stack):**
- `"[DIMENSION_NAME]" developer OR engineer job [DOMAIN]`
```

### Quality Criteria

```markdown
## Quality Criteria

### Output Completeness
- [ ] At least [N] [SCOPE_UNITS] mapped
- [ ] All [N] [DIMENSION] categories covered per [SCOPE_UNIT]
- [ ] Each [DIMENSION] has governing body and format identified
- [ ] [ENTITY_TYPE]-[DIMENSION] matrix covers all existing [ENTITY_TYPE_PLURAL]
- [ ] Newly discovered [ENTITY_TYPE_PLURAL] flagged with relevance assessment
- [ ] Convergence trends documented

### Source Quality
- [ ] Sources cited for each [DIMENSION] identification
- [ ] [GOVERNING_BODY] primary sources used where available
- [ ] Cross-referenced against [KNOWN_LIST_PATH]

### Accuracy
- [ ] [DIMENSION] names verified against official documentation
- [ ] [ENTITY_TYPE_PLURAL] listed are [ENTITY_ROLE] (not just participants/users)
- [ ] "Newly discovered" entities confirmed absent from existing list
```

## Customization Points

- **[DOMAIN_DIMENSION]**: The structured artifact being mapped (protocols, certifications, standards, APIs, regulations)
- **[ENTITY_TYPE]**: What you're discovering (companies, products, services, organizations)
- **[SCOPE_UNIT]**: The cross-cutting dimension (countries, industries, market segments, regions)
- **[GOVERNING_BODY]**: Who mandates or publishes the dimension (TSOs, regulators, standards bodies, certification authorities)
- **[KNOWN_LIST_PATH]**: Where the existing entity list lives (for cross-referencing)
- **[CATEGORIES]**: Domain-specific breakdown of the dimension into researchable sub-areas
- **[RELATIONSHIP_VERB]**: How entities relate to the dimension (implement, comply with, are certified for, integrate with)
- **[ENTITY_ROLE]**: What qualifies as a valid entity (software vendor vs. user, certified provider vs. consumer)

## Example Usages

**Energy Protocol Mapping** (see exemplar: `.cursor/exemplars/analysis/market/research-protocols-exemplar.md`):
- Dimension = energy market communication protocols
- Entity = software companies
- Scope = European countries
- Governing bodies = TSOs, regulators (TenneT, BNetzA, EDSN)

**Certification Mapping** (hypothetical):
- Dimension = ISO/SOC/industry certifications
- Entity = SaaS vendors
- Scope = market segments
- Governing bodies = ISO, AICPA, industry associations

**API Standard Mapping** (hypothetical):
- Dimension = open banking / payment APIs (PSD2, Open Banking UK, SWIFT gpi)
- Entity = fintech companies
- Scope = countries / regulatory jurisdictions
- Governing bodies = EBA, FCA, SWIFT

## Quality Criteria

- [ ] Pattern is reusable (3+ use cases identified above)
- [ ] All placeholders clearly marked with `[UPPER_CASE]`
- [ ] 7-step research process is domain-agnostic
- [ ] Customization points explained with guidance
- [ ] Example usages show how to apply the pattern

## Related Templars

- None yet in analysis domain (this is the first)

## Related Exemplars

- `.cursor/exemplars/analysis/market/research-protocols-exemplar.md` - Shows this pattern applied to energy market protocols
