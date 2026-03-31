"""
Connector Registry - Central registry for all data source connectors.

This module provides a unified interface for accessing all connectors.
"""

import logging

from .academic import *
from .academic.arxiv import ArxivConnector
from .base import BaseConnector, SourceConfig
from .financial import *
from .financial.crunchbase import CrunchbaseConnector
from .financial.yahoo_finance import YahooFinanceConnector
from .government import *
from .government.patentsview import PatentsViewConnector
from .government.whois import WHOISConnector
from .news import *
from .news.hacker_news import HackerNewsConnector
from .news.newsapi import NewsAPIConnector
from .product import *
from .product.appstore import AppStoreConnector
from .product.dockerhub import DockerHubConnector
from .product.g2 import G2Connector
from .product.github import GitHubConnector
from .product.gitlab import GitLabConnector
from .product.googleplay import GooglePlayConnector
from .product.maven import MavenCentralConnector
from .product.npm import NPMConnector
from .product.pypi import PyPIConnector
from .product.stackoverflow import StackOverflowConnector
from .social import *
from .social.glassdoor import GlassdoorConnector
from .social.linkedin import LinkedInConnector
from .social.reddit import RedditConnector
from .social.trustpilot import TrustpilotConnector
from .social.youtube import YouTubeConnector

logger = logging.getLogger(__name__)


class ConnectorRegistry:
    """Central registry for managing all data source connectors."""

    def __init__(self):
        self._connectors: dict[str, BaseConnector] = {}
        self._configs: dict[str, SourceConfig] = {}

    def register(self, name: str, connector: BaseConnector) -> None:
        """Register a connector."""
        self._connectors[name] = connector
        logger.info(f"Registered connector: {name}")

    def get(self, name: str) -> BaseConnector | None:
        """Get a connector by name."""
        return self._connectors.get(name)

    def list_connectors(self) -> list[str]:
        """List all registered connector names."""
        return list(self._connectors.keys())

    async def close_all(self) -> None:
        """Close all connectors."""
        for name, connector in self._connectors.items():
            try:
                await connector.close()
                logger.info(f"Closed connector: {name}")
            except Exception as e:
                logger.error(f"Error closing {name}: {e}")


# Global registry instance
_registry: ConnectorRegistry | None = None


def get_registry() -> ConnectorRegistry:
    """Get or create the global registry."""
    global _registry
    if _registry is None:
        _registry = ConnectorRegistry()
    return _registry


