#https://mapequation.github.io/infomap/python/infomap.html

import novelpy
import tqdm
import networkx as nx

for focal_year in tqdm.tqdm(range(2000,2016), desc = "Computing indicator for window of time"):
    companion = novelpy.utils.run_indicator_tools.create_output(client_name = 'mongodb://localhost:27017', 
                   db_name =  'pkg',
                   collection_name = 'articles',
                   var = 'a06_meshheadinglist',
                   sub_var = "DescriptorName_UI",
                   var_id = 'PMID',
                   var_year = 'year',
                   indicator = "foster",
                   focal_year = focal_year)
    companion.get_data()
    g = nx.from_scipy_sparse_matrix(companion.current_adj, edge_attribute='weight')
    Foster = novelpy.indicators.Foster2015(g=g, year = focal_year,
                                           variable = "a06_meshheadinglist",
                                           community_algorithm = "Louvain")
    Foster.get_indicator()
    companion.update_paper_values()
    
