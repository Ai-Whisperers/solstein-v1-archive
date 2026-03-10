from __future__ import annotations

import pytest

from solstein.research.contracts import PipelineRunState, RunState, RunStateTransitionError


def test_pipeline_run_state_valid_transitions() -> None:
    run = PipelineRunState(run_id="run-1")

    run.transition_to(RunState.RUNNING)
    run.transition_to(RunState.PAUSED, reason="manual hold")
    run.transition_to(RunState.RUNNING)
    run.transition_to(RunState.COMPLETED)

    assert run.state == RunState.COMPLETED
    assert run.reason == "manual hold"


def test_pipeline_run_state_invalid_transition_raises() -> None:
    run = PipelineRunState(run_id="run-2")

    with pytest.raises(RunStateTransitionError, match="Invalid run-state transition"):
        run.transition_to(RunState.COMPLETED)


def test_pipeline_run_state_terminal_states_do_not_transition() -> None:
    run = PipelineRunState(run_id="run-3", state=RunState.FAILED)

    with pytest.raises(RunStateTransitionError):
        run.transition_to(RunState.RUNNING)
