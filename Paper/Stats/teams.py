import tqdm
import pymongo
import pandas as pd 
import seaborn as sns

df = pd.read_csv("Data/regression.csv")

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['novelty']
collection = db['output_Author_proximity']


list_of_insertion_intra = []
list_of_insertion_inter = []

for pmid in tqdm.tqdm(df["PMID"]):
    docs = list(collection.find({"PMID":pmid,'authors_novelty_abstract_5':{"$exists":1}}))
    for doc in docs:
        try:
            for author in doc['authors_novelty_abstract_5']["individuals_scores"]:
                list_of_insertion_intra.append([doc["PMID"], author["percentiles"]["10%"]])
        except Exception as e:
            continue
        try:
            for author_comb in doc['authors_novelty_abstract_5']["iter_individuals_scores"]:
                list_of_insertion_inter.append([doc["PMID"], author_comb["percentiles"]["10%"]])
        except Exception as e:
            continue      
        
        
df_intra = pd.DataFrame(list_of_insertion_intra,columns=["PMID","intra"])
df_inter = pd.DataFrame(list_of_insertion_inter,columns=["PMID","inter"])
df_intra['percent_rank'] = df_intra['intra'].rank(pct=True)
df_inter['percent_rank'] = df_inter['inter'].rank(pct=True)


df = pd.read_csv("Data/regression.csv")
df["share_diverse"] = 0
df["count_diverse"] = 0

df_temp = pd.merge(df, df_intra, on = "PMID", how = 'outer')
df.index = df["PMID"]

highly_diverse = df_temp[df_temp["percent_rank"]>0.90].groupby("PMID").count()

count_diverse = {i:0 for i in df["PMID"]}
share_diverse = {i:0 for i in df["PMID"]}

for row in tqdm.tqdm(df_temp[df_temp["percent_rank"]>0.90].groupby("PMID").agg({'PMID':'first', 'percent_rank': 'count', 'nb_aut': 'first'}).iterrows()):
    pmid = row[1]["PMID"]
    count_diverse[pmid] = row[1]["percent_rank"]
    share_diverse[pmid] = row[1]["percent_rank"]/row[1]["nb_aut"]

    

df["share_diverse"] = df['PMID'].map(share_diverse)
df["count_diverse"] = df['PMID'].map(count_diverse)



