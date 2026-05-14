from pymongo import MongoClient
from pymongo.collection import Collection
import os


def get_collection() -> Collection:
    uri = os.environ["WRITERLORE_MONGO_URI"]
    client = MongoClient(uri)
    return client["writerLore"]["memories"]
