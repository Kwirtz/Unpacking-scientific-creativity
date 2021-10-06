import yaml
from novelpy.utils.embedding import Embedding
import pandas as pd
import argparse
parser = argparse.ArgumentParser(
    description='skip and limit mongo args')

parser.add_argument('-skip -limit')
args = parser.parse_args()
skip_ = int(args.skip)
limit_ = int(args.limit)

with open(r"C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
    
client_name = pars['client_name']
db_name = 'novelty'
collection_articles = 'references_embedding'
collection_authors = 'authors_embedding'
collection_keywords = 'meshterms'
collection_embedding = 'articles_embedding'
var_year = 'year'
var_id = 'PMID'
var_id_list = 'pmid_list'
var_pmid_list = 'refs_pmid_wos'
var_auth_id = 'AND_ID'
var_abstract = 'a04_abstract'
var_title = 'ArticleTitle'
var_keyword = 'Mesh_year_category'
subvar_keyword = 'DescUI'
pretrain_path = "C:/Users/Beta/Documents/GitHub/Taxonomy-of-novelty/en_core_sci_lg-0.4.0/en_core_sci_lg/en_core_sci_lg-0.4.0"


embedding = Embedding(
    client_name,
    db_name,
    collection_articles,
    collection_authors,
    collection_keywords,
    collection_embedding,
    var_year,
    var_id,
    var_pmid_list,
    var_id_list,
    var_auth_id,
    pretrain_path,
    var_title,
    var_abstract,
    var_keyword,
    subvar_keyword)

embedding.feed_author_profile(skip_,limit_)
