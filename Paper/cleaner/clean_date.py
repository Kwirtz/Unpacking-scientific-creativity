import pymongo
import yaml
import tqdm
import time
import datetime
import calendar

with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_Kevin']
client_name = pars["pymongo_connection"]


client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['pkg']
collection = db['articles']




def create_year(collection, index = False):
    
    month_abbr2date = {month:i for month,i in zip(calendar.month_abbr,[str(j)  if len(str(j)) > 1 else "0" + str(j) for j in range(13)])}
    docs = collection.find({})    
    for doc in tqdm.tqdm(docs):
        year = doc["Journal_JournalIssue_PubDate_Year"]
        month = doc["Journal_JournalIssue_PubDate_Month"]
        medline = doc["Journal_JournalIssue_PubDate_MedlineDate"]
        query = {'PMID':int(doc['PMID'])}
        
        if year != "" and month != "":
            month = month_abbr2date[month]
            year = year
            s = month + "/" + year
            unix = time.mktime(datetime.datetime.strptime(s, "%m/%Y").timetuple())
            doc_infos = {"year": int(year),"yearmonth": int(year+month), "unix":unix}
            newvalues = {'$set':doc_infos}
            collection.update_one(query,newvalues)
        
        elif year != "" and month == "":
            year = year
            unix = time.mktime(datetime.datetime.strptime(year, "%Y").timetuple())
            doc_infos = {"year": int(year), "unix":unix}
            newvalues = {'$set':doc_infos}
            collection.update_one(query,newvalues)
        
        elif medline != "":
            medline = medline.split("-")[0]
            medline_month = month_abbr2date[medline.split(" ")[1]]
            medline_year = medline.split(" ")[0]
            s = medline_month + "/" + medline_year
            unix = time.mktime(datetime.datetime.strptime(s, "%m/%Y").timetuple())
            doc_infos = {"year": int(medline_year),"yearmonth": int(medline_year+medline_month), "unix":unix}             
            newvalues = {'$set':doc_infos}
            collection.update_one(query,newvalues)        
        else:
            continue
    if index == True:  
        collection.create_index([ ("year",1) ])
        collection.create_index([ ("yearmonth",1) ])

create_year(collection)



#collection.update({}, {'$unset': {'unix':1}}, multi=True)


