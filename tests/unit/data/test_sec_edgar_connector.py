import pytest

from solstein.data.connectors.sec_edgar_connector import SECEdgarConnector


def test_sec_edgar_connector_default_confidence():
    assert SECEdgarConnector.DEFAULT_CONFIDENCE == pytest.approx(0.95)


def test_sec_edgar_connector_user_agent_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SEC_USER_AGENT", "Solstein Test UA")
    connector = SECEdgarConnector(user_agent=None)
    assert connector.user_agent == "Solstein Test UA"


def test_sec_edgar_connector_user_agent_param_overrides_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SEC_USER_AGENT", "Env UA")
    connector = SECEdgarConnector(user_agent="Param UA")
    assert connector.user_agent == "Param UA"


def test_fetch_filing_rejects_empty_ticker():
    connector = SECEdgarConnector(user_agent="Test UA")
    with pytest.raises(ValueError):
        connector.fetch_filing(ticker=" ", year=2024, form_type="10-K")


def test_fetch_filing_rejects_unsupported_form_type():
    connector = SECEdgarConnector(user_agent="Test UA")
    with pytest.raises(ValueError):
        connector.fetch_filing(ticker="AAPL", year=2024, form_type="8-K")


def test_fetch_filing_rejects_invalid_year():
    connector = SECEdgarConnector(user_agent="Test UA")
    with pytest.raises(ValueError):
        connector.fetch_filing(ticker="AAPL", year=1800, form_type="10-K")


def test_extract_minimal_metrics_from_fake_statements():
    import pandas as pd

    income_df = pd.DataFrame(
        [
            {
                "concept": "us-gaap_Revenues",
                "label": "Revenue",
                "standard_concept": "Revenue",
                "dimension": False,
                "abstract": False,
                "2024-09-28": 100.0,
            },
            {
                "concept": "us-gaap_GrossProfit",
                "label": "Gross profit",
                "standard_concept": "GrossProfit",
                "dimension": False,
                "abstract": False,
                "2024-09-28": 40.0,
            },
            {
                "concept": "us-gaap_OperatingIncomeLoss",
                "label": "Operating income",
                "standard_concept": "OperatingIncomeLoss",
                "dimension": False,
                "abstract": False,
                "2024-09-28": 10.0,
            },
        ]
    )
    balance_df = pd.DataFrame(
        [
            {
                "concept": "us-gaap_CashAndCashEquivalentsAtCarryingValue",
                "label": "Cash",
                "standard_concept": "CashAndCashEquivalents",
                "dimension": False,
                "abstract": False,
                "2024-09-28": 55.0,
            }
        ]
    )

    class FakeStatement:
        def __init__(self, df: pd.DataFrame):
            self._df = df

        def to_dataframe(self) -> pd.DataFrame:
            return self._df

    class FakeFinancials:
        def income_statement(self) -> FakeStatement:
            return FakeStatement(income_df)

        def balance_sheet(self) -> FakeStatement:
            return FakeStatement(balance_df)

    connector = SECEdgarConnector(user_agent="Test UA")
    metrics = connector._extract_minimal_metrics(FakeFinancials(), report_date_str="2024-09-28")

    assert metrics["revenue"] == 100.0
    assert metrics["gross_margin"] == pytest.approx(0.4)
    assert metrics["ebitda"] == 10.0
    assert metrics["cash_position"] == 55.0


