"""Database repositories for enrichment operations (Phase 11).

Provides data access layer for enrichment audit trail and cache.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from .database_models import EnrichmentAuditRecord, EnrichmentCacheRecord


class EnrichmentAuditRepository:
    """Repository for enrichment audit trail operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_operation(
        self,
        company_id: str,
        company_name: str | None,
        operation: str,
        source: str | None,
        status: str,
        duration_ms: float | None = None,
        fields_enriched: list[str] | None = None,
        error_message: str | None = None,
        user_id: str | None = None,
        client_id: str | None = None,
    ) -> EnrichmentAuditRecord:
        """Log an enrichment operation to the audit trail."""
        record = EnrichmentAuditRecord(
            company_id=company_id,
            company_name=company_name,
            operation=operation,
            source=source,
            status=status,
            duration_ms=duration_ms,
            fields_enriched=fields_enriched,
            error_message=error_message,
            user_id=user_id,
            client_id=client_id,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_audit_trail(
        self,
        company_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[EnrichmentAuditRecord]:
        """Get audit trail entries, optionally filtered by company_id."""
        query = select(EnrichmentAuditRecord).order_by(desc(EnrichmentAuditRecord.timestamp))

        if company_id:
            query = query.where(EnrichmentAuditRecord.company_id == company_id)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_company_stats(self, company_id: str) -> dict:
        """Get statistics for a company's enrichment operations."""
        query = select(EnrichmentAuditRecord).where(EnrichmentAuditRecord.company_id == company_id)
        result = await self.session.execute(query)
        records = result.scalars().all()

        total = len(records)
        successful = sum(1 for r in records if r.status == "SUCCESS")
        failed = sum(1 for r in records if r.status == "FAILURE")
        avg_duration = sum(r.duration_ms or 0 for r in records) / total if total > 0 else 0

        return {
            "total_operations": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "avg_duration_ms": avg_duration,
        }


class EnrichmentCacheRepository:
    """Repository for enrichment cache operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cached(self, company_id: str) -> EnrichmentCacheRecord | None:
        """Get cached enrichment data for a company."""
        query = select(EnrichmentCacheRecord).where(EnrichmentCacheRecord.company_id == company_id)
        result = await self.session.execute(query)
        record = result.scalar_one_or_none()

        # Check if expired
        if record and record.is_expired():
            await self.delete_cache(company_id)
            return None

        # Update hit count and access time
        if record:
            record.hits += 1
            record.last_accessed_at = datetime.now(timezone.utc)
            self.session.add(record)
            await self.session.flush()

        return record

    async def cache_enrichment(
        self,
        company_id: str,
        enriched_data: dict,
        sources_used: list[str] | None = None,
        fields_enriched: list[str] | None = None,
        ttl_seconds: int = 86400,  # 24 hours
    ) -> EnrichmentCacheRecord:
        """Cache enrichment results for a company."""
        # Delete existing cache if present
        await self.delete_cache(company_id)

        # Create new cache record
        now = datetime.now(timezone.utc)
        record = EnrichmentCacheRecord(
            company_id=company_id,
            enriched_data=enriched_data,
            sources_used=sources_used,
            fields_enriched=fields_enriched,
            cached_at=now,
            ttl_seconds=ttl_seconds,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def delete_cache(self, company_id: str | None = None) -> int:
        """Delete cache entries. If company_id is None, delete all expired entries."""
        if company_id:
            query = delete(EnrichmentCacheRecord).where(EnrichmentCacheRecord.company_id == company_id)
        else:
            # Delete expired entries
            now = datetime.now(timezone.utc)
            query = delete(EnrichmentCacheRecord).where(EnrichmentCacheRecord.expires_at <= now)

        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount

    async def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        query = select(EnrichmentCacheRecord)
        result = await self.session.execute(query)
        records = result.scalars().all()

        datetime.now(timezone.utc)
        valid_cache = [r for r in records if not r.is_expired()]

        total_hits = sum(r.hits for r in valid_cache)

        return {
            "total_entries": len(valid_cache),
            "total_hits": total_hits,
            "avg_hits_per_entry": total_hits / len(valid_cache) if valid_cache else 0,
        }
