# Epic: Multi-Tenancy Implementation (EPIC-030)

## Overview
Complete multi-tenancy implementation ensuring strict data isolation between tenants while enabling efficient resource sharing. Support tenant-specific configurations, customizations, and billing.

## Background
Current tenant support:
- Tenant middleware exists (`api/middleware/tenant.py`)
- Database schema supports tenant_id
- Basic tenant isolation in place
- No tenant onboarding automation
- No per-tenant customization
- Cross-tenant analytics limited

## Goals
- [ ] Strict data isolation (no cross-tenant data leakage)
- [ ] Automated tenant onboarding
- [ ] Per-tenant configuration
- [ ] Tenant-specific feature flags
- [ ] Cross-tenant analytics (admin only)
- [ ] Tenant billing/metering

## Success Metrics
| Metric | Target |
|--------|--------|
| Data Isolation | 100% (verified) |
| Tenant Onboarding | <5 minutes |
| Tenant Customization | 10+ settings |
| Admin Analytics | Real-time |

---

## Stories

### Story 1: Data Isolation Verification
**Points:** 5
**Priority:** P0

Verify complete data isolation between tenants.

**Testing Approach:**
```python
# tests/security/test_tenant_isolation.py

async def test_no_cross_tenant_data_access():
    """Ensure tenants cannot access each other's data."""
    tenant_a = await create_tenant("tenant-a")
    tenant_b = await create_tenant("tenant-b")
    
    # Create company for tenant A
    company_a = await create_company(tenant_id=tenant_a.id)
    
    # Tenant B should not see it
    async with tenant_context(tenant_b):
        companies = await get_companies()
        assert company_a.id not in [c.id for c in companies]

async def test_database_row_level_security():
    """Verify RLS policies work correctly."""
    # Direct DB query should respect tenant
    result = await db.fetch(
        "SELECT * FROM companies WHERE tenant_id = 'tenant-a'",
        tenant_id='tenant-b'  # Should be ignored/rejected
    )
    assert len(result) == 0
```

**Security Audit:**
- [ ] All queries include tenant filter
- [ ] No global queries without tenant_id
- [ ] Admin endpoints properly protected
- [ ] Database RLS policies enabled
- [ ] API endpoints validate tenant access

**Verification Checklist:**
```markdown
## Tenant Isolation Checklist

### Database Level
- [ ] All tables have tenant_id column
- [ ] Foreign keys include tenant_id
- [ ] RLS policies enabled
- [ ] Indexes on tenant_id columns

### Application Level
- [ ] All repository methods filter by tenant
- [ ] No raw SQL without tenant filter
- [ ] Caching keys include tenant_id
- [ ] Background jobs include tenant context

### API Level
- [ ] All endpoints extract tenant from header/API key
- [ ] Tenant validation on every request
- [ ] No tenant_id in request body (extracted from auth)
```

---

### Story 2: Automated Tenant Onboarding
**Points:** 5
**Priority:** P0

Streamline new tenant creation.

**Onboarding Flow:**
```python
# POST /api/v1/admin/tenants
async def create_tenant(request: TenantCreateRequest):
    """
    1. Validate tenant name (unique)
    2. Create tenant record
    3. Create default admin user
    4. Initialize database schema
    5. Create default settings
    6. Send welcome email
    """
    tenant = await tenant_service.create(
        name=request.name,
        plan=request.plan
    )
    
    # Create admin user
    admin = await user_service.create(
        tenant_id=tenant.id,
        email=request.admin_email,
        role=Role.ADMIN
    )
    
    # Initialize tenant data
    await initialize_tenant_data(tenant.id)
    
    # Send welcome email with API key
    await send_welcome_email(admin)
    
    return TenantResponse(tenant=tenant, admin=admin)
```

**Self-Service Onboarding Portal:**
```
/signup
  ├── Enter company details
  ├── Choose plan
  ├── Payment (if applicable)
  ├── Create admin account
  └── Receive API credentials
```

**Tenant Configuration Defaults:**
```python
DEFAULT_TENANT_CONFIG = {
    "max_companies": 1000,
    "max_api_calls_per_day": 10000,
    "max_reports_per_month": 100,
    "allowed_export_formats": ["pdf", "excel", "csv"],
    "default_market": "global",
    "features": {
        "ai_enrichment": True,
        "advanced_scoring": False,
        "api_access": True,
    }
}
```

---

### Story 3: Per-Tenant Configuration
**Points:** 5
**Priority:** P0

