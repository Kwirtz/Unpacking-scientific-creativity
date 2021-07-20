

import time
import os 

import tqdm
import yaml 
import pickle

from package.indicators.utils import * 
from package import Dataset
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
db= 'pkg'

for focal_year in range(2000,2004):
    
    data = Dataset(client_name = pars['client_name'], 
                   db_name =  pars['db_name'],
                   collection_name = pars[db]['collection_name'],
                   var = pars[db]['j_ref']['var'],
                   sub_var = pars[db]['j_ref']['sub_var'])

    docs = data.collection.find({
        #pars[db]['j_ref']['var']:{'$exists':'true'},
        pars[db]['year_var']:{'$eq':focal_year}
        }
        )
    
    docs = [doc for doc in tqdm.tqdm(docs) if pars[db]['j_ref']['var'] in doc.keys()]
    
    pickle.dump(docs, open('D:/PKG/yearly_data/journal' + "/{}.p".format(focal_year), "wb" ) )
    


for focal_year in range(2000,2021):
    data = Dataset(client_name = pars['client_name'], 
                   db_name =  pars['db_name'],
                   collection_name = pars[db]['collection_name'],
                   var = pars[db]['mesh']['var'],
                   sub_var = pars[db]['mesh']['sub_var'])

    docs = data.collection.find({
        pars[db]['mesh']['var']:{'$exists':'true'},
        pars[db]['year_var']:{'$eq':focal_year}
        }
        )
    
    docs = [doc for doc in tqdm.tqdm(docs)]
    
    pickle.dump(docs, open('D:/PKG/yearly_data/mesh' + "/{}.p".format(focal_year), "wb" ) )