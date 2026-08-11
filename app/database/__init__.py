import threading

import pymongo

from app import MONGO_URL, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB_NAME, MONGO_DB_AUTH_SOURCE

# A single shared MongoClient is used process-wide. Creating a new client per
# call (the previous behaviour) spawned a fresh connection pool per request,
# causing constant TCP/TLS handshakes and SDAM (server discovery) overhead.
# The client is created lazily so importing the module never opens sockets.

_client = None
_client_lock = threading.Lock()

# Connection pool tuning for a single-bot process. These limit how many
# sockets stay open and keep one connection warm so the first query of the
# day doesn't pay a cold-connect penalty.
POOL_OPTIONS = {
    "maxPoolSize": 20,
    "minPoolSize": 1,
    "maxIdleTimeMS": 30_000,
    "connectTimeoutMS": 10_000,
    "serverSelectionTimeoutMS": 5_000,
    "appname": "sticker-helper-bot",
}


def get_client() -> pymongo.MongoClient:
    """Return the shared MongoClient, creating it once on first use."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                client_kwargs = dict(POOL_OPTIONS)
                client_kwargs["username"] = MONGO_USERNAME
                client_kwargs["password"] = MONGO_PASSWORD
                if MONGO_DB_AUTH_SOURCE:
                    client_kwargs["authSource"] = MONGO_DB_AUTH_SOURCE
                _client = pymongo.MongoClient(MONGO_URL, **client_kwargs)
    return _client


def database():
    """Return the shared database handle backed by the singleton client."""
    return get_client()[MONGO_DB_NAME]


def close_connection():
    """Close the shared MongoClient, releasing its pool. Call on shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
