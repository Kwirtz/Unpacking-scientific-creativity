from novelpy.utils.embedding import Embedding

embedding = Embedding(
    client_name="mongodb://localhost:27017",
    db_name = "novelty_sample",
	year_variable = 'year',
	time_range = range(1995,2010),
	id_variable = 'PMID',
	pretrain_path = 'en_core_sci_lg-0.4.0/en_core_sci_lg/en_core_sci_lg-0.4.0',
	title_variable = 'ArticleTitle',
	abstract_variable = 'a04_abstract',
	abstract_subvariable = 'AbstractText')

# articles

embedding.get_articles_centroid(
      collection_articles = 'Title_abs_sample',
      collection_embedding = 'embedding')




    








