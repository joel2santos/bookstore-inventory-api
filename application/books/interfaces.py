from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

from domain.books.entities import Book


class AbstractBookRepository(ABC):
    """Repository contract for Book domain entities."""

    @abstractmethod
    def get(self, book_id: int) -> Book:
        """
        Return the book with the given id.

        Raises:
            BookNotFound: if no book exists with the given id.
        """

    @abstractmethod
    def list(self, filters: Optional[dict] = None) -> list[Book]:
        """Return all books, optionally filtered."""

    @abstractmethod
    def search_by_category(self, category: str) -> list[Book]:
        """Return books in the given category."""

    @abstractmethod
    def low_stock(self, threshold: int) -> list[Book]:
        """Return books with stock_quantity below the threshold."""

    @abstractmethod
    def create(self, entity: Book) -> Book:
        """Create a new book and return the persisted entity with its id."""

    @abstractmethod
    def update(self, entity: Book) -> Book:
        """Update an existing book and return the persisted entity."""

    @abstractmethod
    def delete(self, book_id: int) -> None:
        """
        Delete the book with the given id.

        Raises:
            BookNotFound: if no book exists with the given id.
        """

    @abstractmethod
    def save(self, entity: Book) -> Book:
        """Create or update the book and return the persisted entity."""


class AbstractExchangeRateGateway(ABC):
    """Gateway contract for fetching exchange rates."""

    @abstractmethod
    def fetch_rate(self, base_currency: str, target_currency: str) -> Decimal:
        """
        Return the exchange rate from base_currency to target_currency.

        Raises:
            ExchangeRateUnavailable: if the rate cannot be obtained.
        """
