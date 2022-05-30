import novelpy


focal_year = 2000

disruptiveness = novelpy.Disruptiveness(
    collection_name = 'Citation_net',
    focal_year = focal_year,
    id_variable = 'PMID',
    refs_list_variable ='refs_pmid_wos',
    year_variable = 'year')

disruptiveness.get_indicators(parallel = False)

