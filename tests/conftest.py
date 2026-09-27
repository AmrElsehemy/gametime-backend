import os

# The service defaults to production when unset; tests exercise the
# development app unless a test builds its own via create_app().
os.environ.setdefault("GAMETIME_ENVIRONMENT", "development")
