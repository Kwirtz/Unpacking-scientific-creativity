import pymongo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

client = pymongo.MongoClient('mongodb://localhost:27017')
mydb = client["novelty"] 
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
number_of_papers = [doc["Count"] for doc in docs]
number_of_papers = pd.DataFrame(number_of_papers)
number_of_papers.columns = ["n"] 
ax = sns.distplot(number_of_papers[0],hist=False)
plt.title("Density of number of papers per author")
plt.savefig('../Results/plot1.png')



np.mean(number_of_papers)
np.std(number_of_papers)
(number_of_papers>500).sum()
number_of_papers = number_of_papers.sort_values("n")
number_of_papers = number_of_papers.reset_index(drop=True)
prop = int(len(number_of_papers)*0.9999)
number_of_papers.at[prop,"n"]

(1 < number_of_papers < 300)
len(number_of_papers[(number_of_papers.n > 1) & (number_of_papers.n < 300)])
