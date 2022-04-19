import novelpy

ref_cooc = novelpy.utils.create_cooc(
                    collection_name = "references", 
                    year_var="year",
                    var = "c04_referencelist",
                    sub_var = "item",
                    time_window = range(1900,2021),
                    weighted_network = False , self_loop = False)

ref_cooc.main()

