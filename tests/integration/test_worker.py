"""
Integration tests for SolStein background tasks (Celery workers).

Design note on GrowthScorer mocking:
    tasks.py imports GrowthScorer with `from .analytics.scoring import GrowthScorer`
    INSIDE the function body, NOT at module level. This creates a local binding
    that cannot be intercepted by patching either the source module or the tasks module.

    The tests below therefore use the REAL GrowthScorer (it's pure Python, no I/O)
    and only mock the I/O dependencies (repository and exporter). This produces
    tests that are honest about what they exercise.
"""

import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Tests for batch_score_companies
# ---------------------------------------------------------------------------

@patch("solstein.tasks.JsonFileRepository")
@patch("solstein.tasks.get_settings")
def test_batch_score_companies_task(mock_get_settings, mock_repo_class, mock_company):
    """Verify that batch scoring task processes all companies from the repository."""
    from solstein.tasks import batch_score_companies

    mock_repo = MagicMock()
    mock_repo.get_all.return_value = [mock_company]
    mock_repo_class.return_value = mock_repo
    mock_get_settings.return_value = MagicMock()

    # Run task synchronously with real scorer
    result = batch_score_companies(filters={"industry": "Technology"})

    assert result["total_processed"] == 1
    mock_repo.get_all.assert_called_once()


@patch("solstein.tasks.JsonFileRepository")
@patch("solstein.tasks.get_settings")
def test_batch_score_companies_empty_repo(mock_get_settings, mock_repo_class):
    """batch_score_companies must return gracefully when repo returns no companies."""
    from solstein.tasks import batch_score_companies

    mock_repo = MagicMock()
    mock_repo.get_all.return_value = []
    mock_repo_class.return_value = mock_repo
    mock_get_settings.return_value = MagicMock()

    result = batch_score_companies(filters={})

    assert result["total_processed"] == 0
    assert result["results"] == []


@patch("solstein.tasks.JsonFileRepository")
@patch("solstein.tasks.get_settings")
def test_batch_score_companies_result_structure(mock_get_settings, mock_repo_class, mock_company):
    """Each result dict must contain expected keys."""
    from solstein.tasks import batch_score_companies

    mock_repo = MagicMock()
    mock_repo.get_all.return_value = [mock_company]
    mock_repo_class.return_value = mock_repo
    mock_get_settings.return_value = MagicMock()

    result = batch_score_companies(filters={})

    assert len(result["results"]) == 1
    entry = result["results"][0]
    assert "company_id" in entry
    assert "company_name" in entry
    assert "growth_score" in entry
    assert "classification" in entry
    assert entry["status"] == "success"


@patch("solstein.tasks.JsonFileRepository")
@patch("solstein.tasks.get_settings")
def test_batch_score_classification_neutral(mock_get_settings, mock_repo_class, mock_company):
    """
    Company from shared fixture has growth_rate=15.0, profit_margin=10.0.
    Expected growth_score: base(5.0) + 15/20=0.75 + margin_med(1.0) = 6.75 → 'Neutral'
    """
    from solstein.tasks import batch_score_companies

    mock_repo = MagicMock()
    mock_repo.get_all.return_value = [mock_company]
    mock_repo_class.return_value = mock_repo
    mock_get_settings.return_value = MagicMock()

    result = batch_score_companies(filters={})
    assert result["results"][0]["classification"] == "Neutral"


@patch("solstein.tasks.JsonFileRepository")
@patch("solstein.tasks.get_settings")
def test_batch_score_classification_rocket(mock_get_settings, mock_repo_class):
    """Company with high growth should be classified as 'Rocket'."""
    from solstein.tasks import batch_score_companies
    from tests.factories import make_rocket_company

    rocket = make_rocket_company()
    mock_repo = MagicMock()
    mock_repo.get_all.return_value = [rocket]
    mock_repo_class.return_value = mock_repo
    mock_get_settings.return_value = MagicMock()

    result = batch_score_companies(filters={})
    assert result["results"][0]["classification"] == "Rocket"


@patch("solstein.tasks.JsonFileRepository")
@patch("solstein.tasks.get_settings")
def test_batch_score_classification_dinosaur(mock_get_settings, mock_repo_class):
    """Company with negative growth should be classified as 'Dinosaur'."""
    from solstein.tasks import batch_score_companies
    from tests.factories import make_dinosaur_company

    dino = make_dinosaur_company()
    mock_repo = MagicMock()
    mock_repo.get_all.return_value = [dino]
    mock_repo_class.return_value = mock_repo
    mock_get_settings.return_value = MagicMock()

    result = batch_score_companies(filters={})
    assert result["results"][0]["classification"] == "Dinosaur"


# ---------------------------------------------------------------------------
# Tests for export_marketing_report
# ---------------------------------------------------------------------------

@patch("solstein.tasks.JsonFileRepository")
@patch("solstein.tasks.ExcelExporter")
@patch("solstein.tasks.get_settings")
def test_export_marketing_report_task(mock_get_settings, mock_exporter_class, mock_repo_class, mock_company):
    """Verify that export task triggers the Excel exporter."""
    from solstein.tasks import export_marketing_report

    mock_repo = MagicMock()
    mock_repo.get_all.return_value = [mock_company]
    mock_repo_class.return_value = mock_repo

    mock_exporter = MagicMock()
    mock_exporter_class.return_value = mock_exporter

    mock_settings = MagicMock()
    mock_settings.data.export_dir.__truediv__.return_value = "mock_output_path"
    mock_get_settings.return_value = mock_settings

    result = export_marketing_report(filters={}, output_filename="test.xlsx")

    assert "mock_output_path" in str(result)
    mock_exporter.create_dashboard.assert_called_once()


@patch("solstein.tasks.JsonFileRepository")
@patch("solstein.tasks.ExcelExporter")
@patch("solstein.tasks.get_settings")
def test_export_marketing_report_no_companies(mock_get_settings, mock_exporter_class, mock_repo_class):
    """export_marketing_report must return 'No data found' when repo is empty."""
    from solstein.tasks import export_marketing_report

    mock_repo = MagicMock()
    mock_repo.get_all.return_value = []
    mock_repo_class.return_value = mock_repo
    mock_get_settings.return_value = MagicMock()

    result = export_marketing_report(filters={}, output_filename="test.xlsx")

    assert result == "No data found"
    # ExcelExporter must NOT have been called
    mock_exporter_class.return_value.create_dashboard.assert_not_called()
