#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Introduction" data-toc-modified-id="Introduction-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Introduction</a></span><ul class="toc-item"><li><span><a href="#Atypicality,-Commonness-and-Novelty" data-toc-modified-id="Atypicality,-Commonness-and-Novelty-1.1"><span class="toc-item-num">1.1&nbsp;&nbsp;</span>Atypicality, Commonness and Novelty</a></span></li><li><span><a href="#Notations" data-toc-modified-id="Notations-1.2"><span class="toc-item-num">1.2&nbsp;&nbsp;</span>Notations</a></span><ul class="toc-item"><li><ul class="toc-item"><li><span><a href="#-------" data-toc-modified-id="--------1.2.0.1"><span class="toc-item-num">1.2.0.1&nbsp;&nbsp;</span>-------</a></span></li></ul></li></ul></li></ul></li><li><span><a href="#Atypicality" data-toc-modified-id="Atypicality-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Atypicality</a></span><ul class="toc-item"><li><span><a href="#Concept" data-toc-modified-id="Concept-2.1"><span class="toc-item-num">2.1&nbsp;&nbsp;</span>Concept</a></span></li><li><span><a href="#Implementation" data-toc-modified-id="Implementation-2.2"><span class="toc-item-num">2.2&nbsp;&nbsp;</span>Implementation</a></span></li></ul></li><li><span><a href="#Commonness" data-toc-modified-id="Commonness-3"><span class="toc-item-num">3&nbsp;&nbsp;</span>Commonness</a></span><ul class="toc-item"><li><span><a href="#Concept" data-toc-modified-id="Concept-3.1"><span class="toc-item-num">3.1&nbsp;&nbsp;</span>Concept</a></span></li><li><span><a href="#Implementation" data-toc-modified-id="Implementation-3.2"><span class="toc-item-num">3.2&nbsp;&nbsp;</span>Implementation</a></span></li></ul></li><li><span><a href="#Novelty" data-toc-modified-id="Novelty-4"><span class="toc-item-num">4&nbsp;&nbsp;</span>Novelty</a></span><ul class="toc-item"><li><span><a href="#Concept" data-toc-modified-id="Concept-4.1"><span class="toc-item-num">4.1&nbsp;&nbsp;</span>Concept</a></span></li><li><span><a href="#Implementation" data-toc-modified-id="Implementation-4.2"><span class="toc-item-num">4.2&nbsp;&nbsp;</span>Implementation</a></span></li></ul></li><li><span><a href="#Disruptivness" data-toc-modified-id="Disruptivness-5"><span class="toc-item-num">5&nbsp;&nbsp;</span>Disruptivness</a></span><ul class="toc-item"><li><span><a href="#Concept" data-toc-modified-id="Concept-5.1"><span class="toc-item-num">5.1&nbsp;&nbsp;</span>Concept</a></span></li><li><span><a href="#Implementation" data-toc-modified-id="Implementation-5.2"><span class="toc-item-num">5.2&nbsp;&nbsp;</span>Implementation</a></span></li></ul></li><li><span><a href="#K-score" data-toc-modified-id="K-score-6"><span class="toc-item-num">6&nbsp;&nbsp;</span>K-score</a></span><ul class="toc-item"><li><span><a href="#Concept" data-toc-modified-id="Concept-6.1"><span class="toc-item-num">6.1&nbsp;&nbsp;</span>Concept</a></span></li><li><span><a href="#Implementation" data-toc-modified-id="Implementation-6.2"><span class="toc-item-num">6.2&nbsp;&nbsp;</span>Implementation</a></span></li></ul></li><li><span><a href="#Diversity" data-toc-modified-id="Diversity-7"><span class="toc-item-num">7&nbsp;&nbsp;</span>Diversity</a></span><ul class="toc-item"><li><span><a href="#Concept" data-toc-modified-id="Concept-7.1"><span class="toc-item-num">7.1&nbsp;&nbsp;</span>Concept</a></span></li><li><span><a href="#Implementation" data-toc-modified-id="Implementation-7.2"><span class="toc-item-num">7.2&nbsp;&nbsp;</span>Implementation</a></span></li></ul></li></ul></div>

