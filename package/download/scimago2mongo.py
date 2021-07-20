# Download the data here http://er.tacc.utexas.edu/datasets/ped

import pymysql
import pymongo
import tqdm
import re


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
            for doc in docs:
                issn = re.sub(' ','',docs[123]['pISSN'])
                issn  = '-'.join([issn[:4],issn[4:]])
                pkg_doc = collection.find({'Journal_ISSN': issn,
                                 'Journal_JournalIssue_PubDate_Year':doc['ToYear']})
                pmids = [d['PMID'] for d in tqdm.tqdm(pkg_doc)]
                
                collection.update_one({"PMID":pmids}, {"$set":{table:doc}})
                
            with open("D:/PKG/pkg_{}.txt".format(table),"w") as f:
                f.write(str(doc["id"]))    
        else:
            done = True
        i += 1
        pbar.update(1)
pbar.close()






## fro ref

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
            for doc in docs:
                if list_articles:
                    if list_articles[0]["PMID"] == doc["PMID"]:
                        list_articles.append(doc)
                        continue
                    else:
                        collection.find_one_and_update({"PMID":(list_articles[0]["PMID"])}, {"$set":{table:list_articles}})
                        list_articles = [doc]
                else:
                    list_articles = [doc]
            with open("D:/PKG/pkg_{}.txt".format(table),"w") as f:
                f.write(str(doc["id"]))    
        else:
            done = True
        i += 1
        pbar.update(1)
pbar.close()