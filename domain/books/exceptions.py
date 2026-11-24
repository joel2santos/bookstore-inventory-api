"""Domain exceptions for the books bounded context."""


class BookNotFound(Exception):
    """Raised when a requested book does not exist."""


class InvalidISBN(Exception):
    """Raised when an ISBN is malformed or fails validation."""


class ExchangeRateUnavailable(Exception):
    """Raised when an exchange rate cannot be obtained."""


class InvalidCostUSD(Exception):
    """Raised when cost_usd is not strictly positive."""


class InvalidStockQuantity(Exception):
    """Raised when stock_quantity is negative."""
