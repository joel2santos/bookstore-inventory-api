import os
from decimal import Decimal

import requests

from application.books.interfaces import AbstractExchangeRateGateway
from domain.books.exceptions import ExchangeRateUnavailable
from infrastructure.db.models import ExchangeRateConfig


class ExchangeRateGateway(AbstractExchangeRateGateway):
    """Fetch exchange rates from a JSON API, falling back to a stored default rate."""

    def fetch_rate(self, base_currency: str, target_currency: str) -> Decimal:
        url = os.environ.get(
            "EXCHANGE_RATE_API_URL",
            "https://api.exchangerate-api.com/v4/latest/USD",
        )
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            rate = data["rates"][target_currency]
            return Decimal(str(rate))
        except Exception:
            pass

        try:
            config = ExchangeRateConfig.get_singleton()
            rate = config.default_exchange_rate
            if rate is None:
                raise ExchangeRateUnavailable(
                    f"Exchange rate for {base_currency}->{target_currency} unavailable "
                    "(no live rate and no default_exchange_rate configured)"
                )
            return Decimal(str(rate))
        except ExchangeRateUnavailable:
            raise
        except Exception as exc:
            raise ExchangeRateUnavailable(
                f"Exchange rate for {base_currency}->{target_currency} unavailable"
            ) from exc
