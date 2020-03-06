# MongoDB

import pymongo
from pymongo import MongoClient

try:
    client = MongoClient("Your Mongo db url")
    db = client["Your db name"]
except Exception:
    print("Failed to connect to database")
