import pymongo 
import tqdm
import pickle
import yaml


from package.indicators.utils import * 
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
db  = 'pkg'

data = Dataset(client_name = pars['client_name'], 
               db_name =  pars['db_name'],
               collection_name = pars[db]['collection_name'])
data.collection.find({'PMID':int(pmid)})[0]

def hpc2mongo(time_window,var_type,indicator):
    for focal_year in range(time_window[0],time_window[1]):
        docs = pickle.load(open('D:/PKG/yearly_data/' + var_type + "/"+indicator+"_{}.p".format(focal_year), "rb" ) )    
        for doc in tqdm.tqdm(docs):
            pmid, infos = list(doc.items())[0]
            data.update_mongo(int(pmid),infos)
            
        
hpc2mongo([2006,2010],'journal','novelty')
