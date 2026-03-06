# Epic: API Documentation & OpenAPI Specification (EPIC-024)

## Overview
Create comprehensive, automated API documentation with OpenAPI 3.0 specification, interactive documentation portal, and client SDK generation. Transform the current 14-router, 2,779-line API layer into a well-documented, developer-friendly interface.

## Background
Current API documentation is fragmented:
- 14 router files with inconsistent documentation
- No standardized response schemas
- No OpenAPI specification
- Manual documentation prone to staleness
- No API versioning strategy
- Inconsistent error responses

## Goals
- [ ] Auto-generate OpenAPI 3.0 specification from code
- [ ] Interactive API documentation portal (Swagger UI)
- [ ] API versioning strategy (/api/v1/, /api/v2/)
- [ ] Client SDK generation (Python, TypeScript)
- [ ] Comprehensive endpoint documentation
- [ ] Standardized error response format

## Success Metrics
- [ ] 100% of endpoints documented
- [ ] OpenAPI spec validates without errors
- [ ] SDKs generated for 2+ languages
- [ ] API changelog maintained
- [ ] Developer satisfaction score >4/5

---

## Stories

### Story 1: OpenAPI Specification Generation
**Points:** 5
**Priority:** P0

Auto-generate OpenAPI 3.0 spec from FastAPI code.

**Tasks:**
- [ ] Audit all existing Pydantic models for OpenAPI compatibility
- [ ] Add `response_model` to all endpoints
- [ ] Add operation descriptions
- [ ] Add parameter documentation
- [ ] Generate OpenAPI JSON automatically
- [ ] Validate spec with openapi-generator

**Implementation:**
```python
from fastapi import APIRouter
from pydantic import BaseModel

class CompanyResponse(BaseModel):
    """Company information response."""
    id: str = Field(..., description="Unique company identifier")
    name: str = Field(..., description="Company name")
    revenue: float = Field(..., description="Annual revenue in millions")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "eneve",
                "name": "Eneve Energy",
                "revenue": 50.5
            }
        }

@router.get(
    "/companies/{company_id}",
    response_model=CompanyResponse,
    summary="Get company by ID",
    description="Retrieve detailed information about a specific company.",
    responses={
        404: {"description": "Company not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_company(company_id: str) -> CompanyResponse:
    """Get company details.
    
    Returns comprehensive information about the company including
    financials, scoring, and enrichment data.
    """
    return await company_service.get(company_id)
```

**Acceptance Criteria:**
- [ ] All endpoints have response models
- [ ] All parameters documented
- [ ] OpenAPI JSON generated at `/openapi.json`
- [ ] Spec passes validation

---

### Story 2: Interactive API Documentation Portal
**Points:** 5
**Priority:** P0

Deploy Swagger UI with custom branding.

**Tasks:**
- [ ] Configure FastAPI Swagger UI
- [ ] Custom branding (Solstein logo/colors)
- [ ] Add authentication to docs
- [ ] Organize endpoints by tag
- [ ] Add code examples

**Implementation:**
```python
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(
    title="Solstein API",
    description="AI-powered competitive intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Solstein API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico"
    )
```

**Features:**
- [ ] Try-it-now functionality
- [ ] Bearer token authentication
- [ ] Request/response examples
- [ ] Error code documentation

---

### Story 3: API Versioning Strategy
**Points:** 5
**Priority:** P0

Implement proper API versioning.

**Strategy:**
```
/api/v1/companies      # Current version
/api/v2/companies      # Future version with breaking changes
/api/companies         # Alias to latest (v1)
```

**Tasks:**
- [ ] Create versioned router structure
- [ ] Implement version negotiation
- [ ] Add deprecation headers
- [ ] Migration guide for consumers
- [ ] Version lifecycle policy

**Implementation:**
```python
from fastapi import APIRouter, Header

router_v1 = APIRouter(prefix="/api/v1")
router_v2 = APIRouter(prefix="/api/v2")

@router_v1.get("/companies")
async def list_companies_v1():
    """V1: Basic company list."""
    pass

@router_v2.get("/companies")
async def list_companies_v2(
    include_financials: bool = True,
    include_scores: bool = True
):
    """V2: Extended company list with optional fields."""
    pass
```

**Deprecation Policy:**
- Versions supported for 12 months
- Deprecation warnings 6 months before removal
- Migration guides provided

---

### Story 4: Standardize Error Responses
**Points:** 3
**Priority:** P0

Create consistent error response format.

**Current Issue:**
Different error formats across endpoints.

**Standard Error Format:**
```json
{
  "error": {
    "code": "COMPANY_NOT_FOUND",
    "message": "Company with ID 'xyz' not found",
    "details": {
      "company_id": "xyz",
      "suggestion": "Try searching by name"
    },
    "timestamp": "2026-03-06T12:00:00Z",
    "request_id": "req_12345"
  }
}
```

**Tasks:**
- [ ] Create error response schema
- [ ] Implement error handler middleware
- [ ] Add error codes enum
- [ ] Update all endpoints
- [ ] Document all error codes

**Implementation:**
```python
class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: ErrorDetail

class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict = Field(default={}, description="Additional error details")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    request_id: str = Field(..., description="Unique request identifier")

# Error codes enum
class ErrorCode(str, Enum):
    COMPANY_NOT_FOUND = "COMPANY_NOT_FOUND"
    INVALID_PARAMETERS = "INVALID_PARAMETERS"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    # ... etc
```

