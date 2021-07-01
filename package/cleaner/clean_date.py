import pymongo
import yaml
import tqdm
import time
import datetime

with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_Kevin']
client_name = pars["pymongo_connection"]


client = pymongo.MongoClient( client_name)
db = client['pkg']
collection = db['articles']


def create_year(collection, index = False):

    docs = collection.find({})
    
    for doc in tqdm.tqdm(docs):
        try:
            date = doc['DateCompleted'].split('-')
            year = date[0]
            month = date[1]
            day = date[2]
            s = day + "/" + month + "/" + year
            unix = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
            doc_infos = {"year": int(date[0]),"yearmonth": int(year+month), "unix":unix}           
            query = {'PMID':int(doc['PMID'])}
            newvalues = {'$set':doc_infos}
            collection.update_one(query,newvalues)
        except:
            pass
    if index == True:  
        collection.create_index([ ("year",1) ])
        collection.create_index([ ("yearmonth",1) ])


create_year(collection)


