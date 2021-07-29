import pymongo
import tqdm
import requests
import json
import time
import json

client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["F1000"] 
collection = mydb["all"]
collection_cleaned = mydb["merged"]

docs = collection.find()
list_doi = []
for doc in tqdm.tqdm(docs):
    try:
        list_doi.append(doc["doi"])
    except:
        pass

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

pmid2doi = {}
for chunk in tqdm.tqdm(chunks(list_doi,100)):
    dois = ",".join([obj for obj in chunk if obj != None and obj.startswith("10.")])
    response = requests.get("https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={}&format=json".format(dois))
    try:
        for paper in json.loads(response.content)["records"]:
            try:
                pmid2doi[paper["pmid"]] = paper["doi"]
            except:
                pass
    except:
        pass

for pmid in tqdm.tqdm(pmid2doi):
    try:
        doi = pmid2doi[pmid]
        docs = collection.find({"doi":doi})
        doc = next(docs)
        doc["pmid"] = pmid
        collection_cleaned.insert_one(doc)
    except:
        pass
        
    