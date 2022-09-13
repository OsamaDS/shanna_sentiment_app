import pymongo

def createDB():
    db_name='register_users'
    test_client = pymongo.MongoClient('mongodb://localhost:27017/')
    shanadb = test_client[db_name]

    