import pymongo
import tqdm
import random

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

docs = collection.find({"PMID":{"$in":pmid_list}})
docs = list(docs)
[doc.pop("_id") for doc in docs]
collection_sample.insert_many(docs)
