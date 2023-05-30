import pymongo
import pandas as pd 
import numpy as np
import re
import tqdm
import glob
import json
import pickle

with open('Data/deg_cen.pickle', 'rb') as fp:
    deg_cen = pickle.load(fp)


def get_scimago_file(year):

    journals = pd.read_csv(r'Data/scimago_journals/scimagojr {}.csv'.format(str(year)),
                sep=';')

    journals['Issn'] = journals['Issn'].str.split(', ')
    journals = journals.explode('Issn')
    journals['Issn'] = journals['Issn'].astype(str)
    return journals

journals = get_scimago_file(2000)

class CreateVariable:
    
    def __init__(self,
                year):
    
        client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = client['pkg']
        self.collection = self.db['articles']
        self.collection_cit_net = client['novelty']['Citation_net_cleaned']
        self.year = year
        self.journals = get_scimago_file(self.year)
        
    def get_nb_cit_ref(self,pmid):
        try:
            doc = self.collection_cit_net.find_one({'PMID':pmid})
            if 'citations' in doc:
                nb_ref = len(doc['citations']['refs'])
                nb_cit = len(doc['citations']['cited_by'])
                
                self.variables.update({'nb_cit':nb_cit, 'nb_ref': nb_ref})
        except:
            pass
    

    def get_aut_infos(self,author_list):
        nb_aut = len(author_list)
        aff_captured = []
        sum_deg_cen = 0
        sum_deg_cen_cumsum = 0
        for author in author_list:
            if author['Affiliation'] != '':
                aff_captured.append(author['Affiliation'])
            try:
                sum_deg_cen += deg_cen[self.year-1][author["AID"]]["deg_cen"]
            except:
                pass
            try:
                sum_deg_cen_cumsum += deg_cen[self.year-1][author["AID"]]["cumsum"]
            except:
                pass
        try:
            sum_deg_cen_cumsum_mean =  sum_deg_cen_cumsum / nb_aut 
        except:
            sum_deg_cen_cumsum_mean = 0
        share_aff_captured = len(aff_captured)/nb_aut

        self.variables.update({'share_aff_captured':share_aff_captured, 'nb_aut': nb_aut,
                               "sum_deg_cen":sum_deg_cen,"sum_deg_cen_cumsum":sum_deg_cen_cumsum,"sum_deg_cen_cumsum_mean":sum_deg_cen_cumsum_mean  })
    
    def get_nb_entity_and_age_distribution(self,entities,name):
        nb_entity = len(entities)
        ages = [entity['year'] for entity in entities]
        std_age_entitiy = np.std(ages)
        
        self.variables.update({name: nb_entity, name+'_age_std':std_age_entitiy })

    def get_nb_entity_meshterms(self,entities,name):
        nb_entity = len(entities)
        
        self.variables.update({name: nb_entity})

    def get_JIF(self,ISSN):
        ISSN = re.sub('-','',ISSN)
        journal = self.journals[self.journals['Issn'] == ISSN]
        if not journal.empty:
            SJR = float(re.sub(',','.',journal.SJR.iloc[0])) if not pd.isna(journal.SJR.iloc[0]) else None
            journal_ref_per_doc = float(re.sub(',','.',journal['Ref. / Doc.'].iloc[0]))
            journal_cit_per_doc = float(re.sub(',','.',journal['Cites / Doc. (2years)'].iloc[0]))
            journal_category = journal['Categories'].iloc[0]
            if not pd.isna(journal.Coverage.iloc[0]):
                try:
                    journal_first_year = int(journal.Coverage.iloc[0].split('-')[0].split(',')[0]) 
                    journal_age = self.year - journal_first_year
                except:
                    journal_age = None
            else:
                journal_age = None
            self.variables.update({'journal_SJR':SJR,
                                    'journal_ref_per_doc':journal_ref_per_doc,
                                    'journal_cit_per_doc':journal_cit_per_doc,
                                    'journal_category':journal_category,
                                    'journal_age':journal_age})


    def is_review(self,title):
        is_review = 1 if 'review' in title.lower() else 0 
        
        self.variables.update({'is_review':is_review })
    

    def length_text(self,text,name):
        words = text.split()
        words = [word for word in words if len(word)>1]
        lengh_text = len(words)
        
        self.variables.update({name+'_length':lengh_text })

    
    def get_article_variables(self,doc):
        self.variables = {'PMID':doc['PMID'],'year':doc["year"]}
        self.get_nb_cit_ref(doc['PMID'])
        if 'a02_authorlist' in doc:
            self.get_aut_infos(doc['a02_authorlist'])
        if 'c04_referencelist' in doc:
            self.get_nb_entity_and_age_distribution(doc['c04_referencelist'],'c04_referencelist')
        if "a06_meshheadinglist" in doc:
            self.get_nb_entity_meshterms(doc['a06_meshheadinglist'],'a06_meshheadinglist')
        if 'Journal_ISSN' in doc:
            self.get_JIF(doc['Journal_ISSN'])
        if 'ArticleTitle' in doc:
            self.is_review(doc['ArticleTitle'])
            self.length_text(doc['ArticleTitle'],'ArticleTitle')
        if 'a04_abstract' in doc:
            self.length_text(doc['a04_abstract'][0]['AbstractText'],'a04_abstract')
        if 'a05_grantlist' in doc:
            self.variables.update({'nb_grant':len(doc['a05_grantlist'])})
        if 'a05_grantlist' in doc:
            self.variables.update({'nb_grant':len(doc['a05_grantlist'])})                                  
                                   
    def run(self):
        docs = self.collection.find({'year':self.year})
        list_of_insertion = []
        for doc in tqdm.tqdm(docs):
            self.get_article_variables(doc)
            list_of_insertion.append(self.variables)
            if len(list_of_insertion) % 1000 == 0:
                self.db['control_var_2000_2005'].insert_many(list_of_insertion)
                list_of_insertion = []
        self.db['control_var_2000_2005'].insert_many(list_of_insertion)

