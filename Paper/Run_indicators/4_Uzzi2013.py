import novelpy
import tqdm

for focal_year in tqdm.tqdm(range(2000,2016), desc = "Computing indicator for window of time"):
    Uzzi = novelpy.indicators.Uzzi2013(collection_name = "Ref_Journals_sample",
                                           id_variable = 'PMID',
                                           year_variable = 'year',
                                           variable = "c04_referencelist",
                                           sub_variable = "item",
                                           focal_year = focal_year)
    Uzzi.get_indicator()
    
    