---

### Story 5: Client SDK Generation
**Points:** 8
**Priority:** P1

Generate client SDKs from OpenAPI spec.

**Target Languages:**
- Python (primary)
- TypeScript/JavaScript (secondary)

**Tools:**
- `openapi-generator-cli` for SDK generation
- GitHub Actions for automated generation

**Tasks:**
- [ ] Set up openapi-generator
- [ ] Create Python SDK
- [ ] Create TypeScript SDK
- [ ] Add SDK tests
- [ ] Publish to package repositories
- [ ] SDK documentation

**Python SDK Example:**
```python
# Generated SDK usage
from solstein_api import SolsteinClient

client = SolsteinClient(api_key="your_key")
company = client.companies.get("eneve")
print(company.name)  # "Eneve Energy"

# Async support
companies = await client.companies.list_async()
```

**TypeScript SDK Example:**
```typescript
// Generated SDK usage
import { SolsteinClient } from '@solstein/api';

const client = new SolsteinClient({ apiKey: 'your_key' });
const company = await client.companies.get('eneve');
console.log(company.name);  // "Eneve Energy"
```

**CI/CD Integration:**
```yaml
- name: Generate SDKs
  run: |
    openapi-generator-cli generate \
      -i openapi.json \
      -g python \
      -o sdks/python
    openapi-generator-cli generate \
      -i openapi.json \
      -g typescript-fetch \
      -o sdks/typescript
```

---

### Story 6: API Changelog & Communication
**Points:** 3
**Priority:** P1

Maintain API changelog and developer communication.

**Tasks:**
- [ ] Create `API_CHANGELOG.md`
- [ ] Set up API status page
- [ ] Create developer newsletter
- [ ] Add breaking change notifications
- [ ] API usage analytics

**Changelog Format:**
```markdown
# API Changelog

## v1.2.0 (2026-03-06)
### Added
- New endpoint: POST /api/v1/companies/batch
- New field: `company.ai_maturity_score`

### Changed
- Deprecated: GET /api/v1/companies/legacy (use /companies instead)

### Fixed
- Fixed pagination in /companies endpoint

## v1.1.0 (2026-02-15)
...
```

---

### Story 7: Endpoint Organization & Tagging
**Points:** 3
**Priority:** P1

Reorganize 14 routers into logical groups.

**Current:** 14 router files with mixed concerns

**Target Organization:**
```
api/v1/
├── companies/          # Company CRUD
├── research/           # Research pipeline
├── scoring/            # Scoring operations
├── enrichment/         # Data enrichment
├── export/             # Export functionality
├── market/             # Market analysis
├── auth/               # Authentication
├── health/             # Health checks
└── admin/              # Admin operations
```

**Tags for Swagger:**
- Companies
- Research
- Scoring
- Enrichment
- Export
- Market Intelligence
- Authentication
- Admin

---

### Story 8: Developer Onboarding Guide
**Points:** 3
**Priority:** P2

Create comprehensive developer documentation.

**Documentation Sections:**
1. **Getting Started**
   - API key registration
   - First API call
   - SDK installation

2. **Authentication**
   - API key usage
   - Token refresh
   - Rate limits

3. **Core Concepts**
   - Company model
   - Scoring system
   - Enrichment pipeline

4. **Best Practices**
   - Error handling
   - Pagination
   - Caching

5. **Tutorials**
   - Build a company dashboard
   - Automated scoring
   - Export reports

6. **FAQ**
   - Common issues
   - Troubleshooting

---

## Technical Implementation

### FastAPI Configuration
```python
app = FastAPI(
    title="Solstein API",
    description="""
    AI-powered competitive intelligence platform for energy markets.
    
    ## Features
    * Company research and enrichment
    * Automated scoring and classification
    * Market analysis and simulation
    * Export capabilities (PDF, Excel, Markdown)
    
    ## Authentication
    All API requests require an API key passed in the header:
    `Authorization: Bearer YOUR_API_KEY`
    """,
    version="1.0.0",
    terms_of_service="https://solstein.ai/terms",
    contact={
        "name": "Solstein Support",
        "url": "https://solstein.ai/support",
        "email": "api@solstein.ai"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)
```

### Directory Structure
```
docs/api/
├── openapi.json          # Generated spec
├── openapi.yaml          # Generated spec
├── CHANGELOG.md          # API changes
├── MIGRATION.md          # Migration guides
├── postman/              # Postman collection
└── sdks/                 # Generated SDKs
    ├── python/
    └── typescript/
```

---

## Deliverables

1. **OpenAPI 3.0 Specification** (`/openapi.json`)
2. **Interactive Documentation** (`/docs`)
3. **Python SDK** (`pip install solstein-api`)
4. **TypeScript SDK** (`npm install @solstein/api`)
5. **API Changelog** (`API_CHANGELOG.md`)
6. **Developer Guide** (`docs/developers/`)

---

## Definition of Done
- [ ] 100% endpoints documented
- [ ] OpenAPI spec validates
- [ ] SDKs published to registries
- [ ] Interactive docs deployed
- [ ] Developer guide complete
- [ ] Team trained

## Estimated Effort
- **Total Points:** 37
- **Duration:** 6-8 weeks
- **Team:** 1 developer

## Dependencies
- EPIC-019 (Code quality) - Clean code first
- EPIC-023 (Performance) - Document performance characteristics

---

*Created: 2026-03-06*  
*Target Release: Q3 2026*
