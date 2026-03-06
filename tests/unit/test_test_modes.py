from _pytest.monkeypatch import MonkeyPatch

from solstein.core.test_modes import apply_test_mode_seed, resolve_test_mode


def test_resolve_test_mode_defaults() -> None:
    mode = resolve_test_mode()
    assert mode.name == "mixed"
    assert mode.seed == 1337
    assert mode.allow_synthetic is True


def test_resolve_test_mode_strict_real(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("SOLSTEIN_TEST_MODE", "strict_real")
    monkeypatch.setenv("SOLSTEIN_TEST_SEED", "42")

    mode = resolve_test_mode()

    assert mode.name == "strict_real"
    assert mode.seed == 42
    assert mode.allow_synthetic is False


def test_resolve_test_mode_invalid_seed_fallback(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("SOLSTEIN_TEST_MODE", "synthetic")
    monkeypatch.setenv("SOLSTEIN_TEST_SEED", "not-int")

    mode = resolve_test_mode()

    assert mode.name == "synthetic"
    assert mode.seed == 1337
    assert mode.allow_synthetic is True


def test_apply_test_mode_seed_is_deterministic(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("SOLSTEIN_TEST_MODE", "mixed")
    monkeypatch.setenv("SOLSTEIN_TEST_SEED", "2026")

    seed = apply_test_mode_seed()

    assert seed == 2026
