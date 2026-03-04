from __future__ import annotations

import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Protocol, cast, runtime_checkable

import pandas as pd
from loguru import logger

from solstein.data.connectors.constants import (
    SEC_EDGAR_DEFAULT_BASE_SLEEP_S,
    SEC_EDGAR_DEFAULT_CONFIDENCE,
    SEC_EDGAR_DEFAULT_MAX_ATTEMPTS,
    SEC_EDGAR_DEFAULT_MAX_SLEEP_S,
    SEC_EDGAR_DEFAULT_RATE_LIMIT_SLEEP_S,
)


class CompanyNotFoundError(RuntimeError):
    pass


@runtime_checkable
class FilingProtocol(Protocol):
    accession_no: str | None
    filing_date: date | None
    report_date: date | None

    def obj(self) -> object: ...


@runtime_checkable
class StatementProtocol(Protocol):
    def to_dataframe(self) -> pd.DataFrame: ...


@runtime_checkable
class FinancialsProtocol(Protocol):
    def income_statement(self) -> StatementProtocol: ...

    def balance_sheet(self) -> StatementProtocol: ...


@dataclass(frozen=True)
class SecFilingRequest:
    ticker: str
    year: int
    form_type: str


class SECEdgarConnector:
    DEFAULT_CONFIDENCE: float = SEC_EDGAR_DEFAULT_CONFIDENCE

    DEFAULT_MAX_ATTEMPTS: int = SEC_EDGAR_DEFAULT_MAX_ATTEMPTS

    DEFAULT_BASE_SLEEP_S: float = SEC_EDGAR_DEFAULT_BASE_SLEEP_S

    DEFAULT_MAX_SLEEP_S: float = SEC_EDGAR_DEFAULT_MAX_SLEEP_S

    DEFAULT_RATE_LIMIT_SLEEP_S: float = SEC_EDGAR_DEFAULT_RATE_LIMIT_SLEEP_S

    def __init__(self, user_agent: str | None = None):
        from solstein.config import get_settings

        settings = get_settings()
        self.user_agent: str = (
            user_agent or settings.sec_user_agent or "Solstein/0.1 (contact: contact@ai-whisperers.com)"
        )

    def _sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def fetch_filing(self, ticker: str, year: int, form_type: str) -> dict[str, object]:
        request = SecFilingRequest(
            ticker=ticker.upper().strip(),
            year=year,
            form_type=form_type.upper().strip(),
        )
        logger.debug("SEC EDGAR fetch requested: {}", request)

        if not request.ticker:
            raise ValueError("ticker is required")

        if request.form_type not in {"10-K", "10-Q"}:
            raise ValueError(f"Unsupported form_type={request.form_type!r}; expected '10-K' or '10-Q'")

        if request.year < 1994 or request.year > date.today().year + 1:
            raise ValueError(f"Invalid year={request.year}")

        try:
            from edgar import Company, set_identity
        except Exception as e:
            logger.error("SEC EDGAR dependency import failed: {}", e)
            raise

        context = {"ticker": request.ticker, "form_type": request.form_type, "year": request.year}
        max_attempts = self.DEFAULT_MAX_ATTEMPTS

        for attempt in range(1, max_attempts + 1):
            try:
                set_identity(self.user_agent)
                company = Company(request.ticker)
                filings = company.get_filings(form=request.form_type)

                filings_typed = cast(Iterable[FilingProtocol], filings)
                filing = self._select_filing_for_year(filings=filings_typed, year=request.year)
                if filing is None:
                    raise CompanyNotFoundError(
                        f"No SEC filings found for ticker={request.ticker!r} form_type={request.form_type!r} year={request.year}"
                    )

                filing_obj = filing.obj()
                financials_raw = getattr(filing_obj, "financials", None)
                financials = financials_raw if isinstance(financials_raw, FinancialsProtocol) else None

                report_date = filing.report_date
                filing_date = filing.filing_date
                report_date_str = report_date.isoformat() if report_date is not None else None

                metrics = self._extract_minimal_metrics(financials=financials, report_date_str=report_date_str)

                return {
                    "ticker": request.ticker,
                    "form_type": request.form_type,
                    "year": request.year,
                    "accession_no": getattr(filing, "accession_no", None),
                    "filing_date": filing_date.isoformat() if filing_date is not None else None,
                    "report_date": report_date_str,
                    "confidence": self.DEFAULT_CONFIDENCE,
                    **metrics,
                }
            except ValueError:
                raise
            except CompanyNotFoundError:
                raise
            except Exception as e:
                is_rate_limited = self._is_rate_limit_error(e)
                is_retryable = self._is_retryable_error(e)

                if not is_retryable or attempt >= max_attempts:
                    logger.error(
                        "SEC EDGAR fetch failed after {} attempt(s) for {}: {}",
                        attempt,
                        context,
                        e,
                    )
                    raise RuntimeError(
                        f"SEC EDGAR fetch failed for ticker={request.ticker!r} form_type={request.form_type!r} year={request.year}"
                    ) from e

                sleep_s = self._backoff_sleep_s(attempt=attempt, is_rate_limited=is_rate_limited)
                logger.warning(
                    "SEC EDGAR transient failure (attempt {}/{}), sleeping {}s for {}: {}",
                    attempt,
                    max_attempts,
                    sleep_s,
                    context,
                    type(e).__name__,
                )
                self._sleep(sleep_s)

        raise RuntimeError(
            f"SEC EDGAR fetch failed for ticker={request.ticker!r} form_type={request.form_type!r} year={request.year}"
        )

    def _is_rate_limit_error(self, error: Exception) -> bool:
        message = str(error)
        if "Too Many Requests" in message:
            return True
        if " 429" in message or "429" in message:
            return True

        response = getattr(error, "response", None)
        status_code = getattr(response, "status_code", None)
        return status_code == 429

    def _is_retryable_error(self, error: Exception) -> bool:
        if self._is_rate_limit_error(error):
            return True

        if isinstance(error, (TimeoutError, ConnectionError, OSError)):
            return True

        message = str(error)
        if "timed out" in message.lower():
            return True

        response = getattr(error, "response", None)
        status_code = getattr(response, "status_code", None)
        if isinstance(status_code, int) and status_code >= 500:
            return True

        return False

    def _backoff_sleep_s(self, *, attempt: int, is_rate_limited: bool) -> float:
        if is_rate_limited:
            return self.DEFAULT_RATE_LIMIT_SLEEP_S

        sleep_s = self.DEFAULT_BASE_SLEEP_S * (2 ** (attempt - 1))
        return min(sleep_s, self.DEFAULT_MAX_SLEEP_S)

    def _select_filing_for_year(self, filings: Iterable[FilingProtocol], year: int) -> FilingProtocol | None:
        candidates: list[FilingProtocol] = []
        for filing in list(filings):
            report_date = filing.report_date
            if report_date is not None and report_date.year == year:
                candidates.append(filing)

        if not candidates:
            for filing in list(filings):
                filing_date = filing.filing_date
                if filing_date is not None and filing_date.year == year:
                    candidates.append(filing)

        if not candidates:
            return None

        candidates.sort(key=lambda f: f.filing_date.toordinal() if f.filing_date is not None else 0)
        return candidates[-1]

    def _extract_minimal_metrics(
        self, financials: FinancialsProtocol | None, report_date_str: str | None
    ) -> dict[str, object]:
        if financials is None:
            return {
                "revenue": None,
                "gross_margin": None,
                "ebitda": None,
                "cash_position": None,
            }

        try:
            income_df = financials.income_statement().to_dataframe()
            balance_df = financials.balance_sheet().to_dataframe()
        except Exception as e:
            logger.error("SEC EDGAR statement to_dataframe failed: {}", e)
            return {
                "revenue": None,
                "gross_margin": None,
                "ebitda": None,
                "cash_position": None,
            }

        period_col = report_date_str if report_date_str in income_df.columns else None
        if period_col is None:
            period_cols = [c for c in income_df.columns if isinstance(c, str) and c[:4].isdigit()]
            period_col = period_cols[0] if period_cols else None

        revenue = self._pick_value(
            income_df,
            period_col,
            standard_concepts={"Revenue"},
            concept_contains={"Revenues"},
            label_contains={"Net sales", "Revenue"},
        )
        gross_profit = self._pick_value(
            income_df,
            period_col,
            standard_concepts={"GrossProfit"},
            concept_contains={"GrossProfit"},
            label_contains={"Gross profit"},
        )

        gross_margin: float | None = None
        if isinstance(revenue, (int, float)) and revenue:
            if isinstance(gross_profit, (int, float)):
                gross_margin = gross_profit / revenue

        ebitda = self._pick_value(
            income_df,
            period_col,
            standard_concepts=set(),
            concept_contains={"EBITDA", "OperatingIncomeLoss"},
            label_contains={"EBITDA", "Operating income"},
        )

        cash_position = self._pick_value(
            balance_df,
            report_date_str if report_date_str in balance_df.columns else None,
            standard_concepts={"CashAndCashEquivalents"},
            concept_contains={"CashAndCashEquivalents"},
            label_contains={"Cash"},
        )

        return {
            "revenue": float(revenue) if isinstance(revenue, (int, float)) else None,
            "gross_margin": float(gross_margin) if isinstance(gross_margin, (int, float)) else None,
            "ebitda": float(ebitda) if isinstance(ebitda, (int, float)) else None,
            "cash_position": float(cash_position) if isinstance(cash_position, (int, float)) else None,
        }

    def _pick_value(
        self,
        df: pd.DataFrame,
        period_col: str | None,
        *,
        standard_concepts: set[str],
        concept_contains: set[str],
        label_contains: set[str],
    ) -> float | None:
        if period_col is None:
            return None

        candidates = cast(pd.DataFrame, df.copy())
        if "dimension" in candidates.columns:
            candidates = cast(pd.DataFrame, candidates[candidates["dimension"] == False])  # noqa: E712
        if "abstract" in candidates.columns:
            candidates = cast(pd.DataFrame, candidates[candidates["abstract"] == False])  # noqa: E712

        mask = pd.Series([False] * len(candidates), index=cast(object, candidates.index))
        if standard_concepts and "standard_concept" in candidates.columns:
            mask |= candidates["standard_concept"].isin(list(standard_concepts))
        if concept_contains and "concept" in candidates.columns:
            for needle in concept_contains:
                mask |= candidates["concept"].astype(str).str.contains(needle, case=False, na=False)
        if label_contains and "label" in candidates.columns:
            for needle in label_contains:
                mask |= candidates["label"].astype(str).str.contains(needle, case=False, na=False)

        matched = cast(pd.DataFrame, candidates[mask])
        if matched.empty:
            return None

        value = matched.iloc[0].get(period_col)
        try:
            if pd.isna(value):
                return None
        except Exception:
            return None

        return float(value) if isinstance(value, (int, float)) else None
