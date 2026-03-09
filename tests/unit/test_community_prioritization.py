from datetime import datetime, timedelta, timezone

from solstein.data_sources import APISuggestion, CommunityPrioritizer, CommunityVote, VoteType


def test_rank_orders_suggestions_by_priority_score() -> None:
    prioritizer = CommunityPrioritizer()
    now = datetime.now(timezone.utc)

    suggestions = [
        APISuggestion(
            proposal_id="s1",
            api_name="High Value News API",
            category="News and Media",
            documentation_url="https://example.com/news",
            use_case="Track competitor mentions",
            created_at=now,
        ),
        APISuggestion(
            proposal_id="s2",
            api_name="Low Signal API",
            category="Other",
            documentation_url="https://example.com/other",
            use_case="Unclear",
            created_at=now - timedelta(days=45),
        ),
    ]

    votes = [
        CommunityVote(proposal_id="s1", voter_id="u1", vote_type=VoteType.UP),
        CommunityVote(proposal_id="s1", voter_id="u2", vote_type=VoteType.UP),
        CommunityVote(proposal_id="s2", voter_id="u3", vote_type=VoteType.DOWN),
    ]

    ranked = prioritizer.rank(suggestions, votes)

    assert len(ranked) == 2
    assert ranked[0].suggestion.proposal_id == "s1"
    assert ranked[0].final_priority_score > ranked[1].final_priority_score


def test_rank_uses_neutral_vote_score_when_no_votes() -> None:
    prioritizer = CommunityPrioritizer()
    suggestion = APISuggestion(
        proposal_id="s3",
        api_name="No Vote API",
        category="Financial Data",
        documentation_url="https://example.com/financial",
        use_case="Potential source",
    )

    ranked = prioritizer.rank([suggestion], [])

    assert len(ranked) == 1
    assert ranked[0].vote_score == 0.5


def test_rank_applies_recency_boost() -> None:
    prioritizer = CommunityPrioritizer()
    now = datetime.now(timezone.utc)

    recent = APISuggestion(
        proposal_id="recent",
        api_name="Recent API",
        category="Social Media",
        documentation_url="https://example.com/recent",
        use_case="Recent signal source",
        created_at=now - timedelta(days=2),
    )
    old = APISuggestion(
        proposal_id="old",
        api_name="Old API",
        category="Social Media",
        documentation_url="https://example.com/old",
        use_case="Older source",
        created_at=now - timedelta(days=150),
    )

    votes = [
        CommunityVote(proposal_id="recent", voter_id="u1", vote_type=VoteType.UP),
        CommunityVote(proposal_id="old", voter_id="u2", vote_type=VoteType.UP),
    ]

    ranked = prioritizer.rank([old, recent], votes)

    assert ranked[0].suggestion.proposal_id == "recent"
    assert ranked[0].recency_boost > ranked[1].recency_boost
