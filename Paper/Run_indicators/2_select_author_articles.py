import pymongo 
import yaml
import tqdm
import pickle
with open(r"C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
db= 'pkg'
client_name = pars['client_name']
client = pymongo.MongoClient(client_name)
db = client['PKG']
collection = db['articles']

nb_title = collection.find({'title_embedding':{'$exists':1}}).count()

nb_abs = collection.find({'abstract_embedding':{'$exists':1}}).count()

## Get authors list present between 2000 and 2010

docs = collection.find({'year':{'$gte':2000,'$lte':2010}})
author_list = set()
for doc in tqdm.tqdm(docs):
    if 'a02_authorlist' in doc.keys() and doc['year'] in range(2000,2011):
        for aut in doc['a02_authorlist']:
            author_list.update({aut['AID']})
pickle.dump(authors_list,open(r'C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\Data\authors_list_2000_2010.p' ,'wb'))