# # Introduction
# 

# ## Atypicality, Commonness and Novelty 
# 
# - Atypicality (Uzzi et al 2013), Commonness (Lee et al 2015) and Novelty (Wang et al 2017) are All indicators that works with references of an article at a journal level.
# All these indicators uses journals combinaison to represente knowledge combinaison.
# 
# 
# - All indicators works yearly and uses journals adjacency matrices but we need to emphasis on some differences. Consider for example that we are in year $y_t$, and that the sample start at year $y_0$, for a given indicator we need to consider:
#     
#     - Atypicality (Weighted network - Allow self-loop)
#         
#         - All current combinaison in $y_t$ (Adjacency matrix for $y_t$)
#                
#         - All items and year items in $y_t$ (Dict of list of dict: for each article a list of references with journal name and year of publication)
#                 
#         - A set of unique items
#         
#     - Commmonness (Weighted network - Allow self-loop)
#        
#         - All current combinaison in $y_t$
#        
#     - Novelty (Unweighted network - No self-loop):  
#     
#         - All past combinaison to verify that a combinaison were never made before (Adjacency matrix from $y_0$ to $y_{t-1}$)
#                 
#         - Past combinaison (on b years) to calculate the cosine similairty (Adjacency matrix from $y_{t-b-1}$ to $y_{t-1}$)
#                 
#         - Futur combinaison (on f years) to verify the reutilisation of the given combinaision (Adjacency matrix from $y_{t+1}$ to $y_{t+f+1}$)
# 
# 
# - Each indicator will return an adjacency matrix that represent the difficulty of every possible combinaison
# 
# 
# - After computing the indicator adjacency matrix, we generate a adjacency matrix for each document with the same dimension and simply do element-wise multiplication to filter out difficulties for each combination made in a given article
# 
# 
# - We finally update in mongo for each article and for each indicator :
# 
#     - all combinaisons of references made
#     
#     - the difficulty of each of these combinaisons
#     
#     - how many time the combinaison were made within the article
#     
#     
# ## Notations
# 
# - $D$ is defined as our set of document $d$ of dimension $n$
# 
# 
# - The set of nodes $V$ of dimension $v$ represent here the journals, a given journal is defined as $V_i$
# 
# 
# - The set of edges is noted $E$. The number of combinations between $V_i$ and $V_j$ is written $w({V_i,V_j})$. The degree of a node $V_i$ is written $k_i$.
# 
# 
# - $N$ is defined as the total number of edges (combinaisons) in $G$, $N=\Sigma_{i=1}^{v}\Sigma_{j=1}^{v}w(V_i,V_j)$
# 
# 
# - Our global network of journal citation can be written as $G=(V,E,w)$
# 
# 
# - Each document have his own network, which can be defined as $G_d$, $E_d$ is then the subset of edges present in document $d$. It uses the same set of nodes $V$ as $G$ for simplicity. $G_d=(V,E_d,w_d)$ In some of cases $G_d$ is an unweighted network and will be written then $G_d=(V,E_d)$ 
# 
# 
# - $w({V_i,V_j})$ is expressed as the sum of all $w({V_i,V_j})=\Sigma_{d=1}^{n}w_d(V_i,V_j)$ where $w_d(V_i,V_j) = 1$ if the graph is unweighted. 
# 
# 
# - Since all indicators works with a focal year, we will define the focal year $y_t$. The first year of the data set is $y_0$ and the last as $y_n$
# 
# 
# - Then each year $y_t$ is represented by a subgraph noted $G_t=(V,E_t,w_t)$
# 
# 
# - In case of novelty a la wang we are dealing with 4 subgraphs of $G$, we need to consider two different past set of documents (noted $P$ and $P'$), and a set of futur document (noted $F$). We will defined this differents subgraphs as follow:
# 
#     - $G_t=(V,E_t,w_t)$ is a subgraph of $G$ from year $y_t$ (documents published year $y_t$)
#     
#     - $G_P=(V,E_P,w_P)$ is a subgraph of $G$ from year $y_0$ to $y_{t-1}$ (documents published before year $y_t$)
#     
#     - $G_{P'}=(V,E_{P'},w_{P'})$ is a subgraph of $G$ from year $y_{t-b-1}$ to $y_{t-1}$ is used to measure the cosine similarity between nodes. this set is a subgraph of $G_P$ (documents are published in a given window before year $y_t$)
#     
#     - $G_F=(V,E_F,w_F)$ is a subgraph of $G$ from year $y_{t+1}$ to $y_{t+f+1}$ (documents published in a given window after year $y_t$)
#     
# 

