import argparse

parser = argparse.ArgumentParser(description='compute novelty, var = journal or mesh')

parser.add_argument('-year')
parser.add_argument('-var')
args = parser.parse_args()
focal_year = int(args.year)
var = str(args.var)

if var == 'journal':
    pars_var = 'j_ref'
    path1 = '/home2020/home/beta/ppelleti/Taxonomy-of-novelty/Data/CR_year_category/unweighted_network_no_self_loop'
elif var == 'mesh':
    pars_var = 'mesh'
    path1 = r'C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\Data\Mesh_year_category\weighted_network_self_loop'

#path1 = r'C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\Data\Mesh_year_category\weighted_network_self_loop'
#path2 = '/home2020/home/beta/ppelleti/Taxonomy-of-novelty'
path2 = r'C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty'

       

import time
import sys, os
os.chdir(path2)
print(os.getcwd())
sys.path.append(os.getcwd())
import tqdm
import yaml 
import numpy as np
import pandas as pd
import pickle
from scipy.sparse import lil_matrix
from joblib import Parallel, delayed
from package.indicators.utils import * 
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
db  = 'pkg'

focal_year = 2000

from package import Novelty
indicator = 'novelty'
window = 3

unique_items = list(
        pickle.load(
            open(path1 + "/name2index.p", "rb" )).keys()) 

#docs = pickle.load(open(path2 +'/Paper/Data/yearly_data/{}'.format(var) + "/{}.p".format(focal_year), "rb" ) )
# docs = pickle.load(open('D:/PKG/yearly_data/{}'.format(var) + "/{}.p".format(focal_year), "rb" ) )
# print('loaded')
# data = Dataset(var = pars[db][pars_var]['var'],
#                 sub_var = pars[db][pars_var]['sub_var'])

data = Dataset(client_name = pars['client_name'], 
               db_name =  pars['db_name'],
               collection_name = pars[db]['collection_name']),
               var = pars[db][pars_var]['var'],
               sub_var = pars[db][pars_var]['sub_var'])

docs = data.collection.find({
    pars[db][pars_var]['var']:{'$exists':'true'},
    pars[db]['year_var']:{'$eq':focal_year}
    }
    )
print('iterate over document')
items = data.get_items(docs,
                        focal_year, 
                        indicator,
                        restrict_wos_journal = False)

print('calculate past matrix')
past_adj = sum_adj_matrix(range(1980,focal_year),
                          path1)

print('calculate futur matrix')
futur_adj = sum_adj_matrix(range(focal_year+1,focal_year+window+1),
                          path1)

print('calculate difficulty matrix')
difficulty_adj = sum_adj_matrix(range(focal_year-window,focal_year),
                          path1)
t = time.time()
scores_adj = Novelty(past_adj,
                      futur_adj,
                      difficulty_adj,
                      n_reutilisation = 1)
print(time.time()-t)

pickle.dump(scores_adj, open('D:/PKG/indicators_adj/{}'.format(var) + "/{}_{}.p".format('novelty',focal_year), "wb" ) )


print('scores saved')


def populate_list(idx,current_item,unique_items,indicator,scores_adj,var,window):
    if len(current_item)>2:
            try:
                current_adj = get_adjacency_matrix(unique_items,
                                                    [current_item],
                                                    unique_pairwise = True,
                                                    keep_diag=False)
    
                infos = get_paper_score(current_adj,
                                        scores_adj,
                                        unique_items,
                                        indicator,
                                 	item_name = var,
                                 	window = str(window),
                                 	n_reutilisation = str(1))
                return {idx:infos}
            except:
                return None

current_items = items['current_items']
populate_list(idx,current_items[idx],unique_items,indicator,scores_adj,var,window)

docs_infos = Parallel(n_jobs=20)(delayed(populate_list)(idx,current_items[idx],unique_items,indicator,scores_adj,var,window) for idx in tqdm.tqdm(current_items.keys()))
print('yo')


pickle.dump(docs_infos, open(path2 + '/Paper/Data/yearly_data/{}'.format(var) + "/{}_{}.p".format('novelty',focal_year), "wb" ) )
