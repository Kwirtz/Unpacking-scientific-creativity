import tqdm
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['pkg']
collection = db['control_var_2000_2005']
collection_articles = db["articles"]
collection_restricted = db["articles_2000_2005"]
PMIDs = []

docs = collection.find()
for doc in tqdm.tqdm(docs):
    PMIDs.append(doc["PMID"])

docs = collection_articles.find({},{'_id': 0})
list_of_insertion = []
dict_PMIDs = {i:0 for i in PMIDs}

for doc in tqdm.tqdm(docs):
    if doc["PMID"] in dict_PMIDs:
        list_of_insertion.append(doc)
    if len(list_of_insertion) == 10000:
        collection_restricted.insert_many(list_of_insertion)
        list_of_insertion = []
    
collection_restricted.insert_many(list_of_insertion)
