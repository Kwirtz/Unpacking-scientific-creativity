import pymongo
import tqdm
import requests
import json
import time
import json

client = pymongo.MongoClient('mongodb://localhost:27017')
mydb = client["F1000"] 
collection = mydb["all"]
mydb_novelty = client["novelty"]
collection_novelty = mydb_novelty["Meshterms"]


n = collection.count_documents({"PMID":{"$exists":1}})
        
docs = collection.find()

list_of_insertion = []
for doc in tqdm.tqdm(docs):
    try:
        fp = collection_novelty.find_one({"PMID":doc["PMID"]})
        year = fp["year"]
    except:
        continue
    list_of_insertion.append(pymongo.UpdateOne({"PMID": int(doc["PMID"])},
                                           {'$set': {"year": year}},
                                           upsert = False))
    if len(list_of_insertion) == 10000:
        collection.bulk_write(list_of_insertion)
        list_of_insertion = []
collection.bulk_write(list_of_insertion)