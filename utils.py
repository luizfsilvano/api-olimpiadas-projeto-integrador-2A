from pymongo import MongoClient

def get_db_handle(db_name, uri):
    client = MongoClient(uri)
    db_handle = client[db_name]
    return db_handle, client