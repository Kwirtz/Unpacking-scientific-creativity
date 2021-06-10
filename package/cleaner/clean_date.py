import pymongo
import yaml
import tqdm


with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_Kevin']
client_name = pars["pymongo_connection"]


client = pymongo.MongoClient( client_name)
db = client['pkg']
collection = db['articles']


def create_year(collection,year_month = False):

    docs = collection.find({'DateCompleted':{'$exists':1}})
    
    for doc in tqdm.tqdm(docs):
        try:
            if year_month == False:
                year = int(doc['DateCompleted'].split('-')[0])
                doc_infos = {"year": int(year)}
            else:
                date = doc['DateCompleted'].split('-')
                year = date[0]
                month = date[1]
                doc_infos = {"yearmonth": int(year+month)}               
            query = {'PMID':int(doc['PMID'])}
            newvalues = {'$set':doc_infos}
            collection.update_one(query,newvalues)
        except:
            pass
    if year_month == False:    
        collection.create_index([ ("year",1) ])
    else:
        collection.create_index([ ("yearmonth",1) ])


create_year(collection)
create_year(collection,year_month = True)

