"""STORY-256: Regression tests for runtime selection behavior.

Verify that:
1. pipeline.run_market_intelligence is the canonical synchronous entry-point
2. pipeline_async no longer exports a run_market_intelligence alias
3. The deprecated feature flag emits a DeprecationWarning
4. The canonical pipeline module carries the CANONICAL RUNTIME banner
"""

import warnings


class TestCanonicalRuntimeSelection:
    """Verify the canonical pipeline is the sole synchronous entry-point."""

    def test_pipeline_exports_run_market_intelligence(self) -> None:
        """The synchronous run_market_intelligence lives in pipeline module."""
        from solstein.research.pipeline import run_market_intelligence

        assert callable(run_market_intelligence)

    def test_pipeline_async_exports_async_variant(self) -> None:
        """The async module exports run_market_intelligence_async."""
        from solstein.research.pipeline_async import run_market_intelligence_async

        assert callable(run_market_intelligence_async)

    def test_pipeline_async_no_longer_exports_sync_alias(self) -> None:
        """The backward-compat alias was removed from pipeline_async (STORY-256)."""
        import solstein.research.pipeline_async as mod

        assert not hasattr(mod, "run_market_intelligence"), (
            "pipeline_async should no longer export run_market_intelligence alias"
        )

    def test_canonical_pipeline_has_canonical_banner(self) -> None:
        """pipeline.py docstring includes CANONICAL RUNTIME marker."""
        import solstein.research.pipeline as mod

        assert "CANONICAL RUNTIME" in (mod.__doc__ or ""), (
            "pipeline.py must carry the CANONICAL RUNTIME docstring banner"
        )


class TestDeprecatedFeatureFlag:
    """Verify the deprecated feature_new_unified_loader emits warnings."""

    def test_feature_flag_true_emits_deprecation_warning(self) -> None:
        """Setting feature_new_unified_loader=True triggers DeprecationWarning."""
        from solstein.config import Settings
        from solstein.core.feature_flags import FeatureFlags

        settings = Settings(feature_new_unified_loader=True)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            FeatureFlags.from_settings(settings)

        deprecation_msgs = [
            w for w in caught
            if issubclass(w.category, DeprecationWarning)
            and "FEATURE_NEW_UNIFIED_LOADER" in str(w.message)
        ]
        assert len(deprecation_msgs) >= 1, (
            "Expected DeprecationWarning for feature_new_unified_loader=True"
        )

    def test_feature_flag_false_no_warning(self) -> None:
        """Default (False) does not emit a DeprecationWarning."""
        from solstein.config import Settings
        from solstein.core.feature_flags import FeatureFlags

        settings = Settings(feature_new_unified_loader=False)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            FeatureFlags.from_settings(settings)

        deprecation_msgs = [
            w for w in caught
            if issubclass(w.category, DeprecationWarning)
            and "FEATURE_NEW_UNIFIED_LOADER" in str(w.message)
        ]
        assert len(deprecation_msgs) == 0, (
            "Default flag value should not emit DeprecationWarning"
        )
