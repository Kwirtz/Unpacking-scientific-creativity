import novelpy
import numpy as np
"""
ref_cooc = novelpy.utils.create_cooc(
                    collection_name = "Meshterms", 
                    year_var="year",
                    var = "Mesh_year_category",
                    sub_var = "descUI",
                    dtype = np.uint32,
                    time_window = range(1900,2021),
                    weighted_network = True, self_loop = True)

ref_cooc.main()
"""
ref_cooc = novelpy.utils.create_cooc(
    collection_name = "references",
    year_var="year",
    dtype = np.uint32,
    var = "c04_referencelist",
    sub_var = "item",
    time_window = range(1781,2006),
    weighted_network = False, self_loop = False)

ref_cooc.main()
