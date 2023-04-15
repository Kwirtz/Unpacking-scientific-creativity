import tqdm
import pymongo



#%% papers stats
client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["pkg"] 
collection = mydb["articles"]

docs = collection.find()

n = 0
for doc in tqdm.tqdm(docs):
    if "year" in doc:
        if doc["year"] >= 1980 and doc["year"] <= 2005:
            n += 1


docs = collection.find({"a14_referencelist":{"$exists":1}}).sort("PMID",pymongo.DESCENDING)
doc = next(docs)

x = collection.count_documents({"a14_referencelist":{"$exists":1}})


#%% 
client = pymongo.MongoClient('mongodb://localhost:27017')
mydb = client["pkg"] 
collection = mydb["articles_2000_2005"]

docs = collection.find({"Journal_ISSN":{"$exists":1}})
list_issn = []

for doc in tqdm.tqdm(docs):
    list_issn.append(doc["Journal_ISSN"])
        
len(set(list_issn))
