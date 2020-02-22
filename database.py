# MongoDB

import pymongo
from pymongo import MongoClient

client = MongoClient("mongodb+srv://moe:123@discord-bot-zsgs1.mongodb.net/test?retryWrites=true&w=majority")
db = client["test"]
collection = db["test"]
