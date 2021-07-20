# From https://github.com/DeyunYinWIPO/Novelty/blob/main/novelty_sci.py

import spacy
import scispacy
import numpy as np
import csv
from sklearn.metrics.pairwise import cosine_similarity

# python3 -m pip install -U scispacy
# python3 -m pip install -U https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.3.0/en_core_sci_lg-0.3.0.tar.gz


def novel(mytxt):
    txt = list(mytxt.values())
    n = len(txt)
    w = np.zeros((n, d))

    # Assign word embedding
    for i in range(n):
        tokens = nlp(txt[i])
        w[i, :] = np.sum([t.vector for t in tokens], axis=0) / len(tokens)
 
    # Compute similarity
    cos_sim = cosine_similarity(w)
    dist_list = []
    for i in range(n):
        for j in range(i+1,n):
            dist_list.append(1 - cos_sim[i][j])

    # Take p-percentile value to compute novelty
    nov_list = []
    for q in q_list:
        nov_list.append([q, np.percentile(dist_list, q)])

    return nov_list
    

def main():  
    # Read input file
    with open(in_file) as f:
        reader = csv.reader(f)
        txt_data = list(reader)
    txt_data.sort(key = lambda x: x[0])
    m = len(txt_data)
    
    # Compute novelty for each doc
    result = []
    mytxt = {}
    for i in range(m):
        dc, rf, txt = txt_data[i]
        mytxt[rf] = txt
        if i < m - 1:
            if txt_data[i+1][0] == dc:
                continue
        nov_list = novel(mytxt)
        result += [[dc, j, k] for (j, k) in nov_list]
        mytxt = {}
    
    return result
    # # Output novelty scores    
    # with open(out_file, "w", newline="") as f:
    #     writer = csv.writer(f)
    #     writer.writerows(result)

# Set word embedding
nlp= spacy.load("en_core_sci_lg")
# Number of dimensions
d = 200

# Set q for novel_q percentile ranks
q_list = [100, 99, 95, 90, 80, 50]

import yaml
from package.indicators.utils import Dataset
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
db = 'pkg'    
focal_year = 2010
data = Dataset(client_name = pars['client_name'], 
               db_name =  pars['db_name'],
               collection_name = pars[db]['collection_name'],
               var = pars[db]['j_ref']['var'],
               sub_var = pars[db]['j_ref']['sub_var'])

docs = data.collection.find({
    pars[db]['j_ref']['var']:{'$exists':'true'},
    pars[db]['year_var']:{'$eq':focal_year}
    }
    )

doc = [docs[0]]a14_referencelist