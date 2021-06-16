import time
import os 

import tqdm
import yaml 
import numpy as np
import pandas as pd
import pickle
from scipy.sparse import lil_matrix

from package.indicators.utils import * 
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']

f1000 = list(pd.read_json(r'D:\PKG\data2605Cleaned\f1000.json')['pmid'])

db  = 'pkg'

from package import Novelty
indicator = 'novelty'
window = 3
db  = 'pkg'
path = r'C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\Data\CR_year_category\unweighted_network_no_self_loop'

unique_items = list(
        pickle.load(
            open(path + "/name2index.p", "rb" )).keys()) 

for focal_year in range(2000,2021):
    docs = pickle.load(docs, open('/home2020/home/beta/ppelleti/Taxonomy-of-novelty/Paper/Data/yearly_data/journal' + "/{}.p".format(focal_year), "wb" ) )
    docs = pickle.load(open('D:/PKG/yearly_data/journal' + "/{}.p".format(focal_year), "rb" ) )
        
    data = Dataset(var = pars[db]['j_ref']['var'],
                   sub_var = pars[db]['j_ref']['sub_var'])
    
    items = data.get_items(docs,
                           focal_year, 
                           indicator,
                           restrict_wos_journal = False)

    past_adj = sum_adj_matrix(range(1980,focal_year),
                              path)

    futur_adj = sum_adj_matrix(range(focal_year+1,focal_year+window+1),
                              path)

    difficulty_adj = sum_adj_matrix(range(focal_year-window,focal_year),
                              path)
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
                                    item_name = 'journal',
                                    window = str(window),
                                    n_reutilisation = str(1))

            docs_infos.append({idx:infos})
    
    pickle.dump(docs, open('D:/PKG/yearly_data/journal' + "/{}.p".format(focal_year), "wb" ) )
    