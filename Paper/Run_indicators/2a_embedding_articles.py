from novelpy.utils.embedding import Embedding
import yaml
import argparse
parser = argparse.ArgumentParser(
    description='')

parser.add_argument('-year_start -year_end')
args = parser.parse_args()
year_start = int(args.year_start)
year_end = int(args.year_end)

embedding = Embedding(
		client_name = 'mongodb://localhost:27017',
		db_name = 'novelty',
		year_variable = 'year',
		time_range = range(2000,2011),
		id_variable = 'PMID',
		references_variable = 'refs_pmid_wos',
		pretrain_path = 'en_core_sci_lg-0.4.0/en_core_sci_lg/en_core_sci_lg-0.4.0',
		title_variable = 'ArticleTitle',
		abstract_variable = 'a04_abstract',
		abstract_subvariable = 'AbstractText')

# articles

embedding.get_articles_centroid(
      collection_articles = 'Title_abs',
      collection_embedding = 'embedding',
      year_range = range(2013,2021,1))

embedding.get_references_embbeding(
      collection_articles = 'Citation_net',
      collection_embedding = 'embedding',
      collection_ref_embedding = 'references_embedding',
      skip_ = 1,
      limit_ = 0)
