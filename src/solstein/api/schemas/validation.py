"""Request/response schemas with validation - Phase 2, Item 2.4

Pydantic models for request validation and response serialization.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict

from solstein.domain.constants import ALLOWED_SEARCH_FIELDS, INDUSTRY_VALID_VALUES

class SearchRequest(BaseModel):
    """Search request with validation."""

    field: str = Field(..., min_length=1, max_length=50, description="Field to search on")
    value: str = Field(..., min_length=1, max_length=1000, description="Search value")
    model_type: str = Field(default="company", min_length=1, max_length=50, description="Model type to search")

    @field_validator("field")
    @classmethod
    def validate_field(cls, v: str, info) -> str:
        """Ensure field is in allowed list."""
        if not v or not v.strip():
            raise ValueError("field cannot be empty or whitespace")
        model_type = info.data.get("model_type", "company")
        allowed = ALLOWED_SEARCH_FIELDS.get(model_type, set())

        if v not in allowed:
            raise ValueError(f"Invalid field '{v}' for {model_type}. Allowed: {sorted(allowed)}")
        return v.strip()

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        """Ensure value is not empty."""
        if not v or not v.strip():
            raise ValueError("value cannot be empty or whitespace")
        return v.strip()

    @field_validator("model_type")
    @classmethod
    def validate_model_type(cls, v: str) -> str:
        """Ensure model type is valid."""
        if not v or not v.strip():
            raise ValueError("model_type cannot be empty")
        if v not in ALLOWED_SEARCH_FIELDS:
            raise ValueError(f"Invalid model_type '{v}'. Allowed: {list(ALLOWED_SEARCH_FIELDS.keys())}")
        return v.strip()

class PaginationParams(BaseModel):
    """Pagination parameters with validation."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate database offset."""
        return (self.page - 1) * self.page_size


class CompanyFilterRequest(BaseModel):
    """Company filter request with validation."""

    industry: Optional[str] = Field(default=None, min_length=2, max_length=100, description="Industry name")
    headquarters: Optional[str] = Field(default=None, min_length=2, max_length=100, description="Headquarters location")
    tier: Optional[str] = Field(default=None, pattern=r"^[A-E]$", description="Company tier (A-E)")
    min_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum score filter")
    max_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Maximum score filter")

    @field_validator("industry")
    @classmethod
    def validate_industry(cls, v: Optional[str]) -> Optional[str]:
        """Validate industry is known."""
        if v:
            if not v.strip():
                raise ValueError("industry cannot be empty or whitespace")
            if v not in INDUSTRY_VALID_VALUES:
                raise ValueError(f"Unknown industry '{v}'. Valid: {sorted(INDUSTRY_VALID_VALUES)}")
            return v.strip()
        return v

    @field_validator("headquarters")
    @classmethod
    def validate_headquarters(cls, v: Optional[str]) -> Optional[str]:
        """Validate headquarters is not empty."""
        if v:
            if not v.strip():
                raise ValueError("headquarters cannot be empty or whitespace")
            return v.strip()
        return v

    @field_validator("min_score", "max_score")
    @classmethod
    def validate_scores(cls, v: Optional[float]) -> Optional[float]:
        """Validate score bounds."""
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("Score must be between 0.0 and 1.0")
        return v

class MarketAnalysisRequest(BaseModel):
    """Market analysis request with validation."""

    industry: str = Field(..., min_length=2, max_length=100, description="Industry to analyze")
    region: Optional[str] = Field(default=None, min_length=2, max_length=100, description="Geographic region")

    @field_validator("industry")
    @classmethod
    def validate_industry(cls, v: str) -> str:
        """Validate industry is known."""
        if not v or not v.strip():
            raise ValueError("industry cannot be empty or whitespace")
        if v not in INDUSTRY_VALID_VALUES:
            raise ValueError(f"Unknown industry '{v}'. Valid: {sorted(INDUSTRY_VALID_VALUES)}")
        return v.strip()

    @field_validator("region")
    @classmethod
    def validate_region(cls, v: Optional[str]) -> Optional[str]:
        """Validate region is not empty."""
        if v:
            if not v.strip():
                raise ValueError("region cannot be empty or whitespace")
            return v.strip()
        return v

class ScoreUpdateRequest(BaseModel):
    """Score update request with validation."""

    ai_score: float = Field(..., ge=0.0, le=1.0, description="AI maturity score")
    growth_score: float = Field(..., ge=0.0, le=1.0, description="Growth score")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score")

    @field_validator("ai_score", "growth_score", "risk_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        """Ensure score is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return round(v, 4)  # Round to 4 decimal places


class CompanyCreateRequest(BaseModel):
    """Company creation request with validation."""

    name: str = Field(..., min_length=2, max_length=255, description="Company name")
    industry: str = Field(..., min_length=2, max_length=100, description="Industry")
    headquarters: Optional[str] = Field(default=None, min_length=2, max_length=100, description="Headquarters location")
    revenue_eur_m: Optional[float] = Field(default=None, ge=0, le=1000000, description="Revenue in millions EUR")
    employees: Optional[int] = Field(default=None, ge=1, le=1000000, description="Number of employees")
    website: Optional[str] = Field(default=None, pattern=r"^https?://", description="Company website URL")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate company name is not empty."""
        if not v or not v.strip():
            raise ValueError("name cannot be empty or whitespace")
        return v.strip()

    @field_validator("industry")
    @classmethod
    def validate_industry(cls, v: str) -> str:
        """Validate industry is known."""
        if not v or not v.strip():
            raise ValueError("industry cannot be empty or whitespace")
        if v not in INDUSTRY_VALID_VALUES:
            raise ValueError(f"Unknown industry '{v}'. Valid: {sorted(INDUSTRY_VALID_VALUES)}")
        return v.strip()

    @field_validator("headquarters")
    @classmethod
    def validate_headquarters(cls, v: Optional[str]) -> Optional[str]:
        """Validate headquarters is not empty."""
        if v:
            if not v.strip():
                raise ValueError("headquarters cannot be empty or whitespace")
            return v.strip()
        return v

    @field_validator("revenue_eur_m")
    @classmethod
    def validate_revenue(cls, v: Optional[float]) -> Optional[float]:
        """Validate revenue is non-negative."""
        if v is not None and v < 0:
            raise ValueError("revenue_eur_m must be non-negative")
        return v

    @field_validator("employees")
    @classmethod
    def validate_employees(cls, v: Optional[int]) -> Optional[int]:
        """Validate employee count is positive."""
        if v is not None and v < 1:
            raise ValueError("employees must be at least 1")
        return v

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        """Validate website URL format."""
        if v:
            if not v.startswith(("http://", "https://")):
                raise ValueError("website must start with http:// or https://")
            if len(v) > 2048:
                raise ValueError("website URL is too long (max 2048 characters)")
        return v
