"""Government and patent data connectors."""

from .patentsview import PatentsViewConnector
from .usaspending import USAspendingConnector
from .wayback import WaybackMachineConnector
from .whois import WHOISConnector

__all__ = [
    "PatentsViewConnector",
    "USAspendingConnector",
    "WaybackMachineConnector",
    "WHOISConnector",
]


from .dns import DNSConnector

__all__.extend([
    "DNSConnector",
])
