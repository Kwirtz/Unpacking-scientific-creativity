import gc
import tqdm
import pickle
import pymongo
import pandas as pd
from collections import defaultdict

Client = pymongo.MongoClient("mongodb://localhost:27017")
db = Client["novelty"]
collection = db["authors"]



authors2deg_cen = defaultdict(lambda: defaultdict(int))

period = collection.distinct("year")
period = [i for i in period if i!=None and i<2006 and i > 1979]


for year in tqdm.tqdm(period):
    docs = collection.find({"year":year})
    for doc in tqdm.tqdm(docs):        
        if "a02_authorlist" in doc:
            if len(doc["a02_authorlist"]) > 1:
                for author in doc["a02_authorlist"]:               
                    authors2deg_cen[year][author["AID"]] += (1/(len(doc["a02_authorlist"]) - 1)) 





columns = ["year","AID","deg_cen"]
list_of_insertion = []
for year in tqdm.tqdm(period):    
    for id_ in tqdm.tqdm(authors2deg_cen[year]):             
        deg_cen = authors2deg_cen[year][id_]
        list_of_insertion.append([year, id_, deg_cen])
        
df=pd.DataFrame(list_of_insertion,columns=columns)

df['cumsum']=df.groupby(["AID"])['deg_cen'].cumsum()
df[df["AID"]==6192779]

del(authors2deg_cen)
gc.collect()

authors_profile = defaultdict(lambda: defaultdict(dict))

for row in tqdm.tqdm(df.iterrows()):
    authors_profile[row[1]["year"]][row[1]["AID"]]["deg_cen"] = row[1]["deg_cen"]
    authors_profile[row[1]["year"]][row[1]["AID"]]["cumsum"] = row[1]["cumsum"]
    
with open('Data/deg_cen.pickle', 'wb') as fp:
    pickle.dump(dict(authors_profile), fp)