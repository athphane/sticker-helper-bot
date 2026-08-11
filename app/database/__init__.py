import pymongo

from app import MONGO_URL, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB_NAME, MONGO_DB_AUTH_SOURCE


def database():
    """Created Database connection"""
    client_kwargs = {
        "username": MONGO_USERNAME,
        "password": MONGO_PASSWORD,
    }
    if MONGO_DB_AUTH_SOURCE:
        client_kwargs["authSource"] = MONGO_DB_AUTH_SOURCE
    client = pymongo.MongoClient(MONGO_URL, **client_kwargs)
    db = client[MONGO_DB_NAME]
    return db
