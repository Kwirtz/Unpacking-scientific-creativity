import sys
sys.path.append('D:/Github/Taxonomy-of-novelty')
import networkx as nx
import pickle
from package.graphs.community.Louvain import * 
from package.graphs.community.Infomap import * 
from package.graphs.community.OSLOM import * 
from joblib import Parallel, delayed
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-y','--year', help='year of choice',required=True)
parser.add_argument('-b','--bootstrap',help='iteration of bootstrap', required=True)
args = parser.parse_args()
# appending a path




#%% Authors


time_window_pre = 0
time_window_post = 0



def compute_novelty(year,variable,B):
    name2index = pickle.load(open("Paper/Data/{}/name2index.p".format(variable),"rb") )
    n = len(name2index)
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


compute_novelty(year = args.year, variable = "a02_authorlist", B = args.bootstrap )

#Parallel(n_jobs=3)(delayed(compute_novelty)(year = i, variable = "a02_authorlist", B = 500) for i in range(1980,2020))