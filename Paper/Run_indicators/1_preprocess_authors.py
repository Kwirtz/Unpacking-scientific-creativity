from novelpy.utils import Embedding
from novelpy.utils import create_authors_past
import novelpy


"""
clean = create_authors_past(client_name = 'mongodb://localhost:27017',
                            db_name = 'novelty_sample',
                            collection_name = "authors_sample",
                            id_variable = "PMID",
                            variable = "a02_authorlist",
                            sub_variable = "AID")

clean.author2paper()
clean.update_db()
"""

embedding = Embedding(
      client_name="mongodb://Pierre:ilovebeta67@localhost:27017",
      db_name = "novelty_final",
      year_variable = 'year',
      id_variable = 'PMID',
      pretrain_path = r'en_core_sci_lg-0.4.0\en_core_sci_lg\en_core_sci_lg-0.4.0',
      title_variable = 'ArticleTitle',
      abstract_variable = 'a04_abstract',
      abstract_subvariable = 'AbstractText',
      aut_id_variable = 'AID',
      aut_pubs_variable = 'PMID_list')


"""
embedding.get_articles_centroid(
      collection_articles = 'Title_abs_sample',
      collection_embedding = 'embedding')
"""



embedding.feed_author_profile(
    aut_id_variable = 'AID',
    aut_pubs_variable = 'PMID_list',
    collection_authors = 'a02_authorlist_AID',
    collection_embedding = 'embedding')

