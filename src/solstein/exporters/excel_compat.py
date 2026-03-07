"""Excel exporter for SolStein dashboards.

EPIC-005: Excel Export Improvements
EPIC-022: Refactored to use modular components

This module provides backwards compatibility while using the improved implementation.
"""

# Re-export from modular components for backwards compatibility
from .excel import (
    ColorPalette,
    ExcelStyles,
    LayoutConstants,
)
from .excel_improved import (
    ImprovedExcelExporter as ExcelExporter,
)


class TemplateExporter:
    def create_dashboard(self, profiles, output_path):
        raise NotImplementedError


__all__ = [
    "ExcelExporter",
    "LayoutConstants",
    "ColorPalette",
    "ExcelStyles",
    "TemplateExporter",
]
