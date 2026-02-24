"""Repository layer for database operations.

This module provides repository classes for CRUD operations on domain models.
Repositories abstract the database layer and provide a clean interface for
business logic.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from solstein.domain.facts import Fact, FactSource, GatheringBatch
from solstein.infrastructure.database import DatabaseManager


class FactRepository:
    """Repository for Fact, GatheringBatch, and FactSource operations.

    Provides CRUD methods for storing and retrieving facts with confidence
    scoring and source tracking.
    """

    def __init__(self, db_manager: DatabaseManager):
        """Initialize repository with database manager.

        Args:
            db_manager: DatabaseManager instance for session management.
        """
        self.db_manager = db_manager

    def create_batch(
        self, company_id: str, status: str = "in_progress"
    ) -> GatheringBatch:
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
        session = self.db_manager.get_session()
        try:
            session.add(batch)
            session.commit()
            session.refresh(batch)
            return batch
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to create batch: {e}") from e
        finally:
            session.close()

    def store(self, fact: Fact) -> str:
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

        session = self.db_manager.get_session()
        try:
            session.add(fact)
            session.commit()
            session.refresh(fact)
            fact_id = str(fact.fact_id)
            return fact_id
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to store fact: {e}") from e
        finally:
            session.close()

    def store_batch(self, facts: List[Fact], batch: GatheringBatch) -> List[str]:
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

        session = self.db_manager.get_session()
        try:
            session.add(batch)
            session.flush()  # Ensure batch_id is generated

            for fact in facts:
                fact.batch_id = batch.batch_id
                session.add(fact)

            session.commit()

            fact_ids = [str(fact.fact_id) for fact in facts]
            return fact_ids
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to store batch: {e}") from e
        finally:
            session.close()

    def get_company_facts(self, company_id: str) -> List[Fact]:
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

        session = self.db_manager.get_session()
        try:
            facts = (
                session.query(Fact)
                .filter_by(company_id=company_id)
                .order_by(Fact.extracted_at.desc())
                .all()
            )
            return facts
        finally:
            session.close()

    def get_facts_by_type(
        self, company_id: str, fact_type: str
    ) -> List[Fact]:
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

        session = self.db_manager.get_session()
        try:
            facts = (
                session.query(Fact)
                .filter_by(company_id=company_id, fact_type=fact_type)
                .order_by(Fact.extracted_at.desc())
                .all()
            )
            return facts
        finally:
            session.close()

    def get_fact_by_id(self, fact_id: str) -> Optional[Fact]:
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

        session = self.db_manager.get_session()
        try:
            fact = session.query(Fact).filter_by(fact_id=fact_id).first()
            return fact
        finally:
            session.close()

    def add_source(
        self,
        fact_id: str,
        source_type: str,
        source_url: Optional[str] = None,
        raw_content: Optional[str] = None,
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

        session = self.db_manager.get_session()
        try:
            # Verify fact exists
            fact = session.query(Fact).filter_by(fact_id=fact_id).first()
            if not fact:
                raise RuntimeError(f"Fact {fact_id} not found")

            source = FactSource(
                fact_id=fact_id,
                source_type=source_type,
                source_url=source_url,
                raw_content=raw_content,
            )
            session.add(source)
            session.commit()
            session.refresh(source)
            return source
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to add source: {e}") from e
        finally:
            session.close()

    def get_batch(self, batch_id: str) -> Optional[GatheringBatch]:
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

        session = self.db_manager.get_session()
        try:
            batch = session.query(GatheringBatch).filter_by(batch_id=batch_id).first()
            return batch
        finally:
            session.close()

    def update_batch_status(self, batch_id: str, status: str) -> GatheringBatch:
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

        session = self.db_manager.get_session()
        try:
            batch = session.query(GatheringBatch).filter_by(batch_id=batch_id).first()
            if not batch:
                raise RuntimeError(f"Batch {batch_id} not found")

            batch.status = status
            session.commit()
            session.refresh(batch)
            return batch
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to update batch status: {e}") from e
        finally:
            session.close()
