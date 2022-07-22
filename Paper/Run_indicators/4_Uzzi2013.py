import novelpy
import tqdm


Uzzi = novelpy.indicators.Uzzi2013(collection_name = "references",
                                   id_variable = 'PMID',
                                   year_variable = 'year',
                                   variable = "c04_referencelist",
                                   sub_variable = "item",
                                   focal_year = 2005)
Uzzi.get_indicator()
