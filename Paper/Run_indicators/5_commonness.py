from novelpy import Dataset, Commonness
import tqdm
import  yaml
with open(r"C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']

for focal_year in tqdm.tqdm(range(2000,2016)):
        
    data = Dataset(client_name = pars['client_name'], 
                   db_name =  'PKG',
                   collection_name = 'articles_test',
                   var_id = 'PMID',
                   var_year = 'Journal_JournalIssue_PubDate_Year',
                   var = 'c04_referencelist',
                   sub_var = 'item',
                   focal_year = focal_year)
    
    data.get_items(indicator = 'commonness')
    
    commonness = Commonness(var = data.VAR,
                            var_year = 'Journal_JournalIssue_PubDate_Year',
                            focal_year = focal_year,
                            current_adj = data.current_adj)
    
    commonness.compute_comb_score()
    #data.update_paper_values(indicator = 'commonness')