# Let's first load package and mongo configuration

# In[1]:


import time
import os 

import tqdm
import yaml 
from package.indicators.utils import * 
from package import Dataset

with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']


# #### -------
# # Atypicality
# 
# ## Concept
# 
# - The goal of the measure proposed by Uzzi et al. (2013) is to compare an observed network with a random network where edges a rearrange randomly at a year level.
# 
# 
# - Basically the idea is to compute the frequency z-score for each journals combinaison. The Z-score is defined as $z=(obs-exp)/\sigma$.
# 
# 
# - Uzzi et al but emphasis on the way we can shuffle the network and chosed to preserve the temporal distribution of references at paper level. Meaning that an document citing 2 article from 1985 and one from 1987 will still cite article published in the same year but the journal can change.
# 
# 
# - Defining the frequency of the combinaison $(V_i,V_j)$ during $y_t$ as  $F_{ijt}=w_t(V_i,V_j)$, we can extract a adjacency matrix of observed frequencies.
# 
# 
# - We now want to compare this observed frequency with a theoretical one in order to compute the z-score. The theoretical frequency is generate throught markov chain monte carlo simulation to preserving the dynamical structure of citations. 
# 
# 
# - In case of Atypicality we are dealing with to different network for year $y_t$. The first is $G_t$ as defined before. The second comes from the fact that we need to preserve the temporal distribution of references present in an article. In this case the set of node $V_y$ take into account the publishing year of the reference, we will note this particular graph $G_{y,t}=(V_y,E_{y,t},w_{y,t})$ where $w_{y,t}(V_{y,i},V_{y,j})$ represent the n umber of combinaison of journal $V_i$ and $V_j$ published year $y$.
# 
# 
# - We generate $s$ random network $G_{y,t}$. for example in $G_{y,t}$ an edge can link $(V_{y,i},V_{y,j})$ so for each sample we need aggregate the results to fit with $G_t$ edge structure $E_t$. We simply  sum over all combinaison after resampling without taking into account the year of publishing. For each sample we compute the observed frequency or each edge $(V_i,V_j)$ that we writte $F^s_{ijt}$.
# 
# 
# - We then compute the mean and standard deviation for each edges frequency and compute a z-score. $z-score_{ijt}=\frac{F_{ijt}-mean(F^s_{ijt})}{std(F^s_{ijt})}$
# 
# 
# - For each paper, taking all combinaison made ($E_d$), we then compute a distribution of z-score written $Z_d$, the 10th percentil ($P_{10}$) of this distribution (the novelty) and the median ($P_{50}$) (the conventionality).
# 
# - The novelty and conventionality for document $d$ is then written:
# 
# $$Novelty_d = P_{10}(Z_d)$$
# $$Conventionality_d = P_{50}(Z_d)$$

# ## Implementation 
# - We first need to load the data for a given year 

# In[1]:


from package import Atypicality

focal_year = 2000
db  = 'pkg'

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


# - We need to specify to get_items the type of indicator we are working with, it will structure the dict in a different way depending on the indicators.
# 
# - for Atypicality it will return:
#     - set of unique items
#     - dict of list of dict, first keys are paper id, then each element of the list is a dict with the journal name and the year of publishing of the reference

# In[ ]:


indicator = 'atypicality'

