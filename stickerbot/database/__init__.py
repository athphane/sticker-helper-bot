import pymongo

from stickerbot import MONGO_URL, MONGO_DB_NAME, MONGO_USERNAME, MONGO_PASSWORD


def database():
    """Created Database connection"""
    client = pymongo.MongoClient(
        MONGO_URL,
        username=MONGO_USERNAME,
        password=MONGO_PASSWORD
    )
    db = client[MONGO_DB_NAME]
    return db
