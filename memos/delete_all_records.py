"""
Destroy records in the collection Memos for the specified user
(who must not be siteUserAdmin)
"""

import pymongo
from pymongo import MongoClient
import sys

import config
CONFIG = config.configuration()


MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(
    CONFIG.DB_USER,
    CONFIG.DB_USER_PW,
    CONFIG.DB_HOST, 
    CONFIG.DB_PORT, 
    CONFIG.DB)

try: 
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, CONFIG.DB)
    print("Got database")
    print("Attempting remove records")
    collection = db.Memos
    records = [ ] 
    for record in collection.find( { "type": "dated_memo" } ):
        records.append(
            { "type": record['type'],
            "date": record['date'],
            "text": record['text']
        })

    print("Records:")
    print(records)

    db.dated.remove({})
    print("records removed")
except Exception as err:
    print("Failed")
    print(err)



        
