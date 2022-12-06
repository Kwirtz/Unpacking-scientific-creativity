import novelpy
import tqdm

for year in tqdm.tqdm(range(2000,2016)):
    Uzzi = novelpy.indicators.Uzzi2013(collection_name = "Meshterms",
                                       id_variable = 'PMID',
                                       year_variable = 'year',
                                       variable = "Mesh_year_category",
                                       sub_variable = "descUI",
                                       focal_year = year)
    Uzzi.get_indicator()