def test_fetch_filing_retries_on_transient_error(monkeypatch: pytest.MonkeyPatch):
    import edgar
    import pandas as pd
    from datetime import date

    income_df = pd.DataFrame(
        [
            {
                "concept": "us-gaap_Revenues",
                "label": "Revenue",
                "standard_concept": "Revenue",
                "dimension": False,
                "abstract": False,
                "2024-09-28": 100.0,
            }
        ]
    )
    balance_df = pd.DataFrame(
        [
            {
                "concept": "us-gaap_CashAndCashEquivalentsAtCarryingValue",
                "label": "Cash",
                "standard_concept": "CashAndCashEquivalents",
                "dimension": False,
                "abstract": False,
                "2024-09-28": 55.0,
            }
        ]
    )

    class FakeStatement:
        def __init__(self, df: pd.DataFrame):
            self._df = df

        def to_dataframe(self) -> pd.DataFrame:
            return self._df

    class FakeFinancials:
        def income_statement(self) -> FakeStatement:
            return FakeStatement(income_df)

        def balance_sheet(self) -> FakeStatement:
            return FakeStatement(balance_df)

    class FakeFilingObj:
        financials = FakeFinancials()

    class FakeFiling:
        accession_no = "0000000000-00-000000"
        report_date = date(2024, 9, 28)
        filing_date = date(2024, 11, 1)

        def obj(self) -> FakeFilingObj:
            return FakeFilingObj()

    call_count = {"n": 0}

    class FakeCompany:
        def __init__(self, ticker: str):
            self.ticker = ticker

        def get_filings(self, *, form: str):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise TimeoutError("timed out")
            return [FakeFiling()]

    monkeypatch.setattr(edgar, "set_identity", lambda _identity: None)
    monkeypatch.setattr(edgar, "Company", FakeCompany)

    connector = SECEdgarConnector(user_agent="Test UA")
    sleep_calls: list[float] = []
    monkeypatch.setattr(connector, "_sleep", lambda seconds: sleep_calls.append(seconds))

    result = connector.fetch_filing(ticker="AAPL", year=2024, form_type="10-K")
    assert call_count["n"] == 2
    assert sleep_calls == [pytest.approx(connector.DEFAULT_BASE_SLEEP_S)]
    assert result["ticker"] == "AAPL"
    assert result["confidence"] == pytest.approx(0.95)
    assert result["cash_position"] == 55.0


def test_fetch_filing_retries_on_rate_limit(monkeypatch: pytest.MonkeyPatch):
    import edgar
    import pandas as pd
    from datetime import date
    from types import SimpleNamespace

    income_df = pd.DataFrame(
        [
            {
                "concept": "us-gaap_Revenues",
                "label": "Revenue",
                "standard_concept": "Revenue",
                "dimension": False,
                "abstract": False,
                "2024-09-28": 100.0,
            }
        ]
    )
    balance_df = pd.DataFrame(
        [
            {
                "concept": "us-gaap_CashAndCashEquivalentsAtCarryingValue",
                "label": "Cash",
                "standard_concept": "CashAndCashEquivalents",
                "dimension": False,
                "abstract": False,
                "2024-09-28": 55.0,
            }
        ]
    )

    class FakeStatement:
        def __init__(self, df: pd.DataFrame):
            self._df = df

        def to_dataframe(self) -> pd.DataFrame:
            return self._df

    class FakeFinancials:
        def income_statement(self) -> FakeStatement:
            return FakeStatement(income_df)

        def balance_sheet(self) -> FakeStatement:
            return FakeStatement(balance_df)

    class FakeFilingObj:
        financials = FakeFinancials()

    class FakeFiling:
        accession_no = "0000000000-00-000000"
        report_date = date(2024, 9, 28)
        filing_date = date(2024, 11, 1)

        def obj(self) -> FakeFilingObj:
            return FakeFilingObj()

    class RateLimitError(Exception):
        def __init__(self):
            super().__init__("Too Many Requests")
            self.response = SimpleNamespace(status_code=429)

    call_count = {"n": 0}

    class FakeCompany:
        def __init__(self, ticker: str):
            self.ticker = ticker

        def get_filings(self, *, form: str):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RateLimitError()
            return [FakeFiling()]

    monkeypatch.setattr(edgar, "set_identity", lambda _identity: None)
    monkeypatch.setattr(edgar, "Company", FakeCompany)

    connector = SECEdgarConnector(user_agent="Test UA")
    sleep_calls: list[float] = []
    monkeypatch.setattr(connector, "_sleep", lambda seconds: sleep_calls.append(seconds))

    result = connector.fetch_filing(ticker="AAPL", year=2024, form_type="10-K")
    assert call_count["n"] == 2
    assert sleep_calls == [pytest.approx(connector.DEFAULT_RATE_LIMIT_SLEEP_S)]
    assert result["ticker"] == "AAPL"


def test_fetch_filing_raises_without_retry_on_non_retryable_error(monkeypatch: pytest.MonkeyPatch):
    import edgar

    class FakeCompany:
        def __init__(self, ticker: str):
            self.ticker = ticker

        def get_filings(self, *, form: str):
            raise Exception("boom")

    monkeypatch.setattr(edgar, "set_identity", lambda _identity: None)
    monkeypatch.setattr(edgar, "Company", FakeCompany)

    connector = SECEdgarConnector(user_agent="Test UA")
    sleep_calls: list[float] = []
    monkeypatch.setattr(connector, "_sleep", lambda seconds: sleep_calls.append(seconds))

    with pytest.raises(RuntimeError):
        connector.fetch_filing(ticker="AAPL", year=2024, form_type="10-K")
    assert sleep_calls == []
