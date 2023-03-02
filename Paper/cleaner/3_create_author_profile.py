import pymongo
import tqdm
from collections import defaultdict
import pickle

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client["pkg"]
collection = db["articles"]
collection_authors = db["authors"]

def skills_dict():
    time_window = range(1980,2020)
    for year in tqdm.tqdm(time_window):
        pmid2skills = defaultdict(list)
        docs = collection.find({"$and":[{"year":year},{"a06_meshheadinglist":{"$exists":1}}]},no_cursor_timeout=True)
        for doc in tqdm.tqdm(docs):
            skills = [mesh["DescriptorName_UI"] for mesh in doc["a06_meshheadinglist"]]
            pmid2skills[doc["PMID"]] = skills
        with open('Paper/Data/pmid2skills/{}.p'.format(year), 'wb') as f:
            pickle.dump(pmid2skills, f)
    return None

skills_dict()

docs = collection_authors.find({},no_cursor_timeout=True, batch_size=1000)
for doc in tqdm.tqdm(docs):
    author_skills = defaultdict(list)
    for paper in doc["more_info"]:
        pmid = paper["PMID"]
        year = paper["PubYear"]
        with open('Paper/Data/pmid2skills/{}.p'.format(year), 'rb') as f:
            pmid2skills = pickle.load(f)
        try:
            author_skills[year].append(pmid2skills[pmid])
        except:
            continue
    collection_authors.update_one({"AND_ID":doc["AND_ID"]},{"skills":author_skills})
    

time_window = range(1980,2020)
for year in tqdm.tqdm(time_window):
    docs = collection.find({"$and":[{"year":year},{"a02_authorlist":{"$exists":1}}]},no_cursor_timeout=True)
    for doc in tqdm.tqdm(docs):
        authors_skills = []
        year = doc["year"]
        for author in doc["a02_authorlist"]:
            a = collection_authors.find_one({"AND_ID":author["AID"]})
            for y in range(year-4,year+2):
                try:
                    authors_skills += a["skills"][y]
                except:
                    continue
            collection.update_one({"PMID":doc["PMID"]},{"a15_authors_skills":author_skills})  
            
docs = collection.find({"AND_ID":25000000})
for i in tqdm.tqdm(range(30000000)):
    collection.find_one({"PMID":i})
