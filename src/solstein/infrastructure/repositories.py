"""Repository layer for database operations.

This module provides repository classes for CRUD operations on domain models.
Repositories abstract the database layer and provide a clean interface for
business logic.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.domain.facts import Fact, FactSource, GatheringBatch
from solstein.infrastructure.database_models import ReleaseGateAuditRecord


class FactRepository:
    """Repository for Fact, GatheringBatch, and FactSource operations.

    Provides CRUD methods for storing and retrieving facts with confidence
    scoring and source tracking.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with async session.

        Args:
            session: AsyncSession instance for database operations.
        """
        self.session = session

    async def create_batch(self, company_id: str, status: str = "in_progress") -> GatheringBatch:
        """Create a new gathering batch.

        Args:
            company_id: Company identifier (string).
            status: Batch status (default: "in_progress").

        Returns:
            GatheringBatch: Created batch record.

        Raises:
            ValueError: If company_id is empty.
        """
        if not company_id:
            raise ValueError("Company ID is required")

        batch = GatheringBatch(company_id=company_id, status=status)
        try:
            self.session.add(batch)
            await self.session.commit()
            await self.session.refresh(batch)
            return batch
        except Exception as e:
            await self.session.rollback()
            raise RuntimeError(f"Failed to create batch: {e}") from e

    async def store(self, fact: Fact) -> str:
        """Store a fact in the database.

        Args:
            fact: Fact object to store.

        Returns:
            str: fact_id of the stored fact.

        Raises:
            ValueError: If fact validation fails.
            RuntimeError: If database operation fails.
        """
        fact.validate()

        try:
            self.session.add(fact)
            await self.session.commit()
            await self.session.refresh(fact)
            fact_id = str(fact.fact_id)
            return fact_id
        except Exception as e:
            await self.session.rollback()
            raise RuntimeError(f"Failed to store fact: {e}") from e

    async def store_batch(self, facts: list[Fact], batch: GatheringBatch) -> list[str]:
        """Store multiple facts in a single batch.

        Args:
            facts: List of Fact objects to store.
            batch: GatheringBatch to associate with facts.

        Returns:
            List[str]: List of fact_ids for stored facts.

        Raises:
            ValueError: If any fact validation fails.
            RuntimeError: If database operation fails.
        """
        if not facts:
            return []

        # Validate all facts before storing
        for fact in facts:
            fact.validate()

        try:
            self.session.add(batch)
            await self.session.flush()  # Ensure batch_id is generated

            for fact in facts:
                fact.batch_id = batch.batch_id
                self.session.add(fact)

            await self.session.commit()

            fact_ids = [str(fact.fact_id) for fact in facts]
            return fact_ids
        except Exception as e:
            await self.session.rollback()
            raise RuntimeError(f"Failed to store batch: {e}") from e

    async def get_company_facts(self, company_id: str) -> list[Fact]:
        """Fetch all facts for a company.

        Args:
            company_id: Company identifier (string).

        Returns:
            List[Fact]: All facts for the company, ordered by extracted_at descending.

        Raises:
            ValueError: If company_id is empty.
        """
        if not company_id:
            raise ValueError("Company ID is required")

        stmt = select(Fact).where(Fact.company_id == company_id).order_by(Fact.extracted_at.desc())
        result = await self.session.execute(stmt)
        facts = list(result.scalars().all())
        return facts

    async def get_facts_by_type(self, company_id: str, fact_type: str) -> list[Fact]:
        """Fetch facts of a specific type for a company.

        Args:
            company_id: Company identifier (string).
            fact_type: Type of fact to retrieve (e.g., "annual_revenue").

        Returns:
            List[Fact]: Facts matching the type, ordered by extracted_at descending.

        Raises:
            ValueError: If company_id or fact_type is empty.
        """
        if not company_id:
            raise ValueError("Company ID is required")
        if not fact_type:
            raise ValueError("Fact type is required")

        stmt = (
            select(Fact)
            .where(Fact.company_id == company_id, Fact.fact_type == fact_type)
            .order_by(Fact.extracted_at.desc())
        )
        result = await self.session.execute(stmt)
        facts = list(result.scalars().all())
        return facts

    async def get_fact_by_id(self, fact_id: str) -> Fact | None:
        """Fetch a single fact by ID.

        Args:
            fact_id: Fact identifier (UUID string).

        Returns:
            Optional[Fact]: Fact if found, None otherwise.

        Raises:
            ValueError: If fact_id is empty.
        """
        if not fact_id:
            raise ValueError("Fact ID is required")

        stmt = select(Fact).where(Fact.fact_id == fact_id)
        result = await self.session.execute(stmt)
        fact = result.scalar_one_or_none()
        return fact


class ReleaseGateAuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_decision(
        self,
        operation: str,
        status: str,
        company_ids: list[str],
        company_names: list[str],
        reason_codes: list[str],
        reason_details: list[dict[str, object]] | None = None,
    ) -> ReleaseGateAuditRecord:
        record = ReleaseGateAuditRecord(
            operation=operation,
            status=status,
            company_ids=company_ids,
            company_names=company_names,
            reason_codes=reason_codes,
            reason_details=reason_details,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def add_source(
        self,
        fact_id: str,
        source_type: str,
        source_url: str | None = None,
        raw_content: str | None = None,
    ) -> FactSource:
        """Add a source record to a fact.

        Args:
            fact_id: Fact identifier (UUID string).
            source_type: Type of source (e.g., "sec_edgar", "companies_house").
            source_url: URL of the source (optional).
            raw_content: Raw API response for audit trail (optional).

        Returns:
            FactSource: Created source record.

        Raises:
            ValueError: If fact_id or source_type is empty.
            RuntimeError: If fact not found or database operation fails.
        """
        if not fact_id:
            raise ValueError("Fact ID is required")
        if not source_type:
            raise ValueError("Source type is required")

        try:
            # Verify fact exists
            stmt = select(Fact).where(Fact.fact_id == fact_id)
            result = await self.session.execute(stmt)
            fact = result.scalar_one_or_none()
            if not fact:
                raise RuntimeError(f"Fact {fact_id} not found")

            source = FactSource(
                fact_id=fact_id,
                source_type=source_type,
                source_url=source_url,
                raw_content=raw_content,
            )
            self.session.add(source)
            await self.session.commit()
            await self.session.refresh(source)
            return source
        except Exception as e:
            await self.session.rollback()
            raise RuntimeError(f"Failed to add source: {e}") from e

    async def get_batch(self, batch_id: str) -> GatheringBatch | None:
        """Fetch a gathering batch by ID.

        Args:
            batch_id: Batch identifier (UUID string).

        Returns:
            Optional[GatheringBatch]: Batch if found, None otherwise.

        Raises:
            ValueError: If batch_id is empty.
        """
        if not batch_id:
            raise ValueError("Batch ID is required")

        stmt = select(GatheringBatch).where(GatheringBatch.batch_id == batch_id)
        result = await self.session.execute(stmt)
        batch = result.scalar_one_or_none()
        return batch

    async def update_batch_status(self, batch_id: str, status: str) -> GatheringBatch:
        """Update the status of a gathering batch.

        Args:
            batch_id: Batch identifier (UUID string).
            status: New status (e.g., "completed", "failed").

        Returns:
            GatheringBatch: Updated batch record.

        Raises:
            ValueError: If batch_id or status is empty.
            RuntimeError: If batch not found or database operation fails.
        """
        if not batch_id:
            raise ValueError("Batch ID is required")
        if not status:
            raise ValueError("Status is required")

        try:
            stmt = select(GatheringBatch).where(GatheringBatch.batch_id == batch_id)
            result = await self.session.execute(stmt)
            batch = result.scalar_one_or_none()
            if not batch:
                raise RuntimeError(f"Batch {batch_id} not found")

            batch.status = status
            await self.session.commit()
            await self.session.refresh(batch)
            return batch
        except Exception as e:
            await self.session.rollback()
            raise RuntimeError(f"Failed to update batch status: {e}") from e
