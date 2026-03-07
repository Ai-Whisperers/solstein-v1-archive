"""Hiring signal definitions.

Signals related to team growth and hiring.
"""

from ..base import Signal, SignalCategory

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
