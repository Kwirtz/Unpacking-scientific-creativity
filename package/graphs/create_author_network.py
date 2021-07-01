import yaml
from package.utils import create_cooc
 
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_Kevin']
client_name = pars["pymongo_connection"]

#%%

test = create_cooc(client_name = client_name, db_name = "pkg",
                   collection_name = "articles", year_var="yearmonth",
                   month=True, var = "a02_authorlist", sub_var = "AID",
                   weighted_network = True)

test.main()

test2 = create_cooc(client_name = client_name, db_name = "pkg", collection_name = "articles",
                 var = "a03_keywordlist", sub_var = "Keyword" )
test2.main()

test3 = create_cooc(client_name = client_name, db_name = "pkg", collection_name = "articles",
                 var = "CR_year_category", sub_var = "journal" )
test3.main()
