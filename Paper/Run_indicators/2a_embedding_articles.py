from novelpy.utils.embedding import Embedding
import yaml
import argparse
parser = argparse.ArgumentParser(
    description='')

parser.add_argument('-year_start -year_end')
args = parser.parse_args()
year_start = int(args.year_start)
year_end = int(args.year_end)

embedding = Embedding(year_variable = 'year',
                time_range = range(year_start,year_end),
                id_variable = 'PMID',
                references_variable = 'refs_pmid_wos',
                pretrain_path = '/home/peltouz/Downloads/en_core_sci_lg-0.4.0/en_core_sci_lg/en_core_sci_lg-0.4.0',
                title_variable = 'ArticleTitle',
                abstract_variable = 'a04_abstract',
                auth_pubs_variable = 'pmid_list',
                id_auth_variable = 'AND_ID',
                keywords_variable = 'Mesh_year_category',
                keywords_subvariable = 'DescUI',
                abstract_subvariable = 'AbstractText',
                client_name = 'mongodb://Pierre:ilovebeta67@localhost:27017',
                db_name = 'novelty_final')


embedding.get_articles_centroid(
      collection_articles = 'articles',
      collection_embedding = 'articles_embedding'
      )