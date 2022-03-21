import os
import json
import tqdm
import pymongo

# Only articles

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["pkg"]
db_novelty = Client["novelty"]
db_sample = Client["novelty_sample"]

collection = db["articles"]
collection_list = [collection for collection in db_novelty.collection_names()]






docs = db_novelty["Meshterms"].aggregate([
    { "$sample": { "size": 5000000 } }
], allowDiskUse=True)

pmid_list = [] 
for doc in tqdm.tqdm(docs):
    if "Mesh_year_category" in doc:
        if doc["year"]>= 1995 and doc["year"] <= 2015:
            pmid_list.append(doc["PMID"])

pmid_lists = [pmid_list[x:x+50000] for x in range(0, len(pmid_list), 50000)]

new_pmid_list = [] 

for pmid_list in pmid_lists:
    docs = collection.find({"PMID":{"$in":pmid_list}})
    
    for doc in tqdm.tqdm(docs):
        if "a06_meshheadinglist" in doc and "c04_referencelist" in doc and "a02_authorlist" in doc and "a04_abstract" in doc:
            new_pmid_list.append(doc["PMID"])



new_pmid_lists = [new_pmid_list[x:x+50000] for x in range(0, len(new_pmid_list), 50000)]


for col in collection_list:
    col_novelty = db_novelty[col]
    col_sample = db_sample[col]
    for new_pmid_list in new_pmid_lists:
        docs = col_novelty.find({"PMID":{"$in":new_pmid_list}})
        docs = list(docs)
        [doc.pop("_id") for doc in docs]  
        col_sample.insert_many(docs)

years = col_sample.find({}).distinct("year")


for col in collection_list:
    try:
        os.makedirs("Data/docs/{}_sample".format(col))
    except FileExistsError:
        # directory already exists
        pass

    for year in tqdm.tqdm(years):
        docs2save = list(db_sample[col].find({"year":year}))
        [doc.pop("_id") for doc in docs2save]
        with open('Data/docs/{}_sample/{}.json'.format(col,year), 'w') as fout:
            json.dump(docs2save, fout)