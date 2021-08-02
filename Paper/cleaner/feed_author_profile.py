import pymongo
import numpy as np
import pandas as pd
import tqdm
from joblib import Parallel, delayed
import argparse
import yaml
parser = argparse.ArgumentParser(
    description='compute author profil using abstract and title centroid, var = from and to ')

parser.add_argument('-from_')
parser.add_argument('-to_')
args = parser.parse_args()

def get_author_profil(doc,client_name,db_name,collection_articles,collection_authors,var_year,var_id,var_auth_id):
    """
    Description
    -----------
    This function calculate a semantic representation of previous work for a given author,
    for each year it calculate a weighted mooving average of all previous article representation.
    Finaly it stores the author representation by year in mongo

    Parameters
    ----------
    and_id : int
        the id of the author

    """
    def weighted_moving_av(df_year):
        #Weithed moving average 
        wma = dict()
        years = df_year.index.sort_values()
        for i in range(1,len(years)):# do not use first year of apparition (no previous work)
            T = years[i-1]-years[0]+1
            knowledge_capital = []
            Sum = 0
            for year in years[:i]:
                t = years[i-1]-year+1
                Sum+= T-t+1
                knowledge_capital.append((T-t+1)*df_year[year])
                
            knowledge_capital_t = np.sum(np.array(knowledge_capital),axis=0)/Sum
            wma.update({ str(years[i]):knowledge_capital_t.tolist()})
        return wma

    client = pymongo.MongoClient(client_name)
    db = client[db_name]
    collection_authors = db[collection_authors]
    collection_articles = db[collection_articles]
    # doc = collection_authors.find({var_auth_id:and_id})[0]
    
    
    infos = list()
    for pmid in doc['pmid_list']:
        try:
            article = collection_articles.find({var_id:pmid},no_cursor_timeout  = True)[0]
            
            year = article[var_year]
            title = np.array(
                article['title_embedding']
                ) if article['title_embedding'] else None
            abstract = np.array(
                article['abstract_embedding']
                ) if article['abstract_embedding'] else None
            
            infos.append({'year':year,
                     'title':title,
                     'abstract':abstract})
        except:
            pass
        
    df = pd.DataFrame(infos)
    if not df.empty:
        df = df[~df['year'].isin([''])]
        df_t = df.drop(columns=['abstract']).dropna()
        df_a = df.drop(columns=['title']).dropna()
        
        abs_year = df_a.groupby('year').abstract.apply(np.mean)
        title_year =  df_t.groupby('year').title.apply(np.mean)
        
        wma_abs = weighted_moving_av(abs_year)
        wma_title = weighted_moving_av(title_year)
        
        collection_authors.update_one({var_auth_id:doc[var_auth_id]},
                                      {'$set':{'embedded_abs_wma':wma_abs,
                                               'embedded_title_wma':wma_title}})
# for i in tqdm.tqdm(range(0,15000000,100)):
#     get_author_profil(i)

with open(r"C:\Users\Beta\Documents\GitHub\Taxonomy-of-novelty\mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
db= 'pkg'
client_name = pars['client_name']
db_name = 'PKG'
collection_articles = 'articles'
collection_authors = 'authors'
var_year = 'Journal_JournalIssue_PubDate_Year'
var_id = 'PMID'
var_auth_id = 'AND_ID'

client = pymongo.MongoClient(client_name)
db = client[db_name]
collection_authors = db[collection_authors]
collection_articles = db[collection_articles]
docs = collection_authors.find(no_cursor_timeout  = True).sort([(var_auth_id, pymongo.ASCENDING)])
and_ids = [doc[var_auth_id] for doc in tqdm.tqdm(docs)]
from_ = int(args.from_)
to_ = int(args.to_)      

for doc in tqdm.tqdm(docs[from_:to_]):
    get_author_profil(doc,
                      client_name,
                      db_name,
                      collection_articles,
                      collection_authors,
                      var_year,
                      var_id,
                      var_auth_id)
# Parallel(n_jobs=35)(delayed(get_author_profil)(doc)for doc in tqdm.tqdm(docs))
   