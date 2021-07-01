import pymongo
import tqdm

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client["pkg"]
collection = db["articles"]
collection_authors = db["authors"]

def year2months(range_):
    time_window = range_
    months = range(1,13)
    months = [str(month) if len(str(month))==2 else "0"+str(month) for month in months]
    temp_list = []
    for year in time_window:
        temp_list += [int(str(year)+month) for month in months]
    time_window = temp_list
    return time_window

period = year2months(range(2000,2021,1))

month = 201801
for month in period:
    docs = collection.find({"yearmonth":month})
    for doc in tqdm.tqdm(docs):
        authors = doc["a02_authorlist"]
        keywords = doc["a03_keywordlist"]
        meshwords = doc["a06_meshheadinglist"]
        unix = doc["unix"]
        meshwords = [meshword["DescriptorName_UI"] for meshword in meshwords]
        {"skills":[{"unix":month,
                   "meshterms":meshwords,
                   "keywords":keywords}]}
        query = {'PMID':int(doc['PMID'])}
        newvalues = {'$set':doc_infos}
        collection.update_one(query,newvalues)

doc = next(docs)
