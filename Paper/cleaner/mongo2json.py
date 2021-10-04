import pymongo
import json
import tqdm
import os
import tqdm
from pymongo import UpdateOne

# datamongo2json
Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["pkg"]
collection = db["articles"]

years = collection.find().distinct("year")

path = "Data/docs/articles"
if not os.path.exists(path):
    os.makedirs(path)
years = [year for year in years if year != None]    
for year in tqdm.tqdm(years):
    docs = collection.find({"year":year,'a06_meshheadinglist':{"$exists":True}},{"_id":0})
    with open(path + "/{}.json".format(year), 'w') as outfile:
        json.dump(list(docs), outfile)
        


# result2mongo

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["pkg"]
collection = db["output"]


path = "Result/foster/a06_meshheadinglist/"
list_files = os.listdir(path)


for file in list_files:
    file_path = path + file
    list_of_insertion = []
    with open(file_path, 'r', encoding='utf-8') as outfile:
        docs = json.load(outfile) 
    for doc in tqdm.tqdm(docs):
        list_of_insertion.append(UpdateOne({'PMID': doc["PMID"]}, {'$set': {'a06_foster': doc['a06_foster']}}, upsert = True))
        break

collection.bulk_write(list_of_insertion)
