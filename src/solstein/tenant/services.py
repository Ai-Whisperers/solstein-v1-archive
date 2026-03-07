"""Tenant-aware services and business logic.

EPIC-030 Story 3: Services that respect tenant boundaries.

Usage:
    from solstein.tenant.services import TenantCompanyService

    service = TenantCompanyService(session)
    companies = await service.get_companies()  # Only returns tenant's companies
"""

from typing import Any, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from loguru import logger

from solstein.tenant.context import TenantAwareRepository, require_tenant, get_current_tenant
from solstein.tenant.models import TenantConfig, TenantLimits, TenantFeatures
from solstein.infrastructure.database_models import CompanyRecord


class TenantCompanyService:
    """Company service with automatic tenant filtering."""

    def __init__(self, session: AsyncSession, tenant_id: Optional[str] = None):
        """Initialize service.

        Args:
            session: Database session.
            tenant_id: Optional tenant ID override.
        """
        self.session = session
        self.tenant_id = tenant_id or require_tenant()

    async def get_companies(self, limit: int = 100, offset: int = 0) -> List[CompanyRecord]:
        """Get companies for current tenant.

        Args:
            limit: Maximum results.
            offset: Pagination offset.

        Returns:
            List of company records.
        """
        query = select(CompanyRecord).where(CompanyRecord.tenant_id == self.tenant_id).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_company(self, company_id: str) -> Optional[CompanyRecord]:
        """Get single company if it belongs to tenant.

        Args:
            company_id: Company ID.

        Returns:
            Company record or None.
        """
        query = (
            select(CompanyRecord)
            .where(CompanyRecord.company_id == company_id)
            .where(CompanyRecord.tenant_id == self.tenant_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_company(self, **kwargs) -> CompanyRecord:
        """Create company for current tenant.

        Args:
            **kwargs: Company fields.

        Returns:
            Created company record.
        """
        company = CompanyRecord(tenant_id=self.tenant_id, **kwargs)
        self.session.add(company)
        await self.session.flush()
        logger.info(f"Created company for tenant {self.tenant_id[:8]}...")
        return company

    async def delete_company(self, company_id: str) -> bool:
        """Delete company if it belongs to tenant.

        Args:
            company_id: Company ID.

        Returns:
            True if deleted.
        """
        company = await self.get_company(company_id)
        if company:
            await self.session.delete(company)
            logger.info(f"Deleted company {company_id} for tenant {self.tenant_id[:8]}...")
            return True
        return False


class TenantConfigService:
    """Manage tenant configuration."""

    def __init__(self, session: AsyncSession):
        """Initialize service.

        Args:
            session: Database session.
        """
        self.session = session

    async def get_config(self, tenant_id: str) -> TenantConfig:
        """Get tenant configuration.

        Args:
            tenant_id: Tenant ID.

        Returns:
            Tenant configuration.
        """
        # In production, fetch from database
        # For now, return default config
        from solstein.tenant.models import get_default_config, TenantPlan

        defaults = get_default_config(TenantPlan.STARTER)
        return TenantConfig(
            tenant_id=tenant_id,
            limits=TenantLimits(**defaults["limits"]),
            features=TenantFeatures(**defaults["features"]),
        )

    async def update_config(self, tenant_id: str, updates: dict[str, Any]) -> TenantConfig:
        """Update tenant configuration.

        Args:
            tenant_id: Tenant ID.
            updates: Configuration updates.

        Returns:
            Updated configuration.
        """
        # In production, persist to database
        config = await self.get_config(tenant_id)

        # Apply updates
        if "limits" in updates:
            for key, value in updates["limits"].items():
                setattr(config.limits, key, value)

        if "features" in updates:
            for key, value in updates["features"].items():
                setattr(config.features, key, value)

        logger.info(f"Updated config for tenant {tenant_id[:8]}...")
        return config

    async def can_use_feature(self, tenant_id: str, feature: str) -> bool:
        """Check if tenant can use a feature.

        Args:
            tenant_id: Tenant ID.
            feature: Feature name.

        Returns:
            True if feature enabled.
        """
        config = await self.get_config(tenant_id)
        return getattr(config.features, feature, False)


class TenantEnrichmentService:
    """Enrichment service with tenant quotas."""

    def __init__(self, session: AsyncSession, tenant_id: Optional[str] = None):
        """Initialize service.

        Args:
            session: Database session.
            tenant_id: Optional tenant ID.
        """
        self.session = session
        self.tenant_id = tenant_id or require_tenant()
        self.config_service = TenantConfigService(session)

    async def enrich_company(self, company_id: str) -> dict[str, Any]:
        """Enrich company data.

        Args:
            company_id: Company ID.

        Returns:
            Enrichment results.

        Raises:
            ValueError: If enrichment not enabled for tenant.
        """
        # Check feature enabled
        if not await self.config_service.can_use_feature(self.tenant_id, "ai_enrichment"):
            raise ValueError("AI enrichment not enabled for this tenant")

        # Check company belongs to tenant
        query = (
            select(CompanyRecord)
            .where(CompanyRecord.company_id == company_id)
            .where(CompanyRecord.tenant_id == self.tenant_id)
        )
        result = await self.session.execute(query)
        company = result.scalar_one_or_none()

        if not company:
            raise ValueError(f"Company {company_id} not found or access denied")

        # Perform enrichment
        logger.info(f"Enriching company {company_id} for tenant {self.tenant_id[:8]}...")

        # Return mock enrichment for now
        return {
            "company_id": company_id,
            "enriched": True,
            "tenant_id": self.tenant_id,
        }


class TenantExportService:
    """Export service with tenant isolation."""

    def __init__(self, session: AsyncSession, tenant_id: Optional[str] = None):
        """Initialize service.

        Args:
            session: Database session.
            tenant_id: Optional tenant ID.
        """
        self.session = session
        self.tenant_id = tenant_id or require_tenant()
        self.company_service = TenantCompanyService(session, self.tenant_id)

    async def export_companies(self, format: str = "excel") -> bytes:
        """Export tenant's companies.

        Args:
            format: Export format (excel, csv, pdf).

        Returns:
            Export data as bytes.
        """
        companies = await self.company_service.get_companies(limit=10000)

        logger.info(f"Exporting {len(companies)} companies for tenant {self.tenant_id[:8]}...")

        # In production, use actual export logic
        # For now, return empty bytes
        return b"mock export data"
