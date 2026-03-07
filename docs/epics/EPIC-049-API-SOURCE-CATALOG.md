# EPIC-049: API Source Catalog & Curation Framework

|**Status:** 🔴 Not Started  
|**Priority:** HIGH (P1)  
|**Story Points:** 34  
|**Sprint Allocation:** 3 sprints  
|**Target Date:** Week 25-27

---

## Problem Statement

Solstein lacks a centralized, structured catalog of data sources. External API lists like OpenClaw exist but are not curated for competitive intelligence use cases. There is no systematic way to evaluate, prioritize, or track API integrations.

### Impact
- No visibility into available data sources
- Ad-hoc API integrations without quality standards
- Duplicate effort when researching APIs
- No metrics on source coverage or quality
- Difficult to identify gaps in data source portfolio

---

## Success Criteria

1. ✅ Centralized API catalog with structured metadata
2. ✅ Quality scoring framework for all data sources
3. ✅ Clear integration criteria and decision framework
4. ✅ Coverage metrics by geography, sector, and data type
5. ✅ Automated catalog updates from external sources (OpenClaw, GitHub, etc.)

---

## Stories

### Story 49.1: Catalog Data Model & Schema (8 pts)
**Task:** Design and implement the API source catalog data model

**Acceptance Criteria:**
- [ ] Catalog schema supports: name, provider, category, auth_type, pricing, rate_limits
- [ ] Coverage metadata: geographies[], sectors[], company_stages[], data_types[]
- [ ] Quality metadata: reliability_score, freshness_score, coverage_score
- [ ] Integration metadata: effort_estimate, maintenance_level, solstein_relevance
- [ ] JSON/YAML export format for catalog distribution
- [ ] Schema validation and versioning

**Implementation:**
```yaml
# docs/data-sources/catalog-schema.yaml
api_source:
  id: string  # unique identifier
  name: string
  provider: string
  description: string
  
  # Categorization
  category: enum[financial, regulatory, news, jobs, social, web, patents, other]
  subcategory: string
  
  # Technical
  auth_type: enum[none, api_key, oauth, oauth2]
  pricing: enum[free, freemium, paid, enterprise]
  rate_limit: string  # e.g., "100/minute"
  
  # Coverage
  coverage:
    geographies: [string]
    sectors: [string]
    company_stages: [startup, growth, enterprise]
    data_types: [funding, financials, news, jobs, patents, web_traffic]
  
  # Quality Scores (0-1)
  quality:
    reliability: float
    freshness: float
    coverage: float
    overall: float  # weighted composite
  
  # Solstein-specific
  solstein:
    relevance: enum[high, medium, low]
    use_cases: [enrichment, discovery, monitoring]
    integration_effort: enum[low, medium, high]
    status: enum[evaluating, planned, in_progress, integrated, deprecated]
```

---

### Story 49.2: Catalog Repository Structure (8 pts)
**Task:** Create organized catalog repository following OpenClaw patterns

**Acceptance Criteria:**
- [ ] Directory structure: `docs/data-sources/{category}/`
- [ ] Each API has individual markdown file with YAML frontmatter
- [ ] Category README with summary statistics
- [ ] Master catalog index with search/filter capabilities
- [ ] Curated "priority" list for quick reference
- [ ] Integration with existing adapter registry

**Structure:**
```
docs/data-sources/
├── README.md                    # Master index
├── INTEGRATION_CRITERIA.md      # Quality standards
├── CATALOG_STATS.md             # Coverage metrics
├── priority-sources.md          # P0 integrations
├── 
├── financial/                   # Financial data APIs
│   ├── README.md
│   ├── alpha-vantage.md
│   ├── yahoo-finance.md
│   └── ...
├── regulatory/                  # Government/regulatory APIs
│   ├── README.md
│   ├── sec-edgar.md
│   ├── companies-house.md
│   └── ...
├── news/                        # News and content APIs
│   ├── README.md
│   ├── newsapi.md
│   └── ...
├── jobs/                        # Job market APIs
│   ├── README.md
│   └── ...
├── social/                      # Social media APIs
│   ├── README.md
│   └── ...
└── web/                         # Web scraping/monitoring
    ├── README.md
    └── ...
```

---

