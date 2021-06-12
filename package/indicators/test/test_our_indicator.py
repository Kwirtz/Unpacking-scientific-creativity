import networkx as nx
import random
import pickle
import yaml 
from package.graphs.community.Louvain import * 
from package.graphs.community.Infomap import * 
from package.graphs.community.OSLOM import * 

g = nx.watts_strogatz_graph(1000, 10, 0.3, seed=12345)
for (u, v) in g.edges():
    g.edges[u,v]['weight'] = random.randint(0,100)

#%% Community

# Louvain algorithm

Louvain = Louvain_based_indicator(g, n = 1000, year = 2000, B = 50)
results = Louvain.get_indicator()

Louvain_par = Louvain_based_indicator(g, B = 50,n_jobs = 5)
results = Louvain_par.get_indicator()

# Infomap

infomap_indicator = Infomap_based_indicator(g,B=500)
results = infomap_indicator.get_indicator()

infomap_indicator = Infomap_based_indicator(g,B=500,n_jobs = 5)
results = infomap_indicator.get_indicator()

# OSLOM


#%% Test using a sparse matrix pickled

adj_matrix = pickle.load(open("Paper/Data/a02_authorlist/1980.p", "rb" ) )
adj_matrix = adj_matrix.tocoo()
name2index = pickle.load(open("Paper/Data/a02_authorlist/name2index.p", "rb" ) )

edge_list = []
for i,j,v in zip(adj_matrix.row, adj_matrix.col, adj_matrix.data):
    edge_list.append((i,j,{"weight":v}))
   
   
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_Kevin']
URI = pars["neo4j_connection"]["URI"]
name = pars["neo4j_connection"]["auth"]["name"]
password = pars["neo4j_connection"]["auth"]["password"]
db_name = "test"

year = 1980
g = nx.Graph(edge_list)


Louvain = Louvain_based_indicator(g, n = len(name2index), year = 1980, variable = "a02_authorlist", B = 1)
results = Louvain.get_indicator()

#%% link prediction