import time
import os 
os.chdir(r'C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty')
import tqdm
import yaml 
import numpy as np
import pandas as pd
import pickle
from scipy.sparse import lil_matrix

from package.indicators.utils import * 
from package import Dataset
from package.utils import create_cooc
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']


from package import Disruptiveness

print('open citation citation_network')

citation_network = pd.read_json('D:\PKG\data2605Cleaned\citation_network.json')
citation_network = citation_network.dropna(subset=['refs_pmids'])
citation_network = citation_network.drop('_id',axis = 1)
citation_network = citation_network[citation_network['Journal_JournalIssue_PubDate_Year'] != '']
citation_network = citation_network.explode('refs_pmids')
citation_network = citation_network.set_index(['PMID', 'refs_pmids'])

db = 'pkg'

f1000 = list(pd.read_json(r'D:\PKG\data2605Cleaned\f1000.json')['pmid'])
print('compute Disruptiveness')

data = Dataset(client_name = pars['client_name'], 
               db_name =  pars['db_name'],
               collection_name = pars[db]['collection_name'])

i=0
docs = data.collection.find({'refs_pmids':{'$exists':1},
                             'PMID':{'$in':f1000}},no_cursor_timeout=True)

docs = [doc for doc in tqdm.tqdm(docs)]

j= 0
for doc in tqdm.tqdm(docs):
    j+=1
    if j>1926:
        try:
            i+=1
            infos = Disruptiveness(doc['PMID'],
                                   doc[pars[db]['year_var']],
                                   doc['refs_pmids'],
                                   citation_network)
        
            data.update_mongo(doc['PMID'],infos)
        except Exception as e:
            print(e)
        with open('D:\PKG\data2605Cleaned\last_i_f1000.txt','w') as last_i:
            last_i.write(str(i))