### Story 49.3: Catalog CLI & Management Tools (8 pts)
**Task:** Build CLI tools for catalog management

**Acceptance Criteria:**
- [ ] `solstein catalog list` - List all sources with filters
- [ ] `solstein catalog search <query>` - Search by name, category, provider
- [ ] `solstein catalog show <source_id>` - Display detailed source info
- [ ] `solstein catalog add <source_file>` - Add new source to catalog
- [ ] `solstein catalog validate` - Validate all catalog entries
- [ ] `solstein catalog stats` - Generate coverage statistics
- [ ] `solstein catalog export` - Export to JSON/YAML

**Implementation:**
```python
# src/solstein/cli/catalog_commands.py
@click.group()
def catalog():
    """Manage API source catalog."""
    pass

@catalog.command()
@click.option('--category', '-c', help='Filter by category')
@click.option('--relevance', '-r', help='Filter by Solstein relevance')
@click.option('--status', '-s', help='Filter by integration status')
def list(category, relevance, status):
    """List API sources in catalog."""
    ...

@catalog.command()
@click.argument('query')
def search(query):
    """Search catalog for API sources."""
    ...
```

---

### Story 49.4: Integration Decision Framework (5 pts)
**Task:** Document clear criteria for API integration decisions

**Acceptance Criteria:**
- [ ] Integration criteria document published
- [ ] Scoring rubric for API evaluation
- [ ] Decision matrix: effort vs. value
- [ ] Approval workflow documented
- [ ] Examples of accepted/rejected integrations

**Criteria Categories:**
1. **Data Value** (40% weight)
   - Relevance to competitive intelligence
   - Coverage (geography, sector, company stage)
   - Data quality and freshness
   - Uniqueness (not available elsewhere)

2. **Technical Fit** (30% weight)
   - API quality (documentation, stability)
   - Authentication complexity
   - Rate limits and scalability
   - Data format and normalization effort

3. **Business Viability** (20% weight)
   - Cost (free, affordable, expensive)
   - Terms of service compatibility
   - Provider stability and longevity
   - Support and community

4. **Maintenance Burden** (10% weight)
   - API stability and change frequency
   - Monitoring requirements
   - Error handling complexity

---

### Story 49.5: Catalog Automation & Sync (5 pts)
**Task:** Automate catalog updates from external sources

**Acceptance Criteria:**
- [ ] Importer for OpenClaw API list (filter relevant categories)
- [ ] Importer for GitHub API lists (public-apis, etc.)
- [ ] Scheduled sync job for catalog updates
- [ ] Duplicate detection and merging
- [ ] Change tracking (added, removed, modified APIs)

**Implementation:**
```python
# src/solstein/data_sources/importers/openclaw_importer.py
class OpenClawImporter:
    """Import and filter APIs from OpenClaw list."""
    
    RELEVANT_CATEGORIES = [
        'NEWS-APIS',
        'JOBS-APIS', 
        'SOCIAL-MEDIA-APIS',
        'LEAD-GENERATION-APIS',
        'SEO-TOOLS-APIS'
    ]
    
    async def import_catalog(self) -> list[APISource]:
        """Import relevant APIs from OpenClaw."""
        raw_apis = await self.fetch_openclaw_list()
        filtered = self.filter_by_category(raw_apis)
        scored = self.score_relevance(filtered)
        return [api for api in scored if api.solstein_relevance != 'low']
```

---

## Definition of Done

- [ ] API catalog schema defined and documented
- [ ] Catalog repository structure created with 50+ sources documented
- [ ] CLI tools for catalog management operational
- [ ] Integration decision framework published
- [ ] Automated import from OpenClaw (200-300 relevant APIs)
- [ ] Coverage metrics dashboard showing gaps
- [ ] Team trained on catalog usage and maintenance

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Catalog becomes stale | High | Medium | Automated sync, scheduled reviews |
| Too many low-quality sources | Medium | Medium | Strict relevance criteria |
| Maintenance overhead | Medium | Medium | Community contributions, automation |
| Schema changes break integrations | Low | High | Version schema, migration guides |

---

## Resources

- **Developers:** 1-2 backend engineers
- **Time:** 3 weeks
- **Dependencies:** None (foundational)

---

*Epic created from OpenClaw API list analysis*
