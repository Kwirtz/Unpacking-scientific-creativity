from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
import pymongo
import tqdm
import time
import re
import datetime
import calendar
import requests
import json

class dl_f1000():

    def __init__(self, username, password, mongo_uri, db_name):
        self.username = username
        self.password = password
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        client = pymongo.MongoClient(self.mongo_uri)
        self.mydb = client[self.db_name]
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox()

    def clean_date(self,date):
        month_dict = {month: index for index, month in enumerate(calendar.month_abbr) if month}
        date = date.split(" ")
        day = re.sub("[a-z]*","",date[0])
        month = str(month_dict[date[1]])
        year = date[2]
        s = "/".join([day,month,year])
        unix = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
        return unix
    
    def get_hrefs_all(self, fs_file = None):

        if fs_file != None:
            try:
                with open(fs_file,"r") as f:
                    processed = int(f.read())
            except:
                processed = 0   
                
        collection = self.mydb["hrefs"]
        self.driver.get("https://facultyopinions.com/prime/recommendations?evaluationPublishedInLastDays=&page=1&show=100")
        WebDriverWait(self.driver, 10).until(lambda driver: self.driver.find_elements(By.XPATH, "//span[@class='css-a23cf7']"))
        n_pages = int(re.sub('\D', '', self.driver.find_element(By.XPATH, "//span[@class='css-a23cf7']").text))
        print(n_pages)
        for i in tqdm.tqdm(range(n_pages),total=n_pages):
            if fs_file != None:
                if i < processed:
                    continue
            if i != 0:
                self.driver.get("https://facultyopinions.com/prime/recommendations?evaluationPublishedInLastDays=&page={}&show=100".format(i+1))
            WebDriverWait(self.driver, 10).until(lambda driver: self.driver.find_elements(By.XPATH, ".//article[@class='css-35jzck e1pdjjwz9']"))
            publications = self.driver.find_elements(By.XPATH, ".//article[@class='css-35jzck e1pdjjwz9']")
            post_list = []
            for pub in publications:
                href = pub.find_element(By.XPATH,".//a[@class='css-10i63lj e1pdjjwz7']").get_attribute("href")
                post = {"href":href}
                post_list.append(post)
            collection.insert_many(post_list)
            time.sleep(10)
            if fs_file:
                with open(fs_file, "w+") as f:
                    f.write(str(i))

    def connect_driver(self):
        self.driver.get("https://facultyopinions.com/prime/signin?target=%2Fprime%2Farticle%3FarticleId%3D738472488%26target%3D%2Fprime%2F738472488")
        
        element = self.driver.find_element_by_name("j_username")
        element.send_keys(self.username)
        
        element = self.driver.find_element_by_name("j_password")
        element.send_keys(self.password)
        
        self.driver.find_element_by_xpath("//input[@value='Sign in']").click()
    
    def get_infos_utils(self, url):
        collection = self.mydb["all"]        
        self.driver.get(url)
        recommendations = self.driver.find_elements(By.XPATH, "//article[@class='recommendation']")
        list_reco = {}
        list_reco["Recommendations"] = {}
        i = 0
        for reco in recommendations:
            WebDriverWait(self.driver, 10).until(lambda driver: self.driver.find_elements(By.XPATH, ".//div[@class='recommendations-badge']"))
            cats = [cat.text for cat in reco.find_elements(By.XPATH,".//div[@class='classifications']/span")]
            rating = reco.find_element(By.XPATH,".//span[@class='rating-label']").text
            date = reco.find_element(By.XPATH,".//span[@class='recommendation-date']").text
            unix_date = self.clean_date(date)
            text = reco.find_element(By.XPATH,".//section[@class='recommendation-content']/p").text
            authors = reco.find_elements(By.XPATH,".//div[contains(@class,'member-box recommending-member')]")
            authors_to_insert = []
            for author in authors:
                author_name = author.find_element(By.XPATH,".//a[@class='member-name']").text
                faculties = author.find_elements(By.XPATH,".//p[contains(@class,'faculties')]/a")
                faculties = [faculty.text for faculty in faculties]
                affs = author.find_elements(By.XPATH,".//div[@class='organisation-details']")
                list_aff_cleaned = []
                for aff in affs:
                    list_aff_cleaned.append("<EOT> ".join([aff.text for aff in aff.find_elements(By.XPATH,".//p")]))
                try:
                    orcid = author.find_element(By.XPATH,".//a[@id='orcid-tooltip-1037939']").get_attribute("href")
                except:
                    orcid = None
                authors_to_insert.append({"name":author_name,"faculties":faculties, "affs":list_aff_cleaned,"orcid":orcid})
            element_to_hover_over = self.driver.find_element(By.XPATH,".//div[@class='recommendations-badge']")
            try:
                list_reco["PMID"] = (int(element_to_hover_over.find_element(By.XPATH,"./div").get_attribute("data-pmid")))
            except:
                continue
            try:
                hover = ActionChains(self.driver).move_to_element(element_to_hover_over)
                hover.perform()
                WebDriverWait(self.driver, 10).until(lambda driver: self.driver.find_elements(By.XPATH, ".//span[@class='sw3bb7a']"))
            except Exception as e:
                print(str(e))
            try:
                list_reco["global_score"] = float(element_to_hover_over.find_element(By.XPATH,".//span[@class='sw3bb7a']").text)
                list_reco["RCR_WSS"] = [i.text for i in element_to_hover_over.find_elements(By.XPATH,".//span[@class='bzytydn']//span/strong")]
            except Exception as e:
                print(str(e))
            list_reco["Recommendations"][str(i)] = {"categories":cats,"rating":rating,"date":unix_date,"text":text,
                                 "authors":authors_to_insert}
            i += 1
        collection.insert_one(list_reco)
        time.sleep(3)
            
    def get_infos(self, fs_file = None):
        
        if fs_file != None:
            try:
                with open(fs_file+ "/F1000_lastit.txt","r") as f:
                    processed = int(f.read())
            except Exception as e:
                print(str(e))
                processed = 0      
                
        collection = self.mydb["hrefs"]
        docs = collection.find({},no_cursor_timeout=True)
        it = 0
        for doc in tqdm.tqdm(docs):
            if fs_file != None:
                if it < processed:
                    it += 1
                    continue
            url = doc["href"]
            self.get_infos_utils(url = url)
            if fs_file:
                it += 1
                with open(fs_file+ "/F1000_lastit.txt","w+") as f:
                    f.write(str(it))
            
instance = dl_f1000(username = "bot_alfred@outlook.fr", password = "Bot012345678914061923",
         mongo_uri = 'mongodb://localhost:27017', db_name= "F1000_2")

# Connect to go paper by paper
instance.connect_driver()

# First get href
instance.get_hrefs_all(fs_file = "D:/kevin_data/F1000_hrefs_lastpage.txt")

# Iterate through hrefs
instance.get_infos(fs_file = "D:/kevin_data")


