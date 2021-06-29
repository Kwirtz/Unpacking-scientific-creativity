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

def hpc2mongo(time_window,var_type,indicator):
    for focal_year in range(time_window[0],time_window[1]):
        docs = pickle.load(open('D:/PKG/yearly_data/' + var_type + "/"+indicator+"_{}.p".format(focal_year), "rb" ) )    
        for doc in tqdm.tqdm(docs):
            if doc:
                try:
                    pmid, infos = list(doc.items())[0]
                    data.update_mongo(int(pmid),infos)
                except Exception as e:
                    print(e)

hpc2mongo([2009,2017],'mesh','commonness')



var_type = 'mesh'
indicator = 'commonness'
focal_year = 2000

docs = pickle.load(open('D:/PKG/yearly_data/' + var_type + "/"+indicator+"_{}.p".format(focal_year), "rb" ) )    

i=0
j=0
for doc in tqdm.tqdm(docs):
    try:
        if list(doc.items())[0][1]['journal_novelty_3y_1reu']['comb_infos']:
            i+=1
    except Exception as e:
        if doc:
            print(doc)
        j+=1

i
j