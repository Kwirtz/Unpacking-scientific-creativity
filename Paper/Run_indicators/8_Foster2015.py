#https://mapequation.github.io/infomap/python/infomap.html

import novelpy
import tqdm
import pickle
import networkx as nx

for focal_year in tqdm.tqdm(range(2000,2016)):
    companion = novelpy.utils.run_indicator_tools.create_output(client_name = 'mongodb://localhost:27017', 
                   db_name =  'PKG',
                   collection_name = 'articles',
                   var = 'c04_referencelist',
                   var_id = 'PMID',
                   var_year = 'year',
                   indicator = "foster",
                   focal_year = focal_year)
    companion.get_data()
    g = nx.from_scipy_sparse_matrix(companion.current_adj, edge_attribute='weight')
    Foster = novelpy.indicators.Foster2015(g=g, year = focal_year,
                                           variable = "c04_referencelist",
                                           community_algorithm = "Louvain")
    Foster.get_indicator()
    companion.update_paper_values()
    


# testing stuff

focal_year = 2000

data = novelpy.utils.run_indicator_tools.create_output(client_name = 'mongodb://localhost:27017', 
               db_name =  'pkg',
               collection_name = 'articles',
               var = 'c04_referencelist',
               var_id = 'PMID',
               var_year = 'year',
               indicator = "commonness",
               focal_year = focal_year)

data.get_data()
data.update_paper_values()

