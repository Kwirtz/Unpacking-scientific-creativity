import novelpy

<<<<<<< Updated upstream

focal_year = 2000

disruptiveness = novelpy.Disruptiveness(
    collection_name = 'Citation_net',
    focal_year = focal_year,
    id_variable = 'PMID',
    refs_list_variable ='refs_pmid_wos',
    year_variable = 'year')

disruptiveness.get_indicators(parallel = False)
=======
#parser = argparse.ArgumentParser(description='compute abstract and title centroid, var = pmid and chunksize')

#parser.add_argument('-year')
#args = parser.parse_args()

    
for year in range(2012,2016):
    companion = novelpy.utils.run_indicator_tools.create_output(client_name = 'mongodb://Pierre:ilovebeta67@localhost:27017', 
                   db_name =  'novelty_sample',
                   collection_name = 'Citation_net_sample',
                   var = 'refs_pmid_wos',
                   var_id = 'PMID',
                   var_year = 'year',
                   indicator = "disruptiveness",
                   focal_year = focal_year)
    companion.get_item_paper()
>>>>>>> Stashed changes

