"""Multi-tenant configuration and data models.

EPIC-030 Story 1: Tenant data model with settings and limits.

Usage:
    from solstein.tenant.models import Tenant, TenantConfig

    tenant = Tenant(name="Acme Corp", plan="professional")
    config = TenantConfig(tenant_id=tenant.id)
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TenantPlan(str, Enum):
    """Tenant subscription plans."""

    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TenantStatus(str, Enum):
    """Tenant account status."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    CANCELLED = "cancelled"


class Tenant(BaseModel):
    """Tenant model representing an organization.

    Attributes:
        id: Unique tenant identifier (UUID)
        name: Organization name
        plan: Subscription plan
        status: Account status
        created_at: Creation timestamp
        settings: Tenant-specific settings
        api_key_hash: Hashed API key for authentication
        stripe_customer_id: Stripe customer ID for billing
    """

    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    name: str
    plan: TenantPlan = TenantPlan.STARTER
    status: TenantStatus = TenantStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    settings: dict[str, Any] = Field(default_factory=dict)
    api_key_hash: Optional[str] = None
    stripe_customer_id: Optional[str] = None

    class Config:
        use_enum_values = True


class TenantLimits(BaseModel):
    """Resource limits for a tenant.

    Attributes:
        max_companies: Maximum companies allowed
        max_api_calls_per_day: Daily API call limit
        max_reports_per_month: Monthly report generation limit
        max_users: Maximum team members
        max_storage_gb: Storage limit in GB
    """

    max_companies: int = 1000
    max_api_calls_per_day: int = 10000
    max_reports_per_month: int = 100
    max_users: int = 10
    max_storage_gb: float = 10.0


class TenantFeatures(BaseModel):
    """Feature flags per tenant.

    Attributes:
        ai_enrichment: Enable AI data enrichment
        advanced_scoring: Enable advanced scoring algorithms
        api_access: Enable API access
        custom_branding: Allow custom branding
        webhooks: Enable webhook integrations
        sso: Enable SSO authentication
    """

    ai_enrichment: bool = True
    advanced_scoring: bool = False
    api_access: bool = True
    custom_branding: bool = False
    webhooks: bool = False
    sso: bool = False


class TenantConfig(BaseModel):
    """Complete tenant configuration.

    Combines limits, features, and custom settings.
    """

    tenant_id: str
    limits: TenantLimits = Field(default_factory=TenantLimits)
    features: TenantFeatures = Field(default_factory=TenantFeatures)

    # Customization
    custom_fields: list[dict[str, Any]] = Field(default_factory=list)
    scoring_weights: dict[str, float] = Field(default_factory=dict)

    # Branding
    logo_url: Optional[str] = None
    primary_color: str = "#1976d2"

    # Integrations
    enabled_integrations: list[str] = Field(default_factory=list)
    integration_configs: dict[str, Any] = Field(default_factory=dict)

    # Default settings
    default_market: str = "global"
    allowed_export_formats: list[str] = Field(default_factory=lambda: ["pdf", "excel", "csv"])

    class Config:
        use_enum_values = True


# Default configurations per plan
DEFAULT_TENANT_CONFIGS = {
    TenantPlan.STARTER: {
        "limits": {
            "max_companies": 100,
            "max_api_calls_per_day": 1000,
            "max_reports_per_month": 10,
            "max_users": 3,
            "max_storage_gb": 1.0,
        },
        "features": {
            "ai_enrichment": True,
            "advanced_scoring": False,
            "api_access": True,
            "custom_branding": False,
            "webhooks": False,
            "sso": False,
        },
    },
    TenantPlan.PROFESSIONAL: {
        "limits": {
            "max_companies": 1000,
            "max_api_calls_per_day": 10000,
            "max_reports_per_month": 100,
            "max_users": 10,
            "max_storage_gb": 10.0,
        },
        "features": {
            "ai_enrichment": True,
            "advanced_scoring": True,
            "api_access": True,
            "custom_branding": True,
            "webhooks": True,
            "sso": False,
        },
    },
    TenantPlan.ENTERPRISE: {
        "limits": {
            "max_companies": 999999,  # Effectively unlimited
            "max_api_calls_per_day": 999999,
            "max_reports_per_month": 999999,
            "max_users": 999999,
            "max_storage_gb": 999999.0,
        },
        "features": {
            "ai_enrichment": True,
            "advanced_scoring": True,
            "api_access": True,
            "custom_branding": True,
            "webhooks": True,
            "sso": True,
        },
    },
}


def get_default_config(plan: TenantPlan) -> dict[str, Any]:
    """Get default configuration for a plan.

    Args:
        plan: Tenant subscription plan.

    Returns:
        Default configuration dictionary.
    """
    return DEFAULT_TENANT_CONFIGS.get(plan, DEFAULT_TENANT_CONFIGS[TenantPlan.STARTER])


class TenantUser(BaseModel):
    """User within a tenant.

    Attributes:
        id: User identifier
        tenant_id: Associated tenant
        email: User email
        role: User role within tenant
        created_at: Creation timestamp
        last_login: Last login timestamp
    """

    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    tenant_id: str
    email: str
    role: str = "member"  # admin, member, viewer
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    mfa_enabled: bool = False


class TenantUsage(BaseModel):
    """Tenant usage metrics for billing.

    Attributes:
        tenant_id: Tenant identifier
        date: Date of metrics
        api_calls: Number of API calls
        reports_generated: Number of reports
        storage_gb: Storage used in GB
        companies_tracked: Number of companies
    """

    tenant_id: str
    date: str  # YYYY-MM-DD
    api_calls: int = 0
    reports_generated: int = 0
    storage_gb: float = 0.0
    companies_tracked: int = 0