for year in range(2000,2006):
    CreateVariable(year).run()

#%% Create df for regressions

    
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['pkg']
db_f1000 = client["F1000"]
db_result = client["novelty"]

collection = db['control_var_2000_2005']
collection_f1000 = db_f1000["all"]


collection_shibayama = db_result["output_shibayama"]
collection_author = db_result["output_Author_proximity"]

def get_indicators(id_):
    try:
        DI1 = results["Disruptiveness"][id_]["disruptiveness"]["DI1"]
    except:
        DI1 = None
    try:
        DI5 = results["Disruptiveness"][id_]["disruptiveness"]["DI5"]
    except:
        DI5 = None
    try:
        DI1nok = results["Disruptiveness"][id_]["disruptiveness"]["DI1nok"]
    except:
        DI1nok = None
    try:
        DeIn = results["Disruptiveness"][id_]["disruptiveness"]["DeIn"]
    except:
        DeIn = None
    try:
        Breadth = results["Disruptiveness"][id_]["disruptiveness"]["Breadth"]
    except:
        Breadth = None
    try:
        Depth = results["Disruptiveness"][id_]["disruptiveness"]["Depth"]
    except:
        Depth = None
    try:
        wang_mesh = results['Mesh_year_category_3_1_restricted50_wang'][id_]['Mesh_year_category_wang_3_1_restricted50']["score"]["novelty"]
    except:
        wang_mesh = None  
    try:
        wang_ref = results["c04_referencelist_3_1_restricted50_wang"][id_]["c04_referencelist_wang_3_1_restricted50"]["score"]["novelty"]
    except:
        wang_ref = None
    try:
        foster_mesh = results['Mesh_year_category_foster'][id_]['Mesh_year_category_foster']["score"]["novelty"]
    except:
        foster_mesh = None
    try:
        foster_ref = results['c04_referencelist_foster'][id_]['c04_referencelist_foster']["score"]["novelty"]
    except:
        foster_ref = None
    try:
        uzzi_mesh = results['Mesh_year_category_uzzi'][id_]['Mesh_year_category_uzzi']["score"]["novelty"]
    except:
        uzzi_mesh = None
    try:    
        uzzi_ref = results['c04_referencelist_uzzi'][id_]['c04_referencelist_uzzi']["score"]["novelty"]
    except:
        uzzi_ref = None
    try:
        lee_mesh = results['Mesh_year_category_lee'][id_]['Mesh_year_category_lee']["score"]["novelty"]
    except:
        lee_mesh = None
    try:
        lee_ref = results['c04_referencelist_lee'][id_]['c04_referencelist_lee']["score"]["novelty"]
    except:
        lee_ref = None
    try:
        doc = collection_shibayama.find_one({"PMID":id_,'shibayama_abstract_embedding':{"$exists":1}})
        shibayama_abstract = doc['shibayama_abstract_embedding']["percentiles"]["90%"]
    except:
        shibayama_abstract = None
    try:
        doc = collection_shibayama.find_one({"PMID":id_,'shibayama_title_embedding':{"$exists":1}})
        shibayama_title = doc['shibayama_title_embedding']["percentiles"]["90%"]
    except:
        shibayama_title = None    
        
    try:
        docs = list(collection_author.find({"PMID":id_,'authors_novelty_abstract_5':{"$exists":1}}))
        mean_intra = []
        mean_inter = []
        for doc in docs:
            for author in doc['authors_novelty_abstract_5']["individuals_scores"]:
                mean_intra.append(author["percentiles"]["90%"])
            for author_comb in doc['authors_novelty_abstract_5']["iter_individuals_scores"]:
                mean_inter.append(author_comb["percentiles"]["90%"])
        author_intra_abstract = np.mean(mean_intra)
        author_inter_abstract = np.mean(mean_inter)
    except:
        author_intra_abstract = None
        author_inter_abstract = None
    try:
        docs = list(collection_author.find({"PMID":id_,'authors_novelty_title_5':{"$exists":1}}))
        mean_intra = []
        mean_inter = []
        for doc in docs:
            for author in doc['authors_novelty_title_5']["individuals_scores"]:
                mean_intra.append(author["percentiles"]["10%"])
            for author_comb in doc['authors_novelty_title_5']["iter_individuals_scores"]:
                mean_inter.append(author_comb["percentiles"]["10%"])
        author_intra_title = np.mean(mean_intra)
        author_inter_title = np.mean(mean_inter)
    except:
        author_intra_title = None
        author_inter_title = None
        
    return [DI1, DI5, DI1nok, DeIn, Breadth, Depth, wang_mesh, wang_ref, foster_mesh, foster_ref, 
            uzzi_mesh, uzzi_ref, lee_mesh, lee_ref, shibayama_abstract, shibayama_title,author_intra_abstract,author_inter_abstract,
            author_intra_title,author_inter_title]
    

