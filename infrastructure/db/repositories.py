"""Django implementation of the Book repository contract."""

from decimal import Decimal
from typing import Optional

from application.books.interfaces import AbstractBookRepository
from domain.books.entities import Book
from domain.books.exceptions import BookNotFound, ExchangeRateUnavailable
from infrastructure.db.models import Book as DjangoBook


class DjangoBookRepository(AbstractBookRepository):
    """BookRepository backed by the Django ORM."""

    def get(self, book_id: int) -> Book:
        try:
            row = DjangoBook.objects.get(id=book_id)
        except DjangoBook.DoesNotExist as exc:
            raise BookNotFound(f"Book with id {book_id} not found") from exc
        return self._to_entity(row)

    def list(self, filters: Optional[dict] = None) -> list[Book]:
        queryset = DjangoBook.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return [self._to_entity(row) for row in queryset]

    def search_by_category(self, category: str) -> list[Book]:
        rows = DjangoBook.objects.filter(category=category)
        return [self._to_entity(row) for row in rows]

    def low_stock(self, threshold: int) -> list[Book]:
        rows = DjangoBook.objects.filter(stock_quantity__lt=threshold)
        return [self._to_entity(row) for row in rows]

    def create(self, entity: Book) -> Book:
        row = DjangoBook.objects.create(
            title=entity.title,
            author=entity.author,
            category=entity.category,
            isbn=entity.isbn,
            supplier_country=entity.supplier_country,
            cost_usd=entity.cost_usd,
            selling_price_local=entity.selling_price_local,
            stock_quantity=entity.stock_quantity,
        )
        return self._to_entity(row)

    def update(self, entity: Book) -> Book:
        if entity.id is None:
            raise ValueError("Cannot update a book without an id")
        try:
            row = DjangoBook.objects.get(id=entity.id)
        except DjangoBook.DoesNotExist as exc:
            raise BookNotFound(f"Book with id {entity.id} not found") from exc
        row.title = entity.title
        row.author = entity.author
        row.category = entity.category
        row.isbn = entity.isbn
        row.supplier_country = entity.supplier_country
        row.cost_usd = entity.cost_usd
        row.selling_price_local = entity.selling_price_local
        row.stock_quantity = entity.stock_quantity
        row.save()
        return self._to_entity(row)

    def delete(self, book_id: int) -> None:
        deleted, _ = DjangoBook.objects.filter(id=book_id).delete()
        if deleted == 0:
            raise BookNotFound(f"Book with id {book_id} not found")

    def save(self, entity: Book) -> Book:
        if entity.id is None:
            return self.create(entity)
        return self.update(entity)

    @staticmethod
    def _to_entity(row: DjangoBook) -> Book:
        return Book(
            id=row.id,
            title=row.title,
            author=row.author,
            category=row.category,
            isbn=row.isbn,
            supplier_country=row.supplier_country,
            cost_usd=row.cost_usd,
            selling_price_local=row.selling_price_local,
            stock_quantity=row.stock_quantity,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
