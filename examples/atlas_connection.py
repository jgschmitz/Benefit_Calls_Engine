"""Shared Atlas connection; importing this module performs no network calls."""
from functools import lru_cache
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME, require_settings

@lru_cache(maxsize=1)
def mongo_client(uri):
    return MongoClient(uri, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000, socketTimeoutMS=60000, appname='PlanBenefitSummaryDemo')

def collection():
    require_settings('MONGO_URI')
    return mongo_client(MONGO_URI)[DB_NAME][COLLECTION_NAME]
