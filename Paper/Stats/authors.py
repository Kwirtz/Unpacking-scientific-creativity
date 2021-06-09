import pymongo
import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import multiprocessing as mp

client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["pkg"] 
collection = mydb["authors"]

#14.830.455 d'auteurs uniques

docs = collection.aggregate([
    { "$project": {
    "Count": { 
        "$size": { "$ifNull": [ "$pmid_list", [] ] }
    }
}}
])

# evidence of strong power law for number of paper which seems leggit
number_of_papers = tqdm.tqdm([doc["Count"] for doc in docs])
number_of_papers = pd.DataFrame(number_of_papers)
ax = sns.distplot(number_of_papers[0],hist=False)
plt.title("Density of number of papers per author")
plt.savefig('../Results/plot1.png')


# n_authors with atleast one aff detected, usefull to know type for econometrics, papers done by company are more novel
# 8300977
n_authors_with_aff = collection.count_documents({"oa04_affiliations":{"$exists":1}})
 
from utils import *
import pickle
pool = mp.Pool(processes=5)
data = pool.map(read_doc, chunks())
pool.close()
pbar.close()

pickle.dump( data, open( "D:/Github/New-novelty-indicator-using-graph-theory-framework/Data/authors_info.p", "wb" ) )
data = pickle.load( open( "D:/Github/New-novelty-indicator-using-graph-theory-framework/Data/authors_info.p", "rb" ) )
