

import time
import os 

import tqdm
import yaml 
import numpy as np
import pandas as pd
import pickle
from scipy.sparse import lil_matrix

from package.indicators.utils import * 
from package import Dataset
from package.utils import create_cooc
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']

f1000 = list(pd.read_json(r'D:\PKG\data2605Cleaned\f1000.json')['pmid'])

db  = 'pkg'

matrix_cooc = create_cooc(client_name = pars['client_name'], 
                          db_name =  pars['db_name'],
                          collection_name = pars['pkg']['collection_name'],
                           year_var = pars[db]['year_var'],
                           var = pars[db]['j_ref']['var'],
                           sub_var = pars[db]['j_ref']['sub_var'],
                           weighted_network = True,
                           self_loop = True)


# ###  Full code
from package import Atypicality


#matrix_cooc.main()

unique_items = list(pickle.load(
    open( matrix_cooc.path + "/name2index.p", "rb" )).keys())

from package import Atypicality
indicator = 'atypicality'

for y in range(2000,2021):
    t = time.time()
    focal_year = y
    data = Dataset(client_name = pars['client_name'], 
                   db_name =  pars['db_name'],
                   collection_name = pars[db]['collection_name'],
                   var = pars[db]['j_ref']['var'],
                   sub_var = pars[db]['j_ref']['sub_var'])

    docs = data.collection.find({
            pars[db]['j_ref']['var']:{'$exists':'true'},
            pars[db]['year_var']:focal_year
            }
            )

    items = data.get_items(docs,
                           focal_year,
                           indicator, 
                           restrict_wos_journal = False)

    true_current_adj = pickle.load(
        open( matrix_cooc.path + "/{}.p".format(focal_year), "rb" )) 
    
    t = time.time()
    scores_adj = Atypicality(true_current_adj,
                             items['current_items'],
                             unique_items,
                             nb_sample = 10)
    print(time.time()-t)

    for idx in tqdm.tqdm(items['current_items']):
        try:
            if len(items['current_items'][idx])>2:
                doc_items = pd.DataFrame(items['current_items'][idx]).iloc[:,0].tolist()
                current_adj = get_adjacency_matrix(unique_items,
                                                   [doc_items],
                                                   unique_pairwise = False,
                                                   keep_diag=True)

                infos = get_paper_score(current_adj,
                                        scores_adj,
                                        unique_items,
                                        indicator)
                data.update_mongo(idx,infos)
        except:
            pass


# -----
# # Commonness

# ### Full code



from package import Commonness
db  = 'pkg'
indicator = 'commonness'
unique_items = list(
        pickle.load(open( matrix_cooc.path + "/name2index.p", "rb" )).keys())

