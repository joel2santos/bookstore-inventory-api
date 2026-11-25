import os
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from application.books.interfaces import AbstractBookRepository, AbstractExchangeRateGateway
from domain.books.exceptions import BookNotFound, ExchangeRateUnavailable


class CalculateSellingPrice:
    """Calculate the local selling price for a book and persist it."""

    margin_percentage = 40

    def __init__(self, book_repo: AbstractBookRepository, rate_gateway: AbstractExchangeRateGateway):
        self.book_repo = book_repo
        self.rate_gateway = rate_gateway

    def execute(self, book_id: int) -> dict:
        book = self.book_repo.get(book_id)

        target_currency = os.environ.get("DEFAULT_LOCAL_CURRENCY", "VES")
        rate = self.rate_gateway.fetch_rate("USD", target_currency)

        cost_usd: Decimal = book.cost_usd
        cost_local = (cost_usd * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        selling_price_local = (
            cost_local * Decimal(self.margin_percentage / 100 + 1)
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        book.selling_price_local = selling_price_local
        self.book_repo.save(book)

        return {
            "book_id": book.id,
            "cost_usd": str(cost_usd),
            "exchange_rate": str(rate),
            "cost_local": str(cost_local),
            "margin_percentage": self.margin_percentage,
            "selling_price_local": str(selling_price_local),
            "currency": target_currency,
            "calculation_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
