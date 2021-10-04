from novelpy import Dataset, Novelty
import tqdm
import  yaml
with open(r"C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']

for focal_year in tqdm.tqdm(range(2007,2016)):
    
    companion = novelpy.utils.run_indicator_tools.create_output(client_name = pars['client_name'], 
                   db_name =  'PKG',
                   collection_name = 'articles',
                   var = 'a06_meshheadinglist',
                   sub_var = "DescriptorName_UI",
                   var_id = 'PMID',
                   var_year = 'year',
                   indicator = "novelty",
                   focal_year = focal_year)
    
    companion.get_data()
    
    novelty = Novelty(var = data.VAR,
                            var_year = 'Journal_JournalIssue_PubDate_Year',
                            focal_year = focal_year,
                            time_window = 3,
                            n_reutilisation = 1)
    
    novelty.get_matrices_sums()
    novelty.compute_comb_score()

    companion.update_paper_values()