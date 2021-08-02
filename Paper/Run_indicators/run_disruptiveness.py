import novelpy
from joblib import Parallel, delayed
import tqdm
import yaml

with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
    
data = novelpy.Dataset(var = 'refs_pmid_wos',
                       var_id = 'PMID',
                       focal_year = 2001,
                       var_year = 'Journal_JournalIssue_PubDate_Year',
                       client_name = pars['client_name'], 
                       db_name =  pars['db_name'],
                       collection_name = 'citation_data')
data.get_items(indicator = 'distruptiveness')

disruptiveness = novelpy.Disruptiveness(focal_year = 2002,
                                var_id = 'PMID',
                                var_refs_list ='refs_pmid_wos',
                                var_year = 'Journal_JournalIssue_PubDate_Year')

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