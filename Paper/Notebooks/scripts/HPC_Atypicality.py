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
from package.indicators.utils import * 
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
db  = 'pkg'

from package import Atypicality
indicator = 'atypicality'



def populate_list(idx,current_item,unique_items,indicator,scores_adj):
    if len(current_item)>2:
            try:
                current_adj = get_adjacency_matrix(unique_items,
                                                   [current_item],
                                                   unique_pairwise = False,
                                                   keep_diag=True)
    
                infos = get_paper_score(current_adj,
                                        scores_adj,
                                        unique_items,
                                        indicator)
                data.update_mongo(idx,infos)
            except:
                return None
            
            
parser = argparse.ArgumentParser(description='compute atypicality, var = journal or mesh')

parser.add_argument('-year')
parser.add_argument('-var')
parser.add_argument('-load')
parser.add_argument('-nb_sample')
args = parser.parse_args()
focal_year = int(args.year)
nb_sample = int(args.nb_sample)
var = str(args.var)

if var == 'journal':
    pars_var = 'j_ref'
elif var == 'mesh':
    pars_var = 'mesh'


path1 = '/home2020/home/beta/ppelleti/Taxonomy-of-novelty/Data/CR_year_category/weighted_network_self_loop'
path2 = '/home2020/home/beta/ppelleti/Taxonomy-of-novelty'

os.chdir(path2)
print(os.getcwd())
sys.path.append(os.getcwd())



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

true_current_adj_freq = pickle.load(open( path1 + "/{}.p".format(focal_year), "rb" )) 

if args.load:
    # Get nb_sample networks
    all_sampled_adj_freq = []
    for i in tqdm.tqdm(range(nb_sample)):
        sampled_current_adj_freq = pickle.load(
            open(path2 + '/Paper/Data/sample_network/{}'.format(var) + "/sample_{}_{}.p".format(i,focal_year),
                 "rb" ) )
        
        all_sampled_adj_freq.append(sampled_current_adj_freq.A)
        
    samples_3d = np.dstack(all_sampled_adj_freq)
    mean_adj_freq = csr_matrix(np.mean(samples_3d,axis = 2),dtype=float)
    sd_adj_freq = csr_matrix(np.std(samples_3d,axis = 2),dtype=float)
    
    mean_adj_freq.eliminate_zeros()
    sd_adj_freq.eliminate_zeros()
    comb_scores = (true_current_adj_freq-mean_adj_freq)/sd_adj_freq  
    comb_scores[np.isinf(comb_scores)] =  0
    comb_scores[np.isnan(comb_scores)] =  0
    comb_scores = triu(comb_scores,format='csr')
    comb_scores.eliminate_zeros()
    
    pickle.dump(
        comb_scores,
        open(path2 + '/Paper/Data/indicators_adj/{}'.format(var) + "/{}_{}.p".format('atypicality',focal_year),
             "wb" ) )
    
    
    current_items = items['current_items']
    
    print('yo')
    docs_infos = Parallel(n_jobs=12)(
        delayed(populate_list)(idx,
                               current_items[idx],
                               unique_items,
                               indicator,
                               comb_scores) for idx in tqdm.tqdm(current_items.keys()))
    
    pickle.dump(
        docs_infos,
        open(path2 + '/Paper/Data/yearly_data/{}'.format(var) + "/{}_{}.p".format('commonness',focal_year),
             "wb" ) )
    
    print('saved')
    
else:
    # Run nb_sample network shuffling, get the frequency of each combinaison for each sample 
    all_sampled_adj_freq = []
    for i in tqdm.tqdm(range(nb_sample)):
        # Shuffle Network
        sampled_current_items = suffle_network(current_items)
        # Get Adjacency matrix
        sampled_current_adj = get_adjacency_matrix(unique_items,
                                                   sampled_current_items,
                                                   unique_pairwise = False,
                                                   keep_diag =True)
        pickle.dump(
            sampled_current_adj,
            open(path2 + '/Paper/Data/sample_network/{}'.format(var) + "/sample_{}_{}.p".format(i,focal_year),
                 "wb" ) )
    
        


