import argparse

parser = argparse.ArgumentParser(description='compute novelty, var = journal or mesh')

parser.add_argument('-year')
parser.add_argument('-var')
args = parser.parse_args()
focal_year = int(args.year)
var = str(args.var)

if var == 'journal':
    pars_var = 'j_ref'
elif var == 'mesh':
    pars_var = 'mesh'

import time
import sys, os
os.chdir('../../../')
print(os.getcwd())
sys.path.append(os.getcwd())
import tqdm
import yaml 
import numpy as np
import pandas as pd
import pickle
from scipy.sparse import lil_matrix

from package.indicators.utils import * 
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']

path1 = '/home2020/home/beta/ppelleti/Taxonomy-of-novelty/Data/CR_year_category/unweighted_network_no_self_loop'
path2 = '/home2020/home/beta/ppelleti/Taxonomy-of-novelty'
db  = 'pkg'

from package import Novelty
indicator = 'novelty'
window = 3

unique_items = list(
        pickle.load(
            open(path1 + "/name2index.p", "rb" )).keys()) 

docs = pickle.load(open(path2 +'/Paper/Data/yearly_data/{}'.format(var) + "/{}.p".format(focal_year), "rb" ) )
#docs = pickle.load(open('D:/PKG/yearly_data/journal' + "/{}.p".format(focal_year), "rb" ) )
    
data = Dataset(var = pars[db][pars_var]['var'],
               sub_var = pars[db][pars_var]['sub_var'])

items = data.get_items(docs,
                       focal_year, 
                       indicator,
                       restrict_wos_journal = False)

past_adj = sum_adj_matrix(range(1980,focal_year),
                          path1)

futur_adj = sum_adj_matrix(range(focal_year+1,focal_year+window+1),
                          path1)

difficulty_adj = sum_adj_matrix(range(focal_year-window,focal_year),
                          path1)
t = time.time()
scores_adj = Novelty(past_adj,
                     futur_adj,
                     difficulty_adj,
                     n_reutilisation = 1)
print(time.time()-t)
docs_infos = []
for idx in tqdm.tqdm(items['current_items']):
    if len(items['current_items'][idx])>2:
        current_adj = get_adjacency_matrix(unique_items,
                                           [items['current_items'][idx]],
                                           unique_pairwise = True,
                                           keep_diag=False)

        infos = get_paper_score(current_adj,
                                scores_adj,
                                unique_items,
                                indicator,
                                item_name = var,
                                window = str(window),
                                n_reutilisation = str(1))

        docs_infos.append({idx:infos})

pickle.dump(docs_infos, open(path2 + '/Paper/yearly_data/{}'.format(var) + "/{}_{}.p".format('novelty',focal_year), "wb" ) )
