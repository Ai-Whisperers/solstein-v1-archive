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


from .appstore import AppStoreConnector  # noqa: F401
from .googleplay import GooglePlayConnector  # noqa: F401

__all__.extend(
    [
        "AppStoreConnector",
        "GooglePlayConnector",
    ]
)


from .dockerhub import DockerHubConnector  # noqa: F401
from .g2 import G2Connector  # noqa: F401
from .gitlab import GitLabConnector  # noqa: F401
from .maven import MavenCentralConnector  # noqa: F401

__all__.extend(
    [
        "MavenCentralConnector",
        "DockerHubConnector",
        "GitLabConnector",
        "G2Connector",
    ]
)


from .capterra import CapterraConnector  # noqa: F401

__all__.extend(
    [
        "CapterraConnector",
    ]
)

from .bitbucket import BitbucketConnector  # noqa: F401

__all__.extend(
    [
        "BitbucketConnector",
    ]
)
