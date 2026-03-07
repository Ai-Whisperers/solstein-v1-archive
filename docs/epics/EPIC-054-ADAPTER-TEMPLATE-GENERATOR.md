# EPIC-054: API Adapter Template & Generator

|**Status:** 🔴 Not Started  
|**Priority:** MEDIUM (P2)  
|**Story Points:** 21  
|**Sprint Allocation:** 2 sprints  
|**Target Date:** Week 38-39

---

## Problem Statement

Creating new API adapters for Solstein requires repetitive boilerplate code. Each adapter needs to implement the same patterns: authentication, rate limiting, error handling, data normalization, and registration. This slows down API integration and increases inconsistency.

### Impact
- Slow API integration velocity
- Inconsistent adapter implementations
- Repeated boilerplate code
- Higher barrier for new contributors
- Maintenance overhead from varied patterns

---

## Success Criteria

1. ✅ Adapter template/generator tool operational
2. ✅ 80% reduction in boilerplate code for new adapters
3. ✅ Consistent patterns across all adapters
4. ✅ Auto-generated tests for new adapters
5. ✅ Documentation generation from adapter code
6. ✅ CLI tool for scaffolding new adapters

---

## Stories

### Story 54.1: Adapter Template System (8 pts)
**Task:** Create comprehensive adapter templates

**Acceptance Criteria:**
- [ ] Base adapter template with all required methods
- [ ] OpenAPI-based adapter template (for spec-compliant APIs)
- [ ] REST API adapter template (generic)
- [ ] GraphQL adapter template
- [ ] Scraper-based adapter template
- [ ] Template customization options

**Template Structure:**
```
src/solstein/templates/adapters/
├── base_adapter.py.j2           # Base template
├── openapi_adapter.py.j2        # OpenAPI-based
├── rest_adapter.py.j2           # Generic REST
├── graphql_adapter.py.j2        # GraphQL
├── scraper_adapter.py.j2        # Web scraper
└── config.yaml                  # Template configuration
```

**Base Adapter Template:**
```python
# templates/adapters/base_adapter.py.j2
"""{{ adapter_name }} adapter for Solstein.

Generated from template on {{ generation_date }}.
API: {{ api_name }}
Documentation: {{ api_docs_url }}
"""

from solstein.adapters.base import BaseDataSourceAdapter
from solstein.domain.models import DataSourceType, RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.research.discovery import DiscoveryCandidate


class {{ adapter_class_name }}(BaseDataSourceAdapter):
    """{{ api_description }}"""
    
    source_name = "{{ source_name }}"
    source_type = DataSourceType.{{ source_type }}
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "{{ default_base_url }}",
        rate_limit: int = {{ default_rate_limit }},
    ):
        self.api_key = api_key or settings.{{ api_key_setting }}
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.session = self._create_session()
    
    def _create_session(self):
        """Create configured HTTP session."""
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'Solstein/1.0',
        })
        return session
    
    # ------------------------------------------------------------------
    # Required Methods
    # ------------------------------------------------------------------
    
    async def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Discover companies using {{ api_name }}."""
        # TODO: Implement discovery logic
        return []
    
    async def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Enrich company data from {{ api_name }}."""
        # TODO: Implement enrichment logic
        
        raw_data = await self._fetch_company_data(company_name)
        normalized = self._normalize_data(raw_data)
        
        return RawDataSource(
            source_type=self.source_type,
            data=normalized,
            confidence=self.get_confidence(),
        )
    
    async def refresh(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict]:
        """Refresh data for companies."""
        # TODO: Implement refresh logic
        return []
    
    # ------------------------------------------------------------------
    # Quality Metadata
    # ------------------------------------------------------------------
    
    def get_confidence(self) -> float:
        """Return confidence score for this source."""
        return {{ default_confidence }}
    
    def get_authority(self) -> SourceAuthority:
        """Return authority level for conflict resolution."""
        return SourceAuthority.{{ default_authority }}
    
    def supports_incremental(self) -> bool:
        """Return True if incremental refresh is supported."""
        return {{ supports_incremental }}
    
    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------
    
    async def _fetch_company_data(self, company_name: str) -> dict:
        """Fetch raw data from API."""
        url = f"{self.base_url}/companies/search"
        params = {'q': company_name}
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    def _normalize_data(self, raw_data: dict) -> dict:
        """Normalize API response to Solstein schema."""
        return {
            'company_name': raw_data.get('name'),
            'website': raw_data.get('website'),
            'founded_year': raw_data.get('founded'),
            # TODO: Add more fields
        }
```

---

### Story 54.2: Adapter Generator CLI (8 pts)
**Task:** Build CLI tool for generating adapters from templates

**Acceptance Criteria:**
- [ ] `solstein generate adapter` command
- [ ] Interactive wizard for adapter configuration
- [ ] OpenAPI spec import and generation
- [ ] Auto-generation of adapter files
- [ ] Auto-registration in registry
- [ ] Test file generation

**CLI Interface:**
```bash
# Interactive wizard
$ solstein generate adapter
? Adapter name: my_api
? API provider: MyAPI Inc.
? API documentation URL: https://docs.myapi.com
? Authentication type: API Key
? Source type: ENRICHMENT
? Does API support discovery? Yes
? Confidence score (0-1): 0.8
Generating adapter...
✓ Created src/solstein/adapters/enrichment/my_api.py
✓ Created tests/unit/adapters/test_my_api.py
✓ Updated src/solstein/adapters/registry.py

# From OpenAPI spec
$ solstein generate adapter --openapi https://api.myapi.com/openapi.json
✓ Generated adapter from OpenAPI spec
✓ 15 endpoints mapped
✓ Authentication configured

# Non-interactive
$ solstein generate adapter \
    --name my_api \
    --provider "MyAPI Inc." \
    --type enrichment \
    --auth api_key
```

---

### Story 54.3: OpenAPI Import & Generation (5 pts)
**Task:** Generate adapters from OpenAPI specifications

**Acceptance Criteria:**
- [ ] OpenAPI spec parser
- [ ] Endpoint to adapter method mapping
- [ ] Schema to data model conversion
- [ ] Authentication scheme detection
- [ ] Rate limit extraction
- [ ] Documentation generation

---

## Definition of Done

- [ ] Adapter templates created (5+ types)
- [ ] CLI generator tool operational
- [ ] OpenAPI import functional
- [ ] Test generation working
- [ ] Documentation auto-generation
- [ ] 1+ adapter created using generator
- [ ] Team trained on generator usage

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Template rigidity | Medium | Medium | Customizable templates |
| Over-generation | Low | Low | Review process |
| Maintenance | Medium | Low | Version templates |

---

## Resources

- **Developers:** 1-2 backend engineers
- **Time:** 2 weeks
- **Dependencies:** EPIC-049 (catalog), existing adapter patterns

---

*Epic created from OpenClaw API list analysis - improves integration velocity*
