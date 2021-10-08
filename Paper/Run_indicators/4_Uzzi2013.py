from novelpy import Dataset, Atypicality
import tqdm
import  yaml
with open(r"C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']

for focal_year in tqdm.tqdm(range(2000,2016)):
    
    companion = novelpy.utils.run_indicator_tools.create_output(client_name = pars['client_name'], 
                   db_name =  'PKG',
                   collection_name = 'articles',
                   var = 'a06_meshheadinglist',
                   sub_var = "DescriptorName_UI",
                   var_id = 'PMID',
                   var_year = 'year',
                   indicator = "atypicality",
                   focal_year = focal_year)
    
    companion.get_data()
    atypicality = Atypicality(var = data.VAR,
                              var_year = 'Journal_JournalIssue_PubDate_Year',
                              focal_year = focal_year,
                              current_items = data.current_items,
                              unique_items = data.unique_items,
                              true_current_adj_freq = data.current_adj)
    
    atypicality.sample_network(nb_sample = 20)
    atypicality.compute_comb_score()
    
    companion.update_paper_values()