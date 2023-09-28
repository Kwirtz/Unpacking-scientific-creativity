import novelpy
import tqdm

"""
for year in tqdm.tqdm(range(2000,2006)):
    Uzzi = novelpy.indicators.Uzzi2013(collection_name = "Meshterms",
                                       id_variable = 'PMID',
                                       year_variable = 'year',
                                       variable = "Mesh_year_category",
                                       sub_variable = "descUI",
                                       focal_year = year)
    Uzzi.get_indicator()
"""

for year in tqdm.tqdm(range(2005,2006)):
    Uzzi = novelpy.indicators.Uzzi2013(collection_name = "references",
                                       id_variable = 'PMID',
                                       year_variable = 'year',
                                       variable = "c04_referencelist",
                                       sub_variable = "item",
                                       focal_year = year)
    Uzzi.get_indicator()
