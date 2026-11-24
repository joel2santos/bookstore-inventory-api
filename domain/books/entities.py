"""Domain entities for the books bounded context.

Plain Python objects with no framework dependencies.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Book:
    """
    Book domain entity.

    Attributes:
        id: Database primary key, None until persisted.
        title: Book title.
        author: Book author.
        category: Book category.
        isbn: ISBN identifier. For more info about this look up https://www.ean-search.org/isbn-search.html
        supplier_country: Country code of the supplier.
        cost_usd: Cost in USD.
        selling_price_local: Retail price in the local currency, if set.
        stock_quantity: Units on hand.
        created_at: Row creation timestamp, None until persisted.
        updated_at: Row last-update timestamp, None until persisted.
    """

    id: int | None
    title: str
    author: str
    category: str
    isbn: str
    supplier_country: str
    cost_usd: Decimal
    selling_price_local: Decimal | None
    stock_quantity: int
    created_at: datetime | None
    updated_at: datetime | None
