# Download the data here http://er.tacc.utexas.edu/datasets/ped
# Put the data in mysql then convert mysql to pymongo using the following code
import pymysql
import pymongo
import tqdm
import re
import ast
import pandas as pd
import dask.dataframe as dd

class import_pkg2mongo():
    
    def __init__(self, pymysql_host, pymysql_user, pymysql_passwd, mongo_uri, db_name,process_n):
        self.pymysql_host = pymysql_host
        self.pymysql_user = pymysql_user
        self.pymysql_passwd = pymysql_passwd
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.con = pymysql.connect(host = self.pymysql_host, user = self.pymysql_user,
                              passwd = self.pymysql_passwd, db=self.db_name)
        client = pymongo.MongoClient(self.mongo_uri)
        self.mydb = client[self.db_name] 
        self.process_n = process_n
    
    def get_tables(self):
        cur = self.con.cursor()
        query = ("show tables")
        cur.execute(query)
        tables = list(cur.fetchall())
        self.tables = [table[0] for table in tables]
    
    def init_commit_article(self, file = False):
        collection = self.mydb["articles"]
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        
        if file == False:
            query = ("""SELECT * FROM %s LIMIT %s OFFSET %s""")
            done = False

            i = 0
            pbar = tqdm.tqdm()
            while done == False:
                cur.execute(query,("a01_articles", self.process_n, (self.process_n*i)))
                post = cur.fetchall()
                if post:
                    collection.insert_many(post)
                    i += 1
                    pbar.update(1)
                else:
                    done = True
            pbar.close() 
        else:
            with open(file, encoding="utf8") as f:
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
        
        
    def insert_table_article(self, table,fs_file = None):
        # import file in case of failure
        if fs_file != None:
            try:
                with open(fs_file+ "/pkg_{}.txt".format(table),"r") as f:
                    processed = int(f.read())
            except:
                processed = 0

        collection = self.mydb["articles"]
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        query = ("""SELECT * FROM %s LIMIT %s OFFSET %s""")

        
        pbar = tqdm.tqdm()
        done = False
        i = 0
        list_articles = []
        if table.startswith("a"):
            while done == False:
                new_query = query % (table,self.process_n, (processed + self.process_n*i))
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
                    if fs_file != None:
                        with open(fs_file+ "/pkg_{}.txt".format(table),"w") as f:
                            f.write(str(doc["id"]))    
                else:
                    done = True
                i += 1
                pbar.update(1)
        pbar.close()

    def init_commit_author(self, fp_csv, fs_file = None):    
        
        if fs_file != None:
            try:
                with open(fs_file+ "/pkg_author.txt","r") as f:
                    processed = int(f.read())
            except:
                processed = 0
                
        df = pd.read_csv(fp_csv)
        collection = self.mydb["authors"]
        try:
            collection.create_index([ ("AND_ID",1) ])
        except:
            pass
        
        it = 0
        for id_, PMID, AND_ID, AuOrder, LastName, ForeName, Initials, Suffix, AuNum,\
            PubYear, BeginYear in tqdm.tqdm(zip(df["id"],df["PMID"],df["AND_ID"],df["AuOrder"],
                                             df["LastName"],df["ForeName"],df["Initials"],
                                             df["Suffix"],df["AuNum"],df["PubYear"],df["BeginYear"])):
            if fs_file != None:
                if it < processed:
                    it += 1
                    continue 
            info = {"id":id_, "PMID":PMID, "AND_ID":AND_ID, "AuOrder":AuOrder, "LastName":LastName,
                    "ForeName":ForeName, "Initials":Initials, "Suffix":Suffix,
                    "AuNum":AuNum,"PubYear":PubYear, "BeginYear":BeginYear}
            if info["AND_ID"] == 0:
                continue
            if collection.find_one_and_update({"AND_ID":info["AND_ID"]}, {"$push":{"more_info":info,"pmid_list":info["PMID"]}}):
                pass
            else:
                collection.insert_one({"AND_ID":info["AND_ID"],"pmid_list":[info["PMID"]],"more_info":[info]})
            if fs_file:
                with open(fs_file+ "/pkg_author.txt","w") as f:
                    f.write(str(info["id"]))                   
    
    def insert_table_author(self, fp_csv,fs_file = None):
        
        table_name = fp_csv.split('/')[-1].split(".")[0].lower()
        df = dd.read_csv(fp_csv)
        collection = self.mydb["authors"]
        
        if fs_file != None:
            try:
                with open(fs_file+ "/pkg_author.txt","r") as f:
                    processed = int(f.read())
            except:
                processed = 0       
        
        it = 0
        for i in tqdm.tqdm(df.iterrows()):
            if fs_file != None:
                if it < processed:
                    it += 1
                    continue
            info = dict(i[1])
            if info["AND_ID"] == 0:
                continue
            if collection.find_one_and_update({"AND_ID":info["AND_ID"]}, {"$push":{table_name:info}}):
                pass
            else:
                collection.find_one_and_update({"AND_ID":info["AND_ID"]}, {table_name:[info]})
            if fs_file:
                it += 1
                with open(fs_file+ "/pkg_author.txt","w+") as f:
                    f.write(str(it))
    
    def create_issn_csv(self):
        collection = self.mydb["articles"]
        docs = collection.find({},no_cursor_timeout=True, batch_size=self.process_n)
        pmid_issn_year = []
        for doc in tqdm.tqdm(docs,desc="Reading through articles"):
            pmid_issn_year.append({"Journal_ISSN":doc["Journal_ISSN"],
             "Journal_JournalIssue_PubDate_Year":doc["Journal_JournalIssue_PubDate_Year"],
             "PMID":doc["PMID"]})
        pmid_issn_year = pd.DataFrame(pmid_issn_year)
        pmid_issn_year.to_csv("./Paper/Data/PMID_ISSN_YEAR.csv")
    
    
    def insert_scimago(self,table):
        

        collection = self.mydb["articles"]
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        query = ("""SELECT * FROM %s LIMIT %s OFFSET %s""")
 
        pmid_issn = pd.read_csv('./Paper/Data/PMID_ISSN_YEAR.csv')
        pmid_issn = pmid_issn.dropna()
        pmid_issn['id'] = pmid_issn["Journal_ISSN"] + pmid_issn["Journal_JournalIssue_PubDate_Year"].astype(int).astype(str)
        pmid_issn = pmid_issn.drop(['Journal_ISSN',
                                    'Journal_JournalIssue_PubDate_Year'],
                                   axis= 1)
        pmid_issn = pmid_issn.groupby('id')['PMID'].apply(list)
        pmid_issn = pmid_issn.T.to_dict()
        
        pbar = tqdm.tqdm()
        done = False
        i = 0
        if table.startswith("b"):
            while done == False:
                new_query = query % (table,self.process_n, (self.process_n*i))
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
    
    def insert_wos(self,table):
        collection = self.mydb["articles"]
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        query = ("""SELECT * FROM %s LIMIT %s OFFSET %s""")
        
        pmid_issn = pd.read_csv('./Paper/Data/PMID_ISSN_YEAR.csv')
        pmid_issn = pmid_issn.dropna()
        pmid_issn['id'] = pmid_issn["Journal_ISSN"] + pmid_issn["Journal_JournalIssue_PubDate_Year"].astype(int).astype(str)
        pmid_issn = pmid_issn.drop(['Journal_ISSN',
                                    'Journal_JournalIssue_PubDate_Year'],
                                   axis= 1)
        pmid_issn = pmid_issn.groupby('id')['PMID'].apply(list)
        pmid_issn = pmid_issn.T.to_dict()

        pbar = tqdm.tqdm()
        done = False
        i = 0
        list_articles = []
        pmid_list = []
        doc_pmid = set()
        if table.startswith("c"):
            while done == False:
                new_query = query % (table,self.process_n, (self.process_n*i))
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
        
                            doc_pmid = set()
                            list_articles = []
                            pmid_list = []
                else:
                    done = True
                i += 1
                pbar.update(1)
        pbar.close()

item = import_pkg2mongo(pymysql_host='localhost', pymysql_user="root", pymysql_passwd="root",
                 mongo_uri = 'mongodb://localhost:27017', db_name = "pkg" ,process_n = 100000)

# insert table from sql txt file
#item.init_commit_article()

# Insert table by table
#item.get_tables()
#item.insert_table_article(item.tables[5],fs_file = "D:/kevin_data")
#item.tables[5] 156595714

# Insert scimago
#item.insert_scimago(item.tables[-2])
# Insert wos
#item.insert_wos(item.tables[-2])


# Create collection with authors from csv

item.init_commit_author(fp_csv="G:/backup_paper2/pkg/OA01_Author_List/OA01_Author_List.csv",
                        fs_file = "D:/kevin_data")

# Insert author table from csv
#item.insert_table_author(fp_csv="G:/backup_paper2/pkg/OA04_Affiliations/OA04_Affiliations.csv",
 #                        fs_file = "D:/kevin_data")