def get_cat_f1000(id_):
    doc = collection_f1000.find_one({"PMID":id_})
    if doc:
        categories = [j["categories"]for j in [doc["Recommendations"][i] for i in doc["Recommendations"]]]
        categories = [item for sublist in categories for item in sublist]
        try:
            main_category = max(set(categories), key=categories.count)
        except:
            main_category = None
        f1000_score = doc["global_score"]
        if categories:
            categories = "\n".join(categories)
        else:
            categories = None
    else:
        main_category = None
        f1000_score = None
        categories = None
    return [categories,main_category, f1000_score]
    
def get_control_variables(doc):
    PMID = doc["PMID"]
    year = doc["year"]
    try:
        nb_cit = doc["nb_cit"]
    except:
        nb_cit = None
    try:
        nb_meshterms = doc["a06_meshheadinglist"]
    except:
        nb_meshterms = None
    try:
        sum_deg_cen = doc["sum_deg_cen"]
    except:
        sum_deg_cen = None
    try:
        sum_deg_cen_cumsum = doc["sum_deg_cen_cumsum"]
    except:
        sum_deg_cen_cumsum = None        

    try:
        sum_deg_cen_cumsum_mean = doc["sum_deg_cen_cumsum_mean"]
    except:
        sum_deg_cen_cumsum_mean = None    
        
    try:
        nb_ref = doc["nb_ref"]
    except:
        nb_ref = None
    try:
        share_aff_captured = doc["share_aff_captured"]
    except:
        share_aff_captured = None
    try:
        nb_aut = doc["nb_aut"]
    except:
        nb_aut = None
    try:
        c04_referencelist = doc["c04_referencelist"]
    except:
        c04_referencelist = None
    try:
        c04_referencelist_age_std = doc["c04_referencelist_age_std"]
    except:
        c04_referencelist_age_std = None
    try:
        journal_SJR = doc["journal_SJR"]
    except:
        journal_SJR = None
    try:
        journal_ref_per_doc = doc["journal_ref_per_doc"]
    except:
        journal_ref_per_doc = None
    try:
        journal_cit_per_doc = doc["journal_cit_per_doc"]
    except:
        journal_cit_per_doc = None
    try:
        journal_category = doc["journal_category"]
    except:
        journal_category = None
    try:
        journal_age = doc["journal_age"]
    except:
        journal_age = None
    try:
        is_review = doc["is_review"]
    except:
        is_review = None
    try:
        ArticleTitle_length = doc["ArticleTitle_length"]
    except:
        ArticleTitle_length = None
    try:
        a04_abstract_length = doc["a04_abstract_length"]
    except:
        a04_abstract_length = None
    return [PMID,year,nb_cit,nb_ref, nb_meshterms, sum_deg_cen, sum_deg_cen_cumsum, sum_deg_cen_cumsum_mean, share_aff_captured,nb_aut,
            c04_referencelist,c04_referencelist_age_std, journal_SJR, journal_ref_per_doc, journal_cit_per_doc, journal_category, journal_age,
            is_review, ArticleTitle_length,a04_abstract_length]

