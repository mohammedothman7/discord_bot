# MongoDB

import pymongo
from pymongo import MongoClient

try:
    client = MongoClient("mongodb+srv://moe:123@discord-bot-zsgs1.mongodb.net/test?retryWrites=true&w=majority")
    db = client["discord"]
except Exception:
    print("Failed to connect to database")
