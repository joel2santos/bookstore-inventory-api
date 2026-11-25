from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from application.books.services import CalculateSellingPrice
from domain.books.exceptions import BookNotFound, ExchangeRateUnavailable
from infrastructure.db.models import Book as DjangoBook
from infrastructure.db.repositories import DjangoBookRepository
from infrastructure.external.exchange_rate_gateway import ExchangeRateGateway

from .serializers import BookSerializer, PriceCalculationSerializer


class BookPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class BookViewSet(viewsets.ModelViewSet):
    queryset = DjangoBook.objects.all()
    serializer_class = BookSerializer
    pagination_class = BookPagination

    book_repo = DjangoBookRepository()
    rate_gateway = ExchangeRateGateway()

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        category = request.query_params.get("category")
        if not category:
            return Response(
                {"detail": "category query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = self.filter_queryset(
            self.get_queryset().filter(category__icontains=category)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        try:
            threshold = int(request.query_params.get("threshold", 10))
        except (TypeError, ValueError):
            threshold = 10
        queryset = self.filter_queryset(
            self.get_queryset().filter(stock_quantity__lte=threshold)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="calculate-price")
    def calculate_price(self, request, pk=None):
        use_case = CalculateSellingPrice(self.book_repo, self.rate_gateway)
        try:
            result = use_case.execute(int(pk))
        except BookNotFound:
            return Response(
                {"detail": "Book not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ExchangeRateUnavailable:
            return Response(
                {"detail": "Exchange rate unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        serializer = PriceCalculationSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
