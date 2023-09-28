import re
import tqdm
import glob
import json
import pickle
import pymongo
import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict


with open('Data/deg_cen.pickle', 'rb') as fp:
    deg_cen_dict = pickle.load(fp)


    
client = pymongo.MongoClient("mongodb://localhost:27017")
db_result = client["novelty"]
collection = client['pkg']['control_var_2000_2005']
collection_author = db_result["output_Author_proximity"]


list_of_insertion = []
    
for year in tqdm.tqdm(range(2000,2006)):
    docs = collection.find({"year":year})
    for doc in tqdm.tqdm(docs):
        id_ = doc["PMID"]
        year = doc["year"]
        try:
            journal_category = doc["journal_category"]
        except:
            continue
        docs = list(collection_author.find({"PMID":id_,'authors_novelty_abstract_5':{"$exists":1}}))
        for doc in docs:
            for author in doc['authors_novelty_abstract_5']["individuals_scores"]:
                score_intra = author["percentiles"]["90%"]
                list_of_insertion.append([id_,year, journal_category,score_intra,author["AID"]])

columns = ["PMID", "year", "journal_category","score_intra","AID"]


df=pd.DataFrame(list_of_insertion,columns=columns)        

        
        
df['journal_main_cat'] = df['journal_category'].str.split('; ').str.get(0)
df['journal_main_cat'] = df['journal_main_cat'].apply(lambda x: re.sub(' \\(Q\\d\\)$', '', str(x)))

# Step 1: Add a new column for percent rank
df['percent_rank'] = 0.0

# Step 2: Calculate percent rank grouped by main_journal_cat and year
df['percent_rank'] = df.groupby(['journal_main_cat', 'year'])['score_intra'].rank(pct=True)

# Step 3: Add a new column for highly_diverse based on percent rank
df['highly_diverse'] = df['percent_rank'].apply(lambda x: 1 if x >= 0.90 else 0)



grouped_df = df.groupby(['AID', 'year'])

# Step 2: Aggregate the grouped data
new_df = grouped_df.agg({'highly_diverse': 'sum', 'AID': ['count', 'first']})

# Step 3: Create a new DataFrame
new_df = pd.DataFrame(new_df)

# Step 4: Reset the index and flatten the column names
new_df.columns = ['_'.join(col) for col in new_df.columns]
new_df.reset_index(inplace=True)
new_df["share_highly_diverse"] = new_df["highly_diverse_sum"]/new_df["AID_count"]


new_df["deg_cen"] = 0
new_df["deg_cen_cumsum"] = 0

        
for row in tqdm.tqdm(new_df.iterrows()):
    AID = int(row[1]["AID"])
    year = int(row[1]["year"])
    deg_cen = deg_cen_dict[year][AID]["deg_cen"]
    deg_cen_cumsum = deg_cen_dict[year][AID]["cumsum"]
    condition = (df['AID'] == AID) & (df['year'] == year)
    df.loc[condition, ['deg_cen', 'deg_cen_cumsum']] = [deg_cen, deg_cen_cumsum]
        
new_df.set_index(['year', 'AID'], inplace=True)
new_df
# Create a dictionary with the updated values

updates = {(year, AID): {"deg_cen": deg_cen_dict[year][AID]["deg_cen"], "deg_cen_cumsum": deg_cen_dict[year][AID]["cumsum"]}
           for year in deg_cen_dict
           for AID in deg_cen_dict[year]}
    

# Create a DataFrame from the dictionary
update_df = pd.DataFrame.from_dict(updates, orient='index')
        

new_df.update(update_df)

# Reset the index and split it into separate 'year' and 'AID' columns
new_df.reset_index(drop=False, inplace=True)

mean_by_aid = new_df.groupby('AID')['deg_cen_cumsum', 'deg_cen', 'share_highly_diverse'].mean()


plt.hist2d(mean_by_aid['share_highly_diverse'], mean_by_aid['deg_cen_cumsum'], bins=10, cmap='Blues')

# Set plot labels and title
plt.xlabel('Share Highly Diverse')
plt.ylabel('deg_cen_cumsum')
plt.title('Histogram of Share Highly Diverse vs deg_cen_cumsum')

# Show the colorbar
plt.colorbar()

# Show the plot
plt.show()

# Create a scatter plot
plt.scatter(mean_by_aid['share_highly_diverse'], mean_by_aid['deg_cen_cumsum'])

# Set plot labels and title
plt.xlabel('Share Highly Diverse')
plt.ylabel('deg_cen')
plt.title('Scatter Plot of Share Highly Diverse vs deg_cen')

# Show the plot
plt.show()

mean_share_1 = mean_by_aid[mean_by_aid['share_highly_diverse'] > 0.9]['deg_cen_cumsum'].mean()

# Calculate the mean of deg_cen_cumsum for others (share_highly_diverse != 1)
mean_others = mean_by_aid[mean_by_aid['share_highly_diverse'] < 0.1]['deg_cen_cumsum'].mean()

print("Mean of deg_cen_cumsum for share_highly_diverse == 1:", mean_share_1)
print("Mean of deg_cen_cumsum for others:", mean_others)
