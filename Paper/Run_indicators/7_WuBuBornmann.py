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
    companion = novelpy.utils.run_indicator_tools.create_output(client_name = 'mongodb://localhost:27017', 
                   db_name =  'pkg',
                   collection_name = 'articles',
                   var = 'refs_pmid_wos',
                   var_id = 'PMID',
                   var_year = 'year',
                   indicator = "disruptiveness",
                   focal_year = focal_year)
    companion.get_item_paper()

    disruptiveness = novelpy.Disruptiveness(focal_year = year,
                                    var_id = 'PMID',
                                    var_refs_list ='refs_pmid_wos',
                                    var_year = 'year')
    
    Parallel(n_jobs=30)(
        delayed(disruptiveness.compute_scores)(
            focal_paper_id = idx,
            focal_paper_refs = data.current_items[idx],
            tomongo = True,
            client_name = pars['client_name'], 
            db_name = pars['db_name'],
            collection_name = 'citation_data',
            collection2update = 'citation_data') 
        for idx in tqdm.tqdm(list(data.current_items)))