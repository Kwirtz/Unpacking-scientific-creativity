import novelpy
import tqdm

for focal_year in tqdm.tqdm(range(2008,2016), desc = "Computing indicator for window of time"):
    Uzzi = novelpy.indicators.Uzzi2013(client_name = "mongodb://localhost:27017",
                                       db_name =  'novelty',
                                       collection_name = "Meshterms",
                                       id_variable = 'PMID',
                                       year_variable = 'year',
                                       variable = "Mesh_year_category",
                                       sub_variable = "descUI",
                                       focal_year = focal_year)
    Uzzi.get_indicator()
