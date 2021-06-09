from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pymongo
import tqdm
import time
import re
import datetime
import calendar
from selenium.webdriver.firefox.options import Options
import requests
import json




month_dict = {month: index for index, month in enumerate(calendar.month_name) if month}
month_dict_abbr = {month: index for index, month in enumerate(calendar.month_abbr) if month}
def clean_date(date,month_dict):
    date = date.split(" ")
    day = re.sub("[a-z]*","",date[0])
    month = str(month_dict[date[1]])
    year = date[2]
    s = "/".join([day,month,year])
    unix = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
    return unix


client = pymongo.MongoClient('mongodb://Pierre:ilovebeta67@localhost:27017')
mydb = client["F1000"] 
collection = mydb["hrefs"]
options = Options()
options.headless = True
driver = webdriver.Firefox()


classif = ["CHANGES_CLINICAL_PRACTICE","CONFIRMATION","CONTROVERSIAL","GOOD_FOR_TEACHING","HYPOTHESIS","NEGATIVE","NEW_FINDING","NOVEL_DRUG_TARGET",
           "REFUTATION","TECHNICAL_ADVANCE"]

def get_novelty(collection,driver):
    driver.get("https://facultyopinions.com/prime/recommendations?evaluationClassifications=NEW_FINDING&page=1&show=100")
    WebDriverWait(driver, 10).until(lambda driver: driver.find_elements(By.XPATH, "//li[@data-test-id='page-last']"))
    n_pages = int(driver.find_element(By.XPATH, "//li[@data-test-id='page-last']").text)
    
    for i in tqdm.tqdm(range(n_pages),total=n_pages):
        if i != 0:
            driver.get("https://facultyopinions.com/prime/recommendations?evaluationClassifications=NEW_FINDING&page={}&show=100".format(i+1))
        WebDriverWait(driver, 10).until(lambda driver: driver.find_elements(By.XPATH, "//div[@class='css-19837md recommendation']"))
        publications = driver.find_elements(By.XPATH, "//div[@class='css-19837md recommendation']")
        post_list = []
        for pub in publications:
            title = pub.find_element(By.XPATH,".//a[@class='css-1hc97a8']").text
            tags = pub.find_elements(By.XPATH, ".//span[@class='css-w8utjc']")
            recommender_date = pub.find_element(By.XPATH, ".//span[@class='css-1mb0qwt']").text
            recommender = re.sub("\(([^\)]+)\)","",recommender_date)[:-1].lstrip()
            in_parent =re.findall("\((.*?)\)",recommender_date)
            r = re.compile('.*?([0-9]+)$')
            date = list(filter(r.match, in_parent))[0]
            unix = clean_date(date,month_dict)
            tags = [tag.text for tag in tags]
            post = {"title":title,
                    "tags":tags,
                    "recommender":recommender,
                    "date_recommandation":date,
                    "unix_recommandation":unix}
            post_list.append(post)
        collection.insert_many(post_list)
        time.sleep(10)
       
get_novelty(collection,driver)

def get_hrefs_all(collection,driver):
    driver.get("https://facultyopinions.com/prime/recommendations?page=1&show=100")
    WebDriverWait(driver, 10).until(lambda driver: driver.find_elements(By.XPATH, "//li[@data-test-id='page-last']"))
    n_pages = int(driver.find_element(By.XPATH, "//li[@data-test-id='page-last']").text)
    
    for i in tqdm.tqdm(range(n_pages),total=n_pages):
        if i != 0:
            driver.get("https://facultyopinions.com/prime/recommendations?page={}&show=100".format(i+1))
        WebDriverWait(driver, 10).until(lambda driver: driver.find_elements(By.XPATH, "//div[@class='css-19837md recommendation']"))
        publications = driver.find_elements(By.XPATH, "//div[@class='css-19837md recommendation']")
        post_list = []
        for pub in publications:
            href = pub.find_element(By.XPATH,".//a[@class='css-1hc97a8']").get_attribute("href")
            post = {"href":href}
            post_list.append(post)
        collection.insert_many(post_list)
        time.sleep(10)
       
get_hrefs_all(collection,driver)


user_name = "kevin.wirtz@unistra.fr"
password = "0165Noisete."

def connect_driver(username,password,driver):
    driver.get("https://facultyopinions.com/prime/signin?target=%2Fprime%2Farticle%3FarticleId%3D738472488%26target%3D%2Fprime%2F738472488")
    
    element = driver.find_element_by_name("j_username")
    element.send_keys(user_name)
    
    element = driver.find_element_by_name("j_password")
    element.send_keys(password)
    
    driver.find_element_by_xpath("//input[@value='Sign in']").click()



connect_driver(user_name,password,driver)
collection = mydb["hrefs"]
docs = collection.find({},no_cursor_timeout=True)


collection_new = mydb["all"]

first_run = False

if first_run:
    it = 0
