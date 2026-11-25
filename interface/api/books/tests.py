from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

import requests

from infrastructure.db.models import Book, ExchangeRateConfig


class BookAPITests(TestCase):
    """ API tests for the bookstore inventory API. """

    def setUp(self):
        self.client = APIClient()

    # helpers

    def _isbn13(self, n: int) -> str:
        """Build a valid ISBN-13 from an integer index (unique per index)."""
        digits = "978" + f"{n:09d}"  # 12 digits
        total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
        check = (10 - (total % 10)) % 10
        return digits + str(check)

    def _book_payload(self, **overrides):
        payload = {
            "title": "Cien años de soledad",
            "author": "Gabriel García Márquez",
            "category": "Literatura",
            "isbn": self._isbn13(1),
            "supplier_country": "VE",
            "cost_usd": "25.00",
            "stock_quantity": 50,
        }
        payload.update(overrides)
        return payload

    def _create_book(self, **overrides):
        return self.client.post(
            "/books/", self._book_payload(**overrides), format="json"
        )

    # crud

    def test_create_book_success(self):
        response = self._create_book()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

        book = Book.objects.first()
        self.assertEqual(book.title, "Cien años de soledad")
        self.assertEqual(book.author, "Gabriel García Márquez")
        self.assertEqual(book.category, "Literatura")
        self.assertEqual(book.supplier_country, "VE")
        self.assertEqual(book.cost_usd, Decimal("25.00"))
        self.assertEqual(book.stock_quantity, 50)
        self.assertIsNone(book.selling_price_local)
        self.assertEqual(
            list(response.data.keys()),
            [
                "title",
                "author",
                "category",
                "isbn",
                "supplier_country",
                "cost_usd",
                "selling_price_local",
                "stock_quantity",
                "id",
                "created_at",
                "updated_at",
            ],
        )
        self.assertEqual(response.data["title"], "Cien años de soledad")
        self.assertEqual(response.data["cost_usd"], "25.00")
        self.assertEqual(response.data["stock_quantity"], 50)
        self.assertIsNone(response.data["selling_price_local"])

    def test_create_book_cost_usd_zero(self):
        response = self._create_book(cost_usd="0.00")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 0)

    def test_create_book_cost_usd_negative(self):
        response = self._create_book(cost_usd="-5.00")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 0)

    def test_create_book_stock_negative(self):
        response = self._create_book(stock_quantity=-1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 0)

    def test_create_book_duplicate_isbn(self):
        self._create_book(isbn="978-84-376-0494-7")
        response = self._create_book(isbn="978-84-376-0494-7")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 1)

    def test_create_book_invalid_isbn(self):
        response = self._create_book(isbn="123")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 0)

    def test_create_book_valid_isbn_10(self):
        response = self._create_book(isbn="0-306-40615-2")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["isbn"], "0-306-40615-2")

    def test_create_book_valid_isbn_13(self):
        response = self._create_book(isbn="978-84-376-0494-7")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["isbn"], "978-84-376-0494-7")

    def test_get_book_by_id(self):
        create_response = self._create_book()
        book_id = create_response.data["id"]

        response = self.client.get(f"/books/{book_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], book_id)
        self.assertEqual(response.data["title"], "Cien años de soledad")

    def test_get_book_not_found(self):
        response = self.client.get("/books/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_book(self):
        create_response = self._create_book()
        book_id = create_response.data["id"]

        response = self.client.put(
            f"/books/{book_id}/",
            {
                "title": "Nuevo título",
                "author": "Autor nuevo",
                "category": "Técnica",
                "isbn": "978-84-376-0494-7",
                "supplier_country": "CO",
                "cost_usd": "30.00",
                "stock_quantity": 5,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Nuevo título")
        self.assertEqual(response.data["category"], "Técnica")
        self.assertEqual(response.data["stock_quantity"], 5)

        book = Book.objects.get(id=book_id)
        self.assertEqual(book.title, "Nuevo título")

    def test_delete_book(self):
        create_response = self._create_book()
        book_id = create_response.data["id"]

        response = self.client.delete(f"/books/{book_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)

        response = self.client.get(f"/books/{book_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_books_paginated(self):
        for n in range(12):
            self._create_book(isbn=self._isbn13(n))

        response = self.client.get("/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])

    def test_search_by_category(self):
        self._create_book(isbn=self._isbn13(0), category="Literatura")
        self._create_book(isbn=self._isbn13(1), category="Literatura")
        self._create_book(isbn=self._isbn13(2), category="Técnica")

        response = self.client.get("/books/search/?category=Literatura")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        for book in response.data["results"]:
            self.assertIn("Literatura", book["category"])

    def test_search_missing_category(self):
        response = self.client.get("/books/search/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_low_stock_filter(self):
        self._create_book(isbn=self._isbn13(0), stock_quantity=5)
        self._create_book(isbn=self._isbn13(1), stock_quantity=15)
        self._create_book(isbn=self._isbn13(2), stock_quantity=3)
        self._create_book(isbn=self._isbn13(3), stock_quantity=20)

        response = self.client.get("/books/low-stock/?threshold=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        for book in response.data["results"]:
            self.assertLessEqual(book["stock_quantity"], 10)

    def test_low_stock_default_threshold(self):
        self._create_book(isbn=self._isbn13(0), stock_quantity=5)
        self._create_book(isbn=self._isbn13(1), stock_quantity=15)

        response = self.client.get("/books/low-stock/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["stock_quantity"], 5)

    # price calc

    @patch("infrastructure.external.exchange_rate_gateway.requests.get")
    def test_calculate_price_success(self, mock_get):
        book = Book.objects.create(
            title="El aleph",
            author="Jorge Luis Borges",
            category="Literatura",
            isbn=self._isbn13(9),
            supplier_country="VE",
            cost_usd=Decimal("10.00"),
            stock_quantity=5,
        )

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"rates": {"VES": "36.5"}}
        mock_get.return_value = mock_response

        response = self.client.post(f"/books/{book.id}/calculate-price/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_keys = {
            "book_id",
            "cost_usd",
            "exchange_rate",
            "cost_local",
            "margin_percentage",
            "selling_price_local",
            "currency",
            "calculation_timestamp",
        }
        self.assertEqual(set(response.data.keys()), expected_keys)
        self.assertEqual(response.data["book_id"], book.id)
        self.assertEqual(response.data["cost_usd"], "10.00")
        self.assertEqual(response.data["exchange_rate"], "36.5")
        self.assertEqual(response.data["margin_percentage"], 40)
        self.assertEqual(response.data["currency"], "VES")
        self.assertIsNotNone(response.data["selling_price_local"])
        self.assertIsNotNone(response.data["calculation_timestamp"])
        book.refresh_from_db()
        self.assertEqual(book.selling_price_local, Decimal(response.data["selling_price_local"]))

    @patch("infrastructure.external.exchange_rate_gateway.requests.get")
    def test_calculate_price_api_failure_db_fallback(self, mock_get):
        book = Book.objects.create(
            title="El aleph",
            author="Jorge Luis Borges",
            category="Literatura",
            isbn=self._isbn13(8),
            supplier_country="VE",
            cost_usd=Decimal("10.00"),
            stock_quantity=5,
        )
        ExchangeRateConfig.objects.create(
            default_currency="VES",
            default_exchange_rate=Decimal("37.000000"),
        )

        mock_get.side_effect = requests.exceptions.RequestException("API down")

        response = self.client.post(f"/books/{book.id}/calculate-price/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exchange_rate"], "37.000000")
        self.assertEqual(response.data["currency"], "VES")
        self.assertIsNotNone(response.data["selling_price_local"])

    @patch("infrastructure.external.exchange_rate_gateway.requests.get")
    def test_calculate_price_no_fallback(self, mock_get):
        book = Book.objects.create(
            title="El aleph",
            author="Jorge Luis Borges",
            category="Literatura",
            isbn=self._isbn13(7),
            supplier_country="VE",
            cost_usd=Decimal("10.00"),
            stock_quantity=5,
        )
        mock_get.side_effect = requests.exceptions.RequestException("API down")

        response = self.client.post(f"/books/{book.id}/calculate-price/")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_calculate_price_book_not_found(self):
        response = self.client.post("/books/99999/calculate-price/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # status codes

    def test_http_status_codes(self):
        self.assertEqual(self.client.get("/books/").status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.post("/books/", {"isbn": "bad"}, format="json").status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            self.client.get("/books/99999/").status_code, status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            self.client.get("/books/search/").status_code, status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.client.delete("/books/99999/").status_code, status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            self.client.post("/books/99999/calculate-price/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # business rules

    def test_db_constraint_cost_usd_positive(self):
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title="Bad book",
                author="Author",
                category="Literatura",
                isbn=self._isbn13(5),
                supplier_country="VE",
                cost_usd=Decimal("0.00"),
                stock_quantity=5,
            )

    def test_db_constraint_stock_non_negative(self):
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title="Bad book",
                author="Author",
                category="Literatura",
                isbn=self._isbn13(6),
                supplier_country="VE",
                cost_usd=Decimal("10.00"),
                stock_quantity=-1,
            )

    def test_db_constraint_isbn_unique(self):
        Book.objects.create(
            title="Book A",
            author="Author",
            category="Literatura",
            isbn=self._isbn13(9),
            supplier_country="VE",
            cost_usd=Decimal("10.00"),
            stock_quantity=5,
        )
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title="Book B",
                author="Author",
                category="Literatura",
                isbn=self._isbn13(9),  # dupe
                supplier_country="VE",
                cost_usd=Decimal("10.00"),
                stock_quantity=5,
            )
