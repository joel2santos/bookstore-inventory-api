#!/usr/bin/env python3
"""
Seed the bookstore inventory database with realistic sample books.

Usage (inside the API container — bypasses API rate limits, fastest):
  docker compose exec app python scripts/seed_books.py --count 100

Usage (against the running HTTP API from host):
  python scripts/seed_books.py --mode api --count 40 --base-url http://localhost/api
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import urllib.error
import urllib.request
from decimal import Decimal
from pathlib import Path

CATEGORIES = [
    "Literatura Clásica",
    "Science Fiction",
    "Software Engineering",
    "History",
    "Philosophy",
    "Mystery",
    "Fantasy",
    "Economics",
    "Design",
    "Poetry",
]

AUTHORS = [
    "Miguel de Cervantes",
    "Gabriel García Márquez",
    "Jorge Luis Borges",
    "Ursula K. Le Guin",
    "Frank Herbert",
    "Martin Kleppmann",
    "Robert C. Martin",
    "Yuval Noah Harari",
    "Hannah Arendt",
    "Agatha Christie",
    "Brandon Sanderson",
    "Don Norman",
    "Mary Oliver",
    "Octavia E. Butler",
    "Calvino Italo",
]

TITLE_PREFIXES = [
    "The Art of",
    "Chronicles of",
    "Reflections on",
    "Foundations of",
    "Shadows in",
    "Letters from",
    "Echoes of",
    "A Brief History of",
    "Patterns for",
    "Tales of",
]

TITLE_NOUNS = [
    "Solitude",
    "Distributed Systems",
    "The Labyrinth",
    "Tomorrow",
    "Quiet Design",
    "The Archipelago",
    "Reason",
    "Midnight",
    "Paper & Ink",
    "Distant Stars",
    "Modern Craft",
    "Lost Cities",
]

COUNTRIES = ["ES", "US", "GB", "MX", "AR", "DE", "FR", "JP", "CO", "CL"]


def generate_isbn13(index: int) -> str:
    """Generate a valid, deterministic ISBN-13 with check digit."""
    # Prefix 978-0 + 8-digit sequence -> 12 digits + check digit
    base12 = f"9780{10000000 + index:08d}"
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base12))
    check = (10 - (total % 10)) % 10
    raw = f"{base12}{check}"
    return f"{raw[:3]}-{raw[3]}-{raw[4:8]}-{raw[8:12]}-{raw[12]}"


def build_books(count: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    books: list[dict] = []

    for i in range(1, count + 1):
        prefix = rng.choice(TITLE_PREFIXES)
        noun = rng.choice(TITLE_NOUNS)
        title = f"{prefix} {noun} #{i}"
        author = rng.choice(AUTHORS)
        category = rng.choice(CATEGORIES)
        country = rng.choice(COUNTRIES)
        cost_usd = round(rng.uniform(6.50, 68.00), 2)

        # Mix out-of-stock, low-stock (1..10), and healthy stock (11..80)
        roll = rng.random()
        if roll < 0.1:
            stock = 0
        elif roll < 0.35:
            stock = rng.randint(1, 10)
        else:
            stock = rng.randint(11, 80)

        books.append(
            {
                "title": title,
                "author": author,
                "category": category,
                "isbn": generate_isbn13(i + seed * 1000),
                "supplier_country": country,
                "cost_usd": cost_usd,
                "stock_quantity": stock,
            }
        )
    return books


def seed_via_db(books: list[dict]) -> int:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    from infrastructure.db.models import Book

    objs = [
        Book(
            title=b["title"],
            author=b["author"],
            category=b["category"],
            isbn=b["isbn"],
            supplier_country=b["supplier_country"],
            cost_usd=Decimal(str(b["cost_usd"])),
            stock_quantity=b["stock_quantity"],
        )
        for b in books
    ]
    created = Book.objects.bulk_create(objs, ignore_conflicts=True)
    return len(created)


def seed_via_api(books: list[dict], base_url: str) -> int:
    url = f"{base_url.rstrip('/')}/books/"
    created = 0
    for b in books:
        data = json.dumps(b).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201):
                    created += 1
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(f"[WARN] {b['isbn']}: HTTP {exc.code} -> {body}", file=sys.stderr)
            if exc.code == 429:
                print("[ERROR] Rate limit reached; use --mode db inside the container.", file=sys.stderr)
                break
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate bookstore database with sample books.")
    parser.add_argument("--count", type=int, default=60, help="Number of books to generate (default: 60)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument(
        "--mode",
        choices=("db", "api"),
        default="db",
        help="Insert via Django ORM ('db') or HTTP POST ('api')",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost/api",
        help="API base URL when using --mode api (default: http://localhost/api)",
    )
    args = parser.parse_args()

    books = build_books(args.count, args.seed)
    if args.mode == "db":
        inserted = seed_via_db(books)
    else:
        inserted = seed_via_api(books, args.base_url)

    print(f"Seeded {inserted} books (requested {args.count}, mode={args.mode}).")


if __name__ == "__main__":
    main()
