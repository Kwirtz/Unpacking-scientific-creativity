import pymongo
import tqdm
import random

# First version with collection authors

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["novelty"]
collection = db["authors"]

db_sample = Client["novelty_sample"]
collection_sample = db_sample["authors_sample"]


docs = collection.aggregate([
    { "$match": { "pmid_list": { "$exists": True } } },
    { "$sample": { "size": 30000 } }
])

docs = list(docs)
[doc.pop("_id") for doc in docs]

collection_sample.insert_many(docs)

pmid_list = []
for doc in tqdm.tqdm(docs):
    pmid_list += doc["pmid_list"]
    pmid_list = list(set(pmid_list))
    
    
Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["novelty"]
collection = db["meshterms"]

db_sample = Client["novelty_sample"]
collection_sample = db_sample["meshterms_sample"]



# Only articles

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["pkg"]
collection = db["articles"]

docs = collection.aggregate([
    { "$sample": { "size": 300000 } }
])

pmid_list = [doc["PMID"] for doc in docs]

db_sample = Client["novelty_sample"]
collection_authors = db["authors"]
collection_meshterms = db["meshterms"]
collection_references = db["references"]


docs = collection.find({"PMID":{"$in":pmid_list}})
docs = list(docs)
[doc.pop("_id") for doc in docs]

authors = []
meshterms = []
references = []

n = 0 
for doc in tqdm.tqdm(docs):
    if "a06_meshheadinglist" in doc and "c04_referencelist" in doc and "a02_authorlist" in doc:
        authors.append({"PMID":doc["PMID"],"year":doc["year"],"a02_authorlist":doc["a02_authorlist"]})
        meshterms.append({"PMID":doc["PMID"],"year":doc["year"],"a06_meshheadinglist":doc["a06_meshheadinglist"]})
        references.append({"PMID":doc["PMID"],"year":doc["year"],"c04_referencelist":doc["c04_referencelist"]})
        
collection_sample.insert_many(docs)
