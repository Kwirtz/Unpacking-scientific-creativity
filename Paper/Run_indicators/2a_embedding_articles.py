from novelpy.utils.embedding import Embedding
import yaml
import argparse
parser = argparse.ArgumentParser(
    description='')

parser.add_argument('-pmid_start -lipmid_endmit')
args = parser.parse_args()
pmid_start = int(args.pmid_start)
pmid_end = int(args.pmid_end)


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


embedding.get_articles_centroid(pmid_start = pmid_start,
                          pmid_end = pmid_end,
                          chunk_size=1000)