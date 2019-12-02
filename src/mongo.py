import getpass
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
#Get Password
connection = os.getenv("pass")

#Connect to DB
client = MongoClient(connection)
def connectCollection(database, collection):
    db = client[database]
    coll = db[collection]
    return db, coll