import pymongo
import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

## F1000 stats

#180k paper, a bit more than 80k with pmid, only able to match 79k with pkg

client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["F1000"] 
collection = mydb["merged"]

collection.find({"recommendations":{"$size":1}})
cats = ["Changes Clinical Practice","Confirmation","Controversial","Good for Teaching","Interesting Hypothesis","Negative/Null Result",
              "New Finding","Novel Drug Target","Refutation","Technical Advance"]

# Categories 

df_cat = pd.DataFrame(columns = cats, dtype='int8')
docs = collection.find()

for doc in tqdm.tqdm(docs):
    df_cat.loc[doc["pmid"]] = [1 if cat in doc["recommendations"][0]["cats"] else 0 for cat in cats]

corr_cat = df_cat.corr()

count_cat = []
for column in df_cat:
    count_cat.append(df_cat[column].sum())

fig, ax = plt.subplots()    
width = 0.75 # the width of the bars 
ind = np.arange(len(count_cat))  # the x locations for the groups
ax.barh(ind, count_cat, width, color="blue")
ax.set_yticks(ind+width/2)
ax.set_yticklabels(cats, minor=False)
plt.title('title')


    
# rating

ratings = ["Exceptional","Very Good","Good","Dissent"]


df_ratings = pd.DataFrame(columns = ratings, dtype='int8')
docs = collection.find()

for doc in tqdm.tqdm(docs):
    df_ratings.loc[doc["pmid"]] = [1 if rating==doc["recommendations"][0]["rating"] else 0 for rating in ratings]

df_ratings.corr()

count_rating = []
for column in df_ratings:
    count_rating.append(df_ratings[column].sum())
   
fig, ax = plt.subplots()    
width = 0.75 # the width of the bars 
ind = np.arange(len(count_rating))  # the x locations for the groups
ax.barh(ind, count_rating, width, color="blue")
ax.set_yticks(ind+width/2)
ax.set_yticklabels(ratings, minor=False)
plt.title('title')