columns = ["PMID","year","nb_cit","nb_ref","nb_meshterms","sum_deg_cen","sum_deg_cen_cumsum", "sum_deg_cen_cumsum_mean",
           "share_aff_captured","nb_aut","c04_referencelist",
           "c04_referencelist_age_std", "journal_SJR", "journal_ref_per_doc", "journal_cit_per_doc",
           "journal_category", "journal_age", "is_review", "ArticleTitle_length","a04_abstract_length",
           "DI1","DI5","DI1nok","DeIn","Breadth","Depth","wang_mesh", "wang_ref","foster_mesh",
           "foster_ref","uzzi_mesh","uzzi_ref","lee_mesh","lee_ref", "shibayama_abstract", "shibayama_title",
           "author_intra_abstract","author_inter_abstract", "author_intra_title","author_inter_title",
           "categories", "main_category", "f1000_score"]

list_of_insertion = []
    
for year in tqdm.tqdm(range(2000,2006)):
    docs = collection.find({"year":year})
    files = glob.glob('Result/**/{}.json'.format(year), recursive = True)
    results = {}
    for file in files:
        indicator = file.split("\\")[1]
        if indicator != "Disruptiveness":
            indicator = "{}".format(file.split("\\")[2]) + "_" + indicator
        results[indicator] = {paper["PMID"]:paper for paper in  json.load(open(file))}
    for doc in tqdm.tqdm(docs):
        id_ = doc["PMID"]
        cv = get_control_variables(doc)        
        indicators = get_indicators(id_)
        f1000 = get_cat_f1000(id_)
        list_of_insertion.append(cv+indicators+f1000)


df=pd.DataFrame(list_of_insertion,columns=columns)

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['novelty']
collection = db['output_Author_proximity']


list_of_insertion_intra = []
list_of_insertion_inter = []

for pmid in tqdm.tqdm(df["PMID"]):
    docs = list(collection.find({"PMID":pmid,'authors_novelty_abstract_5':{"$exists":1}}))
    for doc in docs:
        try:
            for author in doc['authors_novelty_abstract_5']["individuals_scores"]:
                list_of_insertion_intra.append([doc["PMID"], author["percentiles"]["90%"]])
        except Exception as e:
            continue
        try:
            for author_comb in doc['authors_novelty_abstract_5']["iter_individuals_scores"]:
                list_of_insertion_inter.append([doc["PMID"], author_comb["percentiles"]["90%"]])
        except Exception as e:
            continue      
        
        
df_intra = pd.DataFrame(list_of_insertion_intra,columns=["PMID","intra"])
df_inter = pd.DataFrame(list_of_insertion_inter,columns=["PMID","inter"])
df_intra['percent_rank'] = df_intra['intra'].rank(pct=True)
df_inter['percent_rank'] = df_inter['inter'].rank(pct=True)


df_temp = pd.merge(df, df_intra, on = "PMID", how = 'outer')
df.index = df["PMID"]


count_diverse = {i:0 for i in df["PMID"]}
share_diverse = {i:0 for i in df["PMID"]}
count_typical = {i:0 for i in df["PMID"]}
share_typical = {i:0 for i in df["PMID"]}


for row in tqdm.tqdm(df_temp[df_temp["percent_rank"]>0.90].groupby("PMID").agg({'PMID':'first', 'percent_rank': 'count', 'nb_aut': 'first'}).iterrows()):
    pmid = row[1]["PMID"]
    count_diverse[pmid] = row[1]["percent_rank"]
    share_diverse[pmid] = row[1]["percent_rank"]/row[1]["nb_aut"]

for row in tqdm.tqdm(df_temp[df_temp["percent_rank"]<0.50].groupby("PMID").agg({'PMID':'first', 'percent_rank': 'count', 'nb_aut': 'first'}).iterrows()):
    pmid = row[1]["PMID"]
    count_typical[pmid] = row[1]["percent_rank"]
    share_typical[pmid] = row[1]["percent_rank"]/row[1]["nb_aut"]
    

df["share_diverse"] = df['PMID'].map(share_diverse)
df["count_diverse"] = df['PMID'].map(count_diverse)
df["share_typical"] = df['PMID'].map(share_typical)
df["count_typical"] = df['PMID'].map(count_typical)

df.to_csv("Data/regression.csv",index=False)

#df_temp = pd.read_csv("Data/regression.csv")[["PMID",'uzzi_mesh', 'uzzi_ref']]
#df = pd.merge(df_temp, df.reset_index(drop=True).drop(['uzzi_mesh', 'uzzi_ref'], axis=1), on='PMID', how='inner')
#doc = collection.find_one({"PMID":11051549})


#df = pd.read_csv("Data/regression.csv")
#df = df.drop_duplicates(subset="PMID", keep='first')
#df.to_csv("Data/regression.csv",index=False)
{AND_ID:8542016}

{PMID:11802423}
10592202
10592278
11072346