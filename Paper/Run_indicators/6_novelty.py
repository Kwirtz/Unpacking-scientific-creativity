from novelpy import Dataset, Novelty
import tqdm
import  yaml
with open(r"C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']

for focal_year in tqdm.tqdm(range(2007,2016)):
        
    data = Dataset(client_name = pars['client_name'], 
                   db_name =  'PKG',
                   collection_name = 'articles_test',
                   var_id = 'PMID',
                   var_year = 'Journal_JournalIssue_PubDate_Year',
                   var = 'c04_referencelist',
                   sub_var = 'item',
                   focal_year = focal_year)
    
    data.get_items(indicator = 'novelty')
    
    novelty = Novelty(var = data.VAR,
                            var_year = 'Journal_JournalIssue_PubDate_Year',
                            focal_year = focal_year,
                            time_window = 3,
                            n_reutilisation = 1)
    
    novelty.get_matrices_sums()
    novelty.compute_comb_score()