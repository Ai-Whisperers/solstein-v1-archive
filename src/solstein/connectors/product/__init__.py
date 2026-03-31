"""Product and developer connectors."""

from .github import GitHubConnector
from .npm import NPMConnector
from .producthunt import ProductHuntConnector
from .pypi import PyPIConnector
from .stackoverflow import StackOverflowConnector

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


from .dockerhub import DockerHubConnector
from .g2 import G2Connector
from .gitlab import GitLabConnector
from .maven import MavenCentralConnector

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
