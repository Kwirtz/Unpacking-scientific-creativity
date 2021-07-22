# Download the data here http://er.tacc.utexas.edu/datasets/ped

import pymysql
import pymongo
import tqdm
import re
import pandas as pd


# PMID YEAR ISSN

pmid_issn = pd.read_csv('D:/PKG/PMID_ISSN_YEAR.csv')
pmid_issn = pmid_issn.dropna()
pmid_issn['id'] = pmid_issn["Journal_ISSN"] + pmid_issn["Journal_JournalIssue_PubDate_Year"].astype(int).astype(str)
pmid_issn = pmid_issn.drop(['Journal_ISSN',
                            'Journal_JournalIssue_PubDate_Year'],
                           axis= 1)

pmid_issn = pmid_issn.groupby('id')['PMID'].apply(list)
pmid_issn = pmid_issn.T.to_dict()

# Insert table

con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='scimago')
cur = con.cursor()
if cur.connection:
    print("connection exists")
    
query = ("show tables")
cur.execute(query)
tables = list(cur.fetchall())
tables = [table[0] for table in tables]

client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["PKG"] 
collection = mydb["articles"]

table = tables[0]
    
try:
    with open("D:/PKG/pkg_{}.txt".format(table),"r") as f:
        processed = int(f.read())
except:
    processed = 0
        
query = ("""SELECT * FROM %s LIMIT %s OFFSET %s""")
process_n = 200000
con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='scimago')
cur = con.cursor(pymysql.cursors.DictCursor)



pbar = tqdm.tqdm()
done = False
i = 0
list_articles = []
if table.startswith("b"):
    while done == False:
        new_query = query % (table,process_n, (processed + process_n*i))
        cur.execute(new_query)
        docs = cur.fetchall()
        if docs:
            for doc in tqdm.tqdm(docs):
                issn = re.sub(' ','',doc['pISSN'])
                issn_year  = '-'.join([issn[:4],issn[4:]])+str(doc['ToYear'])
                
                if issn_year in pmid_issn.keys():
                    pmids = pmid_issn[issn_year]
                    for pmid in pmids:
                        collection.update_one({"PMID":pmid}, {"$set":{table:doc}})
                  
        else:
            done = True
        i += 1
        pbar.update(1)
pbar.close()







# ## fro ref

# pbar = tqdm.tqdm()
# done = False
# i = 0
# list_articles = []
# if table.startswith("b"):
#     while done == False:
#         new_query = query % (table,process_n, (processed + process_n*i))
#         cur.execute(new_query)
#         docs = cur.fetchall()
#         if docs:
#             for doc in docs:
#                 if list_articles:
#                     if list_articles[0]["PMID"] == doc["PMID"]:
#                         list_articles.append(doc)
#                         continue
#                     else:
#                         collection.find_one_and_update({"PMID":(list_articles[0]["PMID"])}, {"$set":{table:list_articles}})
#                         list_articles = [doc]
#                 else:
#                     list_articles = [doc]
#             with open("D:/PKG/pkg_{}.txt".format(table),"w") as f:
#                 f.write(str(doc["id"]))    
#         else:
#             done = True
#         i += 1
#         pbar.update(1)
# pbar.close()