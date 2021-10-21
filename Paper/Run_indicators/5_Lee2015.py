import novelpy
import tqdm

for focal_year in tqdm.tqdm(range(2000,2016), desc = "Computing indicator for window of time"):
    Lee = novelpy.indicators.Lee2015(collection_name = 'meshterms_sample',
                                           id_variable = 'PMID',
                                           year_variable = 'year',
                                           variable = 'a06_meshheadinglist',
                                           sub_variable = "descUI",
                                           focal_year = focal_year)
    Lee.get_indicator()
    