Allow tenant-specific settings.

**Configuration Store:**
```python
class TenantConfig(BaseModel):
    tenant_id: str
    
    # Limits
    max_companies: int = 1000
    max_api_calls_per_day: int = 10000
    
    # Features
    features: dict[str, bool] = {
        "ai_enrichment": True,
        "advanced_scoring": False,
        "custom_branding": False,
    }
    
    # Customization
    custom_fields: list[dict] = []
    scoring_weights: dict[str, float] = {}
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: str = "#1976d2"
    
    # Integrations
    enabled_integrations: list[str] = []
    integration_configs: dict = {}
```

**Feature Flags per Tenant:**
```python
async def can_use_feature(tenant_id: str, feature: str) -> bool:
    config = await get_tenant_config(tenant_id)
    return config.features.get(feature, False)

# Usage
if await can_use_feature(current_tenant.id, "advanced_scoring"):
    score = await calculate_advanced_score(company)
else:
    score = await calculate_basic_score(company)
```

**Tenant Override Example:**
```python
# Tenant A: Energy focus
tenant_a_config = {
    "default_market": "energy",
    "scoring_weights": {
        "sustainability": 0.3,  # Higher weight
        "financial_health": 0.2
    }
}

# Tenant B: Tech focus
tenant_b_config = {
    "default_market": "technology",
    "scoring_weights": {
        "innovation": 0.3,
        "growth_rate": 0.25
    }
}
```

---

### Story 4: Tenant Admin Portal
**Points:** 8
**Priority:** P1

Web UI for tenant administration.

**Features:**
- [ ] Usage dashboard
- [ ] User management
- [ ] API key management
- [ ] Billing information
- [ ] Configuration settings
- [ ] Audit logs

**Dashboard Widgets:**
```
┌─────────────────────────────────────┐
│  Usage This Month                   │
│  API Calls: 5,234 / 10,000 (52%)   │
│  Companies: 45 / 100 (45%)          │
│  Reports: 12 / 100 (12%)            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Recent Activity                    │
│  • User john@example.com logged in │
│  • Generated report for Shell       │
│  • API key rotated                  │
└─────────────────────────────────────┘
```

**User Management:**
```python
@router.post("/admin/users")
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(require_admin)
):
    """Create new user in tenant."""
    return await user_service.create(
        tenant_id=current_user.tenant_id,
        email=request.email,
        role=request.role
    )
```

---

### Story 5: Cross-Tenant Analytics (Admin)
**Points:** 5
**Priority:** P1

Platform-wide analytics for admin users.

**Aggregated Metrics:**
```python
# Only accessible by platform admins
@router.get("/admin/analytics/usage")
@require_role(Role.PLATFORM_ADMIN)
async def get_platform_analytics():
    return {
        "total_tenants": await count_tenants(),
        "active_tenants_last_30d": await count_active_tenants(days=30),
        "total_companies": await count_companies(),
        "total_api_calls_today": await count_api_calls(since="today"),
        "revenue_this_month": await calculate_revenue(),
        "top_tenants_by_usage": await get_top_tenants(limit=10),
        "tenant_growth": await get_tenant_growth_over_time(),
    }
```

**Privacy Protection:**
```python
# Never expose tenant-specific data
# Aggregate only

# ✅ GOOD: Aggregate metrics
{
    "total_companies": 15000,
    "average_companies_per_tenant": 150
}

# ❌ BAD: Individual tenant data (privacy violation)
{
    "tenants": [
        {"name": "Shell", "company_count": 500},  # Exposes customer data!
        {"name": "BP", "company_count": 300}
    ]
}
```

---

### Story 6: Tenant Billing & Metering
**Points:** 8
**Priority:** P1

Track and bill tenant usage.

**Metering:**
```python
class UsageMeter:
    async def record_api_call(self, tenant_id: str, endpoint: str):
        await redis.incr(f"usage:{tenant_id}:api_calls:{today()}")
        await redis.expire(f"usage:{tenant_id}:api_calls:{today()}", 86400 * 30)
    
    async def record_report_generated(self, tenant_id: str, format: str):
        await redis.incr(f"usage:{tenant_id}:reports:{today()}")
    
    async def get_usage(self, tenant_id: str, month: str) -> UsageReport:
        return UsageReport(
            api_calls=await get_daily_usage(tenant_id, "api_calls", month),
            reports_generated=await get_daily_usage(tenant_id, "reports", month),
            storage_gb=await calculate_storage(tenant_id),
        )
```

