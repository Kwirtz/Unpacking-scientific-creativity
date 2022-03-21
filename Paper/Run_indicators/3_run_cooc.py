import novelpy

ref_cooc = novelpy.utils.create_cooc(
                    collection_name = "Ref_Journals_sample", 
                    year_var="year",
                    var = "c04_referencelist",
                    sub_var = "item",
                    weighted_network = False , self_loop = False)

ref_cooc.main()

