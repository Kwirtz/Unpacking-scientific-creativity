import networkx as nx
import pickle
from package.graphs.community.Louvain import * 
from package.graphs.community.Infomap import * 
from package.graphs.community.OSLOM import * 

#%% Authors
name2index = pickle.load(open("Paper/Data/a02_authorlist/name2index.p", "rb" ) )
n = len(name2index)
time_window_pre = 0
time_window_post = 0



def compute_novelty(year_range,variable,B):
    name2index = pickle.load(open("Paper/Data/{}/name2index.p".format(variable),"rb") )
    n = len(name2index)
    for year in year_range:
        focal = pickle.load(open("Paper/Data/{}/{}.p".format(variable,year),"rb" ))
        if time_window_pre != 0:
            for past in range(year-time_window_pre,year,1):
                focal +=  pickle.load(open("Paper/Data/{}/{}.p".format(past,variable),"rb" ))
        if time_window_post != 0:
            for future in range(year+1, year+time_window_post+1, 1):
                focal += pickle.load(open("Paper/Data/{}/{}.p".format(future,variable),"rb" ))
        focal = focal.tocoo()
        edge_list = [(i,j,{"weight":v}) for i,j,v in zip(focal.row, focal.col, focal.data)]
        g = nx.Graph(edge_list)
    
        Louvain = Louvain_based_indicator(g, n = n, year = year, variable = variable, B = B)
        results = Louvain.get_indicator()

compute_novelty(year_range = range(1980,2020), variable = "a02_authorlist", B = 500)