items = data.get_items(docs,
                       focal_year,
                       indicator, 
                       restrict_wos_journal = False)


# In[ ]:


items.keys()


# - Now that we have all relevant items for $y_t$ we can compute the current adjacency matrix, in graph.indicators.utils we have a function that create an adjacency matrix using:
#     - a list of unique items present in data
#     - a list of all list of journal by paper
#     - if you want to consider a unweighted network (unique_pairwise)
#     - if you want to keep the diagonal
#     
# - Since here we have a dict with journal name and year for each references, we just need to get a list of journal name to construct the adjacency matrix

# In[ ]:


true_current_items = {
    pmid:[items['current_items'][pmid][i]['journal']
     for i in range(len(items['current_items'][pmid]))] 
    for pmid in tqdm.tqdm(items['current_items'])
}


# - We can now compute the adjacency matrix

# In[ ]:


true_current_adj = get_adjacency_matrix(items['unique_items'],
                                        true_current_items.values(),
                                        unique_pairwise = False,
                                        keep_diag =True)


# - Finaly we can compute the difficulty for each combinaison and store it in an adjacency matrix. This matrix represent in the case of atypicality all possible Z-Scores
# 
# - Since Uzzi et al. 2013 shuffle the network to preserve the dynamic of citation (that's why we need the year of publishing for each reference) we need to specify how many time we want to shuffle the network (here it's 50)
# 

# In[ ]:


t = time.time()
scores_adj = Atypicality(true_current_adj,
                         items['current_items'],
                         items['unique_items'],
                         nb_sample = 10)
print(time.time()-t)


# - We now have to produce an adjacency matrix for each article
# - We then multiply this matrix by the score matrix from the indicator through ```get_paper_score```. Each combinaison is then store in a dict with the difficulty and update in mongo 

# In[ ]:


for idx in tqdm.tqdm(items['current_items']):
    if len(items['current_items'][idx])>2:
        current_adj = get_adjacency_matrix(items['unique_items'],
                                           [true_current_items[idx]],
                                           unique_pairwise = False,
                                           keep_diag=True)
        
        infos = get_paper_score(current_adj,
                                scores_adj,
                                items['unique_items'],
                                indicator)
        data.update_mongo(idx,infos)


# ###  Full code

# In[ ]:


from package import Atypicality

for y in range(2000,2021):
    t = time.time()
    focal_year = y
    db  = 'pkg'

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

    indicator = 'atypicality'

    items = data.get_items(docs,
                           focal_year,
                           indicator, 
                           restrict_wos_journal = False)

    true_current_items = {
        pmid:[items['current_items'][pmid][i]['journal']
         for i in range(len(items['current_items'][pmid]))] 
        for pmid in tqdm.tqdm(items['current_items'])
    }

    true_current_adj = get_adjacency_matrix(items['unique_items'],
                                            true_current_items.values(),
                                            unique_pairwise = False,
                                            keep_diag =True)


    scores_adj = Atypicality(true_current_adj,
                             items['current_items'],
                             items['unique_items'],
                             nb_sample = 10)
    print(time.time()-t)

    for idx in tqdm.tqdm(items['current_items']):
        if len(items['current_items'][idx])>2:
            try:
                current_adj = get_adjacency_matrix(items['unique_items'],
                                                   [true_current_items[idx]],
                                                   unique_pairwise = False,
                                                   keep_diag=True)

                infos = get_paper_score(current_adj,
                                        scores_adj,
                                        items['unique_items'],
                                        indicator)
                data.update_mongo(idx,infos)
            except:
                pass


