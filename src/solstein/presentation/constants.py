"""Constants for presentation, templates, and data quality indicators."""

# Adaptive Template Thresholds
ADAPTIVE_TEMPLATE_SPARSE_THRESHOLD = 40  # < 40% complete = sparse
ADAPTIVE_TEMPLATE_MODERATE_THRESHOLD = 70  # 40-70% = moderate
ADAPTIVE_TEMPLATE_RICH_THRESHOLD = 70  # > 70% = rich

# Data Quality Indicators
DATA_QUALITY_AI_SCORE_THRESHOLD = 5  # Threshold for AI score consistency check

# Narrative Consistency Checker
NARRATIVE_CONSISTENCY_AI_MODERATE_MIN = 4  # Moderate AI maturity minimum
NARRATIVE_CONSISTENCY_AI_MODERATE_MAX = 6  # Moderate AI maturity maximum
NARRATIVE_CONSISTENCY_AI_STRONG_MIN = 6  # Strong AI maturity minimum
NARRATIVE_CONSISTENCY_AI_STRONG_MAX = 8  # Strong AI maturity maximum
NARRATIVE_CONSISTENCY_AI_VERY_STRONG_MIN = 8  # Very strong AI maturity minimum
NARRATIVE_CONSISTENCY_AI_VERY_STRONG_MAX = 10  # Very strong AI maturity maximum

NARRATIVE_CONSISTENCY_PHOENIX_MIN = 7.0  # Phoenix classification minimum
NARRATIVE_CONSISTENCY_PHOENIX_MAX = 10.0  # Phoenix classification maximum
NARRATIVE_CONSISTENCY_SALT_MIN = 4.0  # Salt classification minimum
NARRATIVE_CONSISTENCY_SALT_MAX = 7.0  # Salt classification maximum
NARRATIVE_CONSISTENCY_LEAD_MIN = 0.0  # Lead classification minimum
NARRATIVE_CONSISTENCY_LEAD_MAX = 4.0  # Lead classification maximum

# Export Configuration
EXPORT_MARKDOWN_TOP_COMPANIES_LIMIT = 20  # Maximum companies to export
EXPORT_COMPETITORS_LIMIT = 10  # Maximum competitors to show
EXPORT_COMPETITORS_BRIEF_LIMIT = 5  # Maximum competitors for brief format
EXPORT_CUSTOMERS_LIMIT = 10  # Maximum customers to show
EXPORT_TECH_STACK_LIMIT = 5  # Maximum tech stack items
EXPORT_AI_SCORE_THRESHOLD = 3  # Threshold for AI score classification
EXPORT_REVENUE_THRESHOLD_B = 20  # Revenue threshold in billions
EXPORT_ERROR_MAX_LENGTH = 60  # Maximum error message length
EXPORT_ERROR_TRUNCATE_LENGTH = 57  # Length to truncate error to
EXPORT_FIELD_NAME_MAX_LENGTH = 40  # Maximum field name length

# Excel Export
EXCEL_TITLE_FONT_SIZE = 18  # Title font size
EXCEL_HEADER_FONT_SIZE = 12  # Header font size
EXCEL_SUBHEADER_FONT_SIZE = 11  # Subheader font size
EXCEL_DATA_FONT_SIZE = 10  # Data font size
EXCEL_TITLE_ROW_HEIGHT = 40  # Title row height
EXCEL_HEADER_ROW_HEIGHT = 30  # Header row height
EXCEL_COLUMN_WIDTH_NARROW = 12  # Narrow column width
EXCEL_COLUMN_WIDTH_MEDIUM = 20  # Medium column width
EXCEL_COLUMN_WIDTH_WIDE = 35  # Wide column width
EXCEL_COLUMN_WIDTH_VERY_WIDE = 50  # Very wide column width
