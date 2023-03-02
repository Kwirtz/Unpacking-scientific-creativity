import yaml
import pymongo
import tqdm

def get_author_profile(doc,
                       var_id,
                       var_auth_id, 
                       var_year,
                        client_name,
                        db_name,
                        collection_articles,
                        collection_authors):
      
    client = pymongo.MongoClient(client_name)
    db = client[db_name]
    collection_authors = db[collection_authors]
    collection_articles = db[collection_articles]
    authors_profiles = list()
    current_year = doc[var_year]
    for auth in doc['a02_authorlist']:
        profile = collection_authors.find({var_auth_id,auth['AID']})[0]
        abs_profile = profile['embedded_abs_wma'][str(current_year)]
        title_profile = profile['embedded_title_wma'][str(current_year)]
        authors_profiles.append({'AND_ID' : auth['AID'],
                                 'abs_profile' : abs_profile,
                                 'title_profile' :title_profile})
    collection_articles.update_one({var_id:doc['var_id']},
                                   {'$set':{'authors_profiles':authors_profiles}})