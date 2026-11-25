"""
Test settings.

Overrides DATABASES to sqlite3 so the test suite can run with Django's
auto test database without a live PostgreSQL instance. Everything else is
inherited from config.settings.
"""
from config.settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
