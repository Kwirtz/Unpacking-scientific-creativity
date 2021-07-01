# Download the data here http://er.tacc.utexas.edu/datasets/ped

import pymysql
import pymongo
import tqdm

con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='a03_keywordlist')
cur = con.cursor()
if cur.connection:
    print("connection exists")

# What's in the box ?

"""
cur = con.cursor(pymysql.cursors.DictCursor)
query = ("SELECT * FROM a02_authorlist LIMIT 1000 OFFSET 20000000")
cur.execute(query)
box = cur.fetchall()
"""

# tables
query = ("show tables")
cur.execute(query)
tables = list(cur.fetchall())
tables = [table[0] for table in tables]

cur = con.cursor(pymysql.cursors.DictCursor)
query = ("SELECT * FROM a01_articles LIMIT %s OFFSET %s")


client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["pkg"] 
collection = mydb["articles"]

def init_create():

    done = False
    process_n = 200000
    i = 0
    pbar = tqdm.tqdm()
    while done == False:
        cur.execute(query,(process_n, (process_n*i)))
        post = cur.fetchall()
        if post:
            collection.insert_many(post)
            i += 1
            pbar.update(1)
        else:
            done = True
            
    collection.create_index([ ("PMID",1) ])

init_create()

# Insert table

con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='a03_keywordlist')
cur = con.cursor()
if cur.connection:
    print("connection exists")
    
query = ("show tables")
cur.execute(query)
tables = list(cur.fetchall())
tables = [table[0] for table in tables]

client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["pkg"] 
collection = mydb["articles"]


table = tables[0]
    
try:
    with open("D:/kevin_data/pkg_{}.txt".format(table),"r") as f:
        processed = int(f.read())
except:
    processed = 0
        
query = ("""SELECT * FROM %s LIMIT %s OFFSET %s""")
process_n = 200000
con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='a03_keywordlist')
cur = con.cursor(pymysql.cursors.DictCursor)

pbar = tqdm.tqdm()
done = False
i = 0
list_articles = []
if table.startswith("a"):
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
                        collection.find_one_and_update({"PMID":(doc["PMID"]-1)}, {"$set":{table:list_articles}})
                        list_articles = [doc]
                else:
                    list_articles = [doc]
            with open("D:/kevin_data/pkg_{}.txt".format(table),"w") as f:
                f.write(str(doc["id"]))    
        else:
            done = True
        i += 1
        pbar.update(1)
pbar.close()


# create table_authors

query = ("""SELECT * FROM %s LIMIT %s OFFSET %s""")
process_n = 200000
table = "oa01_author_list"

con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='pkg')
cur = con.cursor(pymysql.cursors.DictCursor)
new_query = query % (table,process_n, 29000000)
cur.execute(new_query)
post = cur.fetchall()


query = ("""SELECT MAX(id) FROM a02_authorlist""")
con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='pkg')
cur = con.cursor(pymysql.cursors.DictCursor)
cur.execute(query)
post = cur.fetchall()




# second method nosql_oriented



client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["pkg"] 
collection = mydb["authors"]

#collection.create_index([ ("AND_ID",1) ])

query = ("""SELECT * FROM oa01_author_list LIMIT %s OFFSET %s""")

process_n = 200000
try:
    with open("D:/kevin_data/pkg_author.txt","r") as f:
        processed = int(f.read())
except:
    processed = 0

con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='pkg')
cur = con.cursor(pymysql.cursors.DictCursor)

pbar = tqdm.tqdm()
done = False
i = 0
while done == False:
    new_query = query % (process_n, (processed + process_n*i))
    cur.execute(new_query)
    docs = cur.fetchall()
    if docs:
        for doc in docs:
            if doc["AND_ID"] == 0:
                continue
            if collection.find_one_and_update({"AND_ID":doc["AND_ID"]}, {"$push":{"more_info":doc,"pmid_list":doc["PMID"]}}):
                pass
            else:
                collection.insert_one({"AND_ID":doc["AND_ID"],"pmid_list":[doc["PMID"]],"more_info":[doc]})
            with open("D:/kevin_data/pkg_author.txt","w") as f:
                f.write(str(doc["id"]))
    else:
        done = True
    i += 1
    pbar.update(1)
 
# Insert author related tables

client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["pkg"] 
collection = mydb["authors"]

con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='pkg')
cur = con.cursor()
if cur.connection:
    print("connection exists")
    
query = ("show tables")
cur.execute(query)
tables = list(cur.fetchall())
tables = [table[0] for table in tables]



table = tables[37]
    
try:
    with open("D:/kevin_data/pkg_{}.txt".format(table),"r") as f:
        processed = int(f.read())
except:
    processed = 0
        
query = ("""SELECT * FROM %s LIMIT %s OFFSET %s""")
process_n = 200000
con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='pkg')
cur = con.cursor(pymysql.cursors.DictCursor)

pbar = tqdm.tqdm()
done = False
i = 0
while done == False:
    new_query = query % (table,process_n, (processed + process_n*i))
    cur.execute(new_query)
    docs = cur.fetchall()
    if docs:
        for doc in docs:
            if doc["AND_ID"] != 0:
                if collection.find_one_and_update({"AND_ID":(doc["AND_ID"])}, {"$push":{table:doc}}):
                    continue
                else:
                    collection.find_one_and_update({"AND_ID":(doc["AND_ID"])}, {"$set":{table:[doc]}})
        with open("D:/kevin_data/pkg_{}.txt".format(table),"w") as f:
            f.write(str(doc["id"]))    
    else:
        done = True
    i += 1
    pbar.update(1)
pbar.close()

#collection.update_many({}, {'$unset': {table:1}})
#%% Trying to understand the fuck is going on

con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='pkg')
cur = con.cursor(pymysql.cursors.DictCursor)

for table in tables:
    query = ("""SHOW KEYS FROM %s WHERE Key_name = 'PRIMARY'""")
    new_query = query % (table)
    cur.execute(new_query)
    post = cur.fetchall()
    print(post) 

# inspect mongodb
docs = collection.find({'a04_abstract': {"$exists": 1}}).sort("PMID",pymongo.DESCENDING)
doc = next(docs)
n = 0
for doc in tqdm.tqdm(docs):
    pmid = ["PMID"]
    break

collection.index_information()
{"$and"'a14_referencelist.1': {"$exists": 1}}
{"$and":[ {'a14_referencelist.1': {"$exists": 1}}, {'a13_affiliationlist.1': {"$exists": 1}}]}

# inspect mysql

con = pymysql.connect(host = 'localhost', user = 'root',passwd = 'root', db='pkg')
cur = con.cursor(pymysql.cursors.DictCursor)
query = ("""SELECT * FROM c01_articles_simple LIMIT 10""")
cur.execute(query)
docs = cur.fetchall()
