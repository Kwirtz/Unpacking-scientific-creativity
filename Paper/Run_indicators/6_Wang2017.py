import novelpy
import tqdm


for focal_year in tqdm.tqdm(range(2000,2016)):
    
    Wang = novelpy.indicators.Wang2017(collection_name = 'meshterms_sample',
                                               id_variable = 'PMID',
                                               year_variable = 'year',
                                               variable = 'a06_meshheadinglist',
                                               sub_variable = "descUI",
                                               focal_year = focal_year,
                                               time_window_cooc = 3,
                                               n_reutilisation = 1)
    Wang.get_indicator()