
import argparse

parser = argparse.ArgumentParser(description='compute commonness, var = journal or mesh')

parser.add_argument('-year')
parser.add_argument('-var')
args = parser.parse_args()
focal_year = int(args.year)
var = str(args.var)

if var == 'journal':
    pars_var = 'j_ref'
elif var == 'mesh':
    pars_var = 'mesh'


path1 = '/home2020/home/beta/ppelleti/Taxonomy-of-novelty/Data/CR_year_category/weighted_network_self_loop'
path2 = '/home2020/home/beta/ppelleti/Taxonomy-of-novelty'


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

from package.indicators.utils import * 
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
db  = 'pkg'

from package import Commonness
indicator = 'commonness'

unique_items = list(
        pickle.load(
            open(path1 + "/name2index.p", "rb" )).keys()) 

docs = pickle.load(open(path2 +'/Paper/Data/yearly_data/{}'.format(var) + "/{}.p".format(focal_year), "rb" ) )
#docs = pickle.load(open('D:/PKG/yearly_data/journal' + "/{}.p".format(focal_year), "rb" ) )
    

data = Dataset(var = pars[db]['j_ref']['var'],
               sub_var = pars[db]['j_ref']['sub_var'])

docs = data.collection.find({
    pars[db]['j_ref']['var']:{'$exists':'true'},
    pars[db]['year_var']:{'$eq':focal_year}
    }
    )


items = data.get_items(docs,
                       focal_year,
                       indicator, 
                       restrict_wos_journal = False)

current_adj = pickle.load(open( path1 + "/{}.p".format(focal_year), "rb" )) 


t = time.time()
scores_adj = Commonness(current_adj)
time.time() - t 

for idx in tqdm.tqdm(items['current_items']):
    if len(items['current_items'][idx])>2:
        try:
            current_adj = get_adjacency_matrix(unique_items,
                                               [items['current_items'][idx]],
                                               unique_pairwise = False,
                                               keep_diag=True)

            infos = get_paper_score(current_adj,
                                    scores_adj,
                                    unique_items,
                                    indicator)
            docs_infos.append({idx:infos})
        except:
            pass



pickle.dump(docs_infos, open(path2 + '/Paper/yearly_data/{}'.format(var) + "/{}_{}.p".format('commonness',focal_year), "wb" ) )
