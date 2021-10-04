import novelpy
import tqdm
import yaml

with open(r"C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']

for focal_year in tqdm.tqdm(range(2000,2016)):
        
    companion = novelpy.utils.run_indicator_tools.create_output(client_name = 'mongodb://localhost:27017', 
                   db_name =  'pkg',
                   collection_name = 'articles',
                   var = 'a06_meshheadinglist',
                   sub_var = "DescriptorName_UI",
                   var_id = 'PMID',
                   var_year = 'year',
                   indicator = "commonness",
                   focal_year = focal_year)
    
    companion.get_data()
    
    commonness = novelpy.indicators.commonness.Commonness(var = companion.VAR,
                            var_year = 'year',
                            focal_year = focal_year,
                            current_adj = companion.current_adj)
    
    commonness.compute_comb_score()
    companion.update_paper_values()
