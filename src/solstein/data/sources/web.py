"""Web scraping data sources for Solstein."""

from __future__ import annotations

import requests
from loguru import logger

from .models import ProductInfo


class WebSource:
    """Website scraping data source."""

    async def scrape_company_website(self, company_name: str, website: str) -> ProductInfo:
        """
        Scrape company website for product information.

        Note: Be respectful of robots.txt and rate limits.
        """
        try:
            response = requests.get(
                website,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SolsteinBot/1.0)"},
            )
            response.raise_for_status()

            html = response.text.lower()

            # Extract potential product/feature keywords
            product_keywords = [
                "software",
                "platform",
                "solution",
                "service",
                "product",
                "app",
                "application",
                "tool",
                "system",
                "api",
                "cloud",
                "saas",
                "enterprise",
                "analytics",
                "ai",
                "ml",
                "machine learning",
                "automation",
                "digital",
                "mobile",
                "web",
                "dashboard",
            ]

            tech_keywords = [
                "python",
                "java",
                "javascript",
                "typescript",
                "react",
                "angular",
                "vue",
                "node",
                "aws",
                "azure",
                "gcp",
                "kubernetes",
                "docker",
                "sql",
                "postgresql",
                "mongodb",
                "redis",
                "graphql",
                "rest",
                "microservices",
                "microservice",
                "serverless",
                "lambda",
            ]

            products = [kw for kw in product_keywords if kw in html]
            tech_stack = [kw for kw in tech_keywords if kw in html]

            return ProductInfo(
                company_name=company_name,
                main_products=products[:10],
                features=[],
                pricing_model=None,
                target_customers=[],
                tech_stack=tech_stack[:10],
            )

        except Exception as e:
            logger.error(f"Error scraping {website}: {e}")
            return ProductInfo(
                company_name=company_name,
                main_products=[],
                features=[],
                tech_stack=[],
            )
