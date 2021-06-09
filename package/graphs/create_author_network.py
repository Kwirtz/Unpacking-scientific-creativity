import pymongo
import yaml
import tqdm
from joblib import Parallel, delayed
from collections import defaultdict
import itertools
from scipy.sparse import lil_matrix
import numpy as np
import pickle
import os
from package.utils import create_cooc
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_Kevin']
client_name = pars["pymongo_connection"]
URI = pars["neo4j_connection"]["URI"]
name = pars["neo4j_connection"]["auth"]["name"]
password = pars["neo4j_connection"]["auth"]["password"]

#%%
        
test = create_cooc(client_name = client_name, db_name = "pkg", collection_name = "articles",
                 var = "a02_authorlist", sub_var = "AID" )
test.main()

test2 = create_cooc(client_name = client_name, db_name = "pkg", collection_name = "articles",
                 var = "a03_keywordlist", sub_var = "Keyword" )
test2.main()

test3 = create_cooc(client_name = client_name, db_name = "pkg", collection_name = "articles",
                 var = "a14_referencelist", sub_var = "RefArticleId" )
test3.main()



client = pymongo.MongoClient(client_name)
db = client["pkg"]
collection = db["articles"]

final_list = []
for year in tqdm.tqdm(range(1980,2020)):
    ids_list = []
    docs = collection.find({'year':year})
    for doc in tqdm.tqdm(docs):
        try:
            authors = doc["a02_authorlist"]
        except:
            continue
        authors = [author["AID"] for author in authors]
        for author in authors:
            ids_list.append(author)
    ids_list = list(set(ids_list))
    final_list += ids_list
    final_list = list(set(final_list))

name2index = {name:index for name,index in zip(final_list, range(0,len(final_list),1))}
index2name = {index:name for name,index in zip(final_list, range(0,len(final_list),1))}
pickle.dump( name2index, open( "Data/Authors/name2index.p", "wb" ) )
pickle.dump( index2name, open( "Data/Authors/index2name.p", "wb" ) )


for year in tqdm.tqdm(range(1980,2020)):
    x = lil_matrix((len(final_list), len(final_list)), dtype = np.int16)
    docs = collection.find({'year':year})
    for doc in tqdm.tqdm(docs):
        try:
            authors = doc["a02_authorlist"]
        except:
            continue
        authors = [author["AID"] for author in authors]
        for combi in list(itertools.combinations(authors, r=2)):
            combi = sorted(combi)
            ind_1 = name2index[combi[0]]
            ind_2 = name2index[combi[1]]
            x[ind_1,ind_2] += 1
    x = x.tocsr()
    pickle.dump( x, open( "Data/Authors/{}.p".format(year), "wb" ) )
    #x = x.tocoo()
    #list_of_insertion = [{"source":i,"target":j,"weight":v} for i,j,v in zip(x.row, x.col, x.data)]



#%% test section

def process_cursor_node(client_name, skip_n, limit_n):
    print('Starting process',skip_n//limit_n,'...')
    client = pymongo.MongoClient(client_name)
    db = client["pkg"]
    collection = db["authors"]
    cursor = collection.find({}).skip(skip_n).limit(limit_n)
    list_of_insertion = []
    for doc in cursor:        
        list_of_insertion.append({"name":doc["AND_ID"]})
    print('Completed process',skip_n//limit_n,'...')
    cursor.close()
    return list_of_insertion
    
n_cores = 6                
collection_size = 14900000
batch_size = 20000
skips = range(0, collection_size, batch_size)

nodes = Parallel(n_jobs=n_cores)(delayed(process_cursor_node)(client_name,skip_n,batch_size) for skip_n in tqdm.tqdm(skips))
