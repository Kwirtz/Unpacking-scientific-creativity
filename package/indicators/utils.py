import numpy as np
from sklearn import preprocessing
from scipy.sparse import csr_matrix, triu, lil_matrix
from scipy.linalg import norm
from itertools import combinations, chain
import pandas as pd
from random import sample
import tqdm
import networkx as nx
import pymongo
import time
import pickle
from joblib import Parallel, delayed

def get_comb(item):
    combi = [tuple(sorted(comb)) for comb in combinations(item,2)]
    return combi
    

def get_adjacency_matrix(unique_items,
                         items_list,
                         unique_pairwise,
                         keep_diag):
    
    lb = preprocessing.MultiLabelBinarizer(classes=sorted(unique_items))
    if unique_pairwise:
        dtm_mat = csr_matrix(lb.fit_transform(items_list))
        adj_mat = dtm_mat.T.dot(dtm_mat)
    else:
        # combi = []
        # #adj_mat = csr_matrix((len(lb.classes),len(lb.classes)))
        # for item in tqdm.tqdm(items_list):
        #     for comb in combinations(item,2):
        #         combi.append(tuple(sorted(comb)))
        #         #i = np.where(np.array(lb.classes) == comb[0])
        #         #j = np.where(np.array(lb.classes) == comb[1])
        #         #adj_mat[i,j] = int(adj_mat.A[i,j])+1
                
        combi = Parallel(n_jobs= 20)(delayed(get_comb)(item)
                                      for item in tqdm.tqdm(items_list,
                                                            desc ='feed network'))  
        combi = list(chain.from_iterable(combi))
        G = nx.MultiGraph(combi)
        G.add_nodes_from(lb.classes)
        adj_mat = nx.adjacency_matrix(G,nodelist=sorted(G.nodes()))
    if keep_diag == False:
        adj_mat.setdiag(0)
    adj_mat.eliminate_zeros()
    return adj_mat


# Moslty used for Novelty
   
def sum_adj_matrix(time_window,path):
    
    unique_items = list(
        pickle.load(open( path + "/name2index.p", "rb" )).keys()) 
    matrix = lil_matrix((len(unique_items),len(unique_items)))
    
    for focal_year in tqdm.tqdm(time_window):
        fy_cooc = pickle.load(open( path + "/{}.p".format(focal_year), "rb" )) 
        matrix += fy_cooc 
        
    return matrix


def get_difficulty_cos_sim(difficulty_adj):
     
     difficulty_norms = np.apply_along_axis(norm, 0, difficulty_adj.A)[np.newaxis]
     difficulty_norms = difficulty_norms.T.dot(difficulty_norms)
     cos_sim = difficulty_adj.dot(difficulty_adj)/difficulty_norms
     cos_sim = csr_matrix(triu(np.nan_to_num(cos_sim)))
     cos_sim.setdiag(0)
     cos_sim.eliminate_zeros()
     return cos_sim
 
# Mostly used in Atypicality    
 
# def get_comb_freq(adj_mat):
#     nb_comb = np.sum(triu(adj_mat))
#     return adj_mat/nb_comb
    
def suffle_network(current_items):
    
    lst = []
    for idx in current_items:
        for item in current_items[idx]:
          lst.append({'idx':idx,
                      'journal':item['journal'],
                      'year': item['year']})  
    df = pd.DataFrame(lst)    
    print('start sampling')
    years = set(df.year)
    for year in  years:
        journals_y = list(df.journal[df.year == year])
        df.journal[df.year == year] = sample(journals_y,k = len(journals_y))
    # random_network = []
    # for idx in tqdm.tqdm(current_items,desc='make sampled journal list'):
    #     journal_list = list(df.journal[df.idx == idx])
    #     random_network.append(journal_list)
    random_network = list(df.groupby('idx')['journal'].apply(list))
    # random_network = Parallel(n_jobs= 20)(delayed(lambda df, idx: list(df.journal[df.idx == idx]))(df, idx)
    #                                   for idx in tqdm.tqdm(current_items))  
    return random_network
        
def get_unique_value_used(all_sampled_adj_freq):
    tuples_set = set()
    for sampled_adj in tqdm.tqdm(all_sampled_adj_freq):
        i_list = sampled_adj.nonzero()[0].tolist()
        j_list = sampled_adj.nonzero()[1].tolist()
        for i, j in zip(i_list,j_list):
            tuples_set.update([(i, j)])
    return list(tuples_set)

def get_cell_mean_sd(value,all_sampled_adj_freq):
    count = []
    for sampled_adj in all_sampled_adj_freq:
        count.append(sampled_adj[value[0],value[1]])
    return value, np.mean(count), np.std(count)

def get_comb_mean_sd(all_sampled_adj_freq,unique_values):
    
    mean_comb = lil_matrix(all_sampled_adj_freq[0].shape)
    sd_comb = lil_matrix(all_sampled_adj_freq[0].shape)
    
    # #mean_sd_list = [get_cell_mean_sd(value,all_sampled_adj_freq) for value in tqdm.tqdm(unique_values)]
    # print('get mean and sd')
    # mean_sd_list = Parallel(n_jobs= 20)(delayed(get_cell_mean_sd)(value,all_sampled_adj_freq)
    #                                     for value in tqdm.tqdm(unique_values))
    
    
    # row, col, mean, sd = [], [], [], []
    # for value, m, s in tqdm.tqdm(mean_sd_list):
    #     row.append(value[0])
    #     col.append(value[1])
    #     mean.append(m)
    #     sd.append(s)
        
    # mean_comb = sparse.coo_matrix((mean, (row, col)),
    #                               shape=all_sampled_adj_freq[0].shape)
    # sd_comb = sparse.coo_matrix((sd, (row, col)),
    #                               shape=all_sampled_adj_freq[0].shape)
    
    for value in tqdm.tqdm(unique_values):
        value, mean, sd = get_cell_mean_sd(value,all_sampled_adj_freq)
        mean_comb[value[0],value[1]] = mean
        sd_comb[value[0],value[1]] = sd
    # print('populate matrix')
    # for value, mean, sd in tqdm.tqdm(mean_sd_list):
    #     mean_comb[value[0],value[1]] = mean
    #     sd_comb[value[0],value[1]] = sd
    
    return mean_comb, sd_comb
        
        
