import sys
sys.path.append('D:\Github\Taxonomy-of-novelty')
#sys.path.append('$HOME\Taxonomy-of-novelty')
import networkx as nx
import pickle
from package.graphs.community.Louvain import * 
from package.graphs.community.OSLOM import * 
from joblib import Parallel, delayed
import argparse
import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('-y','--year', help='year or month of choice',required=True)
parser.add_argument('-bs','--start',help='Range start of bootstrap', required=True)
parser.add_argument('-be','--end',help='Range end of bootstrap', required=True)
parser.add_argument('-d','--date', help='year or month of choice',required=True)
parser.add_argument('-v','--variable', help='variable to create indicator',required=True)
args = parser.parse_args()

time_window_pre = 0
time_window_post = 0

def compute_novelty(date, year, variable,B):
    name2index = pickle.load(open("Paper/Data/{}/{}/weighted_network_self_loop/name2index.p".format(date,variable),"rb") )
    n = len(name2index)
    focal = pickle.load(open("Paper/Data/{}/{}/weighted_network_self_loop/{}.p".format(date,variable,year),"rb" ))
    if time_window_pre != 0:
        for past in range(year-time_window_pre,year,1):
            focal +=  pickle.load(open("Paper/Data/{}/{}/weighted_network_self_loop/{}.p".format(date,variable,past),"rb" ))
    if time_window_post != 0:
        for future in range(year+1, year+time_window_post+1, 1):
            focal += pickle.load(open("Paper/Data/{}/{}/weighted_network_self_loop/{}.p".format(date,variable,future),"rb" ))
    focal = focal.tocoo()
    edge_list = [(i,j,{"weight":v}) for i,j,v in zip(focal.row, focal.col, focal.data)]
    g = nx.Graph(edge_list)

    Louvain = Louvain_based_indicator(g, n = n, year = year, variable = variable, B = B)
    results = Louvain.get_indicator()

for i in tqdm.tqdm(range(int(args.start),int(args.end),1)):
    compute_novelty(date = args.date, year = int(args.year), variable = args.variable,B = i)
