import novelpy
import tqdm

for focal_year in tqdm.tqdm(range(2000,2011), desc = "Computing indicator for window of time"):
    shibayama = novelpy.indicators.Shibayama2021(
        client_name = 'mongodb://localhost:27017',
		db_name = 'novelty',
        collection_name = 'embedding',
        id_variable = 'PMID',
        year_variable = 'year',
        ref_variable = 'refs_embedding',
        entity = ['title_embedding','abstract_embedding'],
        focal_year = focal_year)
    
    shibayama.get_indicator()