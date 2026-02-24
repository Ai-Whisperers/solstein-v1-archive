from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from solstein.infrastructure.database import Base
from solstein.infrastructure.database_models import (
    ContradictionRecord,
    ContradictionTransitionRecord,
    ResearchRunRecord,
)
from solstein.infrastructure.research_dual_write import (
    ContradictionLifecycleError,
    transition_contradiction_status,
)


def _create_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return Session(engine)


def _create_run(session: Session) -> ResearchRunRecord:
    run = ResearchRunRecord(
        run_id="run-contradiction-test",
        market="Test Market",
        seed_company="Test Seed",
        status="completed",
        strict_provenance=False,
        created_at=datetime.now(UTC),
    )
    session.add(run)
    session.commit()
    return run


def test_new_contradiction_defaults_open() -> None:
    with _create_session() as session:
        run = _create_run(session)
        contradiction = ContradictionRecord(
            run_id=run.id,
            company_id="c-1",
            metric_key="revenue",
            contradiction_type="variance",
            details={"metric": "revenue"},
        )
        session.add(contradiction)
        session.commit()

        stored = session.execute(
            select(ContradictionRecord).where(
                ContradictionRecord.id == contradiction.id
            )
        ).scalar_one()
        assert stored.status == "open"
        assert stored.updated_at is not None
        assert stored.resolved_at is None
        assert stored.ignored_at is None


def test_open_to_resolved_records_transition() -> None:
    with _create_session() as session:
        run = _create_run(session)
        contradiction = ContradictionRecord(
            run_id=run.id,
            company_id="c-2",
            metric_key="revenue",
            contradiction_type="variance",
            details={"metric": "revenue"},
            status="open",
            updated_at=datetime.now(UTC),
        )
        session.add(contradiction)
        session.commit()

        _ = transition_contradiction_status(
            session=session,
            contradiction_id=contradiction.id,
            to_status="resolved",
            changed_by="analyst",
            reason="validated",
        )

        stored = session.execute(
            select(ContradictionRecord).where(
                ContradictionRecord.id == contradiction.id
            )
        ).scalar_one()
        assert stored.status == "resolved"
        assert stored.resolved_at is not None
        assert stored.ignored_at is None

        transition = session.execute(
            select(ContradictionTransitionRecord).where(
                ContradictionTransitionRecord.contradiction_id == contradiction.id
            )
        ).scalar_one()
        assert transition.from_status == "open"
        assert transition.to_status == "resolved"
        assert transition.changed_at is not None
        assert transition.changed_by == "analyst"
        assert transition.reason == "validated"


def test_invalid_transition_rejected_without_mutation() -> None:
    with _create_session() as session:
        run = _create_run(session)
        created_at = datetime.now(UTC)
        contradiction = ContradictionRecord(
            run_id=run.id,
            company_id="c-3",
            metric_key="revenue",
            contradiction_type="variance",
            details={"metric": "revenue"},
            status="resolved",
            updated_at=created_at,
            resolved_at=created_at,
        )
        session.add(contradiction)
        session.commit()

        with pytest.raises(ContradictionLifecycleError) as exc_info:
            _ = transition_contradiction_status(
                session=session,
                contradiction_id=contradiction.id,
                to_status="open",
                changed_by="analyst",
                reason="reopen",
            )

        assert exc_info.value.code == "CONTRADICTION_INVALID_TRANSITION"

        stored = session.execute(
            select(ContradictionRecord).where(
                ContradictionRecord.id == contradiction.id
            )
        ).scalar_one()
        expected_created_at = created_at.replace(tzinfo=None)
        assert stored.status == "resolved"
        assert stored.resolved_at == expected_created_at
        assert stored.updated_at == expected_created_at
        transitions = session.execute(
            select(ContradictionTransitionRecord).where(
                ContradictionTransitionRecord.contradiction_id == contradiction.id
            )
        ).scalars()
        assert list(transitions) == []
