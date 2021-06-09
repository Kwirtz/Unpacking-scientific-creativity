import networkx as nx
import pickle
from package.graphs.community.Louvain import * 
from package.graphs.community.Infomap import * 
from package.graphs.community.OSLOM import * 
#%% Authors
time_window_pre = 0
time_window_post = 0


name2index = pickle.load(open("Data/Authors/name2index.p","rb") )
index2name = pickle.load(open("Data/Authors/index2name.p","rb") )
n = len(name2index)


year = 2000
for year in range(1980,2021,1):
    focal = pickle.load(open("Data/Authors/{}.p".format(year),"rb") )
    if time_window_pre != 0:
        for past in range(year-time_window_pre,year,1):
            focal += pickle.load(open("Data/Authors/{}.p".format(past),"rb") )
    if time_window_post != 0:
        for past in range(year+1, year+time_window_post+1, 1):
            focal += pickle.load(open("Data/Authors/{}.p".format(past),"rb") )
    focal = focal.tocoo()
    edge_list = [(i,j,{"weight":v}) for i,j,v in zip(focal.row, focal.col, focal.data)]
    g = nx.Graph(edge_list)

Louvain = Louvain_based_indicator(g, B = 50)
results = Louvain.get_indicator()

