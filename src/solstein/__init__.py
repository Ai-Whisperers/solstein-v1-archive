"""
SolStein - AI-Powered Competitive Intelligence Platform

The Viking sunstone revealed the sun through clouds.
Solstein reveals the competitive landscape through market fog.
"""

__version__ = "0.1.0"
__author__ = "AI Whisperers"
__email__ = "team@ai-whisperers.com"

import logging
import sys
from importlib import import_module
from typing import TYPE_CHECKING, Any

from loguru import logger

from .constants import ScoringWeights, Thresholds
from .domain.models import AIMaturity, Company, CompanyTier, ThreatLevel
from .exceptions import (
    DataLoadError,
    LLMAvailabilityError,
    SolsteinError,
    ValidationError,
)

if TYPE_CHECKING:
    from .data.unified import UnifiedCompanyLoader
    from .exporters.excel import ExcelExporter

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    level="INFO",
)


# Intercept standard logging
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame: Any = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


__all__ = [
    # Version
    "__version__",
    # Domain Models
    "Company",
    "CompanyTier",
    "ThreatLevel",
    "AIMaturity",
    # Data & I/O
    "UnifiedCompanyLoader",
    "ExcelExporter",
    # Exceptions
    "SolsteinError",
    "DataLoadError",
    "ValidationError",
    "LLMAvailabilityError",
    # Constants
    "ScoringWeights",
    "Thresholds",
    # Legacy exports for backward compatibility
    "logger",
    "InterceptHandler",
]


def __getattr__(name: str) -> Any:
    if name == "UnifiedCompanyLoader":
        return import_module("solstein.data.unified").UnifiedCompanyLoader
    if name == "ExcelExporter":
        return import_module("solstein.exporters.excel").ExcelExporter
    raise AttributeError(f"module 'solstein' has no attribute {name!r}")