# -----
# # Commonness
# 
# ## Concept
# 
# 
# - The goal of the measure proposed by Lee et al. (2013) is to compare the weight of an observed network with a theoretical network (Observed vs Expected frequency of edges) at a year level.
# 
# 
# - The obserbed frequency of combinaison $(V_i,V_j)$ during $y_t$ is the number of edges written $w_t(V_i,V_j)$, theoretical frequency are then $\frac{k_i*k_j}{N_t}$. The number of links for i and j multply together and divided by the total number of combinaison made in $y_t$.
# 
# $$ Commonness_{ijt} = \frac{w_t(V_i,V_j)*N_t}{k_i*k_j} $$
# 
# - For each paper, taking all combinaison made ($E_d$), we then compute a distribution of commonness-score written $C_d$, the 10th percentil ($P_{10}$) of this distribution.
# 
# 
# - The commonness for document $d$ is then written:
# 
# $$Commonness_d = -log(P_{10}(C_d))$$
# 
# ## Implementation 
# 
# 
# - We first need to load the data for a given year 

# In[2]:


from package import Commonness


# In[3]:


focal_year = 2000
db  = 'pkg'

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


# - We need to specify to get_items the type of indicator we are working with, it will structure the dict in a different way depending on the indicators.
#  
# - for Commonness it will return:
#     - set of unique items
#     - dict of list, first keys are paper id, then each element of the list is a journal name 

# In[4]:


indicator = 'commonness'

items = data.get_items(docs,
                       focal_year,
                       indicator, 
                       restrict_wos_journal = False)


# In[5]:


items


# - Now that we have all relevant items for $y_t$ we can compute the current adjacency matrix, in graph.indicators.utils we have a function that create an adjacency matrix using:
#     - a list of unique items present in data
#     - a list of all list of journal by paper
#     - if you want to consider a unweighted network (unique_pairwise)
#     - if you want to keep the diagonal

# - We can now compute the adjacency matrix

# In[6]:


current_adj = get_adjacency_matrix(items['unique_items'],
                                   items['current_items'].values(),
                                   unique_pairwise = False,
                                   keep_diag=True)


# - Finaly we can compute the difficulty for each combinaison and store it in an adjacency matrix. This matrix represent in the case of Commonness all possible Z-Scores

# In[7]:


t = time.time()
scores_adj = Commonness(current_adj)
time.time() - t 


# - We now have to produce an adjacency matrix for each article
# - We then multiply this matrix by the score matrix from the indicator through ```get_paper_score```. Each combinaison is then store in a dict with the difficulty and update in mongo 

# In[2]:


for idx in tqdm.tqdm(items['current_items']):
    if len(items['current_items'][idx])>2:
        current_adj = get_adjacency_matrix(items['unique_items'],
                                           [items['current_items'][idx]],
                                           unique_pairwise = False,
                                           keep_diag=True)
        
        infos = get_paper_score(current_adj,
                                scores_adj,
                                items['unique_items'],
                                indicator)
        data.update_mongo(idx,infos)


# In[9]:


infos


# ### Full code

# In[ ]:


from package import Commonness
db  = 'pkg'
indicator = 'commonness'

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

    current_adj = get_adjacency_matrix(items['unique_items'],
                                       items['current_items'].values(),
                                       unique_pairwise = False,
                                       keep_diag=True)

    t = time.time()
    scores_adj = Commonness(current_adj)
    time.time() - t 

    for idx in tqdm.tqdm(items['current_items']):
        if len(items['current_items'][idx])>2:
            try:
                current_adj = get_adjacency_matrix(items['unique_items'],
                                                   [items['current_items'][idx]],
                                                   unique_pairwise = False,
                                                   keep_diag=True)

                infos = get_paper_score(current_adj,
                                        scores_adj,
                                        items['unique_items'],
                                        indicator)
                data.update_mongo(idx,infos)
            except:
                pass


