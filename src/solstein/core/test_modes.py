from __future__ import annotations

from dataclasses import dataclass
import os
import random


@dataclass(frozen=True)
class TestMode:
    name: str
    seed: int
    allow_synthetic: bool


def resolve_test_mode() -> TestMode:
    mode = os.getenv("SOLSTEIN_TEST_MODE", "mixed").strip().lower()
    seed_raw = os.getenv("SOLSTEIN_TEST_SEED", "1337")
    try:
        seed = int(seed_raw)
    except ValueError:
        seed = 1337

    if mode not in {"synthetic", "mixed", "strict_real"}:
        mode = "mixed"

    allow_synthetic = mode in {"synthetic", "mixed"}
    return TestMode(name=mode, seed=seed, allow_synthetic=allow_synthetic)


def apply_test_mode_seed() -> int:
    mode = resolve_test_mode()
    random.seed(mode.seed)
    return mode.seed
