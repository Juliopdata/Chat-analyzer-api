from pymongo import MongoClient
import getpass
from dotenv import load_dotenv
import os
load_dotenv()
#Get Password
connection = os.getenv("pass")

#Connect to DB
client = MongoClient(connection)
def connectCollection(database, collection):
    db = client[database]
    coll = db[collection]
    return db, coll