# ----
# # Novelty
# 
# ## Concept
# 
# 
# 
# - The goal of the measure proposed by Wang et al. (2017) is to propose an measur of difficulty on pair of references that were never made before, and that are reused after this publication's year of publishing (reusers do not have to cite directly the paper that create the combinaison).
# 
# 
# - Basically the idea is to compute the cosine similarity for each journals combinaison in order to take into account their common friend few years before. the cosine similarity between $V_i$ and $V_j$ is defined : 
# 
# $$COS(V_i,V_j) = \frac{V_i.V_j}{\|V_i\| \|V_j\|}$$
# 
# 
# - As said in the introduction we are dealing with 4 subgraphs of $G$, two different past set of documents and a set of futur document: 
#     - $G_t=(V,E_t,w_t)$ is a subgraph of $G$ from year $y_t$ 
# 
#     - $G_P=(V,E_P,w_P)$ is a subgraph of $G$ from year $y_0$ to $y_{t-1}$ 
#     
#     - $G_{P'}=(V,E_{P'},w_{P'})$ is a subgraph of $G$ from year $y_{t-b-1}$ to $y_{t-1}$ is used to measure the cosine similarity between nodes.($G_{P'} \subset G_P$)
#     
#     - $G_F=(V,E_F,w_F)$ is a subgraph of $G$ from year $y_{t+1}$ to $y_{t+f+1}$ 
# 
# 
# - We are interested in new combinaison that are reused. So we want to keep all element of $E_t \notin E_P$ and $E_t \in E_F$. More precisely we are looking for edges belonging to the following subset (that we call $E_N$): 
# $$E_N = (E_t \cap E_F) \cap \overline{E_P}$$
# 
# - Cosine similarities are calcuted using edges and weigth from $G_{p'}$
# 
# 
# - Then for each document we compute an undirected and unweighted network, the novelty is the sum of all edges from $E_d \in E_N$ 
# 
# $$ Novelty_d = log \left(  \sum\limits_{(V_i,V_j)\in E_N}(1-COS(V_i,V_j) + 1 \right) $$
# 

# ## Implementation 
# 
# - We first need to load the data for a given year 

# In[ ]:


from package import Novelty


# In[ ]:


focal_year = 2016
window = 3
db  = 'pkg'

data = Dataset(client_name = pars['client_name'], 
               db_name =  pars['db_name'],
               collection_name = pars[db]['collection_name'],
               var = pars[db]['ref']['var'],
               sub_var = pars[db]['ref']['sub_var'])

docs = data.collection.find({
    pars[db]['ref']['var']:{'$exists':'true'},
    pars[db]['year_var']:{'$lt':str(focal_year+window)}
    }
    )


# - We need to specify to get_items the type of indicator we are working with, it will structure the dict in a different way depending on the indicators.
# 
# - for Novelty it will return:
#     - set of unique items
#     - dict of list, first keys are paper id, then each element of the list is a journal name 
#     - past items list of list, each list element is a paper composed of a list of journal names 
#     - past items (on b year) list of list, each list element is a paper composed of a list of journal names 
#     - futur items (on f year) list of list, each list element is a paper composed of a list of journal names 

# In[ ]:


indicator = 'novelty'

items = data.get_items(docs,
                       focal_year, 
                       indicator,
                       window, 
                       restrict_wos_journal = False)


# In[ ]:


items.keys()


# - We can now compute all adjacency matrices

# In[ ]:


past_adj = get_adjacency_matrix(items['unique_items'],
                                items['past_items'],
                                unique_pairwise = True,
                                keep_diag=False)

futur_adj = get_adjacency_matrix(items['unique_items'],
                                 items['futur_items'],
                                 unique_pairwise = True,
                                 keep_diag=False)

difficulty_adj = get_adjacency_matrix(items['unique_items'],
                                      items['difficulty_items'],
                                      unique_pairwise = True,
                                      keep_diag=False)


# - Finaly we can compute the difficulty for each combinaison and store it in an adjacency matrix. This matrix represent in the case of Novelty all cosine similarity
# 
# - We need to specify the past adjacency matrix, the past adjacency matrix to compute the difficulty and the futur adjacency matrix to test for reutilisation. Also one nned to specify the threshold for the number of reutilisation necessary to be take into acount.

# In[ ]:


t = time.time()
scores_adj = Novelty(past_adj,
                     futur_adj,
                     difficulty_adj,
                     n_reutilisation = 1)
print(time.time()-t)


# In[ ]:


scores_adj


