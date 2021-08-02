# Download the data here http://er.tacc.utexas.edu/datasets/ped

import pymysql
import pymongo
import tqdm
import re
import pandas as pd


# PMID YEAR ISSN

pmid_issn = pd.read_csv('D:/PKG/final_folder_260721/Data/PMID_ISSN_YEAR.csv')
pmid_issn = pmid_issn.dropna()
pmid_issn = pmid_issn.set_index('PMID')
pmid_issn = pmid_issn.rename(columns={'Journal_ISSN':'item',
                                      'Journal_JournalIssue_PubDate_Year':'year'})

pmid_issn = pmid_issn[~pmid_issn.year.isin([''])]
pmid_issn['year'] = pmid_issn.year.astype(int)
pmid_issn = pmid_issn.T.to_dict()

# Insert table

con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='wosref')
cur = con.cursor()
if cur.connection:
    print("connection exists")
    
query = ("show tables")
cur.execute(query)
tables = list(cur.fetchall())
tables = [table[0] for table in tables]

client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["PKG"] 
collection = mydb["articles_test"]

table = tables[0]
    
# try:
#     with open("D:/PKG/pkg_{}.txt".format(table),"r") as f:
#         processed = int(f.read())
# except:
processed = 0
        
query = ("""SELECT * FROM %s LIMIT %s OFFSET %s""")
process_n = 1000000
con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='wosref')
cur = con.cursor(pymysql.cursors.DictCursor)



pbar = tqdm.tqdm()
done = False
i = 0
list_articles = []
pmid_list = []
doc_pmid = set()
if table.startswith("c"):
    while done == False:
        new_query = query % (table,process_n, (processed + process_n*i))
        cur.execute(new_query)
        docs = cur.fetchall()
        if docs:
            for doc in tqdm.tqdm(docs):
                doc_pmid.update([doc['PMID']])
                if len(doc_pmid) == 1:
                    pmid = list(doc_pmid)[0]
                    pmid_list.append(doc['RefArticleId'])
                    try:
                        info = pmid_issn[doc['RefArticleId']]
                        list_articles.append(info)
                    except:
                        pass
                else:
                    collection.update_one({"PMID":pmid},
                                              {"$set":{table:list_articles,
                                                        'refs_pmid_wos':pmid_list}})

                    doc_pmid = set([doc['PMID']])
                    list_articles = []
                    pmid_list = [doc['RefArticleId']]
                    pmid = list(doc_pmid)[0]
                    try:
                        info = pmid_issn[doc['RefArticleId']]
                        list_articles.append(info)
                    except:
                        pass
        else:
            done = True
        i += 1
        pbar.update(1)
pbar.close()


