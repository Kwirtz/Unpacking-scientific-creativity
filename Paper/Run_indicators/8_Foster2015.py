#https://mapequation.github.io/infomap/python/infomap.html

import novelpy
import tqdm

for focal_year in tqdm.tqdm(range(2000,2016), desc = "Computing indicator for window of time"):
    Foster = novelpy.indicators.Foster2015(collection_name = "Ref_Journals_sample",
                                           id_variable = 'PMID',
                                           year_variable = 'year',
                                           variable = "c04_referencelist",
                                           sub_variable = "item",
                                           focal_year = focal_year,
                                           community_algorithm = "Louvain")
    Foster.get_indicator()
    
