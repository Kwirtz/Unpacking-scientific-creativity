import novelpy
import tqdm


for focal_year in tqdm.tqdm(range(2000,2016)):
 
    Wang = novelpy.indicators.Wang2017(collection_name = "Ref_Journals_sample",
                                           id_variable = 'PMID',
                                           year_variable = 'year',
                                           variable = "c04_referencelist",
                                           sub_variable = "item",
                                           focal_year = focal_year,
                                           time_window_cooc = 3,
                                           n_reutilisation = 1)
    Wang.get_indicator()
    

