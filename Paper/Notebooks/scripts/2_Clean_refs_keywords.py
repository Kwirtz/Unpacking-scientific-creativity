#!/usr/bin/env python
# coding: utf-8

# # Clean references
# 
# - For each document we want to extract the journal used in each references with the publishing year of the cited article. If we are dealing with Web of Science data we match the journal name with the WOS master journal list present in the folder 'Parper/Data'. This allows us to add the subject category of the journal. 

# - import first modules and mongodb configuration

# In[1]:


import os 
os.chdir('../../')

import yaml
import numpy as np
from joblib import Parallel, delayed
import multiprocessing
num_cores = multiprocessing.cpu_count() - 1


# In[2]:


from package import Reference_cleaner
import tqdm


# - Create a function to update mongodb yearly. This function extract journals and year of publication for each reference in a document.
# 
# - ```IS_WOS``` allows to deal with Web of Science and Pubmed Knowledge Graph documents.

# In[3]:


def clean_ref_update_mongo(IS_WOS,year):

    with open("mongo_config.yaml", "r") as infile:
        pars = yaml.safe_load(infile)['PC_PP']

    if IS_WOS:
        data = Reference_cleaner(pars['client_name'],
                                 pars['db_name'],
                                 pars['wos']['collection_name'],
                                 IS_WOS)
        
        PATH = '/home/peltouz/Documents/GitHub/New-novelty-indicator-using-graph-theory-framework/Data sample/raxdata/'
        data.wos_cr2mongo(PATH)
        
        PATH = '/home/peltouz/Documents/GitHub/New-novelty-indicator-using-graph-theory-framework/Data/Wos_j_list/'
        data.get_wos_J_list(PATH)
        
        cr_var = 'CR'
        pmid_var = pars['wos']['pmid']
        
    else:
        data = Reference_cleaner(pars['client_name'],
                                 pars['db_name'],
                                 pars['pkg']['collection_name'],
                                 IS_WOS)
        
        cr_var = 'a14_referencelist'
        pmid_var = pars['pkg']['pmid']
        
    year_var = pars['pkg']['year_var'] if IS_WOS else pars['pkg']['year_var']
    docs = data.collection.find({'$and':[{cr_var:{'$exists':'true'}},
                                          {year_var:str(year)}]})
    
    for doc in docs:
        j_dict = data.get_item_year_cat(doc[cr_var],'reference')
        query = { pmid_var: doc[pmid_var] }
        newvalues = { "$set": j_dict }
        data.collection.update_one(query, newvalues)
    
clean_ref_update_mongo(False,2016)

# - For all year in the data set clean up ref in parallel

# In[ ]:


years = range(1975,2021)
IS_WOS = np.repeat(False,len(years))

Parallel(n_jobs=6)(
    delayed(clean_ref_update_mongo)(
        is_wos, year
    ) for is_wos, year in zip(IS_WOS,years)
)


# - Plot the distribution of the share of references captured in a document (Only relevant for WoS)

# In[ ]:


share_ref = [i['share_ref_captured'] for i in tqdm.tqdm(data.collection.find({"share_ref_captured":{"$exists":True}}))]
plt.figure()
fig = sns.displot(share_ref, kde=True).set(title='Share of References in WOS Journal Citation Reports').fig
fig.savefig('/home/peltouz/Documents/GitHub/New-novelty-indicator-using-graph-theory-framework/Figures/'+'wos_share_ref_captured.png')


# # Clean Keywords
# 
# - Mesh terms are already cleaned, we just need restructure the variable in order to fit with the structur used in the section above. Here we will integrate the first year of appearence of the meshterm and the two frist element of the TreeNumber (the top two levels of meshterms classification hierarchy following Uddin and Khan, 2016)

# In[3]:


def update_keyword_mongo(year):
    try:
        with open("mongo_config.yaml", "r") as infile:
            pars = yaml.safe_load(infile)['PC_PP']
    
        data = Reference_cleaner(pars['client_name'],
                                 pars['db_name'],
                                 pars['pkg']['collection_name'],
                                 False)
        
        k_var = 'a06_meshheadinglist'
        pmid_var = pars['pkg']['pmid']
        year_var = pars['pkg']['year_var']
        docs = data.collection.find({'$and':[{k_var:{'$exists':'true'}},
                                              {year_var:str(year)}]})
        
        for doc in docs:
            j_dict = data.get_item_year_cat(doc[k_var],'keyword')
            query = { pmid_var: doc[pmid_var] }
            newvalues = { "$set": j_dict }
            data.collection.update_one(query, newvalues)
    except:
        pass

# In[ ]:


years = range(1975,2021)

Parallel(n_jobs=6)(
    delayed(update_keyword_mongo)(
        year
    ) for year in years
)

