from .settings import *

# Override database for CI
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # in-memory DB for faster tests
    }
}
