from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class VoteType(StrEnum):
    UP = "up"
    DOWN = "down"


@dataclass(frozen=True)
class CommunityVote:
    proposal_id: str
    voter_id: str
    vote_type: VoteType
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class APISuggestion:
    proposal_id: str
    api_name: str
    category: str
    documentation_url: str
    use_case: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    labels: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PrioritizedSuggestion:
    suggestion: APISuggestion
    up_votes: int
    down_votes: int
    vote_score: float
    recency_boost: float
    final_priority_score: float


class CommunityPrioritizer:
    def __init__(self) -> None:
        self.vote_weight = 0.8
        self.recency_weight = 0.2

    def rank(self, suggestions: list[APISuggestion], votes: list[CommunityVote]) -> list[PrioritizedSuggestion]:
        grouped_votes: dict[str, list[CommunityVote]] = {}
        for vote in votes:
            grouped_votes.setdefault(vote.proposal_id, []).append(vote)

        prioritized: list[PrioritizedSuggestion] = []
        for suggestion in suggestions:
            proposal_votes = grouped_votes.get(suggestion.proposal_id, [])
            up_votes = sum(1 for vote in proposal_votes if vote.vote_type == VoteType.UP)
            down_votes = sum(1 for vote in proposal_votes if vote.vote_type == VoteType.DOWN)

            vote_score = _normalize_vote_score(up_votes, down_votes)
            recency_boost = _recency_boost(suggestion.created_at)
            final_priority = vote_score * self.vote_weight + recency_boost * self.recency_weight

            prioritized.append(
                PrioritizedSuggestion(
                    suggestion=suggestion,
                    up_votes=up_votes,
                    down_votes=down_votes,
                    vote_score=round(vote_score, 4),
                    recency_boost=round(recency_boost, 4),
                    final_priority_score=round(final_priority, 4),
                )
            )

        return sorted(prioritized, key=lambda item: item.final_priority_score, reverse=True)


def _normalize_vote_score(up_votes: int, down_votes: int) -> float:
    total = up_votes + down_votes
    if total == 0:
        return 0.5
    ratio = (up_votes - down_votes) / total
    return max(0.0, min(1.0, (ratio + 1) / 2))


def _recency_boost(created_at: datetime) -> float:
    now = datetime.now(timezone.utc)
    age_days = max(0.0, (now - created_at).total_seconds() / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.7
    if age_days <= 90:
        return 0.4
    return 0.2
