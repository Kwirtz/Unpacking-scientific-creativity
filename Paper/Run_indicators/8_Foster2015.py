#https://mapequation.github.io/infomap/python/infomap.html

import novelpy
import tqdm
import pickle
import networkx as nx

for focal_year in tqdm.tqdm(range(2000,2016)):
    data = novelpy.indicators.utils.create_output(client_name = 'mongodb://localhost:27017', 
                   db_name =  'PKG',
                   collection_name = 'articles',
                   var_id = 'PMID',
                   var_year = 'Journal_JournalIssue_PubDate_Year',
                   var = 'c04_referencelist',
                   sub_var = 'item',
                   focal_year = focal_year)
    
    g = nx.from_scipy_sparse_matrix(cooc_mat, edge_attribute='weight')
    Foster = novelpy.indicators.Foster2015(g=g, year = focal_year, variable = "c04_referencelist", community_algorithm = "Louvain")
    Foster.get_indicator()
    path = "Data/c04_referencelist/weighted_network_self_loop/{}.p".format(focal_year)    
    cooc_mat += pickle.load(open(path, "rb"))



# testing stuff

focal_year = 2000

data = novelpy.indicators.utils.create_output(client_name = 'mongodb://localhost:27017', 
               db_name =  'pkg',
               collection_name = 'articles',
               var = 'c04_referencelist',
               var_id = 'PMID',
               var_year = 'year',
               indicator = "commonness",
               focal_year = focal_year)

data.get_data()
data.update_paper_values()