**Pricing Tiers:**
```python
PLANS = {
    "starter": {
        "price": 99,
        "limits": {
            "companies": 100,
            "api_calls_per_day": 1000,
            "reports_per_month": 10,
        }
    },
    "professional": {
        "price": 499,
        "limits": {
            "companies": 1000,
            "api_calls_per_day": 10000,
            "reports_per_month": 100,
        }
    },
    "enterprise": {
        "price": None,  # Custom
        "limits": {
            "companies": float('inf'),
            "api_calls_per_day": float('inf'),
            "reports_per_month": float('inf'),
        }
    }
}
```

**Billing Integration:**
```python
# Stripe integration
async def charge_tenant(tenant_id: str, amount: Decimal):
    tenant = await get_tenant(tenant_id)
    
    await stripe.charges.create(
        amount=int(amount * 100),  # Convert to cents
        currency="usd",
        customer=tenant.stripe_customer_id,
        description=f"Solstein usage - {datetime.now().strftime('%Y-%m')}"
    )
```

---

### Story 7: Tenant Data Export/Import
**Points:** 5
**Priority:** P2

Allow tenants to export/import their data.

**GDPR Compliance:**
```python
@router.post("/gdpr/export")
async def export_tenant_data(
    current_user: User = Depends(get_current_user)
):
    """Export all tenant data (GDPR Article 15)."""
    tenant_id = current_user.tenant_id
    
    data = {
        "companies": await get_companies(tenant_id),
        "scoring_history": await get_scoring_history(tenant_id),
        "reports": await get_reports(tenant_id),
        "users": await get_users(tenant_id),
        "api_usage": await get_api_usage(tenant_id),
    }
    
    return create_export_archive(data)

@router.delete("/gdpr/delete")
async def delete_tenant_data(
    current_user: User = Depends(require_admin)
):
    """Delete all tenant data (GDPR Article 17)."""
    tenant_id = current_user.tenant_id
    
    # Soft delete with 30-day grace period
    await soft_delete_tenant(tenant_id)
    
    # Schedule permanent deletion
    await schedule_deletion(tenant_id, days=30)
```

**Migration Support:**
```python
# Export from tenant A, import to tenant B
async def migrate_tenant_data(source_tenant_id: str, target_tenant_id: str):
    data = await export_tenant_data(source_tenant_id)
    await import_tenant_data(target_tenant_id, data)
```

---

### Story 8: Tenant Health Monitoring
**Points:** 3
**Priority:** P2

Monitor tenant-specific health metrics.

**Per-Tenant Metrics:**
```python
TENANT_METRICS = {
    "api_requests_per_minute",
    "error_rate",
    "average_response_time",
    "active_users",
    "data_quality_score",
}
```

**Tenant Health Dashboard:**
```
┌─────────────────────────────────────┐
│  Tenant Health Overview             │
├─────────────────────────────────────┤
│  🟢 Acme Corp    - Healthy          │
│  🟢 Shell        - Healthy          │
│  🟡 BP          - High API errors   │
│  🔴 Exxon       - Rate limited      │
└─────────────────────────────────────┘
```

---

## Technical Implementation

### Database Schema
```sql
-- Tenant table
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    plan VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    settings JSONB DEFAULT '{}'
);

-- All tables have tenant_id
CREATE TABLE companies (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(255),
    -- ... other fields
);

-- Row Level Security
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON companies
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

### Middleware
```python
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    # Extract tenant from API key or JWT
    tenant_id = extract_tenant_id(request)
    
    # Set tenant context
    request.state.tenant_id = tenant_id
    
    # Set DB RLS variable
    await db.execute("SET app.current_tenant = :tenant_id", {"tenant_id": tenant_id})
    
    response = await call_next(request)
    return response
```

---

## Definition of Done
- [ ] 100% data isolation verified
- [ ] Tenant onboarding <5 minutes
- [ ] Per-tenant configuration working
- [ ] Admin analytics operational
- [ ] Billing system functional
- [ ] GDPR compliance verified

## Estimated Effort
- **Total Points:** 44
- **Duration:** 7-9 weeks
- **Team:** 1 senior developer

## Dependencies
- EPIC-016 (Security) - Authentication foundation
- EPIC-027 (Security Hardening) - Security audit

---

*Created: 2026-03-06*  
*Target Release: Q4 2026*
