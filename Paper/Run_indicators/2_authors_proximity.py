import novelpy


for focal_year in range(2000,2010):

	author_proximity = novelpy.indicators.Author_proximity(
	                 client_name = 'mongodb://localhost:27017',
	                 db_name =  'novelpy',
	                 collection_name = 'articles_authors_profiles',
	                 id_variable = 'PMID',
	                 year_variable = 'year',
	                 aut_profile_variable = 'authors_profiles',
	                 entity = ['title_profile','abs_profile'],
	                 focal_year = focal_year,
	                 windows_size = 5)

	author_proximity.get_indicator()