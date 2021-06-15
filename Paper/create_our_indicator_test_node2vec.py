#%%% link prediction
#%% test node2vec

import torch_geometric
import torch
import pickle
import networkx as nx

variable = "a02_authorlist"
year = 1980

focal = pickle.load(open("Paper/Data/{}/{}.p".format(variable,year),"rb" ))
focal = focal.tocoo()
focal = [(i,j,{"weight":v}) for i,j,v in zip(focal.row, focal.col, focal.data)]
focal = nx.Graph(focal)
data = torch_geometric.utils.from_networkx(focal)
