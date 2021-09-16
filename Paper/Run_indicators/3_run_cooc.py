from novelpy.utils.cooc_utils import create_cooc

import yaml
with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']



ref_cooc = create_cooc(client_name = pars['client_name'],
                    db_name = "PKG",
                    collection_name = "articles", 
                    year_var="year",
                    var = "c04_referencelist",
                    sub_var = "item",
                    weighted_network = False, self_loop = False)

#ref_cooc.main()

ref_cooc = create_cooc(client_name = pars['client_name'],
                    db_name = "PKG",
                    collection_name = "articles", 
                    year_var="year",
                    var = "c04_referencelist",
                    sub_var = "item",
                    weighted_network = True, self_loop = True)

#ref_cooc.main()

ref_mesh = create_cooc(client_name = 'mongodb://localhost:27017',
                    db_name = "pkg",
                    collection_name = "articles", 
                    year_var="year",
                    var = "a06_meshheadinglist",
                    sub_var = "DescriptorName_UI",
                    weighted_network = False, self_loop = False)

ref_mesh.main()

ref_mesh = create_cooc(client_name = 'mongodb://localhost:27017',
                    db_name = "PKG",
                    collection_name = "articles", 
                    year_var="year",
                    var = "a06_meshheadinglist",
                    sub_var = "DescriptorName_UI",
                    weighted_network = True, self_loop = True)

#ref_mesh.main()