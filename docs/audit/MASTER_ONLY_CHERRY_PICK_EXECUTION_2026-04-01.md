# Master-Only Cherry-Pick Execution Result

Date: 2026-04-01
Branch: `reconcile/master-into-develop-2026-04-01`
Reference plan: `docs/audit/MASTER_ONLY_CHERRY_PICK_PLAN_2026-04-01.md`

## Scope Reviewed

This execution pass applied the review order defined in the plan:

1. verify whether `01f94def` is already materially present on `develop`
2. review only the narrow candidate deltas from `755eab6c`
3. avoid direct cherry-picks

## Result

No `master`-only code commit was approved for cherry-pick.

No manual port was approved in this execution pass.

## Verified Decisions

### `01f94def`

Status:

- closed as already materially present on `develop`

Evidence already verified in the plan remains valid:

- [src/solstein/security/jwt.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/security/jwt.py)
- [tests/conftest.py](/home/gestalt/Desktop/solstein/solstein/tests/conftest.py)
- [tests/unit/test_classification.py](/home/gestalt/Desktop/solstein/solstein/tests/unit/test_classification.py)
- [src/solstein/analytics/constants.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/analytics/constants.py)

Decision:

- no cherry-pick
- no manual port

### `755eab6c`

Status:

- reviewed narrowly and not approved for cherry-pick

## File-By-File Review Outcome

### `pyproject.toml`

Reviewed file:

- [pyproject.toml](/home/gestalt/Desktop/solstein/solstein/pyproject.toml)

Candidate deltas considered from `master`:

- `target-version = "py312"`
- per-file ignore for `src/solstein/connectors/**/__init__.py` -> `F401`
- per-file ignore for `tests/factories/__init__.py` -> `F401`
- additional ignore entries such as `B028`, `B905`, `F403`, `F405`, `F821`, `SIM105`, `SIM110`, `SIM117`, `N818`, `UP041`, `UP046`, `UP047`, `W293`

Decision:

- no `pyproject.toml` changes approved

Rationale:

- current connector packages and [tests/factories/__init__.py](/home/gestalt/Desktop/solstein/solstein/tests/factories/__init__.py) already pass Ruff without adding those new per-file ignores
- there is no current evidence that `py312` targeting is required to parse the reviewed code paths
- adding broad ignore entries without a failing current-file justification would increase masking rather than improve signal

### Connector Re-Export Ignores

Reviewed files included:

- [src/solstein/connectors/__init__.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/connectors/__init__.py)
- [src/solstein/connectors/academic/__init__.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/connectors/academic/__init__.py)
- [src/solstein/connectors/financial/__init__.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/connectors/financial/__init__.py)
- [src/solstein/connectors/news/__init__.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/connectors/news/__init__.py)

Decision:

- no new Ruff per-file ignore added

Rationale:

- `ruff check tests/factories/__init__.py src/solstein/connectors --output-format concise` passed without errors
- because the current code already passes, importing the `master` ignore exceptions would weaken the gate for no demonstrated benefit

### Auth / Dependency Exception Chaining

Reviewed file:

- [src/solstein/api/dependencies.py](/home/gestalt/Desktop/solstein/solstein/src/solstein/api/dependencies.py)

Decision:

- no port from `master`

Rationale:

- `develop` uses a Supabase-auth path that differs materially from the `master` implementation
- the `master` commit's `from None` pattern cannot be transplanted safely by assumption
- this path needs current-state review, not branch-history replay

## Additional Observation

Repository-wide Ruff still reports substantial unrelated debt outside the reviewed cherry-pick scope.

Observed result:

- `ruff check . --output-format concise` reported `260` errors

This does not justify importing `master`'s broad lint commit. It confirms the opposite: any cleanup should be targeted and owned explicitly, not backfilled through branch reconciliation.

## Practical Conclusion

Using the approved plan as written led to a conservative result:

- no direct cherry-picks
- no manual ports yet
- `develop` remains the canonical branch
- future reconciliation should continue as narrow current-state remediation, not `master` backporting

## Next Valid Follow-Up

If another reconciliation pass is needed, the next safe step is:

1. open a dedicated lint/config story on `develop`
2. fix current Ruff violations in bounded slices owned by subsystem
3. only then reconsider whether any leftover `master` diff still carries unique value
