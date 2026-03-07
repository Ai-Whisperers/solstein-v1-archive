"""Currency conversion for Solstein."""

from __future__ import annotations

from datetime import datetime

from loguru import logger

from .models import Currency


class CurrencyConverter:
    """
    Currency converter with live rates.

    Handles conversion between all major currencies including crypto.
    Preserves source currency throughout the chain.
    """

    def __init__(self):
        self._rates: dict[str, float] = {}
        self._last_update: datetime | None = None

    def set_rates(self, rates: dict[tuple[Currency, Currency], float]) -> None:
        """Set exchange rates."""
        for (from_curr, to_curr), rate in rates.items():
            key = f"{from_curr.value}_{to_curr.value}"
            self._rates[key] = rate
        self._last_update = datetime.now()

    def convert(
        self,
        amount: float,
        from_currency: Currency,
        to_currency: Currency,
    ) -> float:
        """Convert amount from one currency to another."""
        if from_currency == to_currency:
            return amount

        if from_currency == Currency.BTC or to_currency == Currency.BTC:
            btc_key = f"BTC_{Currency.USD.value}"
            if btc_key not in self._rates:
                logger.warning("BTC rate not available")
                return amount

            btc_rate = self._rates[btc_key]

            if from_currency == Currency.BTC:
                usd_amount = amount * btc_rate
            else:
                usd_amount = amount

            if to_currency == Currency.BTC:
                return usd_amount / btc_rate
            elif to_currency == Currency.USD:
                return usd_amount
            else:
                usd_to_target = self._rates.get(f"USD_{to_currency.value}", 1.0)
                return usd_amount * usd_to_target

        key = f"{from_currency.value}_{to_currency.value}"
        rate = self._rates.get(key)

        if rate is None:
            usd_key = f"{from_currency.value}_USD"
            usd_to_key = f"USD_{to_currency.value}"

            from_usd = self._rates.get(usd_key, 1.0)
            to_usd = self._rates.get(usd_to_key, 1.0)

            if from_usd and to_usd:
                return amount * (to_usd / from_usd)

            logger.warning(f"Currency rate not found: {from_currency} -> {to_currency}")
            return amount

        return amount * rate

    def get_rate(self, from_currency: Currency, to_currency: Currency) -> float | None:
        """Get exchange rate between two currencies."""
        if from_currency == to_currency:
            return 1.0

        key = f"{from_currency.value}_{to_currency.value}"
        return self._rates.get(key)

    @property
    def last_update(self) -> datetime | None:
        return self._last_update
