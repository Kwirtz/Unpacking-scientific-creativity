import pymongo
import pandas as pd 
import numpy as np
import re
import tqdm
import glob
import json

df = pd.read_csv("Data/regression.csv")

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['novelty']
collection = db['output_Author_proximity']

Author_prox_title = {i:{} for i in df["PMID"]}
Author_prox_abstract = {i:{} for i in df["PMID"]}

for pmid in tqdm.tqdm(df["PMID"]):
    docs = list(collection.find({"PMID":pmid,'authors_novelty_abstract_5':{"$exists":1}}))
    intra = []
    inter = []
    for doc in docs:
        try:
            for author in docs[0]['authors_novelty_abstract_5']["individuals_scores"]:
                intra.append(author["percentiles"]["10%"])
            for author_comb in docs[0]['authors_novelty_abstract_5']["iter_individuals_scores"]:
                inter.append(author_comb["percentiles"]["10%"])
            Author_prox_abstract[pmid]["intra"] = intra
            Author_prox_abstract[pmid]["inter"] = inter
        except:
            continue


docs = collection.find()
for doc in tqdm.tqdm(docs):
    try:
        docs = list(collection_author.find({"PMID":id_,'authors_novelty_abstract_5':{"$exists":1}}))
        mean_intra = []
        mean_inter = []
        for doc in docs:
            for author in docs[0]['authors_novelty_abstract_5']["individuals_scores"]:
                mean_intra.append(author["percentiles"]["10%"])
            for author_comb in docs[0]['authors_novelty_abstract_5']["iter_individuals_scores"]:
                mean_inter.append(author_comb["percentiles"]["10%"])
        author_intra_abstract = np.mean(mean_intra)
        author_inter_abstract = np.mean(mean_inter)
    except:
        author_intra_abstract = None
        author_inter_abstract = None
    try:
        docs = list(collection_author.find({"PMID":id_,'authors_novelty_title_5':{"$exists":1}}))
        mean_intra = []
        mean_inter = []
        for doc in docs:
            for author in docs[0]['authors_novelty_title_5']["individuals_scores"]:
                mean_intra.append(author["percentiles"]["10%"])
            for author_comb in docs[0]['authors_novelty_title_5']["iter_individuals_scores"]:
                mean_inter.append(author_comb["percentiles"]["10%"])
        author_intra_title = np.mean(mean_intra)
        author_inter_title = np.mean(mean_inter)
    except:
        author_intra_title = None
        author_inter_title = None
#{PMID:10552265}