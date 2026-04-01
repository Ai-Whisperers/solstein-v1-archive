"""Typed pagination wrappers for FastAPI responses.

Usage::

    from solstein.api.schemas.pagination import PaginatedResponse

    @router.get("/companies", response_model=PaginatedResponse[CompanySchema])
    async def list_companies(
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> PaginatedResponse[CompanySchema]:
        items, total = await repo.get_page(limit=limit, offset=offset)
        return PaginatedResponse.build(items=items, total=total, limit=limit, offset=offset)
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field, computed_field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated API response envelope.

    Attributes:
        items: The result items for this page.
        total: Total number of matching records across **all** pages.
        limit: Maximum items per page (as requested).
        offset: Zero-based offset of the first item in *items*.
        has_next: ``True`` if there are more pages after this one.
        has_prev: ``True`` if there are pages before this one.
    """

    items: list[T] = Field(description="Result items for this page.")
    total: int = Field(ge=0, description="Total matching records.")
    limit: int = Field(ge=1, description="Page size.")
    offset: int = Field(ge=0, description="Zero-based start offset.")

    @computed_field  # type: ignore[misc]
    @property
    def has_next(self) -> bool:
        """Whether more pages follow this one."""
        return self.offset + self.limit < self.total

    @computed_field  # type: ignore[misc]
    @property
    def has_prev(self) -> bool:
        """Whether pages precede this one."""
        return self.offset > 0

    @computed_field  # type: ignore[misc]
    @property
    def page(self) -> int:
        """Current 1-based page number (floor division)."""
        return (self.offset // self.limit) + 1

    @computed_field  # type: ignore[misc]
    @property
    def total_pages(self) -> int:
        """Total number of pages for this result set."""
        if self.limit == 0:
            return 0
        return (self.total + self.limit - 1) // self.limit

    @classmethod
    def build(
        cls,
        *,
        items: list[T],
        total: int,
        limit: int,
        offset: int,
    ) -> PaginatedResponse[T]:
        """Convenience factory — avoids repeated keyword args at call sites."""
        return cls(items=items, total=total, limit=limit, offset=offset)

    model_config = {"arbitrary_types_allowed": True}


class CursorPage(BaseModel, Generic[T]):
    """Cursor-based pagination for streaming/real-time endpoints.

    Attributes:
        items: Result items.
        next_cursor: Opaque cursor for the next page, or ``None`` if this is the last page.
        prev_cursor: Opaque cursor for the previous page, or ``None`` if first.
    """

    items: list[T] = Field(description="Result items.")
    next_cursor: str | None = Field(None, description="Cursor for next page.")
    prev_cursor: str | None = Field(None, description="Cursor for previous page.")

    model_config = {"arbitrary_types_allowed": True}


__all__ = ["PaginatedResponse", "CursorPage"]
