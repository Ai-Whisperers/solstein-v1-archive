"""Operational signal definitions.

Signals related to operational excellence and compliance.
"""

from ..base import Signal, SignalCategory

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
