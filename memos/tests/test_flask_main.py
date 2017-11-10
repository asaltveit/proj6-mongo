from pymongo import MongoClient
import config
import nose

try: 
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, CONFIG.DB)
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    

def add_record():
	"""
	Adds a record to data base.
	This covers 'saving' a record.
	"""
	record = { "type": "dated",
        "text": "moo" 
    }
	collection.insert(record)

def test_delete():
	"""
	Tests if a record is added ('saved') correctly, 
	then if it is deleted properly.
	"""
	add_record()
	assert get_memos() == "[{'type': 'dated', 'text': 'moo'}]"
	collection.remove({"type": "dated"}, 1)
	assert get_memos() == '[]'

def test_date_order():
	"""
	Order is by a filter on client side.
	"""
def test_date():

