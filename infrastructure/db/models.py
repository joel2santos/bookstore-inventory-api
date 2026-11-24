import os

from django.db import models


class Book(models.Model):
    """
    Book persisted in the database.
    """

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    isbn = models.CharField(max_length=17, unique=True)
    supplier_country = models.CharField(max_length=2)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price_local = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    stock_quantity = models.PositiveIntegerField()
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(cost_usd__gt=0),
                name="cost_usd_positive",
            ),
            models.CheckConstraint(
                check=models.Q(stock_quantity__gte=0),
                name="stock_quantity_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"


class ExchangeRateConfig(models.Model):
    """
    Singleton exchange-rate configuration.
    This is setted like this and not in an environment variable because it can be changed by the user in the admin panel.
    Remember! Our country (Vzla) has a very volatile exchange rate, so it is important to have this in the database so we don't
    have to redeploy everytime the exchange rate changes. This is a singleton model, so there will be only one instance of this model in the database :)
    """

    id = models.BigAutoField(primary_key=True)
    default_currency = models.CharField(max_length=3)
    default_exchange_rate = models.DecimalField(max_digits=10, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exchange_rate_config"

    def save(self, *args, **kwargs):
        """Delete any other instance before saving so only one row exists."""
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    @classmethod
    def get_singleton(cls) -> "ExchangeRateConfig":
        """Return the existing row, or create one seeded from env."""
        instance = cls.objects.first()
        if instance is None:
            instance = cls(
                default_currency=os.environ.get("DEFAULT_LOCAL_CURRENCY", "VES"),
            )
            instance.save()
        return instance

    def __str__(self) -> str:
        return f"{self.default_currency} @ {self.default_exchange_rate}"
