import novelpy
    
for year in range(2005,2016):
    companion = novelpy.utils.run_indicator_tools.create_output(client_name = 'mongodb://Pierre:ilovebeta67@localhost:27017', 
                   db_name =  'novelty',
                   collection_name = 'Citation_net',
                   var = 'refs_pmid_wos',
                   var_id = 'PMID',
                   var_year = 'year',
                   indicator = "disruptiveness",
                   focal_year = focal_year)
    companion.get_item_paper()

