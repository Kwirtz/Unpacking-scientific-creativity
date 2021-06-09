

import time
import os 
os.chdir('../../')

import tqdm
import yaml 
import numpy as np
import pandas as pd
import pickle
from scipy.sparse import lil_matrix

from package.indicators.utils import * 
from package import Dataset
from package.utils import create_cooc
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_PP']

var_names = ['j_ref','mesh']

db  = 'pkg'
for var in var_names:
    matrix_w_sl_cooc = create_cooc(client_name = pars['client_name'], 
                              db_name =  pars['db_name'],
                              collection_name = pars['pkg']['collection_name'],
                               year_var = pars[db]['year_var'],
                               var = pars[db][var]['var'],
                               sub_var = pars[db][var]['sub_var'],
                               weighted_network = True,
                               self_loop = True)
    matrix_w_sl_cooc.main()
    
    
    
    matrix_uw_nsl_cooc = create_cooc(client_name = pars['client_name'], 
                            db_name =  pars['db_name'],
                            collection_name = pars['pkg']['collection_name'],
                            year_var = pars[db]['year_var'],
                            var = pars[db][var]['var'],
                            sub_var = pars[db][var]['sub_var'],
                            weighted_network = False,
                            self_loop = False)
    matrix_uw_nsl_cooc.main() 
