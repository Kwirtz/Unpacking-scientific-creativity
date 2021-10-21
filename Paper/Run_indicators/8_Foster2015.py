#https://mapequation.github.io/infomap/python/infomap.html

import novelpy
import tqdm

for focal_year in tqdm.tqdm(range(2000,2016), desc = "Computing indicator for window of time"):
    Foster = novelpy.indicators.Foster2015(collection_name = 'meshterms_sample',
                                           id_variable = 'PMID',
                                           year_variable = 'year',
                                           variable = 'a06_meshheadinglist',
                                           sub_variable = "descUI",
                                           focal_year = focal_year,
                                           community_algorithm = "Louvain")
    Foster.get_indicator()
    
