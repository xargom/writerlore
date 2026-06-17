from pymongo import MongoClient
from pymongo.collection import Collection
import os


def get_collection() -> Collection:
    uri = os.environ.get("WRITERLORE_MONGO_URI")
    if not uri:
        raise RuntimeError("WRITERLORE_MONGO_URI is not set")
    client = MongoClient(uri)
    return client["writerLore"]["memories"]
