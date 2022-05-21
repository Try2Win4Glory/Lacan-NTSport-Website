import pymongo
import os
client = pymongo.MongoClient(f'mongodb+srv://Malakai:{os.getenv("DB_KEY")}@cluster0.dfvrs.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
class DBClient:
    def __init__(self):
        self.client = client
        self.db = self.client.comps
    def get_array(self, collection, dict):
        return collection.find_one(dict)
    def update_array(self, collection, old, new, debug=False):
        replaceOne = collection.replace_one(old, new)
        if debug:
            print(replaceOne.matched_count)
            print(replaceOne.modified_count)
        return replaceOne
    def create_doc(self, collection, data):
        return collection.insert_one(data)