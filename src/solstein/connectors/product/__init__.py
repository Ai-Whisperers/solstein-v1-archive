"""Product and developer connectors."""

from .github import GitHubConnector
from .stackoverflow import StackOverflowConnector
from .producthunt import ProductHuntConnector
from .npm import NPMConnector
from .pypi import PyPIConnector

__all__ = [
    "GitHubConnector",
    "StackOverflowConnector",
    "ProductHuntConnector",
    "NPMConnector",
    "PyPIConnector",
]


from .appstore import AppStoreConnector
from .googleplay import GooglePlayConnector

__all__.extend([
    "AppStoreConnector",
    "GooglePlayConnector",
])


from .maven import MavenCentralConnector
from .dockerhub import DockerHubConnector
from .gitlab import GitLabConnector
from .g2 import G2Connector

__all__.extend([
    "MavenCentralConnector",
    "DockerHubConnector",
    "GitLabConnector",
    "G2Connector",
])


from .capterra import CapterraConnector

__all__.extend([
    "CapterraConnector",
])

from .bitbucket import BitbucketConnector

__all__.extend([
    "BitbucketConnector",
])