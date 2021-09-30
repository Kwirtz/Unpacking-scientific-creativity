import pymongo
import json
import tqdm
import os

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["pkg"]
collection = db["articles"]

years = collection.find().distinct("year")

path = "Data/docs/articles"
if not os.path.exists(path):
    os.makedirs(path)
years = [year for year in years if year != None]    
for year in tqdm.tqdm(years):
    docs = collection.find({"year":year},{"_id":0})
    with open(path + "/{}.json".format(year), 'w') as outfile:
        json.dump(list(docs), outfile)