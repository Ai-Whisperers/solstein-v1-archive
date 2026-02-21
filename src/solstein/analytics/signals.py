"""Signal extraction framework and definitions.

Defines 50+ signals across 8 categories:
- Growth (revenue, users, deployments)
- Financial Health (funding, burn rate, efficiency)
- Technical (AI adoption, modern stack, open source)
- Hiring (team growth, key roles, retention)
- Product (user satisfaction, feature adoption)
- Market (competitive position, market share)
- Operational (process maturity, automation)
- Strategic (partnerships, funding rounds, pivots)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SignalCategory(str, Enum):
    """Categories of signals used in scoring."""

    GROWTH = "growth"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    HIRING = "hiring"
    PRODUCT = "product"
    MARKET = "market"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"


@dataclass
class Signal:
    """Represents a single signal extracted from data sources."""

    name: str
    category: SignalCategory
    description: str
    value: float | None = None
    text: str | None = None
    source: str | None = None
    confidence: float = 0.5
    evidence: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert signal to dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "value": self.value,
            "text": self.text,
            "source": self.source,
            "confidence": self.confidence,
            "evidence": self.evidence or {},
        }


class SignalDefinitions:
    """Registry of all available signals (50+) across 8 categories."""

    GROWTH_SIGNALS = [
        Signal(
            name="Year-over-Year Revenue Growth Rate",
            category=SignalCategory.GROWTH,
            description="Percentage growth in annual revenue",
        ),
        Signal(
            name="Quarterly Revenue Trend",
            category=SignalCategory.GROWTH,
            description="Trend in quarterly revenue (ascending/stable/declining)",
        ),
        Signal(
            name="Monthly Recurring Revenue (MRR)",
            category=SignalCategory.GROWTH,
            description="Predictable monthly revenue from subscriptions",
        ),
        Signal(
            name="Annual Recurring Revenue (ARR)",
            category=SignalCategory.GROWTH,
            description="Annualized predictable revenue",
        ),
        Signal(
            name="Active User Growth",
            category=SignalCategory.GROWTH,
            description="Month-over-month user acquisition rate",
        ),
        Signal(
            name="Daily Active Users (DAU)",
            category=SignalCategory.GROWTH,
            description="Number of users engaging daily",
        ),
        Signal(
            name="Monthly Active Users (MAU)",
            category=SignalCategory.GROWTH,
            description="Number of users engaging monthly",
        ),
        Signal(
            name="User Churn Rate",
            category=SignalCategory.GROWTH,
            description="Percentage of users leaving per month",
        ),
        Signal(
            name="Market Expansion Rate",
            category=SignalCategory.GROWTH,
            description="Speed of entering new geographies/verticals",
        ),
        Signal(
            name="Product Deployment Frequency",
            category=SignalCategory.GROWTH,
            description="Releases per month (GitHub commits/PRs)",
        ),
    ]

    FINANCIAL_SIGNALS = [
        Signal(
            name="Total Funding Raised",
            category=SignalCategory.FINANCIAL,
            description="Cumulative capital raised from all sources",
        ),
        Signal(
            name="Latest Funding Round Size",
            category=SignalCategory.FINANCIAL,
            description="Size and valuation of most recent round",
        ),
        Signal(
            name="Funding Round Velocity",
            category=SignalCategory.FINANCIAL,
            description="Time between funding rounds (faster = better)",
        ),
        Signal(
            name="Monthly Burn Rate",
            category=SignalCategory.FINANCIAL,
            description="Monthly cash consumption",
        ),
        Signal(
            name="Runway Months",
            category=SignalCategory.FINANCIAL,
            description="Months of runway at current burn rate",
        ),
        Signal(
            name="Cash Efficiency Ratio",
            category=SignalCategory.FINANCIAL,
            description="Revenue per dollar of funding",
        ),
        Signal(
            name="Customer Acquisition Cost (CAC)",
            category=SignalCategory.FINANCIAL,
            description="Cost to acquire one customer",
        ),
        Signal(
            name="Customer Lifetime Value (LTV)",
            category=SignalCategory.FINANCIAL,
            description="Total expected revenue per customer",
        ),
        Signal(
            name="LTV-to-CAC Ratio",
            category=SignalCategory.FINANCIAL,
            description="Ratio of LTV to CAC (3:1 is healthy)",
        ),
        Signal(
            name="Gross Margin",
            category=SignalCategory.FINANCIAL,
            description="Percentage of revenue after COGS",
        ),
    ]

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

    HIRING_SIGNALS = [
        Signal(
            name="Engineering Headcount Growth",
            category=SignalCategory.HIRING,
            description="Number of engineers hired in past 12 months",
        ),
        Signal(
            name="Total Headcount Growth",
            category=SignalCategory.HIRING,
            description="Total employees hired per month",
        ),
        Signal(
            name="Engineering Percentage",
            category=SignalCategory.HIRING,
            description="Percentage of team in engineering",
        ),
        Signal(
            name="Key Leadership Positions Filled",
            category=SignalCategory.HIRING,
            description="CTO, VP Engineering, Product leads hired",
        ),
        Signal(
            name="Employee Retention Rate",
            category=SignalCategory.HIRING,
            description="Percentage of employees retained annually",
        ),
        Signal(
            name="Glassdoor Rating",
            category=SignalCategory.HIRING,
            description="Employee satisfaction score",
        ),
        Signal(
            name="LinkedIn Follower Growth",
            category=SignalCategory.HIRING,
            description="Company page follower growth rate",
        ),
        Signal(
            name="University Recruitment Activity",
            category=SignalCategory.HIRING,
            description="Campus hiring and internship programs",
        ),
        Signal(
            name="Senior Talent Acquisition",
            category=SignalCategory.HIRING,
            description="Hiring of 10+ year industry veterans",
        ),
        Signal(
            name="Global Team Expansion",
            category=SignalCategory.HIRING,
            description="Opening of offices in new countries",
        ),
    ]

    PRODUCT_SIGNALS = [
        Signal(
            name="Feature Release Velocity",
            category=SignalCategory.PRODUCT,
            description="Major features released per quarter",
        ),
        Signal(
            name="Product Roadmap Visibility",
            category=SignalCategory.PRODUCT,
            description="Public roadmap availability",
        ),
        Signal(
            name="User Satisfaction (NPS)",
            category=SignalCategory.PRODUCT,
            description="Net Promoter Score from users",
        ),
        Signal(
            name="App Store Rating",
            category=SignalCategory.PRODUCT,
            description="iOS/Android app ratings (4.0+)",
        ),
        Signal(
            name="Feature Adoption Rate",
            category=SignalCategory.PRODUCT,
            description="Percentage of users using key features",
        ),
        Signal(
            name="Integration Ecosystem",
            category=SignalCategory.PRODUCT,
            description="Third-party integrations (Zapier, API partners)",
        ),
        Signal(
            name="Product-Market Fit Signals",
            category=SignalCategory.PRODUCT,
            description="Signs of PMF (usage metrics, retention)",
        ),
        Signal(
            name="Beta/Early Access Program",
            category=SignalCategory.PRODUCT,
            description="Active beta tester community",
        ),
        Signal(
            name="User Documentation Quality",
            category=SignalCategory.PRODUCT,
            description="Comprehensive help center/docs",
        ),
        Signal(
            name="Community Forum Activity",
            category=SignalCategory.PRODUCT,
            description="Active user community discussions",
        ),
    ]

    MARKET_SIGNALS = [
        Signal(
            name="Total Addressable Market (TAM)",
            category=SignalCategory.MARKET,
            description="Size of market opportunity",
        ),
        Signal(
            name="Market Share Percentage",
            category=SignalCategory.MARKET,
            description="Percentage of TAM captured",
        ),
        Signal(
            name="Competitive Differentiation",
            category=SignalCategory.MARKET,
            description="Unique value propositions vs competitors",
        ),
        Signal(
            name="Competitor Analysis Score",
            category=SignalCategory.MARKET,
            description="Evaluation vs top 3 competitors",
        ),
        Signal(
            name="Industry Award Count",
            category=SignalCategory.MARKET,
            description="Gartner, Forrester, or industry awards",
        ),
        Signal(
            name="Media Mention Frequency",
            category=SignalCategory.MARKET,
            description="Press coverage in past 6 months",
        ),
        Signal(
            name="Industry Event Presence",
            category=SignalCategory.MARKET,
            description="Speaking slots at major conferences",
        ),
        Signal(
            name="Analyst Report Coverage",
            category=SignalCategory.MARKET,
            description="Gartner Magic Quadrant, Forrester Wave",
        ),
        Signal(
            name="Brand Recognition Score",
            category=SignalCategory.MARKET,
            description="Brand awareness in target market",
        ),
        Signal(
            name="Pricing Power",
            category=SignalCategory.MARKET,
            description="Ability to raise prices without churn",
        ),
    ]

    OPERATIONAL_SIGNALS = [
        Signal(
            name="Process Maturity Level",
            category=SignalCategory.OPERATIONAL,
            description="Degree of documented processes",
        ),
        Signal(
            name="Compliance Certifications",
            category=SignalCategory.OPERATIONAL,
            description="ISO, SOC2, HIPAA, GDPR compliance",
        ),
        Signal(
            name="System Uptime Percentage",
            category=SignalCategory.OPERATIONAL,
            description="Service availability SLA compliance",
        ),
        Signal(
            name="Incident Response Time",
            category=SignalCategory.OPERATIONAL,
            description="Time to respond to critical incidents",
        ),
        Signal(
            name="Customer Support Response Time",
            category=SignalCategory.OPERATIONAL,
            description="Average time to first response",
        ),
        Signal(
            name="Automation Level",
            category=SignalCategory.OPERATIONAL,
            description="Percentage of manual processes automated",
        ),
        Signal(
            name="Data Center Redundancy",
            category=SignalCategory.OPERATIONAL,
            description="Multi-region/multi-cloud presence",
        ),
        Signal(
            name="Security Audit Frequency",
            category=SignalCategory.OPERATIONAL,
            description="Penetration tests, security reviews",
        ),
        Signal(
            name="Disaster Recovery Plan",
            category=SignalCategory.OPERATIONAL,
            description="RTO/RPO targets and testing",
        ),
        Signal(
            name="Office Space Expansion",
            category=SignalCategory.OPERATIONAL,
            description="Physical presence expansion",
        ),
    ]

    STRATEGIC_SIGNALS = [
        Signal(
            name="Series A Completion",
            category=SignalCategory.STRATEGIC,
            description="Successful Series A fundraise",
        ),
        Signal(
            name="Strategic Partnership Count",
            category=SignalCategory.STRATEGIC,
            description="Number of key partnerships",
        ),
        Signal(
            name="Acquisition of Competitors",
            category=SignalCategory.STRATEGIC,
            description="M&A activity to consolidate market",
        ),
        Signal(
            name="IPO Readiness",
            category=SignalCategory.STRATEGIC,
            description="Indicators of IPO preparation",
        ),
        Signal(
            name="Board Composition Quality",
            category=SignalCategory.STRATEGIC,
            description="Presence of industry veterans",
        ),
        Signal(
            name="Strategic Pivot Execution",
            category=SignalCategory.STRATEGIC,
            description="Successful repositioning of product",
        ),
        Signal(
            name="Investor Repeat Funding",
            category=SignalCategory.STRATEGIC,
            description="Previous investors participating in rounds",
        ),
        Signal(
            name="Strategic Investor Type",
            category=SignalCategory.STRATEGIC,
            description="Tier-1 VC, corporate venture, strategic",
        ),
        Signal(
            name="Customer Diversification",
            category=SignalCategory.STRATEGIC,
            description="Percentage from top 10 customers",
        ),
        Signal(
            name="Vertical Expansion Plans",
            category=SignalCategory.STRATEGIC,
            description="Moving into adjacent markets",
        ),
    ]

    ALL_SIGNALS = (
        GROWTH_SIGNALS
        + FINANCIAL_SIGNALS
        + TECHNICAL_SIGNALS
        + HIRING_SIGNALS
        + PRODUCT_SIGNALS
        + MARKET_SIGNALS
        + OPERATIONAL_SIGNALS
        + STRATEGIC_SIGNALS
    )

    @classmethod
    def get_signals_by_category(cls, category: SignalCategory) -> list[Signal]:
        """Get all signals in a category."""
        return [s for s in cls.ALL_SIGNALS if s.category == category]

    @classmethod
    def get_signal_count(cls) -> int:
        """Get total number of defined signals."""
        return len(cls.ALL_SIGNALS)

    @classmethod
    def get_category_distribution(cls) -> dict[str, int]:
        """Get count of signals per category."""
        distribution = {}
        for category in SignalCategory:
            distribution[category.value] = len(cls.get_signals_by_category(category))
        return distribution
