"""Technical signal definitions.

Signals related to technical capabilities and infrastructure.
"""

from ..base import Signal, SignalCategory

TECHNICAL_SIGNALS = [
    Signal(
        name="AI/ML Adoption Level",
        category=SignalCategory.TECHNICAL,
        description="Extent of AI integration in products/operations",
    ),
    Signal(
        name="Open Source Contribution",
        category=SignalCategory.TECHNICAL,
        description="GitHub stars, forks, contributions",
    ),
    Signal(
        name="Technology Stack Modernization",
        category=SignalCategory.TECHNICAL,
        description="Use of current frameworks (React, Node, Python 3.10+)",
    ),
    Signal(
        name="Cloud Native Architecture",
        category=SignalCategory.TECHNICAL,
        description="Kubernetes, containerization, serverless adoption",
    ),
    Signal(
        name="API-First Design",
        category=SignalCategory.TECHNICAL,
        description="Presence of public/developer APIs",
    ),
    Signal(
        name="Microservices Architecture",
        category=SignalCategory.TECHNICAL,
        description="Degree of service decomposition",
    ),
    Signal(
        name="Mobile App Distribution",
        category=SignalCategory.TECHNICAL,
        description="iOS/Android app availability and ratings",
    ),
    Signal(
        name="Code Quality Metrics",
        category=SignalCategory.TECHNICAL,
        description="Test coverage, linting, security scanning",
    ),
    Signal(
        name="Infrastructure as Code",
        category=SignalCategory.TECHNICAL,
        description="Terraform/CloudFormation/Pulumi usage",
    ),
    Signal(
        name="DevOps Maturity",
        category=SignalCategory.TECHNICAL,
        description="CI/CD pipeline sophistication",
    ),
]
