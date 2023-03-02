import pymongo
import xml.etree.ElementTree as ET
import yaml
import os
import tqdm

os.chdir('../..')

with open("mongo_config.yaml", "r") as infile:
    pars = yaml.safe_load(infile)['PC_BETA']
    
client = pymongo.MongoClient(pars['client_name'])
db = client[pars['db_name']]
collection = db["meshterms"]

tree = ET.parse('Paper/Data/meshterms/desc2021.xml')

meshterms = tree.findall('DescriptorRecord')



for meshterm in tqdm.tqdm(meshterms):
    mesh = {}
    try:
        DescriptorUI = meshterm.find('DescriptorUI').text
        mesh.update({'DescriptorUI':DescriptorUI})
    except: 
        pass
       
    try:
        DescriptorName = meshterm.find('DescriptorName').find('String').text
        mesh.update({'DescriptorName':DescriptorName})
    except: 
        pass
    
    try:
        DateCreated = {} 
        for date_c_info in meshterm.find('DateCreated'):
            var = date_c_info.tag
            DateCreated.update({
                str(var):int(date_c_info.text)
                })
        mesh.update({'DateCreated':DateCreated})
    except: 
        pass
    
    try:
        DateRevised = {} 
        for date_r_info in meshterm.find('DateRevised'):
            var = date_r_info.tag
            DateRevised.update({
                str(var):int(date_r_info.text)
                })
        mesh.update({'DateRevised':DateRevised})
    except: 
        pass
    
    try:
        DateEstablished = {} 
        for date_e_info in meshterm.find('DateEstablished'):
            var = date_e_info.tag
            DateEstablished.update({
                str(var):int(date_e_info.text)
                })
        mesh.update({'DateEstablished':DateEstablished})
    except: 
        pass
    
    try:
        AllowableQualifiersList = []
        for qualifier in meshterm.find('AllowableQualifiersList'):
            AllowableQualifiersList.append({
                'QualifierUI':qualifier.find('QualifierReferredTo').find('QualifierUI').text,
                'QualifierName':qualifier.find('QualifierReferredTo').find('QualifierName').find('String').text,
                'Abbreviation':qualifier.find('Abbreviation').text
                })
        mesh.update({'AllowableQualifiersList':AllowableQualifiersList})
    except: 
        pass
    
    try:
        TreeNumberList = []
        for treenum in meshterm.find('TreeNumberList'):
            TreeNumberList.append(treenum.text)
        mesh.update({'TreeNumberList':TreeNumberList})
    except: 
        pass
    
    collection.insert(mesh)    
    #except:
    #    print('non')
    
collection.create_index([ ("DescriptorUI", 1) ])