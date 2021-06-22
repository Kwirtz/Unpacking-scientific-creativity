import pymongo
import yaml
import tqdm


with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_Kevin']
client_name = pars["pymongo_connection"]


client = pymongo.MongoClient( client_name)
db = client['pkg']
collection = db['articles']


def create_year(collection,year_month = False, index = False):

    docs = collection.find({})
    
    for doc in tqdm.tqdm(docs):
        try:
            date = doc['DateCompleted'].split('-')
            if year_month == False:
                doc_infos = {"year": int(date[0])}
            else:
                year = date[0]
                month = date[1]
                doc_infos = {"yearmonth": int(year+month)}               
            query = {'PMID':int(doc['PMID'])}
            newvalues = {'$set':doc_infos}
            collection.update_one(query,newvalues)
        except:
            pass
    if index == True:
        if year_month == False:    
            collection.create_index([ ("year",1) ])
        else:
            collection.create_index([ ("yearmonth",1) ])


create_year(collection)
create_year(collection,year_month = True)