# - We now have to produce an adjacency matrix for each article
# - We then multiply this matrix by the score matrix from the indicator through ```get_paper_score```. Each combinaison is then store in a dict with the difficulty and update in mongo 

# In[ ]:


for idx in tqdm.tqdm(items['current_items']):
    if len(items['current_items'][idx])>2:
        current_adj = get_adjacency_matrix(items['unique_items'],
                                           [items['current_items'][idx]],
                                           unique_pairwise = True,
                                           keep_diag=False)

        infos = get_paper_score(current_adj,
                                scores_adj,
                                items['unique_items'],
                                indicator,
                                item_name = 'journal',
                                window = str(window),
                                n_reutilisation = str(1))
        
        data.update_mongo(idx,infos)


# ### Full code

# In[ ]:


from package import Novelty

window = 3
db  = 'pkg'
for focal_year in range(2011,2021):
    data = Dataset(client_name = pars['client_name'], 
                   db_name =  pars['db_name'],
                   collection_name = pars[db]['collection_name'],
                   var = pars[db]['j_ref']['var'],
                   sub_var = pars[db]['j_ref']['sub_var'])
    
    docs = data.collection.find({
        pars[db]['j_ref']['var']:{'$exists':'true'},
        pars[db]['year_var']:{'$lt':focal_year+window}
        }
        )
    
    indicator = 'novelty'
    
    items = data.get_items(docs,
                           focal_year, 
                           indicator,
                           window, 
                           restrict_wos_journal = False)
    
    past_adj = get_adjacency_matrix(items['unique_items'],
                                    items['past_items'],
                                    unique_pairwise = True,
                                    keep_diag=False)
    
    futur_adj = get_adjacency_matrix(items['unique_items'],
                                     items['futur_items'],
                                     unique_pairwise = True,
                                     keep_diag=False)
    
    difficulty_adj = get_adjacency_matrix(items['unique_items'],
                                          items['difficulty_items'],
                                          unique_pairwise = True,
                                          keep_diag=False)
    t = time.time()
    scores_adj = Novelty(past_adj,
                         futur_adj,
                         difficulty_adj,
                         n_reutilisation = 1)
    print(time.time()-t)
    
    for idx in tqdm.tqdm(items['current_items']):
        if len(items['current_items'][idx])>2:
            try:
                current_adj = get_adjacency_matrix(items['unique_items'],
                                                   [items['current_items'][idx]],
                                                   unique_pairwise = True,
                                                   keep_diag=False)
    
                infos = get_paper_score(current_adj,
                                        scores_adj,
                                        items['unique_items'],
                                        indicator,
                                        item_name = 'journal',
                                        window = window,
                                        n_reutilisation = str(1))
    
                data.update_mongo(idx,infos)
            except:
                pass


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

import tqdm
import yaml 
from package.graphs.indicators.utils import * 
from package import Dataset

with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']


from package import Disruptiveness


# In[3]:


db  = 'pkg'

key_cite_value = list()

for focal_year in range(1975,2021):
    
    data = Dataset(client_name = pars['client_name'], 
                   db_name =  pars['db_name'],
                   collection_name = pars[db]['collection_name'])
    
    docs = data.collection.find({pars[db]['year_var']:focal_year})
    
    
    # In[ ]:
    
    key_cite_value.extend([
        {
            'pmid':doc['PMID'],
            'refs_pmids':doc['refs_pmids'],
            'year':doc['Journal_JournalIssue_PubDate_Year']
            }
        for doc in tqdm.tqdm(docs) if 'refs_pmids' in doc.keys()]
        )

id = doc['PMID']
    
infos = Disruptiveness(id,
                       doc[pars[db]['year_var']],
                       doc['refs_pmids'],
                       data.collection)


# In[ ]:


for doc in tqdm.tqdm(docs):
    id = doc['PMID']
    
    infos = Disruptiveness(id,
                           doc[pars[db]['year_var']],
                           doc['refs_pmids'],
                           data.collection)
    
    data.update_mongo(id,infos)


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


indicator = 'kw_centrality'

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