async def initialize_default_connectors() -> ConnectorRegistry:
    """Initialize all default connectors."""
    registry = get_registry()

    # Financial connectors
    try:
        yf = YahooFinanceConnector()
        registry.register("yahoo_finance", yf)
    except Exception as e:
        logger.warning(f"Failed to initialize Yahoo Finance: {e}")

    # Academic connectors
    try:
        arxiv = ArxivConnector()
        registry.register("arxiv", arxiv)
    except Exception as e:
        logger.warning(f"Failed to initialize arXiv: {e}")

    # News connectors
    try:
        hn = HackerNewsConnector()
        registry.register("hacker_news", hn)
    except Exception as e:
        logger.warning(f"Failed to initialize Hacker News: {e}")

    # Product/Developer connectors
    try:
        github = GitHubConnector()
        registry.register("github", github)
    except Exception as e:
        logger.warning(f"Failed to initialize GitHub: {e}")

    # Government connectors
    try:
        patents = PatentsViewConnector()
        registry.register("patentsview", patents)
    except Exception as e:
        logger.warning(f"Failed to initialize PatentsView: {e}")

    # Social connectors
    try:
        reddit = RedditConnector()
        registry.register("reddit", reddit)
    except Exception as e:
        logger.warning(f"Failed to initialize Reddit: {e}")


    # Additional product connectors
    try:
        stackoverflow = StackOverflowConnector()
        registry.register("stackoverflow", stackoverflow)
    except Exception as e:
        logger.warning(f"Failed to initialize Stack Overflow: {e}")

    try:
        npm = NPMConnector()
        registry.register("npm", npm)
    except Exception as e:
        logger.warning(f"Failed to initialize npm: {e}")

    try:
        pypi = PyPIConnector()
        registry.register("pypi", pypi)
    except Exception as e:
        logger.warning(f"Failed to initialize PyPI: {e}")

    try:
        appstore = AppStoreConnector()
        registry.register("appstore", appstore)
    except Exception as e:
        logger.warning(f"Failed to initialize App Store: {e}")

    try:
        googleplay = GooglePlayConnector()
        registry.register("googleplay", googleplay)
    except Exception as e:
        logger.warning(f"Failed to initialize Google Play: {e}")

    # Additional social connectors
    try:
        youtube = YouTubeConnector()
        registry.register("youtube", youtube)
    except Exception as e:
        logger.warning(f"Failed to initialize YouTube: {e}")

    try:
        linkedin = LinkedInConnector()
        registry.register("linkedin", linkedin)
    except Exception as e:
        logger.warning(f"Failed to initialize LinkedIn: {e}")

    # Additional financial connectors
    try:
        crunchbase = CrunchbaseConnector()
        registry.register("crunchbase", crunchbase)
    except Exception as e:
        logger.warning(f"Failed to initialize Crunchbase: {e}")

    # Additional government connectors
    try:
        wayback = WaybackMachineConnector()
        registry.register("wayback", wayback)
    except Exception as e:
        logger.warning(f"Failed to initialize Wayback: {e}")

    # Additional package registries
    try:
        maven = MavenCentralConnector()
        registry.register("maven", maven)
    except Exception as e:
        logger.warning(f"Failed to initialize Maven: {e}")

    # Container registries
    try:
        dockerhub = DockerHubConnector()
        registry.register("dockerhub", dockerhub)
    except Exception as e:
        logger.warning(f"Failed to initialize Docker Hub: {e}")

    # Additional code repositories
    try:
        gitlab = GitLabConnector()
        registry.register("gitlab", gitlab)
    except Exception as e:
        logger.warning(f"Failed to initialize GitLab: {e}")

    # Review platforms
    try:
        g2 = G2Connector()
        registry.register("g2", g2)
    except Exception as e:
        logger.warning(f"Failed to initialize G2: {e}")


    # Additional news connectors
    try:
        newsapi = NewsAPIConnector()
        registry.register("newsapi", newsapi)
    except Exception as e:
        logger.warning(f"Failed to initialize NewsAPI: {e}")

    # Domain/WHOIS connectors
    try:
        whois = WHOISConnector()
        registry.register("whois", whois)
    except Exception as e:
        logger.warning(f"Failed to initialize WHOIS: {e}")

    # Additional review platforms
    try:
        glassdoor = GlassdoorConnector()
        registry.register("glassdoor", glassdoor)
    except Exception as e:
        logger.warning(f"Failed to initialize Glassdoor: {e}")

    try:
        trustpilot = TrustpilotConnector()
        registry.register("trustpilot", trustpilot)
    except Exception as e:
        logger.warning(f"Failed to initialize Trustpilot: {e}")

    try:
        trustpilot = TrustpilotConnector()
        registry.register("trustpilot", trustpilot)
    except Exception as e:
        logger.warning(f"Failed to initialize Trustpilot: {e}")

    # Podcast connectors
    try:
        podcastindex = PodcastIndexConnector()
        registry.register("podcastindex", podcastindex)
    except Exception as e:
        logger.warning(f"Failed to initialize Podcast Index: {e}")

    # Startup platforms
    try:
        angellist = AngelListConnector()
        registry.register("angellist", angellist)
    except Exception as e:
        logger.warning(f"Failed to initialize AngelList: {e}")

    try:
        f6s = F6SConnector()
        registry.register("f6s", f6s)
    except Exception as e:
        logger.warning(f"Failed to initialize F6S: {e}")

    # Additional review platforms
    try:
        capterra = CapterraConnector()
        registry.register("capterra", capterra)
    except Exception as e:
        logger.warning(f"Failed to initialize Capterra: {e}")

    # Additional code repositories
    try:
        bitbucket = BitbucketConnector()
        registry.register("bitbucket", bitbucket)
    except Exception as e:
        logger.warning(f"Failed to initialize Bitbucket: {e}")

    # Additional financial/regulatory
    try:
        opencorp = OpenCorporatesConnector()
        registry.register("opencorporates", opencorp)
    except Exception as e:
        logger.warning(f"Failed to initialize OpenCorporates: {e}")

    # Additional startup platforms
    try:
        betalist = BetaListConnector()
        registry.register("betalist", betalist)
    except Exception as e:
        logger.warning(f"Failed to initialize BetaList: {e}")

    # Additional infrastructure
    try:
        dns = DNSConnector()
        registry.register("dns", dns)
    except Exception as e:
        logger.warning(f"Failed to initialize DNS: {e}")

    # Social media
    try:
        twitter = TwitterConnector()
        registry.register("twitter", twitter)
    except Exception as e:
        logger.warning(f"Failed to initialize Twitter: {e}")

    # Regulatory/Government
    try:
        sec = SECEdgarConnector()
        registry.register("sec_edgar", sec)
    except Exception as e:
        logger.warning(f"Failed to initialize SEC EDGAR: {e}")

    logger.info(f"Initialized {len(registry.list_connectors())} connectors")
    return registry
