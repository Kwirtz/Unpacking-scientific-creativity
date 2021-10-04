import novelpy
from joblib import Parallel, delayed
import tqdm
import yaml
import argparse

parser = argparse.ArgumentParser(description='compute abstract and title centroid, var = pmid and chunksize')

parser.add_argument('-year')
args = parser.parse_args()

with open(r"C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
        
for year in range(2012,2016):
    companion = novelpy.utils.run_indicator_tools.create_output(
      client_name = 'mongodb://localhost:27017', 
      db_name =  'pkg',
      collection_name = 'articles')

    embedding = novelpy.Novelty_embedding(
      var_id = 'PMID',
      var_ref = 'refs_embedding',
      var_aut_profile = 'authors_profiles')

    docs = companion.collection.find()
    for doc in tqdm.tqdm(docs):
        embedding.Shibayama2021(
          doc = doc,
          entity = 'title_embedding')
        embedding.Shibayama2021(
          doc = doc,
          entity = 'abstract_embedding')


        embedding.Author_proximity(
          doc = doc,
          entity = 'title_embedding',
          window_size = 10)
        embedding.Author_proximity(
          doc = doc,
          entity = 'abstract_embedding',
          window_size = 10)

        embedding.update_paper_values()