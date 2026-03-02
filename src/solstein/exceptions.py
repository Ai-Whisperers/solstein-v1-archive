"""Custom exceptions for SolStein."""


class SolsteinError(Exception):
    """Base exception for all Solstein errors."""

    pass


class DataLoadError(SolsteinError):
    """Failed to load data from source."""

    pass


class ValidationError(SolsteinError):
    """Input validation failed."""

    pass


class LLMAvailabilityError(SolsteinError):
    """LLM service unavailable."""

    pass


class ConfigurationError(SolsteinError):
    """Configuration error."""

    pass


class ScoringError(SolsteinError):
    """Scoring calculation error."""

    pass


class ExportError(SolsteinError):
    """Export generation error."""

    pass




class SyntheticDataBlockingError(SolsteinError):
    """Raised when synthetic data is detected and should block execution."""
    pass