def get_paper_score(doc_adj,comb_scores,unique_items,indicator,item_name,**kwargs):
    
    doc_comb_adj = csr_matrix(doc_adj.multiply(comb_scores))
    
    unique_comb_idx = triu(doc_comb_adj,k=0).nonzero() if indicator in ['atypicality','commonness'] else triu(doc_comb_adj,k=1).nonzero()
    
    comb_idx = [[],[]]
    for i, j in zip(list(unique_comb_idx[0]),
                    list(unique_comb_idx[1])):
        n = int(doc_adj[i,j])
        for c in range(n):
            comb_idx[0].append(i)
            comb_idx[1].append(j)
    
    
    
    comb_infos = pd.DataFrame([
        {
            'item1':sorted(unique_items)[i],
            'item2':sorted(unique_items)[j],
            'score':doc_comb_adj[i,j]/int(doc_adj[i,j])
            } 
        for i,j in zip(comb_idx[0],comb_idx[1])]
        )
    
    if comb_idx[0]:
        comb_list = comb_infos.score.tolist()
        
        comb_infos = comb_infos.groupby(['item1','item2','score']).size().reset_index()
        comb_infos = comb_infos.rename(columns = {0:'count'}).to_dict('records')
    if isinstance(comb_infos, pd.DataFrame):
        comb_infos = comb_infos if not comb_infos.empty else None

    key = item_name+'_'+indicator
    if 'n_reutilisation' and 'window' in kwargs:
        key = key +'_'+kwargs['window']+'y_'+kwargs['n_reutilisation']+'reu'
    elif 'window' in kwargs:
        key = key +'_'+kwargs['window']+'y'
       
    doc_infos = {
        'nb_comb':len(comb_infos) if comb_infos else 0,
        'comb_infos': comb_infos
        }
    
    
    if indicator == 'novelty':
        score = {'novelty':sum(comb_list) if comb_idx[0] else 0}
    elif indicator == 'atypicality':
        score = {'conventionality': np.median(comb_list) if comb_idx[0] else None,
                 'novelty': np.quantile(comb_list,0.1) if comb_idx[0] else None
                 }
    elif indicator == 'commonness':
        score = {'novelty': -np.log(np.quantile(comb_list,0.1)) if comb_idx[0] else None}
            
        
    doc_infos.update({
        'score':score
        })
    
    return {key:doc_infos}



#### Get infos from dataset depending on the indicator used


class Dataset:
    
    def __init__(self,
                 client_name = None,
                 db_name = None,
                 collection_name = None,
                 var = None,
                 sub_var = None):
        if client_name:
            self.client = pymongo.MongoClient(client_name)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        else:
            collection_name = 'articles'
            
        if 'wos' in collection_name:
            self.VAR_YEAR = 'PY'
            self.VAR_PMID = 'PM'
        elif 'articles' in collection_name:
            self.VAR_YEAR = 'Journal_JournalIssue_PubDate_Year'
            self.VAR_PMID = 'PMID'
        self.VAR = var
        self.SUB_VAR = sub_var
    
    def get_item_infos(self,
                       item,
                       indicator,
                       restrict_wos_journal):
        
        if restrict_wos_journal:
            if 'category' in item.keys():
                if indicator == 'atypicality':
                    if 'year' in item.keys():
                        all_item = [item[self.SUB_VAR]]
                        doc_item = {'journal':item[self.SUB_VAR],
                                          'year':item['year']}
                else:
                    all_item = [item[self.SUB_VAR]]
                    doc_item = item[self.SUB_VAR]    
                    
                return all_item, doc_item
            
        else:
            if indicator == 'atypicality':
                if 'year' in item.keys():
                    all_item = [item[self.SUB_VAR]]
                    doc_item = {'journal':item[self.SUB_VAR],
                                      'year':item['year']}
            else:
                all_item = [item[self.SUB_VAR]]
                doc_item = item[self.SUB_VAR]
            
            return all_item, doc_item
        return [], []
    
    def get_items(self,
                  docs,
                  focal_year,
                  indicator,
                  restrict_wos_journal = False):

        only_focal_y = ['commonness','atypicality']
        ######### Set Objects #########
        all_items = set()
        current_items = dict()
        
        ######### Iterate over documents #########
        for items in tqdm.tqdm(docs):
            doc_items = list()
            for item in items[self.VAR]:
                ######### Get doc item and update journal list #########
                all_item, doc_item = self.get_item_infos(item,
                                                    indicator,
                                                    restrict_wos_journal)
                if doc_item:
                    all_items.update(all_item)
                    doc_items.append(doc_item)
                
            ######### Store items #########
            ### focal year items
            doc_items = list(doc_items)
            
            if items[self.VAR_YEAR] == focal_year:
                current_items.update({
                    str(items[self.VAR_PMID]):doc_items
                })       
                    
        ######### Return dict with items for all periods #########       
        list_items = {
            'unique_items':sorted(tuple(all_items)),
            'current_items':current_items
            }
            
        return list_items

    def update_mongo(self,
                     pmid,
                     doc_infos):
    
        query = { self.VAR_PMID: int(pmid) }
        newvalues = { '$set': doc_infos}
        self.collection.update_one(query,newvalues)
