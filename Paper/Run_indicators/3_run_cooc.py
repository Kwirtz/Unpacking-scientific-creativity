import yaml
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']

from novelpy import create_cooc



test = create_cooc(client_name = pars['client_name'],
                   db_name = "PKG",
                   collection_name = "articles_test",
                   year_var="year",
                   var = "c04_referencelist",
                   sub_var = "item",
                   weighted_network = True,self_loop = True)

#test.main()
test = create_cooc(client_name = pars['client_name'],
                   db_name = "PKG",
                   collection_name = "articles_test", 
                   year_var="year",
                   var = "c04_referencelist",
                   sub_var = "item",
                   weighted_network = False,self_loop = False)

test.main()
# test = create_cooc(client_name = pars['client_name'],
#                    db_name = "PKG",
#                    collection_name = "articles", 
#                    year_var="year",
#                    var = "Mesh_year_category",
#                    sub_var = "descUI",
#                    weighted_network = False, self_loop = False)

# test.main()
# test = create_cooc(client_name = pars['client_name'],
#                    db_name = "PKG",
#                    collection_name = "articles", 
#                    year_var="year",
#                    var = "Mesh_year_category",
#                    sub_var = "descUI",
#                    weighted_network = True, self_loop = True)

# test.main()