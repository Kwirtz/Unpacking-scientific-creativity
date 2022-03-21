import pymongo
import json
import tqdm
import os
import tqdm
from pymongo import UpdateOne

# datamongo2json


def mongo2json(URI,db_name,collection_name, var):
    
    Client = pymongo.MongoClient(URI)
    db = Client[db_name]
    collection = db[collection_name]

    years = collection.find({var:{"$exists":True}}).distinct("year")
    
    path = "Data/docs/{}".format(collection_name)
    if not os.path.exists(path):
        os.makedirs(path)
    years = [year for year in years if year != None]  
      
    for year in tqdm.tqdm(years):
        docs = collection.find({"year":year,var:{"$exists":True}},{"_id":0})
        to_insert = list(docs)
        if to_insert == []:
            continue
        else:
            with open(path + "/{}.json".format(year), 'w') as outfile:
                json.dump(to_insert, outfile)
        
mongo2json(URI = "mongodb://localhost:27017", db_name = 'novelty', collection_name = 'Ref_Journals', var = 'c04_referencelist')
#collection.create_index([("year",1)])

"""
Client = pymongo.MongoClient(URI)
db = Client[db_name]
collection = db[collection_name]

docs = collection.find({},{"_id":0})
with open("authors_sample.json", 'w') as outfile:
    json.dump(list(docs), outfile)
"""
# result2mongo

def json2mongo(URI,db_name,collection_name, indicator, var):
    
    Client = pymongo.MongoClient(URI)
    db = Client[db_name]
    collection = db[collection_name]


    path = "Result/{}/{}/".format(indicator,var)
    list_files = os.listdir(path)

    for file in list_files:
        file_path = path + file
        list_of_insertion = []
        with open(file_path, 'r', encoding='utf-8') as outfile:
            docs = json.load(outfile) 
        for doc in tqdm.tqdm(docs):
            list_of_insertion.append(UpdateOne({'PMID': doc["PMID"]}, {'$set': {var+"_"+indicator : doc[var]}}, upsert = True))
    collection.bulk_write(list_of_insertion)


# You forgot the year ? sad for you

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client['pkg']
collection = db['articles']
db_output = Client['novelty']
collection_output = db_output['references']


docs = collection.find()

list_of_insertion = []
for doc in tqdm.tqdm(docs):
    try:
        list_of_insertion.append(UpdateOne({'PMID': doc["PMID"]}, {'$set': {'year': doc['year']}}, upsert = False))    
    except Exception as e:
        print(e)
    if len(list_of_insertion) % 500000 == 0:
        collection_output.bulk_write(list_of_insertion)
        list_of_insertion = []

collection_output.bulk_write(list_of_insertion)

# change key name

    
Client = pymongo.MongoClient(URI)
db = Client[db_name]
collection = db[collection_name]

collection.update_many( {}, { "$rename": { "Mesh_year_category": "a06_meshheadinglist" } } )

