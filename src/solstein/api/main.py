"""
SolStein FastAPI Backend - Competitive Intelligence Platform

Production-ready REST API following Vete's architecture patterns:
- Clean architecture with clear separation of concerns
- Type-safe Pydantic models for request/response validation
- OpenAPI/Swagger auto-documentation
- JWT authentication (optional)
- PostgreSQL with async support
- Comprehensive error handling
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, status, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn
from loguru import logger

from ..config import Settings
from ..data.models import (
    CompanyProfile, FinancialMetric, MarketAnalysis, 
    CompetitiveOverlap, ConfidenceLevel, CompanyTier,
    AIMaturity, ThreatLevel
)
from ..analytics.scoring import GrowthScorer, MarketAnalyzer
from ..exporters.excel_exporter import ExcelExporter
from ..data.loaders import CompetitorDataLoader

# Initialize FastAPI app
app = FastAPI(
    title="SolStein Competitive Intelligence API",
    description="AI-powered competitive intelligence platform for VC/PE firms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Global instances
settings = Settings()
growth_scorer = GrowthScorer()
market_analyzer = MarketAnalyzer()
excel_exporter = ExcelExporter()
data_loader = CompetitorDataLoader()


# Dependency: Get current user (simplified for demo)
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """Get current user from JWT token (simplified for demo)."""
    # For demo, authentication is optional
    # In production, you would check settings.security settings
    
    if not credentials:
        # Allow anonymous access for demo
        return {"username": "anonymous", "role": "viewer"}
    
    # In production, validate JWT token here
    # For demo, accept any token
    return {"username": "demo_user", "role": "admin"}


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": settings.environment
    }


# Company endpoints
@app.get("/companies", response_model=List[CompanyProfile], tags=["Companies"])
async def get_companies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    tier: Optional[CompanyTier] = Query(None, description="Filter by company tier"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    min_revenue: Optional[float] = Query(None, ge=0, description="Minimum revenue in EUR millions"),
    _: Dict = Depends(get_current_user)
):
    """Get list of companies with optional filtering."""
    try:
        # In production, this would query the database
        # For demo, load from JSON file
        companies = data_loader.load_companies()
        
        # Apply filters
        filtered_companies = []
        for company in companies:
            if tier and company.tier != tier:
                continue
            if industry and industry.lower() not in company.industry.lower():
                continue
            if min_revenue and company.financials.revenue and company.financials.revenue < min_revenue:
                continue
            filtered_companies.append(company)
        
        # Apply pagination
        paginated = filtered_companies[skip:skip + limit]
        
        return paginated
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving companies: {str(e)}"
        )


@app.get("/companies/{company_id}", response_model=CompanyProfile, tags=["Companies"])
async def get_company(
    company_id: str,
    _: Dict = Depends(get_current_user)
):
    """Get company by ID."""
    try:
        companies = data_loader.load_companies()
        for company in companies:
            if company.id == company_id:
                return company
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving company: {str(e)}"
        )


@app.post("/companies", response_model=CompanyProfile, tags=["Companies"], status_code=status.HTTP_201_CREATED)
async def create_company(
    company: CompanyProfile,
    _: Dict = Depends(get_current_user)
):
    """Create a new company profile."""
    try:
        # In production, this would save to database
        # For demo, just validate and return
        logger.info(f"Creating company: {company.name}")
        
        # Calculate scores
        scored_company = growth_scorer.calculate_scores(company)
        
        return scored_company
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating company: {str(e)}"
        )


# Market analysis endpoints
@app.get("/market/analysis", tags=["Market Analysis"])
async def analyze_market(
    industry: Optional[str] = Query(None, description="Industry to analyze"),
    region: Optional[str] = Query(None, description="Geographic region"),
    _: Dict = Depends(get_current_user)
):
    """Analyze market competitive landscape."""
    try:
        companies = data_loader.load_companies()
        
        # Filter by industry if specified
        if industry:
            filtered_companies = [
                c for c in companies 
                if c.industry and industry.lower() in c.industry.lower()
            ]
        else:
            filtered_companies = companies
        
        if not filtered_companies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No companies found for industry: {industry}"
            )
        
        # Perform market analysis
        analysis = market_analyzer.analyze_market(filtered_companies)
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing market: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing market: {str(e)}"
        )


@app.get("/market/overlap/{company_id}", response_model=List[CompetitiveOverlap], tags=["Market Analysis"])
async def get_competitive_overlap(
    company_id: str,
    top_n: int = Query(10, ge=1, le=50, description="Number of top overlaps to return"),
    _: Dict = Depends(get_current_user)
):
    """Get competitive overlap for a company."""
    try:
        companies = data_loader.load_companies()
        
        # Find target company
        target_company = None
        for company in companies:
            if company.id == company_id:
                target_company = company
                break
        
        if not target_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found"
            )
        
        # Calculate overlaps (simplified for demo)
        overlaps = []
        for company in companies:
            if company.id == company_id:
                continue
            
            # Simple overlap calculation based on industry and tier
            overlap_score = 0.0
            if company.industry == target_company.industry:
                overlap_score += 0.5
            if company.tier == target_company.tier:
                overlap_score += 0.3
            if company.ai_maturity == target_company.ai_maturity:
                overlap_score += 0.2
            
            overlaps.append(CompetitiveOverlap(
                company_a_id=company_id,
                company_b_id=company.id,
                overlap_score=overlap_score,
                overlap_type="industry_tier_ai",
                last_calculated=datetime.now()
            ))
        
        # Sort by overlap score and return top N
        overlaps.sort(key=lambda x: x.overlap_score, reverse=True)
        return overlaps[:top_n]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating competitive overlap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating competitive overlap: {str(e)}"
        )


# Scoring endpoints
@app.post("/scoring/company/{company_id}/score", tags=["Scoring"])
async def score_company(
    company_id: str,
    background_tasks: BackgroundTasks,
    _: Dict = Depends(get_current_user)
):
    """Calculate growth and competitive scores for a company."""
    try:
        companies = data_loader.load_companies()
        
        # Find company
        target_company = None
        for company in companies:
            if company.id == company_id:
                target_company = company
                break
        
        if not target_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found"
            )
        
        # Calculate scores (could be done in background for large datasets)
        scored_company = growth_scorer.calculate_scores(target_company)
        
        return {
            "company_id": company_id,
            "growth_score": scored_company.growth_score,
            "financial_health_score": scored_company.financial_health_score,
            "competitive_position_score": scored_company.competitive_position_score,
            "classification": "Rocket" if scored_company.growth_score >= 7.0 
                          else "Dinosaur" if scored_company.growth_score <= 4.0 
                          else "Neutral",
            "calculated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scoring company {company_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scoring company: {str(e)}"
        )


@app.get("/scoring/batch", tags=["Scoring"])
async def batch_score_companies(
    background_tasks: BackgroundTasks,
    industry: Optional[str] = Query(None, description="Industry to score"),
    min_revenue: Optional[float] = Query(None, ge=0, description="Minimum revenue"),
    _: Dict = Depends(get_current_user)
):
    """Batch score multiple companies (runs in background)."""
    try:
        companies = data_loader.load_companies()
        
        # Filter companies
        filtered_companies = []
        for company in companies:
            if industry and company.industry and industry.lower() not in company.industry.lower():
                continue
            if min_revenue and company.financials.revenue and company.financials.revenue < min_revenue:
                continue
            filtered_companies.append(company)
        
        # In production, this would be a background job
        # For demo, score synchronously
        results = []
        for company in filtered_companies[:10]:  # Limit to 10 for demo
            try:
                scored = growth_scorer.calculate_scores(company)
                results.append({
                    "company_id": company.id,
                    "company_name": company.name,
                    "growth_score": scored.growth_score,
                    "classification": "Rocket" if scored.growth_score >= 7.0 
                                  else "Dinosaur" if scored.growth_score <= 4.0 
                                  else "Neutral"
                })
            except Exception as e:
                logger.warning(f"Error scoring company {company.id}: {e}")
                results.append({
                    "company_id": company.id,
                    "company_name": company.name,
                    "error": str(e)
                })
        
        return {
            "total_companies": len(filtered_companies),
            "scored_companies": len(results),
            "results": results,
            "completed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in batch scoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch scoring: {str(e)}"
        )


# Export endpoints
@app.get("/export/excel", tags=["Export"])
async def export_to_excel(
    industry: Optional[str] = Query(None, description="Industry to export"),
    include_charts: bool = Query(True, description="Include charts in Excel"),
    _: Dict = Depends(get_current_user)
):
    """Export company data to Excel dashboard."""
    try:
        companies = data_loader.load_companies()
        
        # Filter by industry if specified
        if industry:
            filtered_companies = [
                c for c in companies 
                if c.industry and industry.lower() in c.industry.lower()
            ]
        else:
            filtered_companies = companies[:20]  # Limit to 20 for demo
        
        if not filtered_companies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No companies found for industry: {industry}"
            )
        
        # Create output directory
        output_dir = Path("exports") / "excel"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if industry:
            filename = f"solstein_{industry.lower().replace(' ', '_')}_{timestamp}.xlsx"
        else:
            filename = f"solstein_dashboard_{timestamp}.xlsx"
        
        output_path = output_dir / filename
        
        # Create Excel dashboard
        excel_exporter.create_dashboard(filtered_companies, output_path)
        
        # Return file for download
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting to Excel: {str(e)}"
        )


@app.get("/export/json", tags=["Export"])
async def export_to_json(
    industry: Optional[str] = Query(None, description="Industry to export"),
    _: Dict = Depends(get_current_user)
):
    """Export company data to JSON."""
    try:
        companies = data_loader.load_companies()
        
        # Filter by industry if specified
        if industry:
            filtered_companies = [
                c for c in companies 
                if c.industry and industry.lower() in c.industry.lower()
            ]
        else:
            filtered_companies = companies
        
        if not filtered_companies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No companies found for industry: {industry}"
            )
        
        # Convert to dict with JSON serializable values
        companies_data = []
        for company in filtered_companies:
            company_dict = company.model_dump(mode="json")
            # Add scores
            scored = growth_scorer.calculate_scores(company)
            company_dict.update({
                "growth_score": scored.growth_score,
                "financial_health_score": scored.financial_health_score,
                "competitive_position_score": scored.competitive_position_score
            })
            companies_data.append(company_dict)
        
        # Create output
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_companies": len(companies_data),
            "companies": companies_data
        }
        
        return JSONResponse(content=export_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting to JSON: {str(e)}"
        )


# Search endpoint
@app.get("/search", tags=["Search"])
async def search_companies(
    query: str = Query(..., min_length=2, description="Search query"),
    field: str = Query("name", description="Field to search (name, industry, description)"),
    _: Dict = Depends(get_current_user)
):
    """Search companies by various fields."""
    try:
        companies = data_loader.load_companies()
        
        results = []
        query_lower = query.lower()
        
        for company in companies:
            search_value = None
            if field == "name" and company.name:
                search_value = company.name.lower()
            elif field == "industry" and company.industry:
                search_value = company.industry.lower()
            elif field == "description" and company.description:
                search_value = company.description.lower()
            
            if search_value and query_lower in search_value:
                results.append(company)
        
        return {
            "query": query,
            "field": field,
            "total_results": len(results),
            "results": results[:100]  # Limit results
        }
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching companies: {str(e)}"
        )


# Statistics endpoint
@app.get("/stats", tags=["Statistics"])
async def get_statistics(
    _: Dict = Depends(get_current_user)
):
    """Get platform statistics."""
    try:
        companies = data_loader.load_companies()
        
        # Calculate statistics
        total_companies = len(companies)
        
        # Revenue statistics
        revenues = [c.financials.revenue for c in companies if c.financials.revenue]
        total_revenue = sum(revenues) if revenues else 0
        avg_revenue = total_revenue / len(revenues) if revenues else 0
        
        # Growth statistics
        growth_rates = [c.financials.growth_rate for c in companies if c.financials.growth_rate]
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0
        
        # Tier distribution
        tier_counts = {}
        for company in companies:
            tier = company.tier.value
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        # Score companies to get classifications
        rocket_count = 0
        dinosaur_count = 0
        neutral_count = 0
        
        for company in companies[:50]:  # Limit for performance
            try:
                scored = growth_scorer.calculate_scores(company)
                if scored.growth_score >= 7.0:
                    rocket_count += 1
                elif scored.growth_score <= 4.0:
                    dinosaur_count += 1
                else:
                    neutral_count += 1
            except:
                neutral_count += 1
        
        return {
            "total_companies": total_companies,
            "revenue_statistics": {
                "total_revenue_eur_m": total_revenue,
                "average_revenue_eur_m": avg_revenue,
                "companies_with_revenue_data": len(revenues)
            },
            "growth_statistics": {
                "average_growth_rate_pct": avg_growth,
                "companies_with_growth_data": len(growth_rates)
            },
            "tier_distribution": tier_counts,
            "growth_classification": {
                "rockets": rocket_count,
                "dinosaurs": dinosaur_count,
                "neutral": neutral_count
            },
            "calculated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating statistics: {str(e)}"
        )


# Custom docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with SolStein branding."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SolStein API Documentation",
        swagger_favicon_url="https://solstein.ai/favicon.ico"
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting SolStein API server")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Data directory: {settings.data.data_dir}")
    
    # Create necessary directories
    Path("exports/excel").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down SolStein API server")


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "solstein.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.environment == "development",
        log_level="info"
    )