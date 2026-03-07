"""
Data Source Connectors - Open data expansion for Solstein.

EPIC-043: Open-Data Source Expansion

This module provides connectors to various open data sources:
- Financial: Yahoo Finance, Crunchbase
- Academic: arXiv, Semantic Scholar
- News: Hacker News, NewsAPI, RSS
- Government: PatentsView, Wayback, WHOIS
- Social: Reddit, YouTube, LinkedIn, Glassdoor, Trustpilot
- Product: GitHub, Stack Overflow, npm, PyPI, App Store, Google Play,
           Maven Central, Docker Hub, GitLab, G2
"""

from .base import (
    BaseConnector,
    ConnectorResult,
    RawData,
    SourceConfig,
)

from .registry import (
    ConnectorRegistry,
    get_registry,
    initialize_default_connectors,
)

# Import all connectors from submodules
from .financial import *
from .academic import *
from .news import *
from .product import *
from .government import *
from .social import *

__all__ = [
    # Base
    "BaseConnector",
    "ConnectorResult",
    "RawData",
    "SourceConfig",
    # Registry
    "ConnectorRegistry",
    "get_registry",
    "initialize_default_connectors",
]

# Extend __all__ with exports from submodules
__all__.extend(financial.__all__)
__all__.extend(academic.__all__)
__all__.extend(news.__all__)
__all__.extend(product.__all__)
__all__.extend(government.__all__)
__all__.extend(social.__all__)