for focal_year in range(2000,2021):
    data = Dataset(client_name = pars['client_name'], 
                   db_name =  pars['db_name'],
                   collection_name = pars[db]['collection_name'],
                   var = pars[db]['j_ref']['var'],
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
    
    current_adj = pickle.load(open( matrix_cooc.path + "/{}.p".format(focal_year), "rb" )) 
    

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
                data.update_mongo(idx,infos)
            except:
                pass


# ----
# # Novelty

from package import Novelty




def sum_adj_matrix(time_window,path):
    
    unique_items = list(
        pickle.load(open( matrix_cooc.path + "/name2index.p", "rb" )).keys()) 
    matrix = lil_matrix((len(unique_items),len(unique_items)))
    
    for focal_year in time_window:
        fy_cooc = pickle.load(open( matrix_cooc.path + "/{}.p".format(focal_year), "rb" )) 
        matrix += fy_cooc 
        
    return matrix



# ### Full code

from package import Novelty
indicator = 'novelty'
window = 3
db  = 'pkg'

unique_items = list(
        pickle.load(open( matrix_cooc.path + "/name2index.p", "rb" )).keys()) 

for focal_year in range(2000,2021):
    data = Dataset(client_name = pars['client_name'], 
                   db_name =  pars['db_name'],
                   collection_name = pars[db]['collection_name'],
                   var = pars[db]['j_ref']['var'],
                   sub_var = pars[db]['j_ref']['sub_var'])

    docs = data.collection.find({
        pars[db]['j_ref']['var']:{'$exists':'true'},
        pars[db]['year_var']:focal_year})
        

    items = data.get_items(docs,
                           focal_year, 
                           indicator,
                           restrict_wos_journal = False)

    past_adj = sum_adj_matrix(range(1980,focal_year),
                              matrix_cooc.path)

    futur_adj = sum_adj_matrix(range(focal_year+1,focal_year+window+1),
                              matrix_cooc.path)

    difficulty_adj = sum_adj_matrix(range(focal_year-window,focal_year),
                              matrix_cooc.path)
    t = time.time()
    scores_adj = Novelty(past_adj,
                         futur_adj,
                         difficulty_adj,
                         n_reutilisation = 1)
    print(time.time()-t)

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

            data.update_mongo(idx,infos)


# # Disruptivness
# 
# ## Concept
# 
# - DI1
# 
# - DI5
# 
# - DI1nok
# 
# - DI5nok
# 
# - DeIn
# 
# - Breadth
# 
# - Depth
# 
# 
# ## Implementation

# In[2]:


from package import Disruptiveness


# In[ ]:


focal_year = 2016
db = 'pkg'
window = 3

data = Dataset(client_name = pars['client_name'], 
               db_name =  pars['db_name'],
               collection_name = pars[db]['collection_name'])

docs = data.collection.find({
    'refs_pmids':{'$exists':1},
    pars[db]['year_var']:focal_year}
    )

citation_network = pd.read_json('D:\PKG\data2605Cleaned\citation_network.json')
citation_network = citation_network.dropna(subset=['refs_pmids'])
citation_network = citation_network.drop('_id',axis = 1)
citation_network = citation_network[citation_network['Journal_JournalIssue_PubDate_Year'] != '']
citation_network = citation_network.explode('refs_pmids')
citation_network = citation_network.set_index(['PMID', 'refs_pmids'])


# In[1]:


doc = docs[0]


# In[8]:


infos = Disruptiveness(doc['PMID'],
                              doc[pars[db]['year_var']],
                              doc['refs_pmids'],
                              citation_network)


# In[ ]:


for focal_year in range(1975,2021):
    
    data = Dataset(client_name = pars['client_name'], 
                   db_name =  pars['db_name'],
                   collection_name = pars[db]['collection_name'])
    
    docs = data.collection.find({pars[db]['year_var']:str(focal_year),
                                'refs_pmids':{'$exists':1}})
    for doc in tqdm.tqdm(docs):

        infos = Disruptiveness(doc['PMID'],
                               doc[pars[db]['year_var']],
                               doc['refs_pmids'],
                               citation_network)

        data.update_mongo(doc['PMID'],infos)


# In[5]:


infos


# # K-score
# 
# ## Concept
# 
# In order to produce the K-score based on Bornmann et al. (2019) we do not 
# 
# ## Implementation

# In[3]:


from package import Kscores


# In[5]:


focal_year = 2016
window = 3
db  = 'pkg'

data = Dataset(client_name = pars['client_name'], 
               db_name =  pars['db_name'],
               collection_name = pars[db]['collection_name'],
               var = pars[db]['mesh']['var'],
               sub_var = pars[db]['mesh']['sub_var'])

docs = data.collection.find({
    pars[db]['mesh']['var']:{'$exists':'true'},
    pars[db]['year_var']:focal_year}
    )


# In[7]:


indicator = 'degree_centrality'

items = data.get_items(docs,
                       focal_year,
                       indicator, 
                       restrict_wos_journal = False,
                       window = 10)

kw_adj = get_adjacency_matrix(items['unique_items'],
                              items['difficulty_items'].values(),
                              unique_pairwise = True,
                              keep_diag = False)
kw_adj = pd.DataFrame(kw_adj.A, columns=items['unique_items'], index=items['unique_items'])
G = nx.from_pandas_adjacency(kw_adj)


# In[11]:


items


# In[90]:


d_c = nx.degree_centrality(G)
#nx.closeness_centrality(G)
#nx.betweenness_centrality(G, normalized = True, endpoints = False)


# In[4]:


for doc in tqdm.tqdm(docs):
    focal_paper_mesh_infos = doc[pars[db]['mesh']['var']]
    focal_paper_year = doc[pars[db]['year_var']]
    infos = Kscores(focal_paper_year, focal_paper_mesh_infos)
    data.update_mongo(doc[pars[db]['pmid']], infos)
    


# In[91]:


d_c


# In[83]:





# In[14]:


list(itertools.chain(*meshs_df.category))


# # Diversity
# 
# ## Concept
# 
# ## Implementation
