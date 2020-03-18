# MongoDB

import pymongo
from pymongo import MongoClient

try:
    client = MongoClient("mongodb+srv://discord_bot:JQcMfuo4UmVjrUcj@cluster0-olgmw.mongodb.net/test?retryWrites=true&w=majority")

    db = client["discord_bot"]
except Exception:
    print("Failed to connect to database")