else:
    with open("D:/kevin_data/F1000_lastit.txt","r") as f:
        it = int(f.read())

for doc in tqdm.tqdm(docs[it:]):
    driver.get(doc["href"])
    
    WebDriverWait(driver, 10).until(lambda driver: driver.find_elements(By.XPATH, "//div[@class='recommendations-wrapper']"))
    try:
        doi = driver.find_element(By.XPATH, "//a[@id='article-doi']").text.split("doi.org/")[-1]
    except:
        doi = None
    # Reco
    recommendations = driver.find_elements(By.XPATH, "//article[@class='recommendation']")
    dict_reco = {} 
    i = 0
    for reco in recommendations:
        authors = reco.find_elements(By.XPATH,".//div[contains(@class,'member-box recommending-member')]")
        names_reco = [author.find_element(By.XPATH,".//a[@class='member-name']").text for author in authors]
        knowledges =  [[domain.text for domain in author.find_elements(By.XPATH,".//p[@class='faculties']/a")] for author in authors]
        affs_reco = [[aff.text for aff in author.find_elements(By.XPATH,".//div[@class='organisation-details']/p")] for author in authors]
        cats = [cat.text for cat in reco.find_elements(By.XPATH,".//div[@class='classifications']/span")]
        rating = reco.find_element(By.XPATH,".//span[@class='rating-label']").text
        date = reco.find_element(By.XPATH,".//span[@class='recommendation-date']").text
        unix_date = clean_date(date,month_dict_abbr)
        text = reco.find_element(By.XPATH,".//section[@class='recommendation-content']/p").text
        list_orcid = []
        for author in authors:
            try:
                list_orcid.append(author.find_element(By.XPATH,".//a[@id='orcid-tooltip-1037939']").get_attribute("href"))
            except:
                list_orcid.append(None)
        dict_reco[str(i)] = {"authors":names_reco,
                             "orcid":list_orcid,
                             "domain":knowledges,
                             "affs":affs_reco,
                             "cats":cats,
                             "rating":rating,
                             "date":date,
                             "unix_date":unix_date,
                             "text":text}
        i += 1
    
    try:
        driver.find_element(By.XPATH, "//span[@class='author affiliations-trigger modal-trigger']").click()    
    
        affs_corresp = driver.find_elements(By.XPATH, "//div[@id='affiliations-popup']//div[@class='affiliations']/p[@class='affiliation']")
        affs_dict = {re.findall("[0-9]+",aff.text)[0]:re.sub(re.findall("[0-9]+",aff.text)[0],"",aff.text,1) for aff in affs_corresp}
        authors = driver.find_elements(By.XPATH, "//div[@id='affiliations-popup']//div[@class='authors']/div[@class='author']") + driver.find_elements(By.XPATH, "//div[@id='affiliations-popup']//div[@class='authors']/div[@class='author additional-author']")
        authors_aff = driver.find_elements(By.XPATH, "//div[@id='affiliations-popup']//div[@class='authors']//sup[@class='author-affiliations-indexes']")
        author = authors[0]
        affiliation = authors_aff[0]
        authors_dict = {}
        j = 0
        for author,affiliation in zip(authors,authors_aff):
            author_name = re.sub(",","",re.sub("[0-9]","", author.find_element(By.XPATH,".//a[@class='author-name']").text))
            author_aff = [affs_dict[re.sub(" ","",aff)] for aff in affiliation.text.split(",")]
            try:
                mail = author.find_element(By.XPATH,".//a[@class='author-email']").get_attribute("href")
            except:
                mail = None
            authors_dict[str(j)] = {"name":author_name,"affs":author_aff,"mail":mail}
            j += 1 
        
        post = {"recommendations":dict_reco,
                "authors_dict":authors_dict,
                "doi":doi}
        
    except:
        post = {"recommendations":dict_reco,
                "authors_dict":None,
                "doi":doi}
    collection_new.insert_one(post)
    it += 1
    with open("D:/kevin_data/F1000_lastit.txt","w+") as f:
        f.write(str(it))
    time.sleep(9)    


docs = collection_new.find({"PMID":{"$exists":0}}, no_cursor_timeout=True)

i = 0
for doc in tqdm.tqdm(docs):
    if i < 85600:
        i += 1 
        continue
    doi = doc["doi"]
    try:
        if doi != None and doi.startswith("10"):
            ids = requests.get("https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={}&format=json&showaiid=yes&tool=my_tool&email=kevin.wirtz%40unistra.fr&.submit=Submit&api_key=167b804841f26407673837b9c02d9d6f7e08".format(doi)) 
            papers = json.loads(ids.content)
            for paper in papers["records"]:
                if paper["pmid"]:
                    collection_new.update_one({'doi': paper["doi"]}, {'$set': {'PMID': int(paper["pmid"])}})
    except:
        pass

   

# bug to solve https://facultyopinions.com/prime/717247956