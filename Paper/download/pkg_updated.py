import tqdm
import re 
import ast
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017')
mydb = client["pkg"] 
collection = mydb["articles_test"]

#init commit
def init_commit():
    with open('G:/backup_paper2/pkg/PKG2020S4_A01_Articles.sql/PKG2020S4_A01_Articles.sql', encoding="utf8") as f:
        key_list = []
        for line in tqdm.tqdm(f):
            if line.startswith('  `'):
                key_name = re.search('`.*?`',line).group(0) 
                key_name = re.sub("`","",key_name)
                key_list.append(key_name)
            if line.startswith("INSERT"):
                docs = line.split(".xml'),")
                docs_cleaned = [re.sub("[()]","",doc)+".xml'" for doc in docs]
                docs_cleaned[0] = re.sub("INSERT INTO `A01_Articles` VALUES ","",docs_cleaned[0])
                docs_cleaned[-1] = re.sub(";\n.xml'","",docs_cleaned[-1])
                docs_cleaned = [ast.literal_eval(doc) for doc in docs_cleaned]
                list_of_insertion = [{key:value for key,value in zip(key_list,doc)}for doc in docs_cleaned]
                collection.insert_many(list_of_insertion)
    
    collection.create_index([ ("PMID",1) ])

# Others articles related 

"""
i = 0
with open('G:/backup_paper2/pkg/PKG2020S4_A02_AuthorList.sql/PKG2020S4_A02_AuthorList.sql', encoding="utf8") as f:
    key_list = []
    for line in tqdm.tqdm(f):
        if line.startswith('  `'):
            key_name = re.search('`.*?`',line).group(0) 
            key_name = re.sub("`","",key_name)
            key_list.append(key_name)
            continue
        if line.startswith("INSERT"):
            table = re.sub("`","",re.search("`.{0,30}`",line).group(0))
            try:
                with open("D:/kevin_data/pkg_{}.txt".format(table),"r") as f:
                    processed = int(f.read())
            except:
                processed = 0
            if i < processed:
                i += 1
                continue
            docs = line.split("),(")
            docs_cleaned = [re.sub("[()]","",doc) for doc in docs]
            docs_cleaned[0] = re.sub("INSERT INTO `{}` VALUES ".format(table),"",docs_cleaned[0])
            docs_cleaned[-1] = re.sub(";\n","",docs_cleaned[-1])
            docs_cleaned = [ast.literal_eval(re.sub("NULL","''",doc)) for doc in docs_cleaned]
            list_of_insertion = [{key:value for key,value in zip(key_list,doc)}for doc in docs_cleaned]
            list_articles = []
            for doc in list_of_insertion:
                if list_articles:
                    if list_articles[0]["PMID"] == doc["PMID"]:
                        list_articles.append(doc)
                    else:
                        collection.find_one_and_update({"PMID":(list_articles[0]["PMID"])}, {"$set":{table:list_articles}})
                        list_articles = [doc]
                else:
                    list_articles = [doc]
        i += 1
        with open("D:/kevin_data/pkg_{}.txt".format(table),"w+") as f:
            f.write(str(i))    

"""


def insert_A(table_name):
    i = 0
    with open('G:/backup_paper2/pkg/{}/{}'.format(table_name,table_name), encoding="utf8") as f:
        key_list = []
        for line in tqdm.tqdm(f):
            if line.startswith('  `'):
                key_name = re.search('`.*?`',line).group(0) 
                key_name = re.sub("`","",key_name)
                key_list.append(key_name)
                continue
            if line.startswith("INSERT"):
                table = re.sub("`","",re.search("`.{0,30}`",line).group(0))
                try:
                    with open("D:/kevin_data/pkg_{}.txt".format(table),"r") as f:
                        processed = int(f.read())
                except:
                    processed = 0
                if i < processed:
                    i += 1
                else:
                    docs = line.split("),(")
                    docs_cleaned = [re.sub("[()]","",doc) for doc in docs]
                    docs_cleaned[0] = re.sub("INSERT INTO `{}` VALUES ".format(table),"",docs_cleaned[0])
                    docs_cleaned[-1] = re.sub(";\n","",docs_cleaned[-1])
                    docs_cleaned = [ast.literal_eval(re.sub("NULL","''",doc)) for doc in docs_cleaned]
                    list_of_insertion = [{key:value for key,value in zip(key_list,doc)}for doc in docs_cleaned]
                    list_articles = []
                    for doc in list_of_insertion:
                        if list_articles:
                            if list_articles[0]["PMID"] == doc["PMID"]:
                                list_articles.append(doc)
                            else:
                                collection.find_one_and_update({"PMID":(list_articles[0]["PMID"])}, {"$set":{table:list_articles}})
                                list_articles = [doc]
                        else:
                            list_articles = [doc]
                    i += 1
                    with open("D:/kevin_data/pkg_{}.txt".format(table),"w+") as f:
                        f.write(str(i))        



insert_A("PKG2020S4_A04_Abstract.sql")



# Authors table











