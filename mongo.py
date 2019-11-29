from pymongo import MongoClient

class CollConection:

    def __init__(self,dbName,collection):
        self.client = MongoClient()
        self.db = self.client[dbName]
        self.collection=self.db[collection]

    def addDocument(self,document):
        a=self.collection.insert_one(document)
        print("Inserted", a.inserted_id)
        return a.inserted_id
    
    def addChiste(self, autor, chiste):
        document={'autor':autor,
                'chiste':chiste}
        return self.addDocument(document)

    






