"""
Excel exporter for SolStein dashboards.

EPIC-005: Excel Export Improvements
- Replaces the monolithic generate_excel_report.py script
- Now delegates to ImprovedExcelExporter for better maintainability

This module provides backwards compatibility while using the improved implementation.
"""

# Re-export from improved implementation for backwards compatibility
from .excel_improved import (
    ImprovedExcelExporter as ExcelExporter,
    LayoutConstants,
    ColorPalette,
    ExcelStyles,
)

__all__ = ["ExcelExporter", "LayoutConstants", "ColorPalette", "ExcelStyles"]
