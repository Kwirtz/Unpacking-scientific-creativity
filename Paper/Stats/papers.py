import pymongo



#%% papers stats
client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["pkg"] 
collection = mydb["articles"]

docs = collection.find({"a14_referencelist":{"$exists":1}}).sort("PMID",pymongo.DESCENDING)
doc = next(docs)

x = collection.count_documents({"a14_referencelist":{"$exists":1}})