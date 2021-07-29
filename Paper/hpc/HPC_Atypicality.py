import argparse
import time
import sys, os
import tqdm
import yaml 
import numpy as np
import pandas as pd
import pickle
from scipy.sparse import lil_matrix, csr_matrix, triu
from joblib import Parallel, delayed
import re


path2 = r'C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty'
os.chdir(path2)
sys.path.append(os.getcwd())



from package.indicators.utils import * 
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
db  = 'pkg'

from package import Atypicality
indicator = 'atypicality'



def populate_list(idx,current_item,unique_items,item_name,indicator,scores_adj):
    if len(current_item)>2:
            try:
                current_adj = get_adjacency_matrix(unique_items,
                                                   [current_item],
                                                   unique_pairwise = False,
                                                   keep_diag=True)
    
                infos = get_paper_score(current_adj,
                                        scores_adj,
                                        list(unique_items.keys()),
                                        indicator,
                                        item_name)
                return {idx:infos}
            except Exception as e:
                print(e)


def compute_comb_score(path2,true_current_adj_freq,nb_sample,var,focal_year):
    # Get nb_sample networks
    all_sampled_adj_freq = []
    for i in tqdm.tqdm(range(nb_sample)):
        sampled_current_adj_freq = pickle.load(
            open(path2 + '/sample_network/{}'.format(var) + "/sample_{}_{}.p".format(i,focal_year),
                 "rb" ) )
        
        all_sampled_adj_freq.append(sampled_current_adj_freq)
    

    unique_values = get_unique_value_used(all_sampled_adj_freq)
    
    mean_adj_freq, sd_adj_freq = get_comb_mean_sd(path2,
                                                  all_sampled_adj_freq,
                                                  unique_values,
                                                  var,
                                                  focal_year)
    
    comb_scores = (true_current_adj_freq-mean_adj_freq)/sd_adj_freq  
    comb_scores[np.isinf(comb_scores)] =  0
    comb_scores[np.isnan(comb_scores)] =  0
    comb_scores = triu(comb_scores,format='csr')
    comb_scores.eliminate_zeros()
        
    pickle.dump(
        comb_scores,
        open(path2 + '/indicators_adj/{}'.format(var) + "/{}_{}.p".format('atypicality',focal_year),
             "wb" ) )
    

  
def update_paper_values(path2,current_items,unique_items,indicator,focal_year):
    comb_scores = pickle.load(
        open(path2 + '/indicators_adj/{}'.format(var) + "/{}_{}.p".format(indicator,focal_year),
             "rb" ) )
    docs_infos = Parallel(n_jobs=12)(
        delayed(populate_list)(idx,
                                current_items[idx],
                                unique_items,
                                indicator,
                                comb_scores) for idx in tqdm.tqdm(current_items.keys()))
    
    pickle.dump(
        docs_infos,
        open(path2 + '/yearly_data/{}'.format(var) + "/{}_{}.p".format(indicator,focal_year),
              "wb" ) )
    
    print('saved')

# Run nb_sample network shuffling, get the frequency of each combinaison for each sample 

def sample_network(path2,current_items,unique_items,nb_sample,focal_year):
        
    allready_computed = [f for f in os.listdir(path2 + '/sample_network/{}'.format(var)) 
                         if re.match(r'sample_[0-9+]_{}'.format(focal_year), f)]
    for i in tqdm.tqdm(range(nb_sample)):
        filename =  "sample_{}_{}.p".format(i,focal_year)
        if filename not in allready_computed:
            # Shuffle Network
            sampled_current_items = suffle_network(current_items)
            # Get Adjacency matrix
            sampled_current_adj = get_adjacency_matrix(unique_items,
                                                       sampled_current_items,
                                                       unique_pairwise = False,
                                                       keep_diag =True)
            pickle.dump(
                sampled_current_adj,
                open(path2 + '/sample_network/{}/'.format(var) + filename,
                     "wb" ) )

parser = argparse.ArgumentParser(description='compute atypicality, var = journal or mesh')

parser.add_argument('-year')
parser.add_argument('-var')
parser.add_argument('-load', type=bool)
parser.add_argument('-nb_sample')
args = parser.parse_args()
focal_year = int(args.year)
nb_sample = int(args.nb_sample)
var = str(args.var)


if var == 'journal':
    pars_var = 'j_ref'
    path1 = r'C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\Data\CR_year_category\weighted_network_self_loop'
elif var == 'mesh':
    pars_var = 'mesh'
    path1 = r'C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\Data\Mesh_year_category\weighted_network_self_loop'

unique_items = pickle.load(
            open(path1 + "/name2index.p", "rb" ))
# docs = pickle.load(open(path2 +'/Paper/Data/yearly_data/{}'.format(var) + "/{}.p".format(focal_year), "rb" ) )

docs = pickle.load(open('D:/PKG/yearly_data/'+var + "/{}.p".format(focal_year), "rb" ) )
    

data = Dataset(var = pars[db][pars_var]['var'],
              sub_var = pars[db][pars_var]['sub_var'])

items = data.get_items(docs,
                      focal_year,
                      indicator, 
                      restrict_wos_journal = False)

current_items = items['current_items']

true_current_adj_freq = pickle.load(open( path1 + "/{}.p".format(focal_year), "rb" )) 
sample_network(r'D:\PKG',current_items,unique_items,nb_sample,focal_year)
#compute_comb_score(r'D:\PKG',true_current_adj_freq,nb_sample,var,focal_year)
#update_paper_values(r'D:\PKG',current_items,unique_items,indicator,focal_year,focal_year)