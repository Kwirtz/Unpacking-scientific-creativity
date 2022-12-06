import pymongo
import pandas as pd 
import numpy as np
import re
import tqdm

def get_scimago_file(year):

    journals = pd.read_csv(r'Data\Scimago_j_list\scimagojr {}.csv'.format(str(year)),
                sep=';')

    journals['Issn'] = journals['Issn'].str.split(', ')
    journals = journals.explode('Issn')
    journals['Issn'] = journals['Issn'].astype(str)
    return journals


class CreateVariable:
    
    def __init__(self,
                year):
    
        client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = client['PKG']
        self.collection = self.db['articles_2000_2005']
        self.collection_cit_net = client['novelty_final']['Citation_network']
        self.year = year
        self.journals = get_scimago_file(self.year)
        
    def get_nb_cit_ref(self,pmid):
        doc = self.collection_cit_net.find_one({'PMID':pmid})
        if 'citations' in doc:
            nb_ref = len(doc['citations']['refs'])
            nb_cit = len(doc['citations']['cited_by'])
            
            self.variables.update({'nb_cit':nb_cit, 'nb_ref': nb_ref})
    

    def get_aut_infos(self,author_list):
        nb_aut = len(author_list)
        aff_captured = []
        for author in author_list:
            if author['Affiliation'] != '':
                aff_captured.append(author['Affiliation'])
        share_aff_captured = len(aff_captured)/nb_aut

        self.variables.update({'share_aff_captured':share_aff_captured, 'nb_aut': nb_aut})
    
    def get_nb_entity_and_age_distribution(self,entities,name):
        nb_entity = len(entities)
        ages = [entity['year'] for entity in entities]
        std_age_entitiy = np.std(ages)
        
        self.variables.update({name: nb_entity, name+'_age_std':std_age_entitiy })


    def get_JIF(self,ISSN):
        ISSN = re.sub('-','',ISSN)
        journal = self.journals[self.journals['Issn'] == ISSN]
        if not journal.empty:
            SJR = float(re.sub(',','.',journal.SJR.iloc[0])) if not pd.isna(journal.SJR.iloc[0]) else None
            journal_ref_per_doc = float(re.sub(',','.',journal['Ref. / Doc.'].iloc[0]))
            journal_cit_per_doc = float(re.sub(',','.',journal['Cites / Doc. (2years)'].iloc[0]))
            journal_category = journal['Categories'].iloc[0]
            if not pd.isna(journal.Coverage.iloc[0]):
                journal_first_year = int(journal.Coverage.iloc[0].split('-')[0].split(',')[0]) 
                journal_age = self.year - journal_first_year
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
        self.variables = {'PMID':doc['PMID']}
        self.get_nb_cit_ref(doc['PMID'])
        if 'a02_authorlist' in doc:
            self.get_aut_infos(doc['a02_authorlist'])
        if 'c04_referencelist' in doc:
            self.get_nb_entity_and_age_distribution(doc['c04_referencelist'],'c04_referencelist')
        if 'Mesh_year_category' in doc:
            self.get_nb_entity_and_age_distribution(doc['Mesh_year_category'],'Mesh_year_category')
        if 'Journal_ISSN' in doc:
            self.get_JIF(doc['Journal_ISSN'])
        if 'ArticleTitle' in doc:
            self.is_review(doc['ArticleTitle'])
            self.length_text(doc['ArticleTitle'],'ArticleTitle')
        if 'a04_abstract' in doc:
            self.length_text(doc['a04_abstract'][0]['AbstractText'],'a04_abstract')
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
