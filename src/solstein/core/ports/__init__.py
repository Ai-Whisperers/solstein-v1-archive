"""Dependency injection ports (interfaces).

This module defines the interfaces (protocols) that components
should implement. Using dependency injection with these ports
allows us to test components in isolation without extensive mocking.

Usage:
    from solstein.core.ports import DataConnector, CompanyRepository
    
    class MyService:
        def __init__(self, connector: DataConnector):
            self.connector = connector
        
        async def fetch(self, company_id: str) -> dict:
            return await self.connector.fetch_facts([company_id])
"""

from typing import Protocol, Any, Optional, List, Dict
from datetime import datetime


class DataConnector(Protocol):
    """Protocol for data connectors.
    
    Any class that fetches data from external sources should
    implement this protocol.
    
    Example:
        class SECEDGARRefreshConnector:
            async def fetch_facts(
                self,
                company_ids: list[str],
                start_date: datetime | None = None,
                end_date: datetime | None = None
            ) -> list[dict[str, Any]]:
                # Implementation
                pass
    """
    
    async def fetch_facts(
        self,
        company_ids: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch facts for given company IDs.
        
        Args:
            company_ids: List of company IDs to fetch data for
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of fact dictionaries
        """
        ...


class CompanyRepository(Protocol):
    """Protocol for company data repositories.
    
    Provides abstract interface for storing and retrieving
    company data, allowing different implementations
    (SQLAlchemy, Supabase, JsonFile, etc.).
    
    Example:
        class SqlAlchemyCompanyRepository:
            async def get_by_id(self, company_id: str) -> Company:
                result = await self.session.execute(...)
                return result.scalar_one()
    """
    
    async def get_by_id(self, company_id: str) -> Optional[Any]:
        """Get company by ID.
        
        Args:
            company_id: Unique company identifier
            
        Returns:
            Company object or None if not found
        """
        ...
    
    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """Get all companies matching filters.
        
        Args:
            filters: Optional filter criteria
            
        Returns:
            List of company objects
        """
        ...
    
    async def save(self, company: Any) -> Any:
        """Save company to repository.
        
        Args:
            company: Company object to save
            
        Returns:
            Saved company object
        """
        ...
    
    async def delete(self, company_id: str) -> bool:
        """Delete company by ID.
        
        Args:
            company_id: Company ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        ...


class FactRepository(Protocol):
    """Protocol for fact storage repositories."""
    
    async def store(self, fact: Dict[str, Any]) -> str:
        """Store a fact and return its ID."""
        ...
    
    async def get_by_company(
        self,
        company_id: str,
        fact_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get facts for a company."""
        ...
    
    async def get_by_type(self, fact_type: str) -> List[Dict[str, Any]]:
        """Get all facts of a specific type."""
        ...


class ScoringEngine(Protocol):
    """Protocol for company scoring engines."""
    
    def calculate_scores(self, company: Any) -> Any:
        """Calculate scores for a company.
        
        Args:
            company: Company object to score
            
        Returns:
            Company with scores calculated
        """
        ...
    
    def classify(self, company: Any) -> str:
        """Classify company based on scores.
        
        Args:
            company: Company with scores
            
        Returns:
            Classification string
        """
        ...


class DataLoader(Protocol):
    """Protocol for data loaders."""
    
    async def load_companies(
        self,
        limit: Optional[int] = None
    ) -> List[Any]:
        """Load companies from data source.
        
        Args:
            limit: Optional limit on number of companies
            
        Returns:
            List of company objects
        """
        ...
    
    async def load_company(self, company_id: str) -> Optional[Any]:
        """Load single company by ID.
        
        Args:
            company_id: Company ID to load
            
        Returns:
            Company object or None
        """
        ...


class EnrichmentService(Protocol):
    """Protocol for data enrichment services."""
    
    async def enrich_company(
        self,
        company: Any,
        sources: Optional[List[str]] = None
    ) -> Any:
        """Enrich company data from external sources.
        
        Args:
            company: Company to enrich
            sources: Optional list of source names
            
        Returns:
            Enriched company object
        """
        ...
    
    async def enrich_batch(
        self,
        companies: List[Any],
        sources: Optional[List[str]] = None
    ) -> List[Any]:
        """Enrich multiple companies.
        
        Args:
            companies: Companies to enrich
            sources: Optional list of source names
            
        Returns:
            List of enriched companies
        """
        ...


__all__ = [
    'DataConnector',
    'CompanyRepository',
    'FactRepository',
    'ScoringEngine',
    'DataLoader',
    'EnrichmentService',
]
