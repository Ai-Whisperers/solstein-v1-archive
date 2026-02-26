"""Enrichment service layer with database integration (Phase 11).

Provides high-level enrichment operations that interact with database.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.data.unified_loader import unified_loader, UnifiedCompany
from solstein.infrastructure.enrichment_repositories import (
    EnrichmentAuditRepository,
    EnrichmentCacheRepository,
)


class EnrichmentService:
    """Service for enrichment operations with database persistence."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.audit_repo = EnrichmentAuditRepository(session)
        self.cache_repo = EnrichmentCacheRepository(session)
    
    async def enrich_company(
        self,
        company_id: str,
        company_name: Optional[str] = None,
        sources: Optional[List[str]] = None,
        use_cache: bool = True,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enrich a single company with caching and audit logging."""
        start_time = datetime.now(timezone.utc)
        sources = sources or ["SEC_EDGAR"]
        
        # Check cache
        if use_cache:
            cached = await self.cache_repo.get_cached(company_id)
            if cached:
                # Log cache hit
                await self.audit_repo.log_operation(
                    company_id=company_id,
                    company_name=company_name,
                    operation="cache_hit",
                    source=",".join(sources),
                    status="SUCCESS",
                    user_id=user_id,
                    client_id=client_id,
                )
                return {
                    "company_id": company_id,
                    "company_name": company_name,
                    "enriched_data": cached.enriched_data,
                    "sources_used": cached.sources_used or sources,
                    "fields_enriched": cached.fields_enriched or [],
                    "from_cache": True,
                }
        
        # Perform enrichment
        try:
            # Log start
            await self.audit_repo.log_operation(
                company_id=company_id,
                company_name=company_name,
                operation="enrich_start",
                source=",".join(sources),
                status="IN_PROGRESS",
                user_id=user_id,
                client_id=client_id,
            )
            
            # Create company object
            company = UnifiedCompany(id=company_id, name=company_name or company_id)
            
            # Enrich
            enriched = unified_loader.enrich_from_connectors(company)
            
            # Track fields enriched
            fields_enriched = []
            if enriched.financials and enriched.financials.revenue:
                fields_enriched.append("revenue")
            if enriched.financials and enriched.financials.employees:
                fields_enriched.append("employees")
            if enriched.financials and enriched.financials.growth_rate:
                fields_enriched.append("growth_rate")
            
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            # Log success
            await self.audit_repo.log_operation(
                company_id=company_id,
                company_name=enriched.name or company_name or company_id,
                operation="enrich_success",
                source=",".join(sources),
                status="SUCCESS",
                duration_ms=duration_ms,
                fields_enriched=fields_enriched,
                user_id=user_id,
                client_id=client_id,
            )
            
            # Cache result
            enriched_dict = {
                "id": enriched.id,
                "name": enriched.name,
                "revenue": enriched.financials.revenue if enriched.financials else None,
                "employees": enriched.financials.employees if enriched.financials else None,
                "growth_rate": enriched.financials.growth_rate if enriched.financials else None,
                "profit_margin": enriched.financials.profit_margin if enriched.financials else None,
                "funding_raised": enriched.financials.funding_raised if enriched.financials else None,
                "valuation": enriched.financials.valuation if enriched.financials else None,
            }
            
            if use_cache and fields_enriched:
                await self.cache_repo.cache_enrichment(
                    company_id=company_id,
                    enriched_data=enriched_dict,
                    sources_used=sources,
                    fields_enriched=fields_enriched,
                )
            
            # Commit changes
            await self.session.commit()
            
            return {
                "company_id": company_id,
                "company_name": enriched.name or company_name,
                "enriched_data": enriched_dict,
                "sources_used": sources,
                "fields_enriched": fields_enriched,
                "duration_ms": duration_ms,
                "from_cache": False,
            }
        
        except Exception as e:
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            # Log failure
            await self.audit_repo.log_operation(
                company_id=company_id,
                company_name=company_name,
                operation="enrich_failure",
                source=",".join(sources),
                status="FAILURE",
                duration_ms=duration_ms,
                error_message=str(e),
                user_id=user_id,
                client_id=client_id,
            )
            
            await self.session.commit()
            raise
    
    async def get_audit_trail(
        self,
        company_id: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Get audit trail for a company."""
        entries = await self.audit_repo.get_audit_trail(company_id=company_id, limit=limit)
        stats = await self.audit_repo.get_company_stats(company_id) if company_id else {}
        
        return {
            "entries": [e.to_dict() for e in entries],
            "stats": stats,
        }
    
    async def clear_cache(self, company_id: Optional[str] = None) -> Dict[str, Any]:
        """Clear cache entries."""
        deleted_count = await self.cache_repo.delete_cache(company_id=company_id)
        cache_stats = await self.cache_repo.get_cache_stats()
        
        await self.session.commit()
        
        return {
            "deleted_count": deleted_count,
            "cache_stats": cache_stats,
        }
