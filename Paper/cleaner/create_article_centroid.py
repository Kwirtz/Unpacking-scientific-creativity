import pymongo
import yaml
import spacy
import scispacy
import tqdm
import numpy as np
import ast
from joblib import Parallel, delayed
import argparse

parser = argparse.ArgumentParser(description='compute abstract and title centroid, var = pmid and chunksize')

parser.add_argument('-pmid')
args = parser.parse_args()
pmid_start = int(args.pmid)

with open(r"C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
db= 'pkg'


nlp = spacy.load("C:/Users/Beta/Documents/GitHub/Taxonomy-of-novelty/en_core_sci_lg-0.4.0/en_core_sci_lg/en_core_sci_lg-0.4.0")

def get_articles_centroid(pmid_start,chunk_size):
    client = pymongo.MongoClient(pars['client_name'])
    db = client['PKG']
    collection = db['articles']
    pmids = np.arange(pmid_start,(pmid_start+chunk_size)).tolist()
    docs = collection.find({'PMID':{'$in':pmids}})
    for doc in docs:
        # try:
        try:
            tokens = nlp(doc['ArticleTitle'])
            article_title_centroid = np.sum([t.vector for t in tokens], axis=0) / len(tokens)
            article_title_centroid = article_title_centroid.tolist()
        except:
            pass
        if 'a04_abstract' in doc.keys() and doc['a04_abstract'] != "" :
            # abstract = ast.literal_eval(doc['a04_abstract'])[0]['AbstractText']
            abstract = doc['a04_abstract'][0]['AbstractText']
            tokens = nlp(abstract)
            article_abs_centroid = np.sum([t.vector for t in tokens], axis=0) / len(tokens)
            article_abs_centroid = article_abs_centroid.tolist()
        else:
            article_abs_centroid = None
        collection.update_one({'PMID':doc['PMID']},
                              {'$set':{'title_embedding':article_title_centroid,
                                       'abstract_embedding':article_abs_centroid}})
        # except:
        #     pass
        
end = pmid_start+1000*4000
for pmid in tqdm.tqdm(range(pmid_start,end,1000)):
    get_articles_centroid(pmid,1000)

