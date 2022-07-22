import novelpy

clean = novelpy.utils.preprocess_disruptiveness.create_citation_network(client_name = 'mongodb://localhost:27017',
                                                                        db_name = 'novelty',collection_name = "Citation_net",
                                                                        id_variable = "PMID", variable = "refs_pmid_wos")
clean.id2citedby()
clean.update_db()