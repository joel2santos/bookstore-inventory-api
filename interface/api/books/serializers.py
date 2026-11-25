from rest_framework import serializers

from infrastructure.db.models import Book as DjangoBook


class BookSerializer(serializers.ModelSerializer):
    def validate_isbn(self, value):
        """ISBN-10 or ISBN-13 check digit; hyphens and spaces are allowed."""
        digits = value.replace("-", "").replace(" ", "")
        if len(digits) == 10 and digits[:-1].isdigit() and digits[-1] in "0123456789Xx":
            check = 10 if digits[-1].upper() == "X" else int(digits[-1])
            total = sum(int(d) * (11 - i) for i, d in enumerate(digits[:9], 1))
            if (total + check) % 11 != 0:
                raise serializers.ValidationError("Invalid ISBN-10 check digit")
            return value
        if len(digits) == 13 and digits.isdigit():
            total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
            if total % 10 != 0:
                raise serializers.ValidationError("Invalid ISBN-13 check digit")
            return value
        raise serializers.ValidationError("Invalid ISBN")

    def validate_cost_usd(self, value):
        if value <= 0:
            raise serializers.ValidationError("cost_usd must be greater than 0")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "stock_quantity must be greater than or equal to 0"
            )
        return value

    class Meta:
        model = DjangoBook
        fields = [
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
        ]
        read_only_fields = ("id", "created_at", "updated_at", "selling_price_local")


class PriceCalculationSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(read_only=True)
    cost_usd = serializers.CharField(read_only=True)
    exchange_rate = serializers.CharField(read_only=True)
    cost_local = serializers.CharField(read_only=True)
    margin_percentage = serializers.IntegerField(read_only=True)
    selling_price_local = serializers.CharField(read_only=True)
    currency = serializers.CharField(read_only=True)
    calculation_timestamp = serializers.DateTimeField(read_only=True)
