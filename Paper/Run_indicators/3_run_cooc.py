import novelpy

ref_cooc = novelpy.utils.cooc_utils.create_cooc(
                    collection_name = "meshterms_sample", 
                    year_var="year",
                    var = "a06_meshheadinglist",
                    sub_var = "descUI",
                    weighted_network = True, self_loop = True)

ref_